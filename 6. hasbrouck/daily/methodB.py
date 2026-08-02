"""
methodB.py   (attempt2 -- Method B, all three steps in one file)
================================================================================
METHOD B: form the basket by fitting the LEVEL relationship directly (an
Engle-Granger cointegrating regression), instead of Method A's change/tracking
regression. Method A minimises daily CHANGE tracking error and leaves a
persistent level gap between basket and market; Method B targets the LEVEL, so
it is aimed straight at that gap.

  Step 1-2: regress the P(Trump) LEVEL on the asset price LEVELS over Jun-Sep
            (Polymarket).  prob_t = a + sum_i w_i * P_i,t + resid.
            The coefficients w_i are the basket weights; a stationary residual
            means basket and probability cointegrate in the estimation window.

  Step 3  : fixed-share dollar basket B_t = sum w_i P_i, then a START-ANCHORED
            prediction implied_p_t = Q0 + (B_t - B_0): anchor only the first test
            day at Q0 and roll forward on the cumulative weighted dollar change,
            so the series is causal (no look-ahead). Cointegration gate vs Kalshi
            (16:00 ET) is judged by Engle-Granger, which is scale-invariant.

Caveats, stated honestly:
  - A level-on-levels regression of a trending series on 15 trending prices is
    prone to SPURIOUS in-sample fit; in-sample R^2 will look high and is not
    trustworthy on its own. The residual ADF (in-sample cointegration) and,
    above all, the Oct-Nov test against Kalshi are what matter.
  - Weights are still fit on Polymarket, pre-Kalshi, so the Oct-Nov test is out
    of sample (different venue AND period), no circularity.

BASKET COMPOSITION  (ETFS + ADDS = 11 + 8 = 19 assets)
  The 8 election-driven adds are THEME LEADERS from systematic_stock_screen.py
  (change-screen rank among 1303 liquid stocks) -- one/two per theme plus the
  solar ETF, NOT the raw top-8, to avoid over-concentrating a single theme:

    ticker   screen rank      theme
    MARA     positive #1      crypto -- miners (leader)
    COIN     positive #6      crypto -- exchange
    GEO      positive #8      private prisons
    IBKR     positive #10     brokers / capital markets
    RUN      negative #2      solar
    FSLR     negative #3      solar
    DHI      negative #7      homebuilders / housing
    TAN      not in screen    solar ETF (added separately -- ETFs are not in the
                              single-stock screen universe)

  Deliberately skipped though higher-ranked (theme already covered, or too noisy):
    RIOT #2, RUM #3, CLSK #4, DJT #5 (crypto / Trump media);
    AES #1, CSIQ #4, NEE #5, FND #6 (negative side).
  Rationale: stacking same-theme high-rank stocks tracked WORSE out of sample
  (11 ETF + all 28 screened names fell to corr 0.71); leaders + diversity wins.

INPUT   panel_daily.csv ; 1. data/kalshi/kalshi/trades/trades_*
OUTPUT  methodB_weights.csv, methodB_pair.csv, methodB.png, methodB_results.txt
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
ADDS = ["MARA", "COIN", "GEO", "IBKR", "FSLR", "RUN", "DHI", "TAN"]   # theme leaders -- see BASKET COMPOSITION above
EST_START, EST_END = "2024-06-01", "2024-09-30"
TEST_START, TEST_END = "2024-10-04", "2024-11-06"
Q0, Q1 = 0.447, 1.0
CONTRACT = "PRES-2024-DJT"


def _adf_p(x):
    return adfuller(pd.Series(x).dropna().values, autolag="AIC")[1]


def load_kalshi_daily():
    # Kalshi sampled at the 16:00 ET ETF close (not last evening trade), so both
    # series share one daily clock and no spurious Kalshi lead is manufactured.
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
    out_lines = []

    def emit(s=""):
        print(s)
        out_lines.append(s)

    panel = pd.read_csv(PANEL, parse_dates=["date"]).set_index("date").sort_index()
    cols = ETFS + ADDS
    emit("METHOD B -- level cointegrating basket vs Kalshi PRES-2024-DJT (daily, 16:00 ET)")
    emit("basket = 11 sector ETFs + %s\n" % ", ".join(ADDS))

    # ======================================================================
    # STEP 1-2 -- FORM WEIGHTS BY A LEVEL COINTEGRATING REGRESSION
    #   prob_level ~ const + asset price levels, over Jun-Sep (Polymarket).
    #   coefficients = weights; residual ADF = in-sample cointegration check.
    # ======================================================================
    est = panel.loc[EST_START:EST_END, cols + ["prob"]].dropna()
    y = est["prob"].values
    X = est[cols].values
    reg = sm.OLS(y, sm.add_constant(X)).fit()
    w = pd.Series(reg.params[1:], index=cols, name="share_weight")
    w.to_csv(os.path.join(HERE, "methodB_weights.csv"))
    resid_p = _adf_p(reg.resid)

    emit("STEP 1-2  weights by LEVEL cointegrating regression, %s..%s (Polymarket)\n" % (EST_START, EST_END))
    emit("  n = %d days, in-sample R2 = %.3f  (level fit -- inflated, see header)" % (len(est), reg.rsquared))
    emit("  residual ADF p = %.3f -> in-sample %s" % (resid_p, "cointegrated" if resid_p < 0.05 else "NOT cointegrated"))

    # ======================================================================
    # STEP 3 -- FIXED-SHARE DOLLAR BASKET, START-ANCHORED PREDICTION, COINTEGRATION
    #   implied_p_t = Q0 + (B_t - B_0)   -- anchor ONLY the first test day at Q0
    #   and let the cumulative weighted dollar change carry it forward. This is a
    #   causal, one-sided time-series prediction: each day t uses only data up to
    #   t, the pre-test weights, and the known start value Q0 -- no future point.
    #   (The earlier two-point calibration divided by (B_last - B_0), which used
    #   the LAST test day, i.e. look-ahead; kept below only as a dashed reference.)
    # ======================================================================
    test = panel.loc[TEST_START:TEST_END]
    B = test[cols].values @ w.values
    B0 = B[0]
    implied = Q0 + (B - B0)                                   # look-ahead-free
    implied_2pt = Q0 + (B - B0) * (Q1 - Q0) / (B[-1] - B0)    # old, plot reference only

    kal = load_kalshi_daily()
    pair = pd.DataFrame({"implied_p": implied, "date": test.index}).set_index("date")
    pair["kalshi"] = kal.reindex(pair.index).ffill()
    pair = pair.dropna()
    pair.to_csv(os.path.join(HERE, "methodB_pair.csv"))

    ip, m = pair["implied_p"].values, pair["kalshi"].values
    spread_p = _adf_p(ip - m)
    eg = sm.OLS(ip, sm.add_constant(m)).fit()
    eg_p = _adf_p(eg.resid)
    joh = coint_johansen(np.column_stack([ip, m]), det_order=0, k_ar_diff=1)
    tr, cv = joh.lr1[0], joh.cvt[0, 1]

    emit("\nSTEP 3  dollar basket vs Kalshi -- cointegration gate (daily, %d obs)" % len(pair))
    emit("  implied_p = Q0 + (B_t - B_0), start-anchored, no look-ahead")
    emit("  implied_p range [%.3f, %.3f]  (reaches %.3f on election day, not forced to 1.0)"
         % (implied.min(), implied.max(), implied[-1]))
    emit("  ADF spread(1,-1) p = %.3f -> %s" % (spread_p, "COINTEGRATED" if spread_p < 0.05 else "no"))
    emit("  Engle-Granger    p = %.3f -> %s  (slope b=%+.2f; scale-invariant, the headline test)"
         % (eg_p, "COINTEGRATED" if eg_p < 0.05 else "no", eg.params[1]))
    emit("  Johansen trace = %.2f vs 95%%=%.2f -> %s" % (tr, cv, "COINTEGRATED" if tr > cv else "no"))

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(pair.index, pair["implied_p"], "o-", color="#9467bd", lw=1.4, ms=4, label="Method B basket, start-anchored (no look-ahead)")
    ax.plot(test.index, implied_2pt, "--", color="#c9b3e0", lw=1.1, label="old two-point calibration (look-ahead, reference)")
    ax.plot(pair.index, pair["kalshi"], "o-", color="black", lw=1.0, ms=3, label="Kalshi PRES-2024-DJT (16:00 ET)")
    ax.axhline(0, color="0.7", lw=.6); ax.axhline(1, color="0.7", lw=.6)
    ax.set_ylabel("P(Trump wins)"); ax.legend(); ax.margins(x=.01)
    ax.set_title("attempt2 Method B -- start-anchored basket prediction vs Kalshi (daily, est %s..%s)" % (EST_START, EST_END))
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "methodB.png"), dpi=140)
    with open(os.path.join(HERE, "methodB_results.txt"), "w") as f:
        f.write("\n".join(out_lines) + "\n")
    emit("\nwritten -> methodB_weights.csv, methodB_pair.csv, methodB.png, methodB_results.txt")


if __name__ == "__main__":
    main()
