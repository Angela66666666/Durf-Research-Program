"""
methodB_etfs_only.py
================================================================================
CONTROL EXPERIMENT (lives at the top of Hasbrouck methodology/, not inside
attempt2). Same Method B recipe -- form basket weights by a LEVEL cointegrating
regression, in dollar space, Jun-Sep on Polymarket -- but using ONLY the 11
sector ETFs, WITHOUT the election-driven adds (DJT/COIN/TAN/GEO).

Question: does the level-fitting method alone make an all-ETF basket cointegrate
with Kalshi, or were the election-driven adds necessary? Then, if it cointegrates,
run the same Hasbrouck price-discovery decomposition. This file is self-contained
(its own VECM / Gonzalo-Granger / Hasbrouck code -- it does NOT call
attempt2/hasbrouck.py, which is the WITH-adds version).

Reads the daily panel already built by attempt2/build_daily_panel.py.

INPUT   6. hasbrouck/daily/panel_daily.csv ; 1. data/kalshi/kalshi/trades/trades_*
OUTPUT  methodB_etfs_only_results.txt   the full printed gate + Hasbrouck output
        methodB_etfs_only_pair.csv      basket implied_p vs Kalshi, daily
        methodB_etfs_only.png           the two lines
================================================================================
"""
import os
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.vector_ar.vecm import coint_johansen, VECM
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
ROOT = os.path.dirname(HERE)                            # Hasbrouck methodology -> Durf
PANEL = os.path.join(HERE, "attempt2", "panel_daily.csv")
TRADES_GLOB = os.path.join(DATA, "kalshi", "kalshi", "trades", "trades_*.parquet")

ETFS = ["VAW", "VCR", "VDC", "VDE", "VFH", "VGT", "VHT", "VIS", "VNQ", "VOX", "VPU"]  # NO adds
EST_START, EST_END = "2024-06-01", "2024-09-30"
TEST_START, TEST_END = "2024-10-04", "2024-11-06"
Q0, Q1 = 0.447, 1.0
CONTRACT = "PRES-2024-DJT"
NAMES = ["basket", "kalshi"]


def _adf_p(x):
    return adfuller(pd.Series(x).dropna().values, autolag="AIC")[1]


def load_kalshi_daily():
    q = f"""
    WITH t AS (
      SELECT (created_time AT TIME ZONE 'America/New_York') AS et, yes_price
      FROM read_parquet('{TRADES_GLOB}') WHERE ticker = '{CONTRACT}'
    )
    SELECT et::date AS d, last(yes_price ORDER BY et) / 100.0 AS prob
    FROM t
    WHERE et::date BETWEEN DATE '{TEST_START}' AND DATE '{TEST_END}'
      AND et::time <= TIME '16:00:00'
    GROUP BY d ORDER BY d
    """
    k = duckdb.sql(q).df(); k["d"] = pd.to_datetime(k["d"])
    return k.set_index("d")["prob"]


def hasbrouck_is(psi, Omega, order):
    p = np.asarray(order)
    M = np.linalg.cholesky(Omega[np.ix_(p, p)])
    psi_o = psi[p]
    out = np.empty(2)
    out[p] = (psi_o @ M) ** 2 / float(psi_o @ Omega[np.ix_(p, p)] @ psi_o)
    return out


def main():
    out = []
    def log(s=""):
        print(s); out.append(s)

    panel = pd.read_csv(PANEL, parse_dates=["date"]).set_index("date").sort_index()

    # STEP 1-2: level cointegrating regression, ETFs only
    est = panel.loc[EST_START:EST_END, ETFS + ["prob"]].dropna()
    reg = sm.OLS(est["prob"].values, sm.add_constant(est[ETFS].values)).fit()
    w = reg.params[1:]
    rp = _adf_p(reg.resid)
    log("METHOD B, ETFs ONLY (11 assets, no election adds)")
    log("  level fit %s..%s: in-sample R2 = %.3f, residual ADF p = %.3f -> in-sample %s\n"
        % (EST_START, EST_END, reg.rsquared, rp, "cointegrated" if rp < 0.05 else "NOT cointegrated"))

    # STEP 3: basket, calibrate, cointegration gate
    test = panel.loc[TEST_START:TEST_END]
    B = test[ETFS].values @ w
    implied = Q0 + (B - B[0]) * (Q1 - Q0) / (B[-1] - B[0])
    kal = load_kalshi_daily()
    pair = pd.DataFrame({"implied_p": implied, "kalshi": kal.reindex(test.index).ffill().values},
                        index=test.index).dropna()
    pair.index.name = "date"
    pair.to_csv(os.path.join(HERE, "methodB_etfs_only_pair.csv"))
    ip, m = pair["implied_p"].values, pair["kalshi"].values

    sp = _adf_p(ip - m)
    eg = sm.OLS(ip, sm.add_constant(m)).fit(); egp = _adf_p(eg.resid)
    joh = coint_johansen(np.column_stack([ip, m]), det_order=0, k_ar_diff=1)
    tr, cv = joh.lr1[0], joh.cvt[0, 1]
    log("COINTEGRATION GATE (daily, %d obs, vs full Method B with adds in brackets):" % len(pair))
    log("  ADF spread(1,-1) p = %.3f -> %-12s [with adds: 0.014]" % (sp, "COINTEGRATED" if sp < 0.05 else "no"))
    log("  Engle-Granger    p = %.3f -> %-12s [with adds: 0.013]  (b=%+.2f)" % (egp, "COINTEGRATED" if egp < 0.05 else "no", eg.params[1]))
    log("  Johansen trace = %.2f vs 95%%=%.2f -> %-12s [with adds: 10.63]" % (tr, cv, "COINTEGRATED" if tr > cv else "no"))

    # Hasbrouck (self-contained)
    res = VECM(pair[["implied_p", "kalshi"]].values, k_ar_diff=1, coint_rank=1, deterministic="ci").fit()
    alpha = res.alpha[:, 0]; Omega = np.cov(res.resid, rowvar=False)
    a_perp = np.array([alpha[1], -alpha[0]]).astype(float)
    gg = a_perp / a_perp.sum() if a_perp.sum() != 0 else np.array([np.nan, np.nan])
    is_a = hasbrouck_is(a_perp, Omega, [0, 1]); is_b = hasbrouck_is(a_perp, Omega, [1, 0])
    lo, hi = np.minimum(is_a, is_b), np.maximum(is_a, is_b)
    rho = Omega[0, 1] / np.sqrt(Omega[0, 0] * Omega[1, 1])
    log("\nHASBROUCK / VECM (indicative -- see caveat):")
    log("  alpha: basket %+.3f , kalshi %+.3f  -> %s leads (smaller |alpha|)"
        % (alpha[0], alpha[1], NAMES[int(abs(alpha[0]) > abs(alpha[1]))]))
    log("  Gonzalo-Granger: basket %.1f%% , kalshi %.1f%%" % (100 * gg[0], 100 * gg[1]))
    log("  Hasbrouck IS (resid corr %+.2f): basket [%.1f%%, %.1f%%], kalshi [%.1f%%, %.1f%%]"
        % (rho, 100 * lo[0], 100 * hi[0], 100 * lo[1], 100 * hi[1]))
    log("\nCaveat: 24 daily obs, small sample, Johansen not confirmed -> indicative only.")

    with open(os.path.join(HERE, "methodB_etfs_only_results.txt"), "w") as f:
        f.write("\n".join(out) + "\n")

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(pair.index, pair["implied_p"], "o-", color="#1f77b4", lw=1.4, ms=4, label="ETFs-only basket (implied P)")
    ax.plot(pair.index, pair["kalshi"], "o-", color="black", lw=1.0, ms=3, label="Kalshi PRES-2024-DJT (16:00 ET)")
    ax.axhline(0, color="0.7", lw=.6); ax.axhline(1, color="0.7", lw=.6)
    ax.set_ylabel("P(Trump wins)"); ax.legend(); ax.margins(x=.01)
    ax.set_title("Method B, ETFs only -- level cointegrating basket vs Kalshi (daily)")
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "methodB_etfs_only.png"), dpi=140)

    log("\nwritten -> methodB_etfs_only_results.txt, methodB_etfs_only_pair.csv, methodB_etfs_only.png")


if __name__ == "__main__":
    main()
