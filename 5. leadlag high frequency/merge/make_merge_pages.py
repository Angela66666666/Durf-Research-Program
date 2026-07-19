"""
make_merge_pages.py  (leadlag/pipeline/merge/)
================================================================================
这个文件做什么 (What this file does)
  把 merge_leadlag 的 4 个池化信号回归结果，渲染成「每类一页」的报告素材：
    · merge_{group}_analysis.md   数据分析文字页（成员/符号/ETF并集/选中的K与ADL阶 +
                                   calendar/event/probit 在 p<0.05/0.10/0.15 三档的
                                   Kalshi-leads vs ETF-leads 方向计数表 + 结论）
    · merge_{group}_lagcoef.png    每个相关 ETF 一个小面板的滞后系数图（实心点=p<0.15）
  供 build_pdf.py 在报告末尾拼出「MERGE — pooled signals」专区。

为什么这么做 (Why)
  merge 之前只落地三张结果 CSV，没有可读页面。这里把池化结果按池化信号整理成与单对页
  同口径（分级阈值、方向计数）的表格 + 图，便于和单合约结论对照。

口径 (Conventions)
  · 方向计数用**原始 p**(与 leadlag_classification 的分级阈值口径一致)。
  · calendar 只取 is_primary_bar 的那套（与单对页一致）。
  · K(滞后窗)、ADL 自滞后阶 n_ylags 直接读回归输出列。

输出 (Outputs, 落在 merge/plots/ 下)
  merge_{group}_analysis.md, merge_{group}_lagcoef.png, merge_order.csv
"""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PIPE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PIPE))
import leadlag_common as C            # noqa: E402
import merge_leadlag as M            # 复用 GROUPS（成员+符号）  # noqa: E402

HERE   = Path(__file__).resolve().parent
PLOTS  = HERE / "plots"; PLOTS.mkdir(exist_ok=True)
THRESH = (0.05, 0.10, 0.15)
CAL = pd.read_csv(HERE / "leadlag_merged_calendar_kalshi_etf.csv")
EV  = pd.read_csv(HERE / "leadlag_merged_event_kalshi_etf.csv")
PRB = pd.read_csv(HERE / "leadlag_merged_probit_kalshi_etf.csv")
C_CAL, C_EV = "#1f77b4", "#d62728"


def _ke_counts(df):
    """返回 {thr: (kalshi_leads, etf_leads)}，用原始 p，方向按 k_lag 正负。"""
    out = {}
    for thr in THRESH:
        s = df[df["p_value"] < thr]
        out[thr] = (int((s["k_lag"] > 0).sum()), int((s["k_lag"] < 0).sum()))
    return out


def _cal_primary(group, etf):
    d = CAL[(CAL["group"] == group) & (CAL["etf"] == etf)]
    if "is_primary_bar" in d.columns:
        dp = d[d["is_primary_bar"]]
        return dp if not dp.empty else d
    return d


def _fmt_ke(ke):
    return "  ".join(f"p<{t:.2f}: K{ke[t][0]}/E{ke[t][1]}" for t in THRESH)


def _meta(df):
    """从一组结果行里取 K、ADL 阶、n_obs（取primary/任意一行）。"""
    if df.empty:
        return "-", "-", "-"
    r = df.iloc[0]
    K  = int(r["K_chosen"]) if "K_chosen" in df.columns and pd.notna(r["K_chosen"]) else "-"
    yl = int(r["n_ylags"]) if "n_ylags" in df.columns and pd.notna(r["n_ylags"]) else "-"
    no = int(r["n_obs"]) if "n_obs" in df.columns and pd.notna(r["n_obs"]) else "-"
    return K, yl, no


def write_group_md(group, members_signs):
    etfs = sorted(set(CAL[CAL["group"] == group]["etf"]).union(EV[EV["group"] == group]["etf"]))
    pos = [t for t, s in members_signs.items() if s > 0]
    neg = [t for t, s in members_signs.items() if s < 0]
    L = [f"MERGE pooled signal:  {group}",
         "",
         f"Members pooled (sign-aligned Δprob, never concatenated price levels):",
         f"  +  {', '.join(pos)}",
         (f"  -  {', '.join(neg)}   (reverse contracts: Δprob flipped so +Δ = same direction)"
          if neg else "  -  (none)"),
         f"Relevant-ETF union ({len(etfs)}): {', '.join(etfs)}",
         "",
         "Pooling engine: per-member lag/ADL shift, member fixed effects, day-clustered SE;",
         "ADL self-lag order chosen per pooled regression by BIC (column n_ylags).",
         "Direction counts below use RAW p (same graded-threshold convention as the single-pair report).",
         ""]
    for mode, df_all, lab in [("calendar", CAL, "CALENDAR (primary bar)"),
                              ("event", EV, "EVENT (active-event subsequence)"),
                              ("probit", PRB, "PROBIT (direction test Pr(ETF up))")]:
        L.append(f"== {lab} ==")
        L.append(f"{'ETF':6s} {'K':>3} {'ADL':>4} {'n_obs':>7}   Kalshi-leads(k>0) / ETF-leads(k<0)")
        for etf in etfs:
            if mode == "calendar":
                d = _cal_primary(group, etf)
            else:
                d = df_all[(df_all["group"] == group) & (df_all["etf"] == etf)]
            if d.empty:
                L.append(f"{etf:6s}   -    -        -   (no result)")
                continue
            K, yl, no = _meta(d)
            L.append(f"{etf:6s} {str(K):>3} {str(yl):>4} {str(no):>7}   {_fmt_ke(_ke_counts(d))}")
        L.append("")
    # 组级结论：把该组所有 ETF 的 calendar+event 方向计数加总，看三档下谁多
    agg = pd.concat([CAL[(CAL['group'] == group)], EV[EV['group'] == group]], ignore_index=True)
    ke = _ke_counts(agg)
    verdict = []
    for t in THRESH:
        k, e = ke[t]
        tag = "Kalshi-leads" if k > e else ("ETF-leads" if e > k else "balanced/none")
        verdict.append(f"p<{t:.2f}: {tag} (K{k}/E{e})")
    L += ["== Conclusion (calendar+event pooled across the group's ETFs) ==",
          "  " + " | ".join(verdict),
          "  Read alongside the single-pair tally; pooling buys df but the lead is in the sign, not magnitude."]
    (PLOTS / f"merge_{group}_analysis.md").write_text("\n".join(L), encoding="utf-8")


def plot_group_lagcoef(group):
    etfs = sorted(set(CAL[CAL["group"] == group]["etf"]).union(EV[EV["group"] == group]["etf"]))
    if not etfs:
        return
    n = len(etfs); ncol = min(3, n); nrow = int(np.ceil(n / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(4.3 * ncol, 3.2 * nrow), squeeze=False)
    for ax in axes.flat:
        ax.axis("off")
    for idx, etf in enumerate(etfs):
        ax = axes[idx // ncol][idx % ncol]; ax.axis("on")
        for d, color, mk, lab in [(_cal_primary(group, etf), C_CAL, "o", "calendar"),
                                  (EV[(EV["group"] == group) & (EV["etf"] == etf)], C_EV, "s", "event")]:
            if d.empty:
                continue
            d = d.sort_values("k_lag")
            ax.plot(d["k_lag"], d["coef"], "-", color=color, marker=mk, ms=4, mfc="none", lw=1.0, label=lab)
            s = d[d["p_value"] < 0.15]                    # 实心点 = 原始 p<0.15
            ax.plot(s["k_lag"], s["coef"], linestyle="none", color=color, marker=mk, ms=7)
        ax.axhline(0, color="gray", lw=0.8); ax.axvline(0, color="gray", ls=":", lw=0.8)
        ax.set_title(etf, fontsize=10); ax.tick_params(labelsize=8)
        ax.set_xlabel("lag j  (j>0 Kalshi leads | j<0 ETF leads)", fontsize=7)
        if idx == 0:
            ax.legend(fontsize=7, loc="best")
    fig.suptitle(f"MERGE {group} — pooled lead-lag coefficients (filled = raw p<0.15)", fontsize=11, y=1.0)
    fig.tight_layout()
    fig.savefig(PLOTS / f"merge_{group}_lagcoef.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def main():
    order = []
    for group, members_signs in M.GROUPS.items():
        if group not in set(CAL["group"]).union(EV["group"]):
            print(f"  {group}: 无结果，跳过"); continue
        write_group_md(group, members_signs)
        plot_group_lagcoef(group)
        order.append({"group": group})
        print(f"  {group}: md + lagcoef 完成")
    pd.DataFrame(order).to_csv(PLOTS / "merge_order.csv", index=False)
    print(f"完成 -> {PLOTS}  (merge_order.csv: {len(order)} 组)")


if __name__ == "__main__":
    main()
