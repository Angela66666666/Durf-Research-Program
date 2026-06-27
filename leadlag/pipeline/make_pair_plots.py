"""
make_pair_plots.py
================================================================================
这个文件做什么 (What this file does)
  为全部 48 对各画基础图，并生成"最能说明问题在前"的排序表（供报告排版用）。
  Draw the base figures for all 48 pairs and produce the "most-illustrative-first"
  ranking table used to order the report.

为什么这么做 (Why)
  把每对的原始共动形态和滞后系数先可视化出来，是肉眼核对回归结论、给报告打底的第一步。
  Visualizing each pair's raw co-movement and lag coefficients is the first sanity
  check on the regressions and the foundation of the report.

思路 / 产图 (Approach / figures, 均 ET、ETF 一律用 return)
  (A) {tag}_timeseries.png       双线时序：左轴 Kalshi 概率(%)，右轴 ETF 累计 log return(%)
  (A-zoom) {tag}_timeseries_zoom.png  仅当活跃窗挤在全窗一小段时额外加，bar 自适应该窗(可到秒级)
  (B) {tag}_lagcoef.png          滞后系数图 b_j vs j（calendar+event 叠加、显著点实心）+ 系数表
                                  j>0: Kalshi 领先 ETF；j<0: ETF 领先 Kalshi
  数据口径沿用 leadlag_common（ET / 盘内 / median 清 outlier），回归结果读自两套 CSV。

输出 (Outputs)
  - plots/{tag}_timeseries.png / _timeseries_zoom.png / _lagcoef.png
  - plots/pair_ranking.csv  排序表（有结果→显著多→p最小→成交多 在前）
  存放位置：leadlag/pipeline/plots/

函数 (Functions)
  snap_plot_bar    把秒数吸附到画图用的细 bar 网格
  zoom_window      定位成交最密集的活跃窗口（>=峰值日 30% 成交量的天）
  stars            p 值 -> 显著性星号
  etf_cumret       ETF mid -> median bar -> 同日 log return -> 全窗累计(%)
  plot_timeseries  画全窗双线时序图 (A)
  plot_timeseries_zoom  画活跃窗放大图 (A-zoom)，bar 自适应
  plot_lagcoef     画滞后系数图 + 右侧系数表 (B)
  main             逐对出三张图、算 n_sig/best_p、写排序表
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import leadlag_common as C

PLOT_BAR = "1min"                 # 画图用的细 bar（median，清尖峰后看形状）
PLOTDIR  = C.HERE / "plots"
PLOTDIR.mkdir(exist_ok=True)

CAL = pd.read_csv(C.HERE / "leadlag_calendar_kalshi_etf.csv")
EV  = pd.read_csv(C.HERE / "leadlag_event_kalshi_etf.csv")
SIG = pd.read_csv(C.SIG_PAIRS_CSV)

C_KAL = "#c0392b"   # Kalshi 红
C_ETF = "#2c6fbb"   # ETF 蓝

# 放大图用的细 bar 网格（比全窗图更细，活跃窗口可放大到秒级）
PLOT_BAR_GRID  = [1, 2, 5, 10, 30, 60, 120, 300, 600]
PLOT_BAR_LABEL = {1: "1s", 2: "2s", 5: "5s", 10: "10s", 30: "30s",
                  60: "1min", 120: "2min", 300: "5min", 600: "10min"}
ZOOM_FRAC = 0.6     # 活跃窗 < 全窗 60% 视为「挤在一起」，额外加放大图


def snap_plot_bar(sec):
    """把秒数吸附到画图用的细 bar 网格（取第一个 >= sec 的档）。Snap seconds to plot-bar grid."""
    for s in PLOT_BAR_GRID:
        if s >= sec:
            return s
    return PLOT_BAR_GRID[-1]


def zoom_window(kalshi):
    """放大到成交最密集的几天（≥峰值日 30% 成交量），聚焦真正的活跃爆发段、剔除零星落单成交。"""
    counts = kalshi.groupby("date").size()
    if counts.empty:
        kt = kalshi["ts_et"]
        return kt.min(), kt.max()
    keep = set(counts[counts >= 0.30 * counts.max()].index)
    kt = kalshi[kalshi["date"].isin(keep)]["ts_et"]
    lo, hi = kt.min(), kt.max()
    pad = max((hi - lo) * 0.03, pd.Timedelta("1min"))
    return lo - pad, hi + pad


def stars(p):
    if pd.isna(p):
        return ""
    return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.10 else ""


def etf_cumret(etf_tk):
    """median-resample ETF mid -> 同日内 log return -> 全窗累计(%)。"""
    eb = C.bar_median_series(etf_tk, "mid", PLOT_BAR).sort_values("ts_et").reset_index(drop=True)
    if eb.empty:
        return eb
    eb["logret"] = eb.groupby("date")["mid"].transform(lambda s: np.log(s).diff()).fillna(0.0)
    eb["cumret_pct"] = eb["logret"].cumsum() * 100.0
    return eb


def plot_timeseries(i, ticker, etf, title_txt, kb, eb, path):
    """画全窗双线时序图 (A)：Kalshi 概率 vs ETF 累计 return。Full-window dual-axis time series."""
    fig, ax1 = plt.subplots(figsize=(13, 4.2))
    ax2 = ax1.twinx()
    for _, g in kb.groupby("date"):
        ax1.plot(g["ts_et"], g["prob"] * 100, color=C_KAL, lw=1.1)
    for _, g in eb.groupby("date"):
        ax2.plot(g["ts_et"], g["cumret_pct"], color=C_ETF, lw=1.1)
    ax1.set_ylabel("Kalshi probability (%)", color=C_KAL, fontsize=10)
    ax2.set_ylabel(f"{etf} cumulative log return (%)", color=C_ETF, fontsize=10)
    ax1.tick_params(axis="y", colors=C_KAL)
    ax2.tick_params(axis="y", colors=C_ETF)
    ax1.set_xlabel("Time (ET)", fontsize=10)
    h = [plt.Line2D([], [], color=C_KAL, lw=1.5),
         plt.Line2D([], [], color=C_ETF, lw=1.5)]
    ax1.legend(h, [f"Kalshi: {ticker}", f"ETF: {etf} (return)"], loc="upper left", fontsize=8)
    fig.suptitle(f"(A) Intraday co-movement  |  {ticker}  ×  {etf}\n{title_txt}",
                 fontsize=11, y=1.02)
    ax1.set_title("timezone: ET  |  market hours 09:30-16:00  |  outlier: median-resampled  |  ETF in return",
                  fontsize=8, color="gray")
    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def plot_timeseries_zoom(ticker, etf, title_txt, kalshi, etf_tk, path):
    """放大到 Kalshi 活跃窗口，bar 自适应该窗成交密度（可到秒级），ETF 累计 return 以窗起点为 0。"""
    lo, hi = zoom_window(kalshi)
    kz = kalshi[(kalshi["ts_et"] >= lo) & (kalshi["ts_et"] <= hi)].copy()
    ez = etf_tk[(etf_tk["ts_et"] >= lo) & (etf_tk["ts_et"] <= hi)].copy()
    if kz.empty or ez.empty:
        return None
    med_gap = C.median_intertrade_sec(kz)
    bar_sec = snap_plot_bar(med_gap if np.isfinite(med_gap) else 60)
    freq = PLOT_BAR_LABEL[bar_sec]

    kb = C.bar_median_series(kz, "prob", freq)
    eb = C.bar_median_series(ez, "mid", freq).sort_values("ts_et").reset_index(drop=True)
    if eb.empty or kb.empty:
        return None
    eb["logret"] = eb.groupby("date")["mid"].transform(lambda s: np.log(s).diff()).fillna(0.0)
    eb["cumret_pct"] = eb["logret"].cumsum() * 100.0   # 以放大窗起点为 0

    fig, ax1 = plt.subplots(figsize=(13, 4.4))
    ax2 = ax1.twinx()
    for _, g in kb.groupby("date"):
        ax1.plot(g["ts_et"], g["prob"] * 100, color=C_KAL, lw=1.3)
    for _, g in eb.groupby("date"):
        ax2.plot(g["ts_et"], g["cumret_pct"], color=C_ETF, lw=1.3)
    ax1.set_ylabel("Kalshi probability (%)", color=C_KAL, fontsize=10)
    ax2.set_ylabel(f"{etf} cumulative log return (%)", color=C_ETF, fontsize=10)
    ax1.tick_params(axis="y", colors=C_KAL); ax2.tick_params(axis="y", colors=C_ETF)
    ax1.set_xlabel("Time (ET)", fontsize=10)
    h = [plt.Line2D([], [], color=C_KAL, lw=1.5), plt.Line2D([], [], color=C_ETF, lw=1.5)]
    ax1.legend(h, [f"Kalshi: {ticker}", f"ETF: {etf} (return)"], loc="upper left", fontsize=8)
    zlabel = f"{kb['ts_et'].min():%Y-%m-%d %H:%M} ~ {kb['ts_et'].max():%Y-%m-%d %H:%M} ET"
    fig.suptitle(f"(A-zoom) Active-window zoom  |  {ticker}  ×  {etf}\n{title_txt}", fontsize=11, y=1.03)
    ax1.set_title(f"zoom: {zlabel}   |   bar={freq} (median)   |   ET   |   ETF in return (re-based to 0 at window start)",
                  fontsize=8, color="gray")
    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return freq


def plot_lagcoef(i, ticker, etf, title_txt, cpair, epair, path):
    """画滞后系数图 (B)：b_j vs 滞后 j（calendar+event 叠加）+ 右侧系数表。Lag-coefficient plot + table."""
    fig = plt.figure(figsize=(13, 5.2))
    gs = fig.add_gridspec(1, 2, width_ratios=[2.0, 1.15], wspace=0.05)
    axp = fig.add_subplot(gs[0])
    axt = fig.add_subplot(gs[1]); axt.axis("off")

    def draw(df, color, marker, label):
        if df.empty:
            return
        df = df.sort_values("k_lag")
        axp.plot(df["k_lag"], df["coef"], "-", color=color, marker=marker, ms=4,
                 mfc="none", lw=1.0, label=label)
        pc = "p_fdr" if "p_fdr" in df.columns else "p_value"   # ④ 实心点=FDR 校正后显著
        s = df[df[pc] < 0.05]
        axp.plot(s["k_lag"], s["coef"], linestyle="none", color=color, marker=marker, ms=7)

    cbar = cpair["bar_freq"].iloc[0] if not cpair.empty else "-"
    draw(cpair, C_ETF, "o", f"calendar (bar={cbar})")
    draw(epair, C_KAL, "s", "event")
    axp.axhline(0, color="gray", lw=0.8)
    axp.axvline(0, color="gray", ls=":", lw=0.8)
    axp.set_xlabel("lag j   ( j>0: Kalshi leads ETF    |    j<0: ETF leads Kalshi )", fontsize=9)
    axp.set_ylabel("joint-lag coefficient  b_j", fontsize=10)
    if cpair.empty and epair.empty:
        axp.text(0.5, 0.5, "No regression result\n(insufficient data after cleaning)",
                 ha="center", va="center", transform=axp.transAxes, color="gray", fontsize=11)
    else:
        axp.legend(fontsize=8, loc="best")
    axp.set_title(f"(B) Lead-lag coefficients  |  {ticker} × {etf}\n{title_txt}", fontsize=10)

    # 右侧表格：每个 k 的 calendar / event 系数 + 显著性
    ks = sorted(set(cpair["k_lag"]).union(set(epair["k_lag"])))
    if not ks:
        axt.text(0.5, 0.5, "no coefficients", ha="center", va="center",
                 transform=axt.transAxes, color="gray", fontsize=9)
        fig.tight_layout()
        fig.savefig(path, dpi=200, bbox_inches="tight")
        plt.close(fig)
        return
    cmap = {r.k_lag: r for r in cpair.itertuples()}
    emap = {r.k_lag: r for r in epair.itertuples()}
    rows, cell_colors = [], []
    def _pf(r):
        return getattr(r, "p_fdr", r.p_value)
    for k in ks:
        cr, er = cmap.get(k), emap.get(k)
        c_txt = f"{cr.coef:+.2e} {stars(_pf(cr))}" if cr else "—"
        e_txt = f"{er.coef:+.2e} {stars(_pf(er))}" if er else "—"
        rows.append([f"{k:+d}", c_txt, e_txt])
        def col(r):
            if r is None: return "white"
            return "#cfe8cf" if _pf(r) < 0.05 else "white"
        cell_colors.append(["white", col(cr), col(er)])
    tbl = axt.table(cellText=rows, colLabels=["k", "calendar b_j", "event b_j"],
                    cellColours=cell_colors, loc="upper center", cellLoc="center")
    tbl.auto_set_font_size(False); tbl.set_fontsize(7.5); tbl.scale(1, 1.05)
    fig.text(0.80, 0.005, "BH-FDR:  *** p_fdr<.01   ** <.05   * <.10    |    green cell = p_fdr<.05  |  solid dot = FDR-sig",
             ha="center", va="bottom", fontsize=7.5, color="gray")

    fig.tight_layout(rect=[0, 0.03, 1, 1])
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def main():
    con = C.make_con()
    print(f"为 {len(SIG)} 组配对出图 -> {PLOTDIR}")
    rank_rows = []
    for i, pair in SIG.iterrows():
        ticker, etf = pair["contract_ticker"], pair["etf"]
        ds, de = str(pair["date_start"]), str(pair["date_end"])
        title_txt = str(pair.get("contract_title", ""))
        tag = f"{i+1:02d}_{ticker}_{etf}".replace("/", "-")

        kalshi = C.load_kalshi(con, ticker, ds, de)
        etf_tk = C.load_etf(con, etf, ds, de)
        n_trades = len(kalshi)
        if kalshi.empty or etf_tk.empty:
            print(f"[{i+1}/{len(SIG)}] {ticker}×{etf}  跳过：无数据")
            continue

        # (A) 全窗图（原样保留）
        kb = C.bar_median_series(kalshi, "prob", PLOT_BAR)
        eb = etf_cumret(etf_tk)
        plot_timeseries(i, ticker, etf, title_txt, kb, eb, PLOTDIR / f"{tag}_timeseries.png")

        # (A-zoom) 仅当活跃窗挤在全窗一小段时，额外加放大图
        full = etf_tk["ts_et"]
        lo, hi = zoom_window(kalshi)
        active_frac = (hi - lo) / (full.max() - full.min()) if full.max() > full.min() else 1.0
        zoom_bar = None
        if active_frac < ZOOM_FRAC:
            zoom_bar = plot_timeseries_zoom(ticker, etf, title_txt, kalshi, etf_tk,
                                            PLOTDIR / f"{tag}_timeseries_zoom.png")

        # (B) 滞后系数图 + 表
        cpair = CAL[(CAL["contract_ticker"] == ticker) & (CAL["etf"] == etf) & (CAL["is_primary_bar"])]
        epair = EV[(EV["contract_ticker"] == ticker) & (EV["etf"] == etf)]
        plot_lagcoef(i, ticker, etf, title_txt, cpair, epair, PLOTDIR / f"{tag}_lagcoef.png")

        cpc = "p_fdr" if "p_fdr" in cpair.columns else "p_value"
        epc = "p_fdr" if "p_fdr" in epair.columns else "p_value"
        n_sig = int((cpair[cpc] < 0.05).sum() + (epair[epc] < 0.05).sum())
        ps = pd.concat([cpair[cpc], epair[epc]])
        best_p = float(ps.min()) if len(ps) else np.nan
        has_result = not (cpair.empty and epair.empty)
        rank_rows.append({"order_idx": i + 1, "tag": tag, "contract_ticker": ticker, "etf": etf,
                          "contract_title": title_txt, "has_result": has_result, "n_sig": n_sig,
                          "best_p": best_p, "n_trades": n_trades, "has_zoom": zoom_bar is not None,
                          "zoom_bar": zoom_bar or ""})
        zmark = f" +zoom({zoom_bar})" if zoom_bar else ""
        print(f"[{i+1}/{len(SIG)}] {ticker}×{etf}  ✓  n_sig={n_sig} best_p={best_p:.1e} n_trades={n_trades}{zmark}")

    # 排序：最能说明问题在上（有结果→显著多→p最小→成交多），数据少/无结果在下
    rk = pd.DataFrame(rank_rows)
    rk["_bp"] = rk["best_p"].fillna(1.0)
    rk = rk.sort_values(["has_result", "n_sig", "_bp", "n_trades"],
                        ascending=[False, False, True, False]).drop(columns="_bp").reset_index(drop=True)
    rk.insert(0, "rank", rk.index + 1)
    rk.to_csv(PLOTDIR / "pair_ranking.csv", index=False)
    print(f"\n排序表 -> {PLOTDIR / 'pair_ranking.csv'}")
    print(rk[["rank", "contract_ticker", "etf", "n_sig", "best_p", "n_trades", "has_zoom"]].head(15).to_string(index=False))
    print("全部完成。")


if __name__ == "__main__":
    main()
