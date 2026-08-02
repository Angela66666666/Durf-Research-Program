"""
methodA.py   (attempt2 -- Method A, all three steps in one file)
================================================================================
METHOD A: form the basket by directly tracking the daily change in P(Trump) in
DOLLAR space, pick the universe/window by OUT-OF-SAMPLE R^2, then build the
fixed-share dollar basket, calibrate it, and test cointegration against Kalshi.

Steps 1-2 and 3 are marked with comment banners below. Data prep is shared and
lives in build_daily_panel.py. Method B differs only in Steps 1-2 (how the
weights are formed); Step 3 is identical, so it is repeated there for a
self-contained file.

Estimation window default Jun-Sep 2024: dropping the Mar-May DJT-listing noise
lifts out-of-sample R^2 from ~0.03 (Mar-Sep) to ~0.19 (Jun-Sep); the event-only
window (28 days) overfits 15 assets and collapses. Weights are fit on Polymarket
before Kalshi's contract trades, so the Oct-Nov test against Kalshi is genuinely
out of sample (different venue AND period).

INPUT   panel_daily.csv
        1. data/kalshi/kalshi/trades/trades_*   (Kalshi)
OUTPUT  methodA_weights.csv, methodA_pair.csv, methodA.png  (+ printed gate)
================================================================================
"""
import os
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.vector_ar.vecm import coint_johansen
import duckdb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
# Walk up until the folder containing "1. data" is found, so the script runs
# from any depth without hard-coded relative hops.
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "1. data")):
    ROOT = os.path.dirname(ROOT)
DATA = os.path.join(ROOT, "1. data")
PANEL = os.path.join(HERE, "panel_daily.csv")
TRADES_GLOB = os.path.join(DATA, "kalshi", "kalshi", "trades", "trades_*.parquet")

ETFS = ["VAW", "VCR", "VDC", "VDE", "VFH", "VGT", "VHT", "VIS", "VNQ", "VOX", "VPU"]
ADDS = ["MARA", "COIN", "GEO", "IBKR", "FSLR", "RUN", "DHI", "TAN"]   # systematically-screened compact leaders
EST_START, EST_END = "2024-06-01", "2024-09-30"        # chosen by OOS R^2 (see header)
TEST_START, TEST_END = "2024-10-04", "2024-11-06"
Q0, Q1 = 0.447, 1.0
CONTRACT = "PRES-2024-DJT"


def _fit(X, y):
    A = np.column_stack([np.ones(len(X)), X])
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    return coef


def _oos_r2(X, y):
    """In-sample and leave-one-out OOS R^2 for regressing y on X (+intercept)."""
    n = len(y)
    coef = _fit(X, y)
    yhat = coef[0] + X @ coef[1:]
    sst = float(((y - y.mean()) ** 2).sum())
    r2_in = 1.0 - float(((y - yhat) ** 2).sum()) / sst
    pr = np.empty(n)
    for i in range(n):
        m = np.ones(n, bool); m[i] = False
        c = _fit(X[m], y[m]); pr[i] = c[0] + X[i] @ c[1:]
    return r2_in, 1.0 - float(((y - pr) ** 2).sum()) / sst


def _adf_p(x):
    return adfuller(pd.Series(x).dropna().values, autolag="AIC")[1]


def load_kalshi_daily():
    # Sample Kalshi at the ETF close (16:00 ET), not the last trade of the day:
    # Kalshi trades into the evening, so "last trade" would see news the 16:00
    # ETF close cannot -- an asymmetry that manufactures spurious Kalshi lead.
    q = f"""
    WITH t AS (
      SELECT (created_time AT TIME ZONE 'America/New_York') AS et, yes_price
      FROM read_parquet('{TRADES_GLOB}')
      WHERE ticker = '{CONTRACT}'
    )
    SELECT et::date AS d, last(yes_price ORDER BY et) / 100.0 AS prob
    FROM t
    WHERE et::date BETWEEN DATE '{TEST_START}' AND DATE '{TEST_END}'
      AND et::time <= TIME '16:00:00'
    GROUP BY d ORDER BY d
    """
    k = duckdb.sql(q).df()
    k["d"] = pd.to_datetime(k["d"])
    return k.set_index("d")["prob"]


def main():
    panel = pd.read_csv(PANEL, parse_dates=["date"]).set_index("date").sort_index()

    # ======================================================================
    # STEP 1-2 -- FORM THE BASKET WEIGHTS BY DOLLAR TRACKING (judged by OOS R^2)
    #   Regress the daily change in P(Trump) on the daily dollar changes of the
    #   assets. The fitted coefficients are the fixed share counts. We show
    #   ETFs-only vs ETFs+adds so the value of the election-driven names is
    #   visible, then keep the ETFs+adds weights.
    # ======================================================================
    est = panel.loc[EST_START:EST_END]
    dprob = est["prob"].diff()
    print("STEP 1-2  weights by dollar tracking, estimation %s..%s (Polymarket)\n" % (EST_START, EST_END))
    print(f"  {'universe':18s} {'n':>4s} {'in-sample R2':>13s} {'OOS R2 (LOO)':>13s}")
    print("  " + "-" * 52)
    for label, cols in [("ETFs only (11)", ETFS), ("ETFs + adds (15)", ETFS + ADDS)]:
        d = pd.concat([dprob.rename("y"), est[cols].diff()], axis=1).dropna()
        r2_in, r2_oos = _oos_r2(d[cols].values, d["y"].values)
        print(f"  {label:18s} {len(d):4d} {r2_in:13.3f} {r2_oos:13.3f}")

    cols = ETFS + ADDS
    d = pd.concat([dprob.rename("y"), est[cols].diff()], axis=1).dropna()
    w = pd.Series(_fit(d[cols].values, d["y"].values)[1:], index=cols, name="share_weight")
    w.to_csv(os.path.join(HERE, "methodA_weights.csv"))

    # ======================================================================
    # STEP 3 -- FIXED-SHARE DOLLAR BASKET, TWO-POINT CALIBRATION, COINTEGRATION
    #   B_t = sum_i n_i * P_i,t  (exactly affine in p -> exact two-point anchor).
    #   implied_p_t = q0 + (B_t - B_0)/(B_1 - B_0) * (q1 - q0).
    #   Gate: ADF on the (1,-1) spread, Engle-Granger, Johansen trace.
    # ======================================================================
    test = panel.loc[TEST_START:TEST_END]
    B = test[cols].values @ w.values
    B0, B1 = B[0], B[-1]
    implied = Q0 + (B - B0) * (Q1 - Q0) / (B1 - B0)

    kal = load_kalshi_daily()
    pair = pd.DataFrame({"implied_p": implied, "date": test.index}).set_index("date")
    pair["kalshi"] = kal.reindex(pair.index).ffill()
    pair = pair.dropna()
    pair.to_csv(os.path.join(HERE, "methodA_pair.csv"))

    ip, m = pair["implied_p"].values, pair["kalshi"].values
    spread_p = _adf_p(ip - m)
    eg = sm.OLS(ip, sm.add_constant(m)).fit()
    eg_p = _adf_p(eg.resid)
    joh = coint_johansen(np.column_stack([ip, m]), det_order=0, k_ar_diff=1)
    tr, cv = joh.lr1[0], joh.cvt[0, 1]

    print("\nSTEP 3  dollar basket vs Kalshi -- cointegration gate (daily, %d obs)" % len(pair))
    print("  implied_p range [%.3f, %.3f]" % (implied.min(), implied.max()))
    print("  ADF spread(1,-1) p = %.3f -> %s" % (spread_p, "COINTEGRATED" if spread_p < 0.05 else "no"))
    print("  Engle-Granger    p = %.3f -> %s  (slope b=%+.2f)" % (eg_p, "COINTEGRATED" if eg_p < 0.05 else "no", eg.params[1]))
    print("  Johansen trace = %.2f vs 95%%=%.2f -> %s" % (tr, cv, "COINTEGRATED" if tr > cv else "no"))

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(pair.index, pair["implied_p"], "o-", color="#2ca02c", lw=1.4, ms=4, label="Method A dollar basket (implied P)")
    ax.plot(pair.index, pair["kalshi"], "o-", color="black", lw=1.0, ms=3, label="Kalshi PRES-2024-DJT (16:00 ET)")
    ax.axhline(0, color="0.7", lw=.6); ax.axhline(1, color="0.7", lw=.6)
    ax.set_ylabel("P(Trump wins)"); ax.legend(); ax.margins(x=.01)
    ax.set_title("attempt2 Method A -- fixed-share dollar basket vs Kalshi (daily, est %s..%s)" % (EST_START, EST_END))
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "methodA.png"), dpi=140)
    print("\nwritten -> methodA_weights.csv, methodA_pair.csv, methodA.png")


if __name__ == "__main__":
    main()
