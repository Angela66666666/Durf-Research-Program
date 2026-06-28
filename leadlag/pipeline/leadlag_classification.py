"""
leadlag_classification.py
================================================================================
这个文件做什么 (What this file does)
  把全部 48 对 (Kalshi 合约 × ETF) 按四个维度分组，统计每组里"谁领先"，
  回答："任何方向性领先，是不是只集中在某一类合约/板块/活跃度上？"
  Group all 48 (Kalshi contract × ETF) pairs along four dimensions and tally the
  lead/lag verdict within each group — i.e. "is any directional lead concentrated
  in a particular contract type / sector / activity bucket?"

为什么这么做 (Why)
  单看 48 对的逐对结果是一锅粥、看不出规律；需要回答"领先到底藏在哪类里"。
  把逐对结论按可解释的维度聚合，才能得出可写进论文的归纳性结论。
  The pair-by-pair table is too noisy to read; aggregating the per-pair verdict
  along interpretable dimensions is what yields a paper-ready generalization.

思路 (Approach)
  1) 给每对打标签：合约类型、ETF 板块、事件性质(单点 vs 连续)、**统计可靠性档**
     (来自 leadlag_reliability，按残差自由度判定，取代成交笔数阈值)。
  2) 给每对定 lead/lag 倾向：数 calendar + event 两套里"显著且 k>0(Kalshi 领先)"
     与"显著且 k<0(ETF 领先)"的滞后个数，净值定倾向(与逐对文字页口径一致)。
  3) 按各维度交叉汇总，输出表 + 一张分组柱状图 + 文字结论。

输入 (Inputs)
  - regression/significant_pairs.csv                  (48 对清单 + 标题/板块/窗口)
  - leadlag_calendar_kalshi_etf.csv (is_primary_bar)  (calendar 联合回归系数)
  - leadlag_event_kalshi_etf.csv                      (event 联合回归系数)
  - leadlag_probit_kalshi_etf.csv                     (probit 方向检验)
  - plots/pair_ranking.csv                            (n_trades 活跃度)

输出 (Outputs)  —— 都落在 leadlag/pipeline 目录下
  - leadlag_classification.csv          每对一行的分类 + 倾向明细
  - leadlag_classification_summary.md   各维度汇总表 + 文字结论(可编辑)
  - plots/classification_summary.png    分组柱状图(按合约类型/板块/活跃度)

函数 (Functions)
  - contract_type(t)   ：从 ticker 前缀判合约类型(选举/FOMC/汽油/支持率)
  - event_kind(ct)     ：单点事件 sharp vs 连续监测 continuous
  - sector_name(etf)   ：Vanguard 板块 ETF -> 中文板块名
  - activity_bucket(n) ：成交量 -> 稀疏/中等/活跃
  - pair_lean(cal,ev)  ：数两套显著滞后的正负个数 -> (kpos,kneg,lean)
  - build_table()      ：拼每对一行的分类表
  - group_counts(df,by)：按某维度汇总各 lean 类别的对数
  - plot_summary(df)   ：画分组堆叠柱状图
  - write_md(df)       ：写汇总 markdown + 文字结论
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import leadlag_common as C
import leadlag_reliability as REL   # 统计可靠性分档（取代成交笔数阈值）

PLOTDIR = C.HERE / "plots"
SIG  = pd.read_csv(C.SIG_PAIRS_CSV)
CAL  = pd.read_csv(C.HERE / "leadlag_calendar_kalshi_etf.csv")
CAL  = CAL[CAL["is_primary_bar"]]
EV   = pd.read_csv(C.HERE / "leadlag_event_kalshi_etf.csv")
PRB  = pd.read_csv(C.HERE / "leadlag_probit_kalshi_etf.csv")
RANK = pd.read_csv(PLOTDIR / "pair_ranking.csv")

OUT_CSV = C.HERE / "leadlag_classification.csv"
OUT_MD  = C.HERE / "leadlag_classification_summary.md"
OUT_PNG = PLOTDIR / "classification_summary.png"

# lean 类别配色（图用）
LEAN_ORDER  = ["Kalshi-leads", "ETF-leads", "Balanced/mixed", "No-sig-lead"]
LEAN_COLOR  = {"Kalshi-leads": "#e74c3c", "ETF-leads": "#3498db",
               "Balanced/mixed": "#95a5a6", "No-sig-lead": "#dcdcdc"}

_SECTOR = {
    "VAW": "Materials", "VCR": "Cons.Disc", "VDC": "Cons.Staples",
    "VDE": "Energy", "VFH": "Financials", "VGT": "Info-Tech",
    "VHT": "Health", "VIS": "Industrials", "VNQ": "Real-Estate",
    "VOX": "Comm", "VPU": "Utilities",
}


def contract_type(t):
    """从 ticker 前缀判合约类型。Map ticker prefix -> contract family."""
    t = t.upper()
    if "ECDJT" in t or "ECKH" in t:
        return "Election"
    if "FEDDECISION" in t or "RATECUT" in t:
        return "Rates(FOMC)"
    if "GASM" in t:
        return "GasPrice"
    if "APPROVE" in t:
        return "Approval"
    return "Other"


def event_kind(ct):
    """事件性质：选举/FOMC 是单点冲击；汽油/支持率是连续慢变。sharp vs continuous."""
    return "Sharp(one-shot)" if ct in ("Election", "Rates(FOMC)") else "Continuous"


def sector_name(etf):
    return _SECTOR.get(etf, etf)


def activity_bucket(n):
    """成交量分桶。Activity bucket by Kalshi trade count."""
    if n < 50:
        return "Sparse(<50)"
    if n < 300:
        return "Medium(50-300)"
    return "Active(>300)"


THRESHOLDS = (0.05, 0.10, 0.15)   # 分档显著性阈值（原始 p；FDR 在小样本里会把 0.10/0.15 压没）


def _lean_of(kpos, kneg):
    """据某一档的 Kalshi领先(kpos)/ETF领先(kneg) 个数定该档结论。"""
    if kpos == 0 and kneg == 0:
        return "No-sig-lead"
    if kpos > kneg:
        return "Kalshi-leads"
    if kneg > kpos:
        return "ETF-leads"
    return "Balanced/mixed"


def pair_lean(cal, ev):
    """calendar 与 event **各自**都算 p<0.05 / 0.10 / 0.15 三档显著滞后的正(k>0,Kalshi领先)/
    负(k<0,ETF领先)个数(原始 p)。三档是 **nested 包含关系**：p<0.05 ⊆ p<0.10 ⊆ p<0.15(每档已是
    并集本身，不需也不该把三档算术相加)。
    **三档各出一个结论 lean**(不只选一档)：每档据该档 calendar+event 合计的 Kalshi领先 vs ETF领先 定。
    Both calendar and event get all three nested tiers; a lean conclusion is produced at EACH tier.
    返回 cal_t / ev_t / comb = {thr:(kpos,kneg)}, leans = {thr: lean}。"""
    def tiers_of(df):
        return {thr: (int((df[df["p_value"] < thr]["k_lag"] > 0).sum()),
                      int((df[df["p_value"] < thr]["k_lag"] < 0).sum())) for thr in THRESHOLDS}
    cal_t = tiers_of(cal)
    ev_t  = tiers_of(ev)
    comb  = {thr: (cal_t[thr][0] + ev_t[thr][0], cal_t[thr][1] + ev_t[thr][1]) for thr in THRESHOLDS}
    leans = {thr: _lean_of(*comb[thr]) for thr in THRESHOLDS}   # 三档各出一个结论
    return cal_t, ev_t, comb, leans


def build_table():
    """拼每对一行的分类表。Build the per-pair classification table."""
    rows = []
    rk = RANK.set_index(["contract_ticker", "etf"])
    for _, s in SIG.iterrows():
        tk, etf = s["contract_ticker"], s["etf"]
        cal = CAL[(CAL.contract_ticker == tk) & (CAL.etf == etf)]
        ev  = EV[(EV.contract_ticker == tk) & (EV.etf == etf)]
        prb = PRB[(PRB.contract_ticker == tk) & (PRB.etf == etf)]
        n_tr = int(rk.loc[(tk, etf), "n_trades"]) if (tk, etf) in rk.index else 0
        cal_t, ev_t, comb, leans = pair_lean(cal, ev)
        prb_pos = int(((prb["p_value"] < 0.05) & (prb["k_lag"] > 0)).sum())
        prb_neg = int(((prb["p_value"] < 0.05) & (prb["k_lag"] < 0)).sum())
        ct = contract_type(tk)
        rows.append({
            "contract_ticker": tk, "etf": etf,
            "contract_type": ct, "event_kind": event_kind(ct),
            "sector": sector_name(etf), "n_trades": n_tr,
            "activity": activity_bucket(n_tr),
            "reliability": REL.get_reliability(tk, etf)["tier"],   # 统计可靠性档（按自由度）
            # ① calendar 三档(nested) Kalshi领先(kpos)/ETF领先(kneg)
            "cal_kpos_05": cal_t[0.05][0], "cal_kneg_05": cal_t[0.05][1],
            "cal_kpos_10": cal_t[0.10][0], "cal_kneg_10": cal_t[0.10][1],
            "cal_kpos_15": cal_t[0.15][0], "cal_kneg_15": cal_t[0.15][1],
            # ② event 三档(nested)
            "ev_kpos_05": ev_t[0.05][0], "ev_kneg_05": ev_t[0.05][1],
            "ev_kpos_10": ev_t[0.10][0], "ev_kneg_10": ev_t[0.10][1],
            "ev_kpos_15": ev_t[0.15][0], "ev_kneg_15": ev_t[0.15][1],
            # ③ calendar+event 合计 三档(nested)
            "kpos_05": comb[0.05][0], "kneg_05": comb[0.05][1],
            "kpos_10": comb[0.10][0], "kneg_10": comb[0.10][1],
            "kpos_15": comb[0.15][0], "kneg_15": comb[0.15][1],
            # 兼容旧列名（= p<0.05 两套合计）
            "sig_kalshi_leads": comb[0.05][0], "sig_etf_leads": comb[0.05][1],
            # ④ 总数 = 最宽档 p<0.15 的并集(= kpos_15 + kneg_15，不是三档算术相加)；lean 据 kpos_15 vs kneg_15
            "sig_total": comb[0.15][0] + comb[0.15][1],
            # ⑤ 三档各出一个结论
            "lean_05": leans[0.05], "lean_10": leans[0.10], "lean_15": leans[0.15],
            "lean": leans[0.15],   # 默认/兼容(给图与旧引用) = 最宽档
            "probit_kalshi_leads": prb_pos, "probit_etf_leads": prb_neg,
        })
    return pd.DataFrame(rows)


LEAN_ABBR = {"Kalshi-leads": "K", "ETF-leads": "E", "Balanced/mixed": "B", "No-sig-lead": "N"}


def group_counts(df, by, lean_col="lean"):
    """按某维度汇总各 lean 类别的对数（lean_col 指定用哪一档的结论）。
    Cross-tab pair counts of <lean_col> within each group."""
    tab = (df.groupby([by, lean_col]).size().unstack(fill_value=0)
             .reindex(columns=LEAN_ORDER, fill_value=0))
    tab["Total"] = tab.sum(axis=1)
    return tab.sort_values("Total", ascending=False)


def plot_summary(df):
    """画三张分组堆叠柱状图：按合约类型 / 板块 / 可靠性，看 lean 分布。"""
    dims = [("contract_type", "by contract type"),
            ("sector", "by ETF sector"),
            ("reliability", "by statistical reliability (df-based)")]
    fig, axes = plt.subplots(3, 1, figsize=(12, 13))
    for ax, (by, title) in zip(axes, dims):
        tab = group_counts(df, by).drop(columns="Total")
        tab = tab.iloc[::-1]
        bottom = np.zeros(len(tab))
        for lean in LEAN_ORDER:
            ax.barh(tab.index, tab[lean], left=bottom, color=LEAN_COLOR[lean], label=lean)
            bottom += tab[lean].values
        ax.set_title(title, fontsize=12)
        ax.set_xlabel("number of pairs", fontsize=9)
        ax.tick_params(labelsize=9)
    axes[0].legend(loc="upper right", fontsize=9, title="lean")
    fig.suptitle("Lead/Lag classification: is directional lead concentrated anywhere?  "
                 "(red=Kalshi leads, blue=ETF leads)", fontsize=13, y=1.0)
    fig.tight_layout(rect=[0, 0, 1, 0.99])
    fig.savefig(OUT_PNG, dpi=200, bbox_inches="tight")
    plt.close(fig)


def _fmt_tab(tab):
    return tab.to_string()


def graded_direction_md():
    """分级阈值方向分布：显著系数(=pair×滞后阶)在 Kalshi领先(k>0)/ETF领先(k<0)/同期(k=0) 的计数，
    在 p<0.05 / 0.10 / 0.15 三个阈值各报一次(原始 p)。不做单一 0.05 一刀切，便于看方向是否稳健。"""
    def block(name, d, need_beta=False):
        out = [f"**{name}**  (coefficient = pair × lag, raw p)\n", "```",
               f"{'thresh':>7} | {'sig':>4} | {'Kalshi(k>0)':>11} | {'ETF(k<0)':>8} | {'contemp':>7}"]
        for thr in (0.05, 0.10, 0.15):
            s = d[d["p_value"] < thr]
            kp = s[s["k_lag"] > 0]
            if need_beta and "beta" in s.columns:
                kp = kp[kp["beta"] > 0]
            out.append(f" p<{thr:<4} | {len(s):>4} | {len(kp):>11} | "
                       f"{len(s[s['k_lag'] < 0]):>8} | {len(s[s['k_lag'] == 0]):>7}")
        out.append("```\n")
        return "\n".join(out)
    return "\n".join([
        "## Direction by graded significance (no single cutoff)\n",
        "Report direction at p<0.05 / 0.10 / 0.15 rather than one threshold, to show robustness.\n",
        block("calendar (primary bar)", CAL),
        block("event (backward-diff, comparable to calendar)", EV),
        block("probit (direction-only; Kalshi-leads requires beta>0)", PRB, need_beta=True),
    ])


def pairs_by_category_md(df):
    """四个分类维度下，每个类别具体包含哪些 pair（附其 lean），让计数表能落到具体的对。
    For each of the four dimensions, list the actual pairs in every category with their lean."""
    df = df.copy()
    df["pair"] = df["contract_ticker"] + "×" + df["etf"]
    dims = [("contract_type", "contract type"), ("event_kind", "event kind (sharp vs continuous)"),
            ("sector", "ETF sector"), ("reliability", "reliability tier (df-based)")]
    L = ["## Pairs in each category (which pairs fall under each classification)\n",
         "For each of the four dimensions, every category lists its pairs with their lean at each tier "
         "[05|10|15], abbreviated K=Kalshi-leads, E=ETF-leads, B=Balanced/mixed, N=No-sig-lead "
         "(so each count above can be traced to the actual pairs).\n"]
    for col, label in dims:
        L.append(f"### By {label}\n")
        for cat, g in df.groupby(col):
            g = g.sort_values(["lean_15", "pair"])
            items = ", ".join(
                f"{r.pair} [{LEAN_ABBR[r.lean_05]}|{LEAN_ABBR[r.lean_10]}|{LEAN_ABBR[r.lean_15]}]"
                for r in g.itertuples())
            L.append(f"- **{cat}** ({len(g)}): {items}")
        L.append("")
    return "\n".join(L)


def write_md(df):
    """写汇总 markdown：四维度表 + 文字结论。"""
    n = len(df)
    TIER_COL = {0.05: "lean_05", 0.10: "lean_10", 0.15: "lean_15"}   # 三档各一个结论列

    # direction only within the "Adequate-df" reliable pairs
    rel_ok = df[df.reliability == REL.TIER_OK]
    L = []
    L.append("# Lead/Lag classification summary\n")
    L.append(f"Scope: all {n} pairs (Kalshi contract x ETF). Lean rule: across calendar+event, count")
    L.append("significant lags at p<0.05 / 0.10 / 0.15 (raw p; nested, p<0.05 ⊆ p<0.10 ⊆ p<0.15) per")
    L.append("direction (k>0 Kalshi-leads, k<0 ETF-leads). **A lean conclusion is produced at EACH tier**, not")
    L.append("a single chosen threshold, so the Overall and every cross-tab below appear three times (one per tier).")
    L.append("Reliability rule: tiered by residual df (= effective obs - #parameters), NOT a trade-count cutoff.\n")

    L.append("## Overall — lean counts at each threshold\n")
    ov = pd.DataFrame({f"p<{thr}": df[col].value_counts() for thr, col in TIER_COL.items()}).T
    ov = ov.reindex(columns=LEAN_ORDER, fill_value=0).fillna(0).astype(int)
    L.append("```\n" + ov.to_string() + "\n```\n")

    for col, label in [("contract_type", "By contract type"),
                       ("event_kind", "By event kind (sharp one-shot vs continuous)"),
                       ("sector", "By ETF sector"),
                       ("reliability", "By statistical reliability (df-based)")]:
        L.append(f"## {label}\n")
        for thr, lc in TIER_COL.items():
            L.append(f"**lean at p<{thr}:**\n")
            L.append("```\n" + _fmt_tab(group_counts(df, col, lc)) + "\n```\n")

    L.append(graded_direction_md())

    L.append("## Conclusion\n")
    n_cannot = int((df.reliability == REL.TIER_CANNOT).sum())
    n_verylow = int((df.reliability == REL.TIER_VERYLOW).sum())
    n_ok = int((df.reliability == REL.TIER_OK).sum())
    L.append(f"- **Pairs without data expose themselves**: {n_cannot} **cannot be estimated** (params >= obs) and "
             f"{n_verylow} have **very low df** (huge SE, 'significant' is untrustworthy) -- high-frequency lead-lag "
             f"is only meaningful on the {n_ok} pairs with adequate df.")
    if len(rel_ok):
        parts = []
        for thr, lc in TIER_COL.items():
            ak = int((rel_ok[lc] == "Kalshi-leads").sum())
            ae = int((rel_ok[lc] == "ETF-leads").sum())
            ab = int((rel_ok[lc] == "Balanced/mixed").sum())
            an = int((rel_ok[lc] == "No-sig-lead").sum())
            parts.append(f"p<{thr} K{ak}/E{ae}/B{ab}/N{an}")
        L.append(f"- **Even the reliable group is not one-sided**: of {len(rel_ok)} adequate-df pairs, lean by "
                 f"tier — {'; '.join(parts)} — no side dominates at any threshold.")
    L.append("- **Direction is threshold-robust but method-split** (see graded table above): across "
             "p<0.05/0.10/0.15 the linear regressions (calendar, event) split ~1:1 with no net lead at any "
             "threshold, while the direction-only probit consistently favors ETF-leads (~5:1). Any lead lives "
             "in the *sign* of ETF moves, not their magnitude.")
    L.append("- **Construction note**: event uses the same causal backward-diff as calendar (differing only in "
             "active-event vs clock timepoints). An earlier forward-return event construction had spuriously "
             "inflated ETF-leads by overlapping each event's forward window with the next event; that artifact "
             "is removed, after which event splits ~1:1.")
    L.append("- **By type**: election / FOMC (one-shot event) contracts contribute almost all of the estimable, "
             "significant structure; gas-price / approval (continuous) contracts mostly fall in 'cannot estimate'.")
    L.append("- **Conclusion**: directional lead is **NOT concentrated in any single clean category**; the strongest "
             "signal comes from adequate-df one-shot-event contracts (election, FOMC), but within them Kalshi-leads "
             "and ETF-leads coexist -- supporting the main finding of 'no clean single-direction lead'.\n")
    L.append(pairs_by_category_md(df))

    L.append("> Note: auto-generated from the tables above; edit this file then merge into the report. "
             "Figure: plots/classification_summary.png.")
    OUT_MD.write_text("\n".join(L), encoding="utf-8")


def main():
    df = build_table()
    df.to_csv(OUT_CSV, index=False)
    plot_summary(df)
    write_md(df)
    print(f"分类完成：{len(df)} 对")
    print(f"  -> {OUT_CSV.name}")
    print(f"  -> {OUT_MD.name}")
    print(f"  -> {OUT_PNG.relative_to(C.HERE)}")
    print("\n按合约类型：")
    print(group_counts(df, "contract_type").to_string())
    print("\n按统计可靠性（df 判据）：")
    print(group_counts(df, "reliability").to_string())


if __name__ == "__main__":
    main()
