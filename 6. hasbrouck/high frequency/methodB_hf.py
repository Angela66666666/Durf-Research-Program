"""
methodB_hf.py   (attempt2 -- STEP 4, part 1: the 1-minute pair)
================================================================================
High-frequency counterpart of methodB.py. Same basket, same weights, same
start-anchored construction -- only the sampling frequency changes, from daily
(24 obs) to 1-minute (~9,400 obs).

WEIGHTS ARE NOT RE-ESTIMATED HERE. They are read from methodB_weights.csv, i.e.
the LEVEL cointegrating regression fitted on DAILY Polymarket data over Jun-Sep,
before the Kalshi contract traded. Re-fitting them on the intraday test window
would destroy the out-of-sample property that the whole design rests on: the
weights must come from a different venue AND a different period than the window
they are tested on.

IMPLIED PROBABILITY -- look-ahead free, and now anchored to Kalshi:

    implied_p_t = anchor + (B_t - B_0),     B_t = sum_i w_i * P_i,t

  The anchor is Kalshi's value in the FIRST minute of the window, not the
  external 0.447 reference used in the daily file. Reason: the daily run showed
  the two series starting 0.053 apart purely because the external anchor did not
  match where Kalshi actually was that day, which put a constant offset into the
  spread that had nothing to do with the data. Anchoring on Kalshi's own opening
  value removes that artefact and is still strictly causal -- it uses the first
  observation of the window only, never a future one.

  What anchoring CANNOT fix, and should not be made to fix, is the basket's
  under-response: daily, the basket moved only ~17% as far as Kalshi did. That
  is a real property of a sector-ETF basket, not a calibration problem, and it
  is left visible. Engle-Granger absorbs it in its slope, which is why EG (not
  the 1:-1 spread ADF) is the test to read.

INPUT   hf_panel_1min.csv      (from build_hf_panel.py)
        methodB_weights.csv    (daily Jun-Sep Polymarket weights)
OUTPUT  hf_pair_1min.csv, methodB_hf.png, methodB_hf_results.txt
================================================================================
"""
import os
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.vector_ar.vecm import coint_johansen
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
# Walk up until the folder containing "1. data" is found, so the script runs
# from any depth without hard-coded relative hops.
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "1. data")):
    ROOT = os.path.dirname(ROOT)

PANEL = os.path.join(HERE, "hf_panel_1min.csv")
# The weights come from the DAILY Method B fit, which lives one folder over.
WEIGHTS = os.path.join(ROOT, "6. hasbrouck", "daily", "methodB_weights.csv")

ETFS = ["VAW", "VCR", "VDC", "VDE", "VFH", "VGT", "VHT", "VIS", "VNQ", "VOX", "VPU"]
ADDS = ["MARA", "COIN", "GEO", "IBKR", "FSLR", "RUN", "DHI", "TAN"]

# Intraday lag order for Johansen. One minute of trading carries far less
# information than one day, so a handful of lags is the intraday analogue of
# k_ar_diff=1 at the daily frequency.
K_AR_DIFF = 5


def _adf_p(x):
    return adfuller(pd.Series(x).dropna().values, autolag="AIC")[1]


def main():
    out_lines = []

    def emit(s=""):
        print(s)
        out_lines.append(s)

    panel = pd.read_csv(PANEL, parse_dates=["minute"]).set_index("minute").sort_index()
    w = pd.read_csv(WEIGHTS, index_col=0).iloc[:, 0]
    cols = ETFS + ADDS
    w = w.reindex(cols)

    emit("METHOD B (HIGH FREQUENCY) -- 1-minute basket vs Kalshi PRES-2024-DJT")
    emit("basket = 11 sector ETFs + %s" % ", ".join(ADDS))
    emit("weights: daily Jun-Sep Polymarket level regression (NOT re-fitted intraday)\n")

    # ---- basket level and start-anchored implied probability --------------
    B = panel[cols].values @ w.values
    anchor = float(panel["kalshi"].iloc[0])
    implied = anchor + (B - B[0])

    pair = pd.DataFrame({"implied_p": implied, "kalshi": panel["kalshi"].values},
                        index=panel.index)
    pair.index.name = "minute"
    pair.to_csv(os.path.join(HERE, "hf_pair_1min.csv"))

    ip, m = pair["implied_p"].values, pair["kalshi"].values
    days = pd.Series(pair.index.date).nunique()

    emit("STEP 3-HF  1-minute pair, %d obs over %d trading days (RTH only)" % (len(pair), days))
    emit("  anchor = Kalshi's first minute = %.3f  (causal; no look-ahead)" % anchor)
    emit("  implied_p range [%.3f, %.3f]   kalshi range [%.3f, %.3f]"
         % (ip.min(), ip.max(), m.min(), m.max()))
    emit("  level correlation  = %+.3f" % np.corrcoef(ip, m)[0, 1])
    emit("  basket move / Kalshi move (first->last) = %.2f"
         % ((ip[-1] - ip[0]) / (m[-1] - m[0]) if m[-1] != m[0] else np.nan))

    # ---- cointegration gate ----------------------------------------------
    spread_p = _adf_p(ip - m)
    eg = sm.OLS(ip, sm.add_constant(m)).fit()
    eg_p = _adf_p(eg.resid)
    joh = coint_johansen(np.column_stack([ip, m]), det_order=0, k_ar_diff=K_AR_DIFF)
    tr, cv = joh.lr1[0], joh.cvt[0, 1]

    emit("\n  cointegration gate (1-minute):")
    emit("    ADF spread(1,-1) p = %.4f -> %s" % (spread_p, "COINTEGRATED" if spread_p < 0.05 else "no"))
    emit("    Engle-Granger    p = %.4f -> %s  (slope b=%+.3f)  <- headline, scale-invariant"
         % (eg_p, "COINTEGRATED" if eg_p < 0.05 else "no", eg.params[1]))
    emit("    Johansen trace = %.2f vs 95%%=%.2f (k_ar_diff=%d) -> %s"
         % (tr, cv, K_AR_DIFF, "COINTEGRATED" if tr > cv else "no"))

    # ---- figure ----------------------------------------------------------
    fig, ax = plt.subplots(figsize=(13, 5))
    x = np.arange(len(pair))                     # sequential index: no overnight gaps drawn
    ax.plot(x, ip, color="#9467bd", lw=1.0, label="Method B basket, 1-min (start-anchored)")
    ax.plot(x, m, color="black", lw=1.0, label="Kalshi PRES-2024-DJT, 1-min")
    # mark day boundaries so the overnight breaks are visible
    d = pd.Series(pair.index.date).values
    for i in np.where(d[1:] != d[:-1])[0]:
        ax.axvline(i + 1, color="0.85", lw=.5, zorder=0)
    ticks = np.where(d[1:] != d[:-1])[0][::4]
    ax.set_xticks(ticks)
    ax.set_xticklabels([str(d[i + 1]) for i in ticks], rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("P(Trump wins)")
    ax.legend(loc="upper left")
    ax.set_title("attempt2 STEP 4 -- 1-minute basket vs Kalshi (RTH, %d obs)" % len(pair))
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "methodB_hf.png"), dpi=140)

    with open(os.path.join(HERE, "methodB_hf_results.txt"), "w") as f:
        f.write("\n".join(out_lines) + "\n")
    emit("\nwritten -> hf_pair_1min.csv, methodB_hf.png, methodB_hf_results.txt")


if __name__ == "__main__":
    main()
