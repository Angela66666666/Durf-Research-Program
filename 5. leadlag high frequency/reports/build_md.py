"""
build_md.py  —  Per-coefficient lead-lag report (Report B of two)
================================================================================
Produces leadlag_pairs_report.md, the PER-COEFFICIENT / probit companion to the
joint-Wald headline (leadlag_granger_report.md). Structure:
  1. Method (joint-lag ADL + probit formulas)
  2. Core statistics & conclusion (classification: graded p<0.05/0.10/0.15 tables)
  3. MERGE — pooled super-signals (per-coefficient; absorbed from the old merge report)
  4. Per-pair detail, ordered most-data-first (text + 6 figures each)
MD only (no PDF). Figures live in ../plots and ../merge/plots.
"""
import re
import sys as _sys
from pathlib import Path as _P
_sys.path.insert(0, str(_P(__file__).resolve().parent.parent / "engine"))
import pandas as pd
import leadlag_common as C

ROOT5     = C.HERE.parent               # "5. leadlag high frequency"
REPORTDIR = _P(__file__).resolve().parent   # reports/
PLOTDIR   = ROOT5 / "plots"
MERGEDIR  = ROOT5 / "merge" / "plots"
IMG       = "../plots"                   # per-pair figures, relative to reports/
MIMG      = "../merge/plots"             # merge figures, relative to reports/
RANK      = pd.read_csv(PLOTDIR / "pair_ranking.csv")
OUT_MD    = REPORTDIR / "leadlag_pairs_report.md"
PAIR_FIGS  = ["timeseries", "zoom2", "leadglance", "leadzoom", "event", "lagcoef"]
COMBO_FIGS = PAIR_FIGS

METHOD = [
    "PER-COEFFICIENT LEAD-LAG — method",
    "",
    "x_t = Kalshi yes-probability change (Delta prob) over bar t ;  y_t = ETF log return over bar t.",
    "Both on causal median bars (right-edge, no look-ahead); ET, regular hours 09:30-16:00; lags shifted",
    "within a trading day (no overnight); bar size and K chosen per contract by trading activity.",
    "",
    "1) JOINT-LAG ADL REGRESSION  (calendar axis = clock-time lags; event axis = event-count lags)",
    "     y_t = a + Sum(j=-K..+K) b_j * x_{t-j} + Sum(i=1..p) phi_i * y_{t-i} + day-FE + e_t",
    "   - b_j significant at j>0  => x's PAST predicts y  => Kalshi leads ETF",
    "   - b_j significant at j<0  => x's FUTURE           => ETF leads Kalshi ;  j=0 = contemporaneous",
    "   - Sum phi_i * y_{t-i} = ETF's own lags (ADL, order p by BIC): nets out ETF momentum so",
    "     autocorrelation is not mistaken for a lead.  x standardized ; SE clustered by day.",
    "",
    "2) PROBIT DIRECTION TEST  (one probit per lag; robust to outliers/magnitude)",
    "     Pr(y_t > 0) = Phi( alpha + beta * x_{t-j} )   for each lag j",
    "   - beta > 0 significant at j>0  => past Kalshi move predicts ETF up/down => Kalshi leads directionally.",
    "",
    "Significance is read at GRADED thresholds p<0.05 / 0.10 / 0.15 (raw p); each pair's lags are",
    "additionally BH-FDR corrected.",
    "",
    "NOTE — this per-coefficient counting is DESCRIPTIVE and lower-power (many lag t-tests). The",
    "CONFIRMATORY direction rests on the joint-Wald Granger test in leadlag_granger_report.md; use this",
    "report to see WHERE (which lag) and with what SIGN the co-movement sits, not to decide who leads.",
]

MERGE_INTRO = [
    "Each pooled signal is treated as one COMBINED CONTRACT: members' Delta prob are sign-aligned (reverse",
    "contracts x -1) and pooled — never their price levels (different thresholds are not comparable).",
    "'Sign-aligned' means each member's Delta prob is multiplied by +-1 so a positive value always denotes the",
    "same real-world direction; the CONTINUOUS magnitude is preserved (not discretized to +-1). The combined",
    "'contract line' in the time-series figures is a SYNTHETIC INDEX = cumulative bar-by-bar mean of members'",
    "sign-aligned Delta prob (start 0.5, in pp) — not a real probability, only a carrier for the group's info flow.",
    "Regression: per-member fixed effects, day-clustered SE, ADL self-lags by BIC; direction counts use raw p",
    "at p<0.05 / 0.10 / 0.15. (The pooled JOINT-WALD Granger version is in leadlag_granger_report.md.)",
]


def _fenced(md_path):
    """把一份 .md 文字原样放进 ```text``` 代码块,保留 monospace 对齐与公式下标。"""
    txt = md_path.read_text(encoding="utf-8").rstrip("\n")
    longest = max((len(m) for m in re.findall(r"`+", txt)), default=0)
    fence = "`" * max(3, longest + 1)
    return f"{fence}text\n{txt}\n{fence}\n"


def _fenced_lines(lines):
    return "```text\n" + "\n".join(lines) + "\n```\n"


def _merge_section(L):
    mo = MERGEDIR / "merge_order.csv"
    mp = MERGEDIR / "merge_pairs_order.csv"
    if not (mo.exists() and mp.exists()):
        L += ["---", "", "## 3. MERGE — pooled super-signals (per-coefficient)", "",
              "_(merge pages not found — run merge/make_merge_pages.py and make_merge_pair_plots.py)_", ""]
        return
    order = pd.read_csv(mo)
    pairs = pd.read_csv(mp)
    L += ["---", "", "## 3. MERGE — pooled super-signals (per-coefficient)", "",
          _fenced_lines(MERGE_INTRO), ""]
    for _, gr in order.iterrows():
        g = gr["group"]
        L += ["---", "", f"### MERGE — {g}  (pooled overview)", ""]
        gmd = MERGEDIR / f"merge_{g}_analysis.md"
        if gmd.exists():
            L.append(_fenced(gmd))
        gpng = MERGEDIR / f"merge_{g}_lagcoef.png"
        if gpng.exists():
            L += [f"![{g} lagcoef]({MIMG}/{gpng.name})", ""]
        for etf in pairs[pairs["group"] == g]["etf"]:
            tag = f"merge_{g}_{etf}"
            L += ["", f"#### {g} (combined)  ×  {etf}", ""]
            cmd = MERGEDIR / f"{tag}_analysis.md"
            if cmd.exists():
                L.append(_fenced(cmd))
            for s in COMBO_FIGS:
                p = MERGEDIR / f"{tag}_{s}.png"
                if p.exists():
                    L.append(f"![{tag} {s}]({MIMG}/{p.name})")
            L.append("")


def main():
    L = ["# Lead-Lag Report (per-coefficient) — Kalshi prediction markets × Vanguard sector ETFs", "",
         "_Per-coefficient / probit view — the companion to the joint-Wald headline "
         "`leadlag_granger_report.md`. Structure: **method → core statistics & conclusion → MERGE "
         "(pooled) → per-pair detail (most-data-first)**. Figures are the PNGs in `../plots` and "
         "`../merge/plots`._", "",
         # ---------- 1. METHOD ----------
         "---", "", "## 1. Method", "", _fenced_lines(METHOD)]
    # ---------- 2. CORE STATISTICS & CONCLUSION ----------
    L += ["---", "", "## 2. Core statistics & conclusion", "",
          "_Direction here = counting significant per-coefficient lags at p<0.05 / 0.10 / 0.15 — a "
          "descriptive, lower-power view. The confirmatory direction is the joint-Wald in the Granger "
          "report; see its reliability caveat (the single-pair lead is driven by very-sparse contracts)._", ""]
    summ = C.HERE / "leadlag_classification_summary.md"   # intermediate generated by leadlag_classification.py (engine/)
    if summ.exists():
        L.append(_fenced(summ))
    cs = PLOTDIR / "classification_summary.png"
    if cs.exists():
        L += [f"![classification summary]({IMG}/{cs.name})", ""]
    # ---------- 3. MERGE ----------
    _merge_section(L)
    # ---------- 4. PER-PAIR DETAIL (most-data-first) ----------
    L += ["---", "", "## 4. Per-pair detail (ordered most-data-first)", "",
          "**Ranking:** has_result → n_trades → n_sig (raw p<0.15) → best_p.  "
          "**Per-pair significance:** raw p<0.15.  **ADL ETF self-lags:** by BIC.", ""]
    for _, r in RANK.iterrows():
        bp = "n/a" if pd.isna(r.best_p) else f"{r.best_p:.1e}"
        noreg = "" if bool(r.has_result) else "  (no regression result)"
        L += ["---", "",
              f"### Rank {int(r['rank'])}/{len(RANK)} — {r.contract_ticker} × {r.etf}"
              f"  (n_sig={int(r.n_sig)}, best_p={bp}, n_trades={int(r.n_trades)}){noreg}", ""]
        md = PLOTDIR / f"{r.tag}_analysis.md"
        if md.exists():
            L.append(_fenced(md))
        for s in PAIR_FIGS:
            p = PLOTDIR / f"{r.tag}_{s}.png"
            if p.exists():
                L.append(f"![{r.tag} {s}]({IMG}/{p.name})")
        L.append("")

    OUT_MD.write_text("\n".join(L), encoding="utf-8")
    print(f"完成 -> {OUT_MD}  ({len(RANK)} single pairs + method + core stats + merge)")


if __name__ == "__main__":
    main()
