"""
make_enhanced_plots.py
================================================================================
这个文件做什么 (What this file does)
  为全部 48 组画四类「增强图」，比基础图更直观地展示局部谁领先。
  Draw four kinds of "enhanced" figures per pair that show local lead direction
  more vividly than the base plots.

为什么这么做 (Why)
  基础时序图看不清隔夜断点和"某段里谁先动"；增强图把盘连盘、按滚动互相关上色、
  标出最大变动点，让领先方向可在图上逐段、逐点找到依据。
  Base plots hide overnight breaks and local lead direction; these bridge sessions,
  color by rolling cross-correlation, and mark the biggest moves so every claim is
  anchored on the chart.

思路 / 产图 (Approach / figures, 数据太稀疏者自动跳过)
  {tag}_zoom2.png      盘连盘放大：压掉隔夜空档，收盘->开盘用虚线连、收盘点画竖线；
                       背景按滚动互相关上色（红=Kalshi 领先，蓝=ETF 领先）
  {tag}_segments.png   分段放大：每个活跃交易日一个子图，同样滚动互相关上色
  {tag}_event.png      event 视角：横轴=事件序号（非钟表时间），对应 event 模式
  {tag}_leadglance.png 一眼看谁先动：标出两边最大的 3 次变动(K#/E#)，下方逐条给 lag 与领先方

  局部领先判定（滚动互相关）：在 win 个 bar 滑窗内，对滞后 l∈[-L,L] 算
  corr(ETF_ret_t, Δprob_{t-l})，取 |corr| 最大的 l；l>0->Kalshi 领先，l<0->ETF 领先，
  |corr|<min_corr 视为不确定（不上色）。

输出 (Outputs)
  plots/{tag}_zoom2.png / _segments.png / _event.png / _leadglance.png
  存放位置：leadlag/pipeline/plots/

函数 (Functions)
  build_aligned     放大窗内两边 median-resample + 规则网格对齐 + 滚动领先标注
  rolling_who_leads 逐 bar 滚动互相关判定局部领先 (+1 Kalshi / -1 ETF / 0 不确定)
  shade_who         按 who 的连续同值段给背景上色
  plot_zoom2        画盘连盘放大图
  plot_segments     画每日分段放大图
  plot_event        画 event 视角图
  plot_leadglance   画"一眼看谁先动"图 + 逐条 lag 表
  main              逐对加载数据、构造对齐序列、出四类图
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import pandas as pd

import leadlag_common as C
from make_pair_plots import zoom_window, snap_plot_bar, PLOT_BAR_LABEL, C_KAL, C_ETF

PLOTDIR = C.HERE / "plots"
SIG = pd.read_csv(C.SIG_PAIRS_CSV)

C_LEAD_K = "#e74c3c"   # Kalshi 领先 背景
C_LEAD_E = "#3498db"   # ETF 领先 背景

# 滚动互相关参数
XCORR_WIN   = 21       # 滑窗 bar 数
XCORR_LMAX  = 5        # 最大滞后 bar
XCORR_MINC  = 0.15     # |corr| 阈值，低于视为不确定


def build_aligned(kalshi, etf_tk, lo, hi, freq):
    """放大窗内，Kalshi prob 与 ETF mid 各自 median-resample 到 freq，逐交易日规则网格对齐(ffill)。"""
    kz = kalshi[(kalshi["ts_et"] >= lo) & (kalshi["ts_et"] <= hi)]
    ez = etf_tk[(etf_tk["ts_et"] >= lo) & (etf_tk["ts_et"] <= hi)]
    kb = C.bar_median_series(kz, "prob", freq)
    eb = C.bar_median_series(ez, "mid", freq)
    if kb.empty or eb.empty:
        return None
    frames = []
    for d in sorted(set(kb["date"]).union(set(eb["date"]))):
        kd = kb[kb["date"] == d].set_index("ts_et")["prob"]
        ed = eb[eb["date"] == d].set_index("ts_et")["mid"]
        if kd.empty or ed.empty:
            continue
        start = min(kd.index.min(), ed.index.min())
        end   = max(kd.index.max(), ed.index.max())
        grid = pd.date_range(start, end, freq=freq)
        prob = kd.reindex(grid).ffill()
        mid  = ed.reindex(grid).ffill().bfill()
        df = pd.DataFrame({"ts_et": grid, "prob": prob.values, "mid": mid.values, "date": d})
        df = df.dropna(subset=["prob", "mid"]).reset_index(drop=True)
        if len(df) < 3:
            continue
        df["dprob"]  = df["prob"].diff().fillna(0.0)
        df["etfret"] = np.log(df["mid"]).diff().fillna(0.0)
        df["who"]    = rolling_who_leads(df["dprob"].values, df["etfret"].values)
        frames.append(df)
    if not frames:
        return None
    al = pd.concat(frames, ignore_index=True)
    al["cumret_pct"] = al["etfret"].cumsum() * 100.0
    al["pos"] = np.arange(len(al))
    return al


def rolling_who_leads(dp, er, win=XCORR_WIN, lmax=XCORR_LMAX, min_corr=XCORR_MINC):
    """逐 bar 滚动互相关判定局部领先：返回 +1(Kalshi领先)/-1(ETF领先)/0(不确定)。"""
    n = len(dp); lab = np.zeros(n)
    half = win // 2
    for t in range(n):
        a, b = max(0, t - half), min(n, t + half + 1)
        if b - a < max(8, 2 * lmax + 2):
            continue
        best_c, best_l = 0.0, 0
        for l in range(-lmax, lmax + 1):
            if l >= 0:
                x, y = dp[a:b - l], er[a + l:b]
            else:
                x, y = dp[a - l:b], er[a:b + l]
            if len(x) < 6 or np.std(x) < 1e-12 or np.std(y) < 1e-12:
                continue
            c = np.corrcoef(x, y)[0, 1]
            if abs(c) > abs(best_c):
                best_c, best_l = c, l
        if abs(best_c) >= min_corr and best_l != 0:
            lab[t] = 1 if best_l > 0 else -1
    return lab


def shade_who(ax, pos, who):
    """按 who 的连续同值段用背景色着色。"""
    if len(pos) == 0:
        return
    i = 0
    while i < len(who):
        j = i
        while j + 1 < len(who) and who[j + 1] == who[i]:
            j += 1
        if who[i] != 0:
            color = C_LEAD_K if who[i] > 0 else C_LEAD_E
            ax.axvspan(pos[i] - 0.5, pos[j] + 0.5, color=color, alpha=0.13, lw=0)
        i = j + 1


def _legend(ax1):
    h = [plt.Line2D([], [], color=C_KAL, lw=1.5),
         plt.Line2D([], [], color=C_ETF, lw=1.5),
         Patch(facecolor=C_LEAD_K, alpha=0.3), Patch(facecolor=C_LEAD_E, alpha=0.3)]
    ax1.legend(h, ["Kalshi prob", "ETF return", "Kalshi leads", "ETF leads"],
               loc="upper left", fontsize=7.5, ncol=2)


def plot_zoom2(ticker, etf, title_txt, al, freq, path):
    """盘连盘连续 x 轴：隔夜空档用虚线连，收盘点画垂直线，背景着色领先方向。"""
    fig, ax1 = plt.subplots(figsize=(13, 4.6))
    ax2 = ax1.twinx()
    sessions = list(al.groupby("date"))
    # 各 session 实线
    for _, g in sessions:
        ax1.plot(g["pos"], g["prob"] * 100, color=C_KAL, lw=1.2)
        ax2.plot(g["pos"], g["cumret_pct"], color=C_ETF, lw=1.2)
    # session 间虚线连接 + 垂直收盘线
    for (_, g0), (_, g1) in zip(sessions[:-1], sessions[1:]):
        ax1.plot([g0["pos"].iloc[-1], g1["pos"].iloc[0]], [g0["prob"].iloc[-1] * 100, g1["prob"].iloc[0] * 100],
                 color=C_KAL, lw=1.0, ls="--", alpha=0.7)
        ax2.plot([g0["pos"].iloc[-1], g1["pos"].iloc[0]], [g0["cumret_pct"].iloc[-1], g1["cumret_pct"].iloc[0]],
                 color=C_ETF, lw=1.0, ls="--", alpha=0.7)
        bound = (g0["pos"].iloc[-1] + g1["pos"].iloc[0]) / 2
        ax1.axvline(bound, color="gray", ls=":", lw=1.0)
        ax1.text(bound, ax1.get_ylim()[1], " market close", rotation=90, va="top", ha="left",
                 fontsize=6.5, color="gray")
    shade_who(ax1, al["pos"].values, al["who"].values)

    ax1.set_ylabel("Kalshi probability (%)", color=C_KAL, fontsize=10)
    ax2.set_ylabel(f"{etf} cumulative log return (%)", color=C_ETF, fontsize=10)
    ax1.tick_params(axis="y", colors=C_KAL); ax2.tick_params(axis="y", colors=C_ETF)
    # x 刻度=各 session 起点，标 ET 时间
    starts = [g["pos"].iloc[0] for _, g in sessions]
    labels = [f"{g['ts_et'].iloc[0]:%m-%d %H:%M}" for _, g in sessions]
    ax1.set_xticks(starts); ax1.set_xticklabels(labels, fontsize=8)
    ax1.set_xlabel("Time (ET) — overnight gaps removed (session-concatenated)", fontsize=9)
    _legend(ax1)
    fig.suptitle(f"(A-zoom2) Active zoom, gaps bridged + lead coloring  |  {ticker} × {etf}\n{title_txt}",
                 fontsize=11, y=1.03)
    ax1.set_title(f"bar={freq} (median)  |  ET  |  dashed=overnight change  |  vertical=market close  |  "
                  f"shade: rolling x-corr lead (red=Kalshi, blue=ETF)", fontsize=7.5, color="gray")
    fig.tight_layout(); fig.savefig(path, dpi=200, bbox_inches="tight"); plt.close(fig)


def plot_segments(ticker, etf, title_txt, al, freq, path):
    """每个活跃交易日一个子图，进一步放大，背景着色领先方向。最多 6 段（取最活跃）。"""
    sessions = list(al.groupby("date"))
    if len(sessions) > 6:
        sessions = sorted(sessions, key=lambda kv: -len(kv[1]))[:6]
        sessions = sorted(sessions, key=lambda kv: kv[0])
    n = len(sessions)
    fig, axes = plt.subplots(n, 1, figsize=(13, 2.7 * n), squeeze=False)
    for ax1, (d, g) in zip(axes[:, 0], sessions):
        ax2 = ax1.twinx()
        x = np.arange(len(g))
        ax1.plot(x, g["prob"].values * 100, color=C_KAL, lw=1.3)
        cr = (g["etfret"].cumsum() * 100).values
        ax2.plot(x, cr, color=C_ETF, lw=1.3)
        shade_who(ax1, x, g["who"].values)
        ax1.set_ylabel("Kalshi %", color=C_KAL, fontsize=8)
        ax2.set_ylabel(f"{etf} ret %", color=C_ETF, fontsize=8)
        ax1.tick_params(axis="y", colors=C_KAL, labelsize=7); ax2.tick_params(axis="y", colors=C_ETF, labelsize=7)
        # x 刻度标真实时刻
        ticks = np.linspace(0, len(g) - 1, min(7, len(g))).astype(int)
        ax1.set_xticks(ticks)
        ax1.set_xticklabels([f"{g['ts_et'].iloc[i]:%H:%M}" for i in ticks], fontsize=7)
        ax1.set_title(f"{d:%Y-%m-%d}  (bar={freq})", fontsize=9)
    _legend(axes[0, 0])
    axes[-1, 0].set_xlabel("Time (ET)", fontsize=9)
    fig.suptitle(f"(A-segments) Per-session zoom + lead coloring  |  {ticker} × {etf}\n{title_txt}",
                 fontsize=11, y=1.0)
    fig.tight_layout(rect=[0, 0, 1, 0.99]); fig.savefig(path, dpi=200, bbox_inches="tight"); plt.close(fig)


def plot_event(ticker, etf, title_txt, kalshi, etf_tk, path):
    """event 视角：横轴=事件序号。事件=30s median bar 上 prob 有变化的点。"""
    kb = C.bar_median_series(kalshi, "prob", "30s").sort_values("ts_et").reset_index(drop=True)
    eb = C.bar_median_series(etf_tk, "mid", "30s").sort_values("ts_et").reset_index(drop=True)
    if len(kb) < 3 or eb.empty:
        return False
    kb["dprob"] = kb.groupby("date")["prob"].diff()
    kb = kb.dropna(subset=["dprob"]).reset_index(drop=True)
    if len(kb) < 3:
        return False
    # 每个事件时点的 ETF mid（asof ≤ 事件时刻），算累计 return
    e_ns = eb["ts_et"].astype("datetime64[ns]").astype("int64").values
    e_mid = eb["mid"].values
    q_ns = kb["ts_et"].astype("datetime64[ns]").astype("int64").values
    idx = np.searchsorted(e_ns, q_ns, side="right") - 1
    mid_at = np.where(idx >= 0, e_mid[np.clip(idx, 0, len(e_mid) - 1)], np.nan)
    logret = np.diff(np.log(mid_at), prepend=np.log(mid_at[0]))
    logret = np.nan_to_num(logret, nan=0.0)
    cumret = np.cumsum(logret) * 100
    ev = np.arange(1, len(kb) + 1)

    fig, ax1 = plt.subplots(figsize=(13, 4.4))
    ax2 = ax1.twinx()
    ax1.plot(ev, kb["prob"].values * 100, color=C_KAL, lw=1.1)
    ax2.plot(ev, cumret, color=C_ETF, lw=1.1)
    ax1.set_ylabel("Kalshi probability (%)", color=C_KAL, fontsize=10)
    ax2.set_ylabel(f"{etf} cumulative log return (%)", color=C_ETF, fontsize=10)
    ax1.tick_params(axis="y", colors=C_KAL); ax2.tick_params(axis="y", colors=C_ETF)
    ax1.set_xlabel("Event index (Kalshi update #)  — calm periods compressed", fontsize=9)
    h = [plt.Line2D([], [], color=C_KAL, lw=1.5), plt.Line2D([], [], color=C_ETF, lw=1.5)]
    ax1.legend(h, [f"Kalshi: {ticker}", f"ETF: {etf} (return)"], loc="upper left", fontsize=8)
    fig.suptitle(f"(A-event) Event-time view (x = event #)  |  {ticker} × {etf}\n{title_txt}", fontsize=11, y=1.03)
    ax1.set_title(f"{len(kb)} events  |  clean bar=30s (median)  |  ET  |  ETF in return", fontsize=8, color="gray")
    fig.tight_layout(); fig.savefig(path, dpi=200, bbox_inches="tight"); plt.close(fig)
    return True


def _fmt_dur(sec):
    sec = abs(int(round(sec)))
    return f"{sec}s" if sec < 90 else f"{sec/60:.0f}min"


def plot_leadglance(ticker, etf, title_txt, al, freq, bar_sec, path):
    """一眼看 leadlag：在两条线上标出最大的几次真实变动(编号竖线)，下方逐条给出
    'Kalshi 某时刻大动 -> 最近的 ETF 大动在 N 个 bar 后'，每条批注都对应图上锚点。"""
    al = al.reset_index(drop=True)
    n = len(al)
    if n < 8:
        return False
    TOPN = 3
    ML = min(8, max(2, n // 4))
    k_ix = sorted(al["dprob"].abs()[al["dprob"].abs() > 0].nlargest(TOPN).index)
    e_ix = sorted(al["etfret"].abs()[al["etfret"].abs() > 0].nlargest(TOPN).index)

    fig = plt.figure(figsize=(13, 6.8))
    gs = fig.add_gridspec(2, 1, height_ratios=[3.0, 1.7], hspace=0.30)
    ax1 = fig.add_subplot(gs[0]); ax2 = ax1.twinx()
    axt = fig.add_subplot(gs[1]); axt.axis("off")

    sessions = list(al.groupby("date"))
    for _, g in sessions:
        ax1.plot(g["pos"], g["prob"] * 100, color=C_KAL, lw=1.2)
        ax2.plot(g["pos"], g["cumret_pct"], color=C_ETF, lw=1.2)
    for (_, g0), (_, g1) in zip(sessions[:-1], sessions[1:]):
        ax1.plot([g0["pos"].iloc[-1], g1["pos"].iloc[0]], [g0["prob"].iloc[-1]*100, g1["prob"].iloc[0]*100],
                 color=C_KAL, ls="--", lw=0.8, alpha=0.6)
        ax2.plot([g0["pos"].iloc[-1], g1["pos"].iloc[0]], [g0["cumret_pct"].iloc[-1], g1["cumret_pct"].iloc[0]],
                 color=C_ETF, ls="--", lw=0.8, alpha=0.6)
        ax1.axvline((g0["pos"].iloc[-1] + g1["pos"].iloc[0]) / 2, color="gray", ls=":", lw=0.8)

    ytop1, ytop2 = ax1.get_ylim()[1], ax2.get_ylim()[1]
    for r, i in enumerate(k_ix, 1):
        ax1.axvline(al["pos"][i], color=C_KAL, lw=1.1, alpha=0.55)
        ax1.text(al["pos"][i], ytop1, f"K{r}", color=C_KAL, fontsize=9, ha="center", va="bottom", weight="bold")
    for r, i in enumerate(e_ix, 1):
        ax2.axvline(al["pos"][i], color=C_ETF, lw=1.1, ls=(0, (4, 2)), alpha=0.55)
        ax2.text(al["pos"][i], ytop2, f"E{r}", color=C_ETF, fontsize=9, ha="center", va="bottom", weight="bold")

    ax1.set_ylabel("Kalshi probability  (%)", color=C_KAL, fontsize=10)
    ax2.set_ylabel(f"{etf} cumulative log return  (%)", color=C_ETF, fontsize=10)
    ax1.tick_params(axis="y", colors=C_KAL); ax2.tick_params(axis="y", colors=C_ETF)
    starts = [g["pos"].iloc[0] for _, g in sessions]
    ax1.set_xticks(starts); ax1.set_xticklabels([f"{g['ts_et'].iloc[0]:%m-%d %H:%M}" for _, g in sessions], fontsize=8)
    ax1.set_xlabel(f"Time (ET), overnight gaps removed   |   1 bar = {freq}  (= lag resolution)", fontsize=9)
    h = [plt.Line2D([], [], color=C_KAL, lw=1.5), plt.Line2D([], [], color=C_ETF, lw=1.5)]
    ax1.legend(h, [f"Kalshi: {ticker}  (K# = its biggest moves)", f"ETF: {etf} return  (E# = its biggest moves)"],
               loc="upper left", fontsize=8)
    fig.suptitle(f"(A-leadglance) Who moves first?  |  {ticker} × {etf}\n{title_txt}", fontsize=11, y=1.02)

    # 下方逐条对应表（每条都能在上图找到 K#/E# 锚点）
    lines = [f"Lead rule: mark the largest cleaned bar-to-bar moves; for each Kalshi move K#, find the nearest large",
             f"ETF move within +/-{ML} bars. lag = #bars between them x {freq}.  ( + => ETF after => KALSHI LEADS ; - => ETF before => ETF LEADS )",
             ""]
    for r, i in enumerate(k_ix, 1):
        w = al.iloc[max(0, i - ML):min(n, i + ML + 1)]
        j = int(w["etfret"].abs().idxmax())
        lag = j - i
        who = "Kalshi leads" if lag > 0 else ("ETF leads" if lag < 0 else "same bar (contemporaneous)")
        lines.append(
            f"K{r}: Kalshi |dP|={al['dprob'][i]*100:+.1f}pp @ {al['ts_et'][i]:%m-%d %H:%M}  ->  "
            f"nearest big ETF move @ {al['ts_et'][j]:%m-%d %H:%M} (ret {al['etfret'][j]*100:+.2f}%);  "
            f"lag = {lag:+d} bar  ~ {('+' if lag>=0 else '-')+_fmt_dur(lag*bar_sec)}   [{who}]")
    y = 0.96
    for ln in lines:
        axt.text(0.0, y, ln, transform=axt.transAxes, family="monospace", fontsize=8.5, va="top", ha="left",
                 weight="bold" if ln.startswith("Lead rule") else "normal")
        y -= 0.135 if ln.startswith("Lead rule") else 0.115
    fig.savefig(path, dpi=200, bbox_inches="tight"); plt.close(fig)
    return True


def main():
    con = C.make_con()
    print(f"为 {len(SIG)} 组配对出增强图 -> {PLOTDIR}")
    for i, pair in SIG.iterrows():
        ticker, etf = pair["contract_ticker"], pair["etf"]
        ds, de = str(pair["date_start"]), str(pair["date_end"])
        title_txt = str(pair.get("contract_title", ""))
        tag = f"{i+1:02d}_{ticker}_{etf}".replace("/", "-")

        kalshi = C.load_kalshi(con, ticker, ds, de)
        etf_tk = C.load_etf(con, etf, ds, de)
        if kalshi.empty or etf_tk.empty:
            print(f"[{i+1}/{len(SIG)}] {ticker}×{etf}  跳过：无数据"); continue

        lo, hi = zoom_window(kalshi)
        med_gap = C.median_intertrade_sec(kalshi[(kalshi['ts_et'] >= lo) & (kalshi['ts_et'] <= hi)])
        bar_sec = snap_plot_bar(med_gap if np.isfinite(med_gap) else 60)
        freq = PLOT_BAR_LABEL[bar_sec]

        al = build_aligned(kalshi, etf_tk, lo, hi, freq)
        made = []
        if al is not None and len(al) >= 5:
            plot_zoom2(ticker, etf, title_txt, al, freq, PLOTDIR / f"{tag}_zoom2.png"); made.append("zoom2")
            plot_segments(ticker, etf, title_txt, al, freq, PLOTDIR / f"{tag}_segments.png"); made.append("segments")
            if plot_leadglance(ticker, etf, title_txt, al, freq, bar_sec, PLOTDIR / f"{tag}_leadglance.png"):
                made.append("leadglance")
        if plot_event(ticker, etf, title_txt, kalshi, etf_tk, PLOTDIR / f"{tag}_event.png"):
            made.append("event")
        print(f"[{i+1}/{len(SIG)}] {ticker}×{etf}  ✓  {made}")
    print("全部完成。")


if __name__ == "__main__":
    main()
