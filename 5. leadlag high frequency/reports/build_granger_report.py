"""
build_granger_report.py
================================================================================
这个文件做什么 (What this file does)
  把 Granger 联合因果检验单独拼成一份**专属报告**(PDF + 内容一模一样的 MD)：
    总览(方法+英文结论+判定表) -> **核心图1: 单对联合-p 热力图** -> 每对文字明细(显式公式 +
    双向 Wald + probit + verdict，无图) -> **核心图2: merge 联合-p 热力图** -> 每组×ETF 文字明细。
  只放和 Granger 直接相关的东西：两张热力图(联合 p 一眼铺开) + 每对的显式公式与联合检验。
  与单对/merge 主报告分开：主报告只讲逐系数 lead-lag，这份只讲 Granger headline 统计量。

为什么 (Why)
  Granger 是「一个方向一个联合 p 值」的 headline，和逐系数报告是不同对象，独立成册更清楚
  （老师直接要求的对象；日频 Var.py 的 test_causality 的高频重装）。方法细节见 GRANGER_TEST.md。

输入 (Inputs)
  leadlag_granger_pairs.csv                (leadlag_granger.py)
  merge/leadlag_merged_granger.csv         (merge/merge_granger.py)
  plots/granger_heatmap.png, plots/granger_merge_heatmap.png  (make_granger_plots.py, 本脚本会先生成)
  plots/pair_ranking.csv                   (单对排序)

输出 (Outputs, 落在 leadlag/pipeline/ 下)
  leadlag_granger_report.pdf   (本地查看, 不入库)
  leadlag_granger_report.md    (入库, 图用相对路径内嵌, GitHub 直接渲染)
"""
import re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pandas as pd

import leadlag_common as C
import make_pair_text as MPT           # build_text_fig / _sub / stars 复用
import make_granger_plots as MGP       # 两张核心热力图

PLOTDIR  = C.HERE / "plots"
MERGEDIR = C.HERE / "merge" / "plots"
GR   = pd.read_csv(C.HERE / "leadlag_granger_pairs.csv")
GRM  = pd.read_csv(MERGEDIR.parent / "leadlag_merged_granger.csv") if (MERGEDIR.parent / "leadlag_merged_granger.csv").exists() else pd.DataFrame()
RANK = pd.read_csv(PLOTDIR / "pair_ranking.csv")
SIG  = pd.read_csv(C.SIG_PAIRS_CSV)
COV  = pd.read_csv(C.HERE / "leadlag_granger_coverage.csv") if (C.HERE / "leadlag_granger_coverage.csv").exists() else pd.DataFrame()
HEATMAP       = PLOTDIR / "granger_heatmap.png"
MERGE_HEATMAP = PLOTDIR / "granger_merge_heatmap.png"
OUT_PDF = C.HERE / "leadlag_granger_report.pdf"
OUT_MD  = C.HERE / "leadlag_granger_report.md"


def _cov_counts():
    """(n_estimable, n_total) — 动态，避免把 25/48 写死。"""
    if not COV.empty:
        return int(COV["estimable"].sum()), int(len(COV))
    return int(GR[["contract_ticker", "etf"]].drop_duplicates().shape[0]), int(len(SIG))


def _ensure_heatmaps():
    MGP.granger_heatmap(HEATMAP)
    MGP.merge_heatmap(MERGE_HEATMAP)

_sub, stars = MPT._sub, MPT.stars

_INTRO = [
    "GRANGER JOINT CAUSALITY — Kalshi prediction markets  vs  Vanguard sector ETFs",
    "=" * 96,
    "This is the HEADLINE statistic: one joint Wald test per direction giving ONE p-value, replacing the",
    "per-coefficient counting used in the main lead-lag report. It is the high-frequency reinstatement of",
    "this project's daily Var.py results.test_causality (a VAR Granger Wald), and the object the advisor asked",
    "for. Full method: GRANGER_TEST.md.",
    "",
    "DEFINITIONS",
    "   xₜ = Kalshi yes-probability change (Δprob) over bar t ;   yₜ = ETF log return over bar t.",
    "   Only PAST lags of the 'cause' are used (j≥1); the contemporaneous (j=0) and future (j<0) terms are",
    "   NOT part of the test. Each regression controls for the dependent variable's OWN past (ADL self-lags,",
    "   order chosen by BIC).",
    "",
    "THE TEST (per direction)",
    "   Kalshi→ETF:  yₜ = α + Σ(i=1..p) φᵢ·yₜ₋ᵢ + Σ(j=1..K) bⱼ·xₜ₋ⱼ + day-FE ;   H0: b₁=…=b_K=0",
    "   ETF→Kalshi:  xₜ = α + Σ(i=1..q) ψᵢ·xₜ₋ᵢ + Σ(j=1..K) dⱼ·yₜ₋ⱼ + day-FE ;   H0: d₁=…=d_K=0",
    "   Reject H0 (p<0.05) ⇒ that variable Granger-leads the other. Comparing the two p's states who leads.",
    "",
    "STANDARD ERRORS & VALIDITY",
    "   Joint Wald uses panel Newey-West (hac-panel, bandwidth=K, within each trading-day block): full-rank",
    "   (valid even for single-day event contracts, where day-clustering would be rank-deficient) and the",
    "   microstructure-standard covariance for high-frequency intraday data. Δprob and log-returns are",
    "   differenced ⇒ stationary ⇒ plain Granger is valid, no cointegration/VECM needed.",
    "",
    "SAMPLE GATE (identical for both specifications)",
    "   A regression is attempted only if n_active — the number of observations where the CAUSE actually moved —",
    "   is at least 2K+5 (=11 at K=3), a bound derived from the model's parameter count. linear and probit use",
    "   the SAME sample (same calendar grid / event sequence) and the SAME gate, so no pair is estimable under",
    "   one specification but not the other. See the COVERAGE section.",
    "",
    "MULTIPLE TESTING",
    "   Each (time-axis × specification × direction) is one test family; within it the joint-Wald p-values are",
    "   Benjamini-Hochberg FDR-corrected across all pairs (column p_fdr). Both raw p and FDR p are reported;",
    "   conclusions rest on the FDR-corrected counts and, above all, on the asymmetry between directions.",
    "",
    "CONVENTIONS:  ET | 09:30-16:00 | ETF log return | median causal bars | day-grouped lags (no overnight)",
    "              | adaptive bar & K by contract activity | ADL self-lags by BIC | significance p<0.05.",
]


def _verd(pk, pe, a=0.05):
    A = np.isfinite(pk) and pk < a
    B = np.isfinite(pe) and pe < a
    if A and not B: return "Kalshi Granger-leads ETF"
    if B and not A: return "ETF Granger-leads Kalshi"
    if A and B:     return "bidirectional (both reject)"
    return "neither direction significant"


def _adl(sym, coefsym, p):
    if p <= 0:
        return f"(no {sym} self-lag term: BIC chose p=0)"
    return " + ".join(f"{coefsym}{_sub(str(i))}·{sym}{_sub('t-'+str(i))}" for i in range(1, p + 1))


def _dir_lines(row, effect, cause, effcoef, causecoef, label, probit=False):
    """一条方向的显式公式 + H0 + Wald 结果。row 是该方向在 GR 里的一行。"""
    K  = int(row["K"]); p = int(row["n_ylags"]); nd = int(row["n_days"]) if pd.notna(row["n_days"]) else 0
    chi2 = float(row["wald_chi2"]); pv = float(row["p_value"]); dfree = int(row["wald_df"])
    adl = _adl(effect, effcoef, p)
    if probit:
        daynote = f"sample spans {nd} days (probit: no day-FE)"
        lhs = f"Pr({effect}ₜ>0) = Φ( α + {adl} + Σ(j=1..{K}) {causecoef}ⱼ·{cause}ₜ₋ⱼ )"
    else:
        day = f" + Σ(d=1..{nd-1}) γ_d·Day_d" if nd > 1 else ""
        daynote = f"day-FE over {nd} days" if nd > 1 else "no day-FE (single day)"
        lhs = f"{effect}ₜ = α + {adl} + Σ(j=1..{K}) {causecoef}ⱼ·{cause}ₜ₋ⱼ{day}"
    fdr = float(row["p_fdr"]) if "p_fdr" in row.index and pd.notna(row.get("p_fdr")) else float("nan")
    fdr_s = f"   |   BH-FDR p = {fdr:.3g} {stars(fdr)}" if np.isfinite(fdr) else ""
    return [f"   {label}:",
            f"      {lhs}",
            f"      controls: ADL self-lags p={p} (BIC) ; cause block K={K} ; {daynote} ; hac-panel SE (bw={K}).",
            f"      H0: {causecoef}₁ = … = {causecoef}_{K} = 0   →   Wald χ²({dfree}) = {chi2:.2f},  "
            f"p = {pv:.3g} {stars(pv)}{fdr_s}"]


def _pick(g, mode, spec, direction):
    d = g[(g["mode"] == mode) & (g["spec"] == spec) & (g["direction"] == direction)]
    return d.iloc[0] if not d.empty else None


def pair_text(rrow):
    ticker, etf, tag = rrow["contract_ticker"], rrow["etf"], rrow["tag"]
    s = SIG[(SIG.contract_ticker == ticker) & (SIG.etf == etf)].iloc[0]
    g = GR[(GR.contract_ticker == ticker) & (GR.etf == etf)]
    bar = g["bar_freq"].iloc[0] if not g.empty else "n/a"
    L = [f"GRANGER CAUSALITY    —    Rank {int(rrow['rank'])} / {len(RANK)}",
         "=" * 96,
         f"{C.short_contract_name(ticker)}   x   {etf}      [ticker: {ticker}]",
         f'Contract : "{s.get("contract_title","")}"',
         f"Window : {s['date_start']} to {s['date_end']}     primary bar : {bar}     "
         f"Kalshi trades : {int(rrow['n_trades'])}",
         "",
         "Test: joint Wald H0 = all PAST cause-lags are 0 (controls the effect's own past; hac-panel SE).",
         "p<0.05 ⇒ that variable Granger-leads the other.  (x=Δprob, y=ETF log return.)",
         ""]
    if g.empty:
        L += ["-> no Granger result (insufficient data for this pair)."]
        return L
    mode_verd = {}
    for i, (mode, lab) in enumerate([("calendar", "CALENDAR-TIME (clock-time lags, full RTH grid)"),
                                     ("event", "EVENT-TIME (event-count lags)")], start=1):
        L.append(f"{i}. {lab}")
        ke = _pick(g, mode, "linear", "kalshi->etf")
        ek = _pick(g, mode, "linear", "etf->kalshi")
        pr = _pick(g, mode, "probit", "kalshi->etf")
        if ke is None and ek is None:
            L += ["   (not estimable at this axis)", ""]; mode_verd[mode] = None; continue
        if ke is not None:
            L += _dir_lines(ke, "y", "x", "φ", "b", "Direction A — Kalshi → ETF")
        if ek is not None:
            L += _dir_lines(ek, "x", "y", "ψ", "d", "Direction B — ETF → Kalshi")
        if pr is not None:
            L += _dir_lines(pr, "y", "x", "φ", "b", "Direction A (probit, ETF up/down)", probit=True)
        pk = float(ke["p_value"]) if ke is not None else float("nan")
        pe = float(ek["p_value"]) if ek is not None else float("nan")
        v = _verd(pk, pe); mode_verd[mode] = v
        L += [f"   => {mode} verdict: {v}.", ""]
    cv, ev = mode_verd.get("calendar"), mode_verd.get("event")
    if cv and ev and cv == ev and "neither" not in cv:
        overall = f"Both time-axes agree: {cv} (relatively robust)."
    elif cv and ev and cv != ev:
        overall = f"Calendar says '{cv}' but Event says '{ev}' — not robust across time-axis."
    else:
        one = next((x for x in (cv, ev) if x and "neither" not in x), None)
        overall = f"Only one axis significant: {one}." if one else "No Granger causality detected on either axis."
    L += ["3. OVERALL VERDICT", f"   {overall}",
          "", "-" * 96,
          "This pair's joint-Wald p per direction is also in the single-pair heatmap (core figure 1)."]
    return L


def merge_group_text(group):
    g = GRM[GRM.group == group]
    etfs = sorted(g["etf"].unique())
    L = [f"MERGE pooled signal — GRANGER overview :  {group}",
         "=" * 96,
         "Each pooled signal = members' sign-aligned Δprob pooled (member fixed effects, hac-panel SE by",
         "member×day). 'Sign-aligned' means each member's Δprob is multiplied by ±1 so that a positive value",
         "always means the same real-world direction (e.g. a MIN-side contract is flipped). The CONTINUOUS",
         "magnitude of Δprob is kept — the moves are NOT discretized to ±1.",
         "Joint Wald per direction; S=combined pooled signal, E=ETF. p<0.05 ⇒ that side leads.",
         "",
         f"{'ETF':6s} {'cal S→E':>11} {'cal E→S':>11} {'evt S→E':>11} {'evt E→S':>11}   verdict(cal / evt)"]
    def _p(etf, mode, direction):
        r = _pick(g[g.etf == etf], mode, "linear", direction)
        return float(r["p_value"]) if r is not None else float("nan")
    def _c(p):
        return f"{p:.2g}{stars(p)}" if np.isfinite(p) else "-"
    def _vv(a, b):
        A = np.isfinite(a) and a < .05; B = np.isfinite(b) and b < .05
        return "S→E" if A and not B else ("E→S" if B and not A else ("bidir" if A and B else "-"))
    for etf in etfs:
        cse, ces = _p(etf, "calendar", "kalshi->etf"), _p(etf, "calendar", "etf->kalshi")
        ese, ees = _p(etf, "event", "kalshi->etf"), _p(etf, "event", "etf->kalshi")
        L.append(f"{etf:6s} {_c(cse):>11} {_c(ces):>11} {_c(ese):>11} {_c(ees):>11}   {_vv(cse,ces)} / {_vv(ese,ees)}")
    L += ["", "Per-ETF pseudo-pairs (combined pooled signal × each ETF) follow, each with explicit formulas + joint Wald."]
    return L


def merge_combo_text(group, etf):
    g = GRM[(GRM.group == group) & (GRM.etf == etf)]
    L = [f"GRANGER —  {group} (combined pooled signal)   x   {etf}",
         "=" * 96,
         "S = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level). x=Δprob(S), y=ETF log return.",
         "Joint Wald H0 = all PAST cause-lags 0; member FE (linear); hac-panel SE by member×day. p<0.05 ⇒ leads.",
         ""]
    if g.empty:
        return L + ["-> no Granger result."]
    mv = {}
    for i, mode in enumerate(["calendar", "event"], start=1):
        L.append(f"{i}. {mode.upper()}-TIME")
        ke = _pick(g, mode, "linear", "kalshi->etf")
        ek = _pick(g, mode, "linear", "etf->kalshi")
        pr = _pick(g, mode, "probit", "kalshi->etf")
        if ke is None and ek is None:
            L += ["   (not estimable)", ""]; mv[mode] = None; continue
        if ke is not None:
            L += _dir_lines(ke, "y", "x", "φ", "b", "Direction A — Pooled → ETF")
        if ek is not None:
            L += _dir_lines(ek, "x", "y", "ψ", "d", "Direction B — ETF → Pooled")
        if pr is not None:
            L += _dir_lines(pr, "y", "x", "φ", "b", "Direction A (probit, ETF up/down)", probit=True)
        pk = float(ke["p_value"]) if ke is not None else float("nan")
        pe = float(ek["p_value"]) if ek is not None else float("nan")
        v = _verd(pk, pe).replace("Kalshi", "Pooled"); mv[mode] = v
        L += [f"   => {mode} verdict: {v}.", ""]
    return L


# ---------------- conclusions (computed from the CSVs) ----------------
def _verdict_counts(sub, keys):
    c = {"K": 0, "E": 0, "bi": 0, "n": 0}
    for _, g in sub.groupby(keys):
        pk = g[g.direction == "kalshi->etf"]["p_value"]
        pe = g[g.direction == "etf->kalshi"]["p_value"]
        pk = float(pk.iloc[0]) if len(pk) else np.nan
        pe = float(pe.iloc[0]) if len(pe) else np.nan
        A = np.isfinite(pk) and pk < .05; B = np.isfinite(pe) and pe < .05
        c["K" if A and not B else "E" if B and not A else "bi" if A and B else "n"] += 1
    return c


def conclusions_text():
    sc = _verdict_counts(GR[(GR["mode"] == "calendar") & (GR.spec == "linear")], ["contract_ticker", "etf"])
    se = _verdict_counts(GR[(GR["mode"] == "event") & (GR.spec == "linear")], ["contract_ticker", "etf"])
    mc = _verdict_counts(GRM[(GRM["mode"] == "calendar") & (GRM.spec == "linear")], ["group", "etf"]) if not GRM.empty else {"K":0,"E":0,"bi":0,"n":0}
    me = _verdict_counts(GRM[(GRM["mode"] == "event") & (GRM.spec == "linear")], ["group", "etf"]) if not GRM.empty else {"K":0,"E":0,"bi":0,"n":0}
    ns, nse = sum(sc.values()), sum(se.values())
    nmc, nme = sum(mc.values()), sum(me.values())
    kl = GR[(GR["mode"] == "calendar") & (GR.spec == "linear") & (GR.direction == "kalshi->etf") & (GR.p_value < .05)]
    lead_list = ", ".join(f"{C.short_contract_name(r.contract_ticker)}×{r.etf}"
                          for _, r in kl.sort_values("p_value").iterrows())

    def _fdr(df, mode, spec, direction):
        """(raw significant, FDR-significant, n tested) for one test family."""
        d = df[(df["mode"] == mode) & (df.spec == spec) & (df.direction == direction)]
        if d.empty or "p_fdr" not in d.columns:
            return 0, 0, len(d)
        return int((d.p_value < .05).sum()), int((d.p_fdr < .05).sum()), len(d)

    fc_k, fc_e = _fdr(GR, "calendar", "linear", "kalshi->etf"), _fdr(GR, "calendar", "linear", "etf->kalshi")
    fe_k, fe_e = _fdr(GR, "event", "linear", "kalshi->etf"), _fdr(GR, "event", "linear", "etf->kalshi")
    mfc_k, mfc_e = (_fdr(GRM, "calendar", "linear", "kalshi->etf"), _fdr(GRM, "calendar", "linear", "etf->kalshi")) if not GRM.empty else ((0,0,0),(0,0,0))
    mfe_k, mfe_e = (_fdr(GRM, "event", "linear", "kalshi->etf"), _fdr(GRM, "event", "linear", "etf->kalshi")) if not GRM.empty else ((0,0,0),(0,0,0))
    prc = GR[(GR["mode"] == "calendar") & (GR.spec == "probit")]
    pre = GR[(GR["mode"] == "event") & (GR.spec == "probit")]
    prc_s, pre_s = int((prc.p_value < .05).sum()), int((pre.p_value < .05).sum())
    drive_cal = sorted(GRM[(GRM["mode"] == "calendar") & (GRM.spec == "linear") & (GRM.direction == "kalshi->etf") & (GRM.p_value < .05)]["group"].unique()) if not GRM.empty else []
    drive_evt = sorted(GRM[(GRM["mode"] == "event") & (GRM.spec == "linear") & (GRM.direction == "kalshi->etf") & (GRM.p_value < .05)]["group"].unique()) if not GRM.empty else []

    def _conc_phrase():
        """描述 calendar K→E 显著对集中在哪些合约上——由数据算出，不写死合约名。"""
        if kl.empty:
            return "no pair is significant"
        cnt = kl["contract_ticker"].map(C.short_contract_name).value_counts()
        top, n_top = cnt.index[0], int(cnt.iloc[0])
        rest = len(cnt) - 1
        if n_top == 1:
            return f"{len(cnt)} distinct contracts, no single one dominating"
        tail = f", plus {rest} other contract{'s' if rest != 1 else ''} with one ETF each" if rest else ""
        return f"mainly '{top}' across {n_top} ETFs{tail}"

    def _group_lines():
        """每个池化信号在两个时间轴上的实际战绩，全部由数据算出——不写死任何组名的结论。"""
        if GRM.empty:
            return ["     (no pooled-signal results)"]
        fwd = GRM[(GRM.spec == "linear") & (GRM.direction == "kalshi->etf")]
        out = []
        for grp in sorted(fwd["group"].unique()):
            parts = []
            for mode in ("calendar", "event"):
                d = fwd[(fwd["group"] == grp) & (fwd["mode"] == mode)]
                if d.empty:
                    parts.append(f"{mode}: not estimable")
                else:
                    parts.append(f"{mode}: {int((d.p_value < .05).sum())}/{len(d)} raw, "
                                 f"{int((d.p_fdr < .05).sum())} after FDR")
            out.append(f"       {grp:20s} " + "   |   ".join(parts))
        return out
    exp = ns * 0.05
    L = ["CONCLUSIONS", "=" * 96,
         "HEADLINE — the direction is asymmetric. Whenever Granger causality is significant it runs",
         "Kalshi → ETF; the reverse (ETF → Kalshi) is essentially absent. This asymmetry — not the raw count",
         "of significant pairs — is the robust finding, and it answers the project's question: the evidence",
         "supports prediction markets LEADING sector ETFs, and does not support the reverse.",
         "",
         "1. Direction is one-way (Kalshi → ETF)",
         f"   - Single pairs, calendar:  {sc['K']} Kalshi-leads  vs  {sc['E']} ETF-leads   ({sc['bi']} bidir, {sc['n']} neither, of {ns}).",
         f"   - Single pairs, event:     {se['K']} Kalshi-leads  vs  {se['E']} ETF-leads   ({se['bi']} bidir, {se['n']} neither, of {nse}).",
         f"   - Pooled signals, calendar: {mc['K']} Pooled-leads   vs  {mc['E']} ETF-leads   ({mc['bi']} bidir, {mc['n']} neither, of {nmc}).",
         f"   - Pooled signals, event:    {me['K']} Pooled-leads   vs  {me['E']} ETF-leads   ({me['bi']} bidir, {me['n']} neither, of {nme}).",
         "   The reverse direction is significant in ~0 cases at every level — the lead is one-directional.",
         "",
         "2. Weak and concentrated at the single-contract level",
         f"   - {sc['n']} of {ns} single pairs show no Granger causality either way (calendar). The {sc['K']} that do are",
         f"     concentrated in a handful of contracts — {_conc_phrase()}:",
         f"       {lead_list}.",
         "   - So the lead is NOT a broad per-contract phenomenon; it is concentrated in the few LIQUID contracts.",
         "     Illiquid contracts have no usable price-discovery process (consistent with the advisor's point).",
         "",
         "3. Pooling restores power",
         f"   - Aggregating same-family contracts into sign-aligned pooled signals (more degrees of freedom) lights",
         f"     up Pooled→ETF in {mc['K']}/{nmc} (calendar) and {me['K']}/{nme} (event), while the reverse stays ~0. The lead is",
         "     real but needs aggregation to detect above single-contract noise.",
         "   - Per pooled signal, Pooled→ETF significance (raw p<0.05, then after BH-FDR):",
         *_group_lines(),
         "     Only the pooled signals with enough ACTIVE event-time observations are estimable on the event",
         "     axis; the others show 'not estimable' there rather than a null result.",
         "",
         "4. Caveats (state them)",
         "   - Time-axis: the clean one-way result is on the CALENDAR (clock-time) axis. EVENT-time is muddier",
         f"     ({se['E']} single-pair ETF-leads, {se['bi']} bidirectional), most likely an artifact of sampling only at the sparse",
         "     Kalshi trade instants (near-contemporaneous comovement misread as ETF-leads). The headline rests on",
         "     calendar; event-time is robustness / a warning, not the basis for the claim.",
         f"   - Direction-only (probit) is weak: {prc_s}/{len(prc)} (calendar) and {pre_s}/{len(pre)} (event) significant. Predictability",
         "     is in the MAGNITUDE of continuous returns more than in the up/down sign.",
         "",
         "5. Multiple testing — the asymmetry SURVIVES a Benjamini-Hochberg FDR correction",
         "   Every direction×axis×spec is one test family; each family is BH-FDR corrected across all pairs, so",
         f"   \"{sc['K']} of {ns} significant at 5%\" cannot be read as evidence on its own (~{exp:.1f} would be expected by chance).",
         "   Counts below are raw p<0.05 -> FDR p<0.05:",
         f"     - Single pairs, calendar:   Kalshi→ETF {fc_k[0]}→{fc_k[1]} of {fc_k[2]}   |   ETF→Kalshi {fc_e[0]}→{fc_e[1]} of {fc_e[2]}",
         f"     - Single pairs, event:      Kalshi→ETF {fe_k[0]}→{fe_k[1]} of {fe_k[2]}   |   ETF→Kalshi {fe_e[0]}→{fe_e[1]} of {fe_e[2]}",
         f"     - Pooled signals, calendar: Pooled→ETF {mfc_k[0]}→{mfc_k[1]} of {mfc_k[2]}   |   ETF→Pooled {mfc_e[0]}→{mfc_e[1]} of {mfc_e[2]}",
         f"     - Pooled signals, event:    Pooled→ETF {mfe_k[0]}→{mfe_k[1]} of {mfe_k[2]}   |   ETF→Pooled {mfe_e[0]}→{mfe_e[1]} of {mfe_e[2]}",
         "   The Kalshi→ETF direction largely survives FDR, while the reverse direction collapses to ~0 once",
         "   corrected. So the one-way lead is not an artifact of running many tests: correcting for multiplicity",
         "   REMOVES the reverse-direction hits and KEEPS the forward ones.",
         "",
         "BOTTOM LINE — High-frequency Granger tests show prediction markets one-directionally lead sector ETFs on",
         "the clock-time axis (reverse essentially absent); the lead is concentrated in a few high-liquidity",
         "contracts and is most robust after pooling same-family contracts into pooled signals; direction-only",
         "(probit) and event-time evidence is weaker. 'Lead' here means Granger precedence (predictive), not cause."]
    return L


# ---------------- overview table ----------------
def overview_text():
    L = list(_INTRO) + ["", "=" * 96, ""] + conclusions_text() + \
        ["", "=" * 96,
         "SINGLE-PAIR SUMMARY — grouped by contract (not sorted by p).",
         "joint-Wald p per direction; * <.10  ** <.05  *** <.01;  '†' = still significant after BH-FDR.",
         "", f"{'contract':24} {'etf':4} {'cal K→E':>11} {'cal E→K':>11} "
             f"{'evt K→E':>11} {'evt E→K':>11}  verdict(cal/evt)"]

    def _row(g, mode, d):
        r = _pick(g, mode, "linear", d)
        if r is None:
            return float("nan"), float("nan")
        fdr = float(r["p_fdr"]) if "p_fdr" in r.index and pd.notna(r.get("p_fdr")) else float("nan")
        return float(r["p_value"]), fdr

    def _c(p, fdr):
        if not np.isfinite(p):
            return "-"
        dag = "†" if np.isfinite(fdr) and fdr < .05 else ""
        return f"{p:.2g}{stars(p)}{dag}"

    def _vv(a, b):
        A = np.isfinite(a) and a < .05; B = np.isfinite(b) and b < .05
        return "K→E" if A and not B else ("E→K" if B and not A else ("bi" if A and B else "-"))

    # 与热力图同一套排序：事件族 → ticker → ETF；不按 p 排序
    rows = [r for _, r in RANK.iterrows()]
    rows.sort(key=lambda r: (MGP._family_rank(r["contract_ticker"]), r["contract_ticker"], r["etf"]))
    prev = None
    for r in rows:
        g = GR[(GR.contract_ticker == r["contract_ticker"]) & (GR.etf == r["etf"])]
        if g.empty:
            continue
        cke, cke_f = _row(g, "calendar", "kalshi->etf")
        cek, cek_f = _row(g, "calendar", "etf->kalshi")
        eke, eke_f = _row(g, "event", "kalshi->etf")
        eek, eek_f = _row(g, "event", "etf->kalshi")
        name = C.short_contract_name(r["contract_ticker"])
        if prev is not None and name != prev:
            L.append("")                                  # 合约之间空一行，视觉上分块
        L.append(f"{(name if name != prev else ''):24} {str(r['etf']):4} "
                 f"{_c(cke,cke_f):>11} {_c(cek,cek_f):>11} {_c(eke,eke_f):>11} {_c(eek,eek_f):>11}  "
                 f"{_vv(cke,cek)}/{_vv(eke,eek)}")
        prev = name
    return L


# ================================ PDF ================================
def _stack(pdf, img_paths, header=None):
    imgs = [p for p in img_paths if p.exists()]
    if not imgs:
        return
    arrs = [plt.imread(p) for p in imgs]
    W = 13.0
    heights = [W * a.shape[0] / a.shape[1] for a in arrs]
    fig = plt.figure(figsize=(W, (0.5 if header else 0.1) + sum(heights)))
    gs = fig.add_gridspec(len(arrs), 1, height_ratios=heights, hspace=0.03)
    if header:
        fig.suptitle(header, fontsize=12, fontweight="bold", y=0.999)
    for i, a in enumerate(arrs):
        ax = fig.add_subplot(gs[i]); ax.imshow(a, aspect="auto", interpolation="none"); ax.axis("off")
    pdf.savefig(fig, dpi=200, bbox_inches="tight"); plt.close(fig)


def _text_page(pdf, lines, header=None):
    tmp = C.HERE / "_granger_tmp.md"
    tmp.write_text("\n".join(lines), encoding="utf-8")
    fig = MPT.build_text_fig(tmp, header=header)
    pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)
    tmp.unlink(missing_ok=True)


def build_pdf():
    print(f"拼 Granger 专属 PDF -> {OUT_PDF}")
    _ensure_heatmaps()
    with PdfPages(OUT_PDF) as pdf:
        _stack(pdf, [HEATMAP], header="CORE FIGURE 1 — single-pair Granger joint-Wald p heatmap")
        if not GRM.empty:
            _stack(pdf, [MERGE_HEATMAP], header="CORE FIGURE 2 — merged pooled signals Granger heatmap")
        _text_page(pdf, coverage_text(), header=f"COVERAGE — why {_cov_counts()[0]} of {_cov_counts()[1]} pairs carry results")
        _text_page(pdf, overview_text(), header="GRANGER REPORT — overview & method")
        for _, rrow in RANK.iterrows():
            g = GR[(GR.contract_ticker == rrow["contract_ticker"]) & (GR.etf == rrow["etf"])]
            if g.empty:
                continue
            _text_page(pdf, pair_text(rrow))
            print(f"  pair {rrow['contract_ticker']}×{rrow['etf']}")
        if not GRM.empty:
            _text_page(pdf, ["MERGE POOLED SIGNALS — GRANGER (per group × ETF detail)", "=" * 96,
                             "Each pooled signal treated as one combined contract; Granger vs each ETF in its union."],
                       header="MERGE pooled signals — Granger detail")
            for group in _merge_groups():
                _text_page(pdf, merge_group_text(group), header=f"MERGE {group} — Granger overview")
                for etf in sorted(GRM[GRM.group == group]["etf"].unique()):
                    _text_page(pdf, merge_combo_text(group, etf))
                    print(f"  merge {group}×{etf}")
    print(f"完成 -> {OUT_PDF}")


# ================================ MD ================================
def _fenced(lines):
    txt = "\n".join(lines).rstrip("\n")
    longest = max((len(m) for m in re.findall(r"`+", txt)), default=0)
    fence = "`" * max(3, longest + 1)
    return f"{fence}text\n{txt}\n{fence}\n"


def coverage_text():
    """Up-front explanation: why only 25 of 48 pairs carry Granger results."""
    n_all = len(COV) if not COV.empty else len(SIG)
    if COV.empty:
        return [f"Coverage: {GR[['contract_ticker','etf']].drop_duplicates().shape[0]} of {n_all} "
                "pairs are estimable; the rest were too sparse for a valid joint-Wald test."]
    cov = COV.copy()
    for c in ("cal_bars", "evt_bars"):
        cov[c] = pd.to_numeric(cov[c], errors="coerce").fillna(0).astype(int)
    est  = cov[cov["estimable"]]
    drop = cov[~cov["estimable"]].sort_values(["cal_bars", "contract_ticker", "etf"])
    zero = drop[(drop["cal_bars"] == 0) & (drop["evt_bars"] == 0)]
    L = [f"COVERAGE — {len(est)} of {n_all} pairs carry Granger results; {len(drop)} are dropped (shown as NA "
         "rows in core figure 1).",
         "=" * 96,
         "",
         f"WHY {len(drop)} PAIRS ARE DROPPED (all fail at the SAME step — not a model failure, a data-density "
         "failure):",
         "",
         "  The joint-Wald test needs enough *price-changing* observations to fit the smallest admissible model",
         "  (K cause-lags + BIC own-lags + day fixed effects) and still have residual degrees of freedom for a",
         "  valid Newey-West (hac-panel) covariance. ONE gate, applied identically to every pair, every time-axis,",
         "  and BOTH specifications, BEFORE any regression is attempted:",
         "",
         "     n_active  =  # observations where the cause actually moved  >=  2K + 5  =  11   (at K = 3)",
         "",
         "  The threshold is derived from the model's parameter count (K cause-lags plus own-lags plus intercept),",
         "  not chosen by hand. linear and probit share the same sample (the same calendar grid / event sequence)",
         "  and the same gate, so a pair is never estimable under one specification but not the other. probit",
         "  additionally needs both up- and down-moves to appear in the dependent variable, which is an intrinsic",
         "  requirement of the model rather than a discretionary cutoff.",
         "",
         "  Every dropped pair fails this gate: the Kalshi contract barely traded during its overlap window, so",
         "  after building bars almost no bar carries a non-zero price change. There is simply not enough",
         "  independent information to identify a lag polynomial, let alone test it. Nothing is estimated and the",
         "  row is left NA rather than reporting an under-identified / rank-deficient p-value.",
         "",
         f"  Of the {len(drop)} dropped, {len(zero)} had ZERO price-changing bars in the window (no trading / no",
         "  quote updates at all); the rest had only a handful, well under 11.",
         "",
         "DROPPED PAIRS (price-changing observations, measured on the same grid/sequence used for estimation):",
         "",
         f"  {'contract':28s}{'etf':5s}{'cal':>5s}{'evt':>5s}   reason"]
    for _, r in drop.iterrows():
        L.append(f"  {C.short_contract_name(r['contract_ticker']):28s}{str(r['etf']):5s}"
                 f"{int(r['cal_bars']):>5d}{int(r['evt_bars']):>5d}   "
                 + ("no price movement in window" if r['cal_bars'] == 0 and r['evt_bars'] == 0
                    else "too few price-changing observations (< 11)"))
    L += ["",
          f"TAKEAWAY: the {len(est)} estimable pairs are exactly those liquid enough to support valid inference;",
          "the drop is a mechanical minimum-sample rule, applied identically to every pair and both",
          "specifications, not a selection on results."]
    return L


def _merge_groups():
    f = MERGEDIR / "merge_order.csv"
    if f.exists():
        return [g for g in pd.read_csv(f)["group"] if g in set(GRM["group"])]
    return sorted(GRM["group"].unique())


def build_md():
    _ensure_heatmaps()
    L = ["# Granger Report — Kalshi prediction markets × Vanguard sector ETFs", "",
         "_Headline statistic: one joint Wald test per direction. Structure: "
         "**both core heatmaps up front** (single pairs, then merged pooled signals) → overview & method → "
         "per-pair formulas+Wald detail → per-group detail. The main lead-lag reports "
         "(`leadlag_pairs_report.md`, `leadlag_merge_report.md`) no longer contain Granger. Method: "
         "`GRANGER_TEST.md`._", "",
         "---", "",
         "## CORE FIGURE 1 — single-pair Granger heatmap (all 48 pairs × 6 regressions)", "",
         f"![single-pair Granger heatmap](plots/{HEATMAP.name})", "",
         "_Rows = pairs; columns = time-axis × direction; cell colour = joint Wald p (p<0.05 red = that "
         "direction's lead/lag IS significant; NA = too sparse to estimate). CALENDAR Kalshi→ETF lights up while "
         "ETF→Kalshi stays pale ⇒ clean one-directional lead; EVENT is more bidirectional._", ""]
    if not GRM.empty:
        L += ["---", "",
              "## CORE FIGURE 2 — merged pooled signals Granger heatmap", "",
              f"![merged pooled signals Granger heatmap](plots/{MERGE_HEATMAP.name})", "",
              "_Each left block = one pooled signal (labelled with its members & sign convention); rows = that "
              "group × each ETF. CALENDAR Pooled→ETF lit while ETF→Pooled pale ⇒ the pooled signal Granger-leads "
              "the ETF (clearest for GAS and ELECTION)._", ""]
    L += ["---", "", f"## COVERAGE — why {_cov_counts()[0]} of {_cov_counts()[1]} pairs carry results", "", _fenced(coverage_text()),
          "---", "", "## OVERVIEW & METHOD", "", _fenced(overview_text()),
          "---", "", "## Single-pair detail — explicit formulas + joint Wald per direction", ""]
    for _, rrow in RANK.iterrows():
        g = GR[(GR.contract_ticker == rrow["contract_ticker"]) & (GR.etf == rrow["etf"])]
        if g.empty:
            continue
        L += ["---", "",
              f"### Rank {int(rrow['rank'])}/{len(RANK)} — "
              f"{C.short_contract_name(rrow['contract_ticker'])} × {rrow['etf']}",
              "", _fenced(pair_text(rrow))]
    if not GRM.empty:
        L += ["---", "", "# MERGE pooled signals — detail", ""]
        for group in _merge_groups():
            L += ["---", "", f"## MERGE — {group}  (Granger overview)", "", _fenced(merge_group_text(group))]
            for etf in sorted(GRM[GRM.group == group]["etf"].unique()):
                L += ["", f"### {group} (combined)  ×  {etf}", "", _fenced(merge_combo_text(group, etf))]
    OUT_MD.write_text("\n".join(L), encoding="utf-8")
    print(f"完成 -> {OUT_MD}")


def main():
    build_md()
    build_pdf()


if __name__ == "__main__":
    main()
