"""
make_granger_plots.py
================================================================================
这个文件做什么 (What this file does)
  Granger 检验的专属图，两类：
  (1) 核心热力图 granger_heatmap / merge_heatmap
      行=配对(或 组×ETF)，列=6 组回归(时间轴×方向)，色=**离散分档**的联合 Wald p。
      每格数字=该组回归的联合 Wald p(H0: 无 Granger 因果)；p<0.05(红)=拒绝=该方向领先显著。
      列标写清"哪个时间轴 + 测谁领先"。一张看尽全局。
  (2) 每对详情图 granger_figure(2×3)
      每个子图=一组回归：x=滞后 j、y=全标准化系数 β、柱色=该 lag 的 p，标题=联合 Wald p。
      没跑成的组写一句"为什么没过门槛"。

为什么 (Why)
  Granger 是"这组系数**同时**为 0 吗"的联合检验，结论挂在**一个 p**上、不在单个 lag。
  热力图直接把每组回归的联合 p 铺开(离散分档一眼看显著)；详情图给系数细节。

用法 (Usage)
  python make_granger_plots.py heatmap          # 单对核心热力图 -> plots/granger_heatmap.png
  python make_granger_plots.py merge-heatmap    # merge 核心热力图 -> plots/granger_merge_heatmap.png
  python make_granger_plots.py                  # 全部单对 2×3 详情 -> plots/{tag}_granger.png
  python make_granger_plots.py TICKER ETF       # 预览一对详情
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np
import pandas as pd

from pathlib import Path as _P
sys.path.insert(0, str(_P(__file__).resolve().parent.parent / "engine"))
import leadlag_common as C
import leadlag_probit as LP          # build_calendar_xy / build_event_xy(probit 口径 x/y 表)

PLOTS = C.HERE.parent / "plots"      # folder-5 plots/ (C.HERE is engine/)
BLUE, RED, GREEN = "#1f77b4", "#d62728", "#2ca02c"
SPECS = [("calendar", "linear", "kalshi->etf"), ("calendar", "linear", "etf->kalshi"),
         ("event", "linear", "kalshi->etf"), ("event", "linear", "etf->kalshi"),
         ("calendar", "probit", "kalshi->etf"), ("event", "probit", "kalshi->etf")]


def _stars(p):
    return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.10 else ""


# ============================ 核心热力图 ============================
def _draw_heatmap(labels, P, col_labels, title, out_png, row_dividers=None, blocks=None,
                  block_rot=90):
    """离散分档热力图核心：P[i,j]=联合 Wald p(可 NaN)。单对/ merge 共用。
    blocks=[(start_row, end_row, 说明文字), ...] 时，在左侧给每个块加"这是什么"的标签。
    block_rot=90 适合高块(merge，每块 9+ 行)；block_rot=0(水平、右对齐)适合矮块
    (单对，每个合约只有 1~9 行，旋转文字会互相压住)。"""
    bounds = [0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.50, 1.0]
    bcolors = ["#b10026", "#fc4e2a", "#fd8d3c", "#feb24c", "#fed976", "#ffeda0", "#ffffcc"]
    blabels = ["p < 0.05   (significant)", "0.05 ≤ p < 0.10", "0.10 ≤ p < 0.15", "0.15 ≤ p < 0.20",
               "0.20 ≤ p < 0.25", "0.25 ≤ p < 0.50", "p ≥ 0.50"]
    cmap = ListedColormap(bcolors); cmap.set_bad("#d9d9d9")
    norm = BoundaryNorm(bounds, cmap.N)
    Pm = np.ma.masked_invalid(P)

    fig, ax = plt.subplots(figsize=(11.5, 0.30 * len(labels) + 3.2))
    ax.imshow(Pm, aspect="auto", cmap=cmap, norm=norm)
    ax.set_xticks(range(len(col_labels))); ax.set_xticklabels(col_labels, fontsize=7.2)
    ax.set_yticks(range(len(labels))); ax.set_yticklabels(labels, fontsize=6.2)
    for x in (1.5, 3.5):
        ax.axvline(x, color="k", lw=2.2)
    for y in (row_dividers or []):
        ax.axhline(y, color="k", lw=1.4)
    tr = ax.get_yaxis_transform()                          # x=轴分数, y=数据坐标
    if block_rot:                                          # 高块：竖排在左侧
        bx, tx, ha = -0.135, -0.165, "center"
    else:                                                  # 矮块：水平右对齐，避免相邻块文字互相压住
        bx, tx, ha = -0.055, -0.070, "right"
    for a, b, txt in (blocks or []):
        ax.plot([bx, bx], [a - 0.45, b + 0.45], transform=tr, color="#222", lw=3, clip_on=False)
        ax.text(tx, (a + b) / 2, txt, transform=tr, rotation=block_rot, ha=ha, va="center",
                fontsize=8.3 if block_rot else 7.6, fontweight="bold", color="#222", clip_on=False)
    for i in range(len(labels)):
        for j in range(P.shape[1]):
            p = P[i, j]
            if np.isnan(p):
                ax.text(j, i, "NA", ha="center", va="center", fontsize=5.2, color="#888")
            elif p < 0.15:
                ax.text(j, i, (f"{p:.0e}" if p < 0.01 else f"{p:.3f}"), ha="center", va="center",
                        fontsize=5.2, color="white" if p < 0.05 else "black", fontweight="bold")
    ax.set_xticks(np.arange(-.5, len(col_labels), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(labels), 1), minor=True)
    ax.grid(which="minor", color="white", lw=0.6); ax.tick_params(which="minor", length=0)
    handles = [Patch(fc=c, ec="gray", label=l) for c, l in zip(bcolors, blabels)]
    handles.append(Patch(fc="#d9d9d9", ec="gray", label="NA (regression not estimable)"))
    ax.legend(handles=handles, title="cell color = joint Wald p", loc="upper left",
              bbox_to_anchor=(1.01, 1.0), fontsize=8, title_fontsize=8.5, frameon=True)
    ax.set_title(title, fontsize=9.4, fontweight="bold", pad=16)
    fig.tight_layout()
    fig.savefig(out_png, dpi=150, bbox_inches="tight"); plt.close(fig)


def _pmatrix(df, keys, key_cols):
    """按 keys(每个是 key_cols 的取值元组)与 SPECS，取联合 Wald p 矩阵。"""
    P = []
    for kv in keys:
        sub = df
        for c, v in zip(key_cols, kv):
            sub = sub[sub[c] == v]
        row = []
        for m, s, d in SPECS:
            cc = sub[(sub["mode"] == m) & (sub.spec == s) & (sub.direction == d)]
            row.append(float(cc.p_value.iloc[0]) if len(cc) else np.nan)
        P.append(row)
    return np.array(P, dtype=float)


# 合约按事件族分组，族内按 ticker：让同一合约的所有 ETF 结果连在一起（而不是按 p 排序）。
# 按 p 排序 + 按 p 上色是冗余的；分组后读者能直接问"这个合约在哪些 ETF 上显著"。
_FAMILY = [("ECDJT", 0), ("ECKH", 1), ("FEDDECISION", 2), ("RATECUT", 3),
           ("AAAGASM", 4), ("538APPROVE", 5)]


def _family_rank(ticker: str) -> int:
    s = ticker[2:] if ticker.startswith("KX") else ticker
    for pat, r in _FAMILY:
        if s.startswith(pat):
            return r
    return 9


def granger_heatmap(out_png):
    G = pd.read_csv(C.HERE / "leadlag_granger_pairs.csv")
    sig = pd.read_csv(C.SIG_PAIRS_CSV)
    col_labels = ["CALENDAR\nKalshi→ETF\n(Kalshi\nleads?)", "CALENDAR\nETF→Kalshi\n(ETF\nleads?)",
                  "EVENT\nKalshi→ETF\n(Kalshi\nleads?)", "EVENT\nETF→Kalshi\n(ETF\nleads?)",
                  "CALENDAR\nprobit K→E\n(Kalshi\nleads,sign)", "EVENT\nprobit K→E\n(Kalshi\nleads,sign)"]
    keys = [tuple(x) for x in sig[["contract_ticker", "etf"]].drop_duplicates().values]
    # 分组排序：事件族 → 合约 ticker → ETF 名。全程不看 p 值。
    keys.sort(key=lambda ke: (_family_rank(ke[0]), ke[0], ke[1]))
    P = _pmatrix(G, keys, ["contract_ticker", "etf"])
    labels = [e for _, e in keys]                     # 行标只留 ETF；合约名交给左侧块标签
    n_allna = int(np.isnan(P).all(axis=1).sum())

    # 合约之间画横线 + 左侧写该合约的可读名（不是 KXECKH276 这种 ticker）
    rd = [i - 0.5 for i in range(1, len(keys)) if keys[i][0] != keys[i - 1][0]]
    blocks, i = [], 0
    while i < len(keys):
        t = keys[i][0]; j = i
        while j < len(keys) and keys[j][0] == t:
            j += 1
        blocks.append((i, j - 1, C.short_contract_name(t)))   # (起始行, 结束行, 可读合约名)
        i = j

    title = ("GRANGER joint-Wald p — all 48 single pairs × 6 regressions, grouped by contract\n"
             "each cell's number = joint Wald p  (H0: NO Granger causality).  p<0.05 (red) = reject H0 = "
             "that direction's lead/lag IS significant.\n"
             f"rows are grouped by contract (left labels), never sorted by p.  {n_allna} all-grey rows = "
             "too sparse to estimate any regression.")
    _draw_heatmap(labels, P, col_labels, title, out_png, row_dividers=rd, blocks=blocks, block_rot=0)


def merge_heatmap(out_png):
    sys.path.insert(0, str(C.HERE.parent / "merge"))
    import merge_leadlag as ML
    M = pd.read_csv(C.HERE.parent / "merge" / "leadlag_merged_granger.csv")
    sig = pd.read_csv(C.SIG_PAIRS_CSV)
    short = {"ELECTION_trump_fav": "ELECTION", "FOMC_easing": "FOMC",
             "GAS_above": "GAS", "APPROVAL_strength": "APPROVAL"}
    col_labels = ["CALENDAR\nPooled→ETF\n(Pooled\nleads?)", "CALENDAR\nETF→Pooled\n(ETF\nleads?)",
                  "EVENT\nPooled→ETF\n(Pooled\nleads?)", "EVENT\nETF→Pooled\n(ETF\nleads?)",
                  "CALENDAR\nprobit P→E\n(Pooled\nleads,sign)", "EVENT\nprobit P→E\n(Pooled\nleads,sign)"]
    gorder = {g: i for i, g in enumerate(ML.GROUPS)}
    combos = [(g, etf) for g, ms in ML.GROUPS.items() for etf in ML.group_etf_union(sig, list(ms))]
    # 按池化信号分组，组内按 ETF 名排序——不按 p 排序（排序+上色都编码 p 是冗余的）
    combos.sort(key=lambda ge: (gorder.get(ge[0], 9), ge[1]))
    P = _pmatrix(M, combos, ["group", "etf"])
    labels = [etf for g, etf in combos]               # 行标只留 ETF；组名交给左侧块标签
    # 组间横线 + 每个块的说明(池化信号=池化了什么、+Δ 含义)
    rd = [i - 0.5 for i in range(1, len(combos)) if combos[i][0] != combos[i - 1][0]]
    desc = {"ELECTION_trump_fav": "ELECTION_trump_fav\n6 election contracts · +Δ = more Trump-favorable",
            "FOMC_easing":        "FOMC_easing\n5 Fed contracts · +Δ = more rate-cut / easing",
            "GAS_above":          "GAS_above\n4 gasoline contracts · +Δ = higher gas price",
            "APPROVAL_strength":  "APPROVAL_strength\n4 approval contracts · +Δ = stronger approval"}
    blocks, i = [], 0
    while i < len(combos):
        g = combos[i][0]; j = i
        while j < len(combos) and combos[j][0] == g:
            j += 1
        blocks.append((i, j - 1, desc.get(g, g)))
        i = j
    title = ("GRANGER joint-Wald p — merged pooled signals: each group × its ETFs × 6 regressions\n"
             "Pooled = pooled sign-aligned member contracts (each left block = one pooled signal, labelled).  "
             "cell = joint Wald p (H0: NO Granger causality); p<0.05 (red) = that direction's lead IS significant.\n"
             "CALENDAR Pooled→ETF lit while ETF→Pooled pale ⇒ the pooled signal Granger-leads the ETF.")
    _draw_heatmap(labels, P, col_labels, title, out_png, row_dividers=rd, blocks=blocks)


# ============================ 每对 2×3 详情图 ============================
def _lin_reason(df, xc, K):
    na = int((df[xc].abs() > 1e-12).sum()) if (df is not None and not df.empty) else 0
    return f"linear not estimable\n(active bars = {na};\nneed ≥ {2*K+5} aligned obs)"


def _pro_reason(tbl):
    if tbl is None or len(tbl) == 0:
        return "probit not run\n(no usable calendar/event table)"
    n = int((tbl["y"] != 0).sum())
    return f"probit not run\n(only {n} up/down bars;\nneed ≥ 30)"


def _panel(ax, res, base, name, reason_fn):
    if res is None or "beta" not in res:
        ax.text(0.5, 0.5, reason_fn(), ha="center", va="center", fontsize=8.5, color="#666")
        ax.set_title(name, fontsize=9); ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values():
            s.set_color("#ccc")
        return
    lags, beta, pv = res["lags"], res["beta"], res["coef_p"]
    for L, b, p in zip(lags, beta, pv):
        if p < 0.05:
            ax.bar(L, b, width=0.8, color=base, edgecolor=base, linewidth=1.1)
        elif p < 0.15:
            ax.bar(L, b, width=0.8, color=base, alpha=0.38, edgecolor=base, linewidth=1.1)
        else:
            ax.bar(L, b, width=0.8, color="white", edgecolor=base, linewidth=1.1)
    ax.axhline(0, color="k", lw=0.8); ax.set_xticks(list(lags)); ax.tick_params(labelsize=8)
    ax.set_xlabel("lag j", fontsize=8)
    ax.set_title(f"{name}\njoint Wald χ²({res['wald_df']}) = {res['wald_chi2']:.1f},  "
                 f"p = {res['p_value']:.2g} {_stars(res['p_value'])}", fontsize=8.6)
    ax.text(0.02, 0.97, f"n_obs={res['n_obs']}  n_active={res['n_active']}  K={res['K']}",
            transform=ax.transAxes, fontsize=6.8, va="top", color="#555")


def granger_figure(al_cal, act, cal_pro, evt_pro, title, out_png):
    fig, axes = plt.subplots(2, 3, figsize=(14, 7.8))
    rows = [("CALENDAR", al_cal, "dprob", "etfret", cal_pro),
            ("EVENT", act, "dprob_e", "etfret_e", evt_pro)]
    for ri, (mode, df, xc, yc, pro) in enumerate(rows):
        na = int((df[xc].abs() > 1e-12).sum()) if (df is not None and not df.empty) else 0
        K = C.choose_k(na)
        ke = C.run_granger_direction(df, xc, yc, K, group_by_day=True, own_lags="auto", return_coefs=True) \
            if (df is not None and not df.empty) else None
        _panel(axes[ri, 0], ke, BLUE, f"{mode} · linear  Kalshi→ETF",
               lambda df=df, xc=xc, K=K: _lin_reason(df, xc, K))
        ek = C.run_granger_direction(df, yc, xc, K, group_by_day=True, own_lags="auto", return_coefs=True) \
            if (df is not None and not df.empty) else None
        _panel(axes[ri, 1], ek, RED, f"{mode} · linear  ETF→Kalshi",
               lambda df=df, xc=xc, K=K: _lin_reason(df, xc, K))
        pr = None
        if pro is not None and len(pro) >= 30:
            pr = C.run_granger_probit(pro, "x", "y", C.choose_k(len(pro)), group_by_day=True,
                                      own_lags="auto", return_coefs=True)
        _panel(axes[ri, 2], pr, GREEN, f"{mode} · probit  Kalshi→ETF", lambda pro=pro: _pro_reason(pro))
        axes[ri, 0].set_ylabel("standardized coef  β\n(comparable across pairs)", fontsize=8)

    handles = [Patch(fc=BLUE, ec=BLUE, label="lag p<0.05"),
               Patch(fc=BLUE, ec=BLUE, alpha=0.38, label="0.05≤p<0.15"),
               Patch(fc="white", ec=BLUE, label="p≥0.15 (n.s.)")]
    fig.legend(handles=handles, loc="lower center", ncol=3, fontsize=8, frameon=False, bbox_to_anchor=(0.5, -0.02))
    fig.suptitle(f"GRANGER regressions — {title}\n"
                 "each panel = one regression; bar = standardized coef per lag; "
                 "TITLE joint-Wald p is the Granger result (H0: all lags = 0)",
                 fontsize=11, fontweight="bold")
    fig.tight_layout(rect=[0, 0.02, 1, 0.94])
    fig.savefig(out_png, dpi=150, bbox_inches="tight"); plt.close(fig)


def _one(con, sig, tk, etf, out_png):
    row = sig[(sig.contract_ticker == tk) & (sig.etf == etf)].iloc[0]
    ds, de = str(row.date_start), str(row.date_end)
    k = C.load_kalshi(con, tk, ds, de); e = C.load_etf(con, etf, ds, de)
    if k.empty or e.empty:
        print("  无数据，跳过", tk, etf); return
    med = C.median_intertrade_sec(k)
    freq = C.BAR_LABEL[C.choose_bar_sec(med if np.isfinite(med) else 60)]
    al_cal, act = C.build_unified_xy(k, e, freq)
    cal_pro, _ = LP.build_calendar_xy(con, tk, etf, ds, de)
    evt_pro, _ = LP.build_event_xy(con, tk, etf, ds, de)
    granger_figure(al_cal, act, cal_pro, evt_pro, f"{tk} × {etf}", out_png)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "heatmap":
        out = PLOTS / "granger_heatmap.png"; granger_heatmap(out); print("saved", out); return
    if len(sys.argv) > 1 and sys.argv[1] == "merge-heatmap":
        out = PLOTS / "granger_merge_heatmap.png"; merge_heatmap(out); print("saved", out); return
    con = C.make_con(); sig = pd.read_csv(C.SIG_PAIRS_CSV)
    if len(sys.argv) > 2:
        tk, etf = sys.argv[1], sys.argv[2]
        out = PLOTS / f"PREVIEW_granger_{tk}_{etf}.png"
        _one(con, sig, tk, etf, out); print("saved", out); return
    for _, r in sig.iterrows():
        tag = f"{r.contract_ticker}_{r.etf}"
        try:
            _one(con, sig, r.contract_ticker, r.etf, PLOTS / f"{tag}_granger.png"); print("ok", tag)
        except Exception as ex:
            print("skip", tag, ex)


if __name__ == "__main__":
    main()
