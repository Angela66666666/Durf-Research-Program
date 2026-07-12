"""
step4_cointegration.py
================================================================================
STEP 4, PART 2b -- COINTEGRATION GATE
  Before any VECM / Hasbrouck, test whether each calibrated basket and Kalshi are
  cointegrated. They are two probability series for the same event, so if they
  share one efficient price their spread should be stationary (mean-reverting).
  If the spread instead wanders (a unit root), the pair is NOT cointegrated and
  the Hasbrouck information-share machinery is not legitimate for it.

  Two readings per plan:
    (1) fixed (1,-1) vector: ADF on spread = implied_p - kalshi. This is what the
        two-point calibration targets (both are meant to be P(Trump)).
    (2) Engle-Granger: regress implied_p on kalshi, ADF on the residual. This lets
        the data pick the cointegrating slope instead of imposing 1.

  Reported over the full window and over a high-liquidity sub-window (from
  2024-10-21, where >~80% of Kalshi bars are fresh) so staleness is not driving
  the verdict.

INPUT   step4_pair.csv
OUTPUT  step4_cointegration.txt
================================================================================
"""
import os
import sys
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.vector_ar.vecm import coint_johansen

MODE = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in ("high_frequency", "daily") else "high_frequency"

HERE = os.path.dirname(os.path.abspath(__file__))
PAIR = os.path.join(HERE, f"step4_pair_{MODE}.csv")

PLANS = ["A_sign_equal", "B_beta_weighted", "C_min_variance"]
SUBWIN_START = "2024-10-21"          # from here Kalshi bars are ~>=80% fresh
JOH_LAGS = 5 if MODE == "high_frequency" else 1     # Johansen k_ar_diff; fewer lags for daily


def _adf(x):
    x = pd.Series(x).dropna().values
    stat, p = adfuller(x, autolag="AIC")[:2]
    return stat, p


def analyse(d, label):
    lines = [f"[{label}]  n = {len(d)} obs, {d['date'].nunique()} days, "
             f"Kalshi fresh {d['market_fresh'].mean() * 100:.0f}%"]
    m = d["kalshi_prob"].values
    for p in PLANS:
        ip = d[f"implied_p_{p}"].values
        # (1) fixed (1,-1) spread
        spread = ip - m
        s_stat, s_p = _adf(spread)
        # (2) Engle-Granger: implied_p = a + b*kalshi + resid
        eg = sm.OLS(ip, sm.add_constant(m)).fit()
        b = eg.params[1]
        r_stat, r_p = _adf(eg.resid)
        # (3) Johansen trace test, r = 0 vs r >= 1
        try:
            j = coint_johansen(np.column_stack([ip, m]), det_order=0, k_ar_diff=JOH_LAGS)
            tr, cv = j.lr1[0], j.cvt[0, 1]     # trace stat at r=0 and its 95% critical value
            joh = "COINTEGRATED" if tr > cv else "no"
            jstr = f"Johansen trace={tr:6.2f} vs 95%={cv:.2f} -> {joh}"
        except Exception as exc:
            jstr = f"Johansen n/a ({exc})"
        c1 = "COINTEGRATED" if s_p < 0.05 else "no"
        c2 = "COINTEGRATED" if r_p < 0.05 else "no"
        lines.append(
            f"  {p:16s}  spread(1,-1) ADF p={s_p:.3f}->{c1:12s} | "
            f"EngleGranger b={b:+6.2f} ADF p={r_p:.3f}->{c2:12s} | {jstr}")
    return lines


def main():
    d = pd.read_csv(PAIR, parse_dates=["ts_et"]).sort_values(["date", "ts_et"]).reset_index(drop=True)
    sub = d[d["date"] >= pd.Timestamp(SUBWIN_START).date().isoformat()].reset_index(drop=True)

    out = [f"STEP 4 [{MODE}] PART 2b - COINTEGRATION GATE (implied_p vs Kalshi)",
           "=" * 78,
           "Cointegrated (Hasbrouck legitimate) requires a stationary spread: ADF/EG",
           "p < 0.05, or Johansen trace > its 95% critical value. Otherwise NOT",
           "cointegrated.", ""]
    out += analyse(d, "full window 2024-10-04..11-06") + [""]
    out += analyse(sub, f"high-liquidity sub-window {SUBWIN_START}..11-06") + [""]
    out += ["Reading: the two-point calibration forces implied_p and Kalshi to agree only",
            "at the two anchors (sample start and election night). Between them the basket",
            "is driven by moves the market may not share, so the spread can wander even",
            "though the endpoints match. Cointegration is the honest test of whether the",
            "pair shares one price over time."]
    txt = "\n".join(out)
    with open(os.path.join(HERE, f"step4_cointegration_{MODE}.txt"), "w") as f:
        f.write(txt)
    print(txt)


if __name__ == "__main__":
    main()
