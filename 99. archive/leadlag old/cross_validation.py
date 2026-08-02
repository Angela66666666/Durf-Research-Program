"""
Cross-validate Profile and Event_unified results to identify TRUE lead-lag candidates.

For each (contract × ETF) pair:
  - Profile  : for each direction, find min p-value across 120 horizons (5–600s)
  - Unified  : for each direction, count significant (p<0.05) coefficients

Classification:
  A — both methods agree Kalshi leads ETF       → top candidates for Kalshi-leads story
  B — both methods agree ETF leads Kalshi       → top candidates for ETF-leads story
  C — methods disagree on direction              → ambiguous, likely noise
  D — neither method shows significant signal    → no lead-lag

Output:
  leadlag/cross_validation_results.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path

HERE = Path(__file__).parent
PROF = pd.read_csv(HERE / "leadlag_profile_results.csv")
UNIF = pd.read_csv(HERE / "leadlag_event_unified_kalshi_etf.csv")
OUT  = HERE / "cross_validation_results.csv"

# Minimum credibility filter: at least 100 Kalshi trades
MIN_TRADES = 100

# ── Profile aggregation: for each (pair, direction), find min p-value horizon ─
prof_peaks = (
    PROF.loc[PROF.groupby(["contract_ticker", "etf", "direction"])["p_value"].idxmin()]
        .reset_index(drop=True)
)
# Pivot to wide: one row per pair, columns by direction
prof_kl = (prof_peaks[prof_peaks["direction"] == "kalshi_leads_etf"]
           [["contract_ticker", "etf", "horizon_sec", "coef", "p_value", "n_kalshi_trades"]]
           .rename(columns={"horizon_sec": "prof_kl_horizon",
                            "coef":        "prof_kl_coef",
                            "p_value":     "prof_kl_p"}))
prof_el = (prof_peaks[prof_peaks["direction"] == "etf_leads_kalshi"]
           [["contract_ticker", "etf", "horizon_sec", "coef", "p_value"]]
           .rename(columns={"horizon_sec": "prof_el_horizon",
                            "coef":        "prof_el_coef",
                            "p_value":     "prof_el_p"}))

prof_wide = prof_kl.merge(prof_el, on=["contract_ticker", "etf"], how="outer")

# ── Unified aggregation: count significant coefs by direction ───────────────────
unif_sig = UNIF[UNIF["p_value"] < 0.05].copy()
unif_counts = (unif_sig.groupby(["contract_ticker", "etf", "direction"]).size()
                       .unstack(fill_value=0).reset_index())
for col in ["kalshi_leads_etf", "etf_leads_kalshi", "contemp"]:
    if col not in unif_counts.columns:
        unif_counts[col] = 0
unif_counts = unif_counts.rename(columns={
    "kalshi_leads_etf": "unif_n_sig_kl",
    "etf_leads_kalshi": "unif_n_sig_el",
    "contemp":          "unif_n_sig_contemp",
})

# Also pull n_obs from unified for sample-size context
unif_nobs = UNIF.groupby(["contract_ticker", "etf"])["n_obs"].first().reset_index()

# ── Merge everything ────────────────────────────────────────────────────────────
xv = (prof_wide
        .merge(unif_counts, on=["contract_ticker", "etf"], how="outer")
        .merge(unif_nobs,    on=["contract_ticker", "etf"], how="left"))

# Fill NaN counts with 0 (pairs that appear in profile but not unified, or vice versa)
for c in ["unif_n_sig_kl", "unif_n_sig_el", "unif_n_sig_contemp"]:
    xv[c] = xv[c].fillna(0).astype(int)

# ── Determine direction per method ─────────────────────────────────────────────
def profile_dir(row):
    pkl = row.get("prof_kl_p", np.nan)
    pel = row.get("prof_el_p", np.nan)
    sig_kl = pd.notna(pkl) and pkl < 0.05
    sig_el = pd.notna(pel) and pel < 0.05
    if sig_kl and sig_el:
        return "BOTH"
    if sig_kl:
        return "kalshi_leads"
    if sig_el:
        return "etf_leads"
    return "none"

def unified_dir(row):
    nkl = row["unif_n_sig_kl"]
    nel = row["unif_n_sig_el"]
    if nkl == 0 and nel == 0:
        return "none"
    if nkl > nel:
        return "kalshi_leads"
    if nel > nkl:
        return "etf_leads"
    return "tie"

xv["profile_direction"] = xv.apply(profile_dir, axis=1)
xv["unified_direction"] = xv.apply(unified_dir, axis=1)

# ── Cross-validation classification ────────────────────────────────────────────
def classify(row):
    p = row["profile_direction"]
    u = row["unified_direction"]
    if p == "kalshi_leads" and u == "kalshi_leads":
        return "A_both_kalshi_leads"
    if p == "etf_leads" and u == "etf_leads":
        return "B_both_etf_leads"
    if p == "BOTH" and u == "kalshi_leads":
        return "A_both_kalshi_leads"   # profile shows both, unified picks kalshi
    if p == "BOTH" and u == "etf_leads":
        return "B_both_etf_leads"
    if p == "BOTH" and u == "tie":
        return "C_ambiguous_both_dirs"
    if (p == "kalshi_leads" and u == "etf_leads") or (p == "etf_leads" and u == "kalshi_leads"):
        return "C_methods_disagree"
    if p == "none" and u == "none":
        return "D_no_signal"
    # one method none, the other something
    return "C_weak_signal"

xv["classification"] = xv.apply(classify, axis=1)

# ── Apply sample size filter to flag credible candidates ────────────────────────
xv["credible_sample"] = (xv["n_kalshi_trades"] >= MIN_TRADES) & (xv["n_obs"] >= 50)

# Order columns nicely
cols = [
    "contract_ticker", "etf", "n_kalshi_trades", "n_obs", "credible_sample",
    "profile_direction", "prof_kl_p", "prof_kl_horizon", "prof_el_p", "prof_el_horizon",
    "unified_direction", "unif_n_sig_kl", "unif_n_sig_el", "unif_n_sig_contemp",
    "classification",
]
xv = xv[cols].sort_values(["classification", "n_kalshi_trades"], ascending=[True, False])

xv.to_csv(OUT, index=False)
print(f"Saved → {OUT}")
print(f"Total pairs: {len(xv)}")

# ── Summary printout ───────────────────────────────────────────────────────────
print("\n" + "="*100)
print("交叉验证分类汇总(仅看 credible_sample = True 的 pair)")
print("="*100)
cred = xv[xv["credible_sample"]]
print(cred["classification"].value_counts().to_string())

for cls in ["A_both_kalshi_leads", "B_both_etf_leads", "C_methods_disagree",
            "C_ambiguous_both_dirs", "C_weak_signal", "D_no_signal"]:
    sub = cred[cred["classification"] == cls]
    if len(sub) == 0:
        continue
    print("\n" + "-"*100)
    print(f"[{cls}] — {len(sub)} pair(s)")
    print("-"*100)
    show_cols = ["contract_ticker", "etf", "n_kalshi_trades", "n_obs",
                 "profile_direction", "prof_kl_p", "prof_kl_horizon",
                 "prof_el_p", "prof_el_horizon",
                 "unif_n_sig_kl", "unif_n_sig_el"]
    with pd.option_context("display.width", 200, "display.max_colwidth", 35,
                           "display.float_format", "{:.4f}".format):
        print(sub[show_cols].to_string(index=False))
