"""
methodB_screened_stocks.py   (attempt2)
================================================================================
Build the basket from the CHANGE-screen thematic leaders (the right tool for
SELECTION: differencing isolates election sensitivity), then construct with
Method B LEVELS (the right tool for calibration). Validate out of sample
(Oct-Nov vs Kalshi) by tracking quality + the cointegration gate.

Selected themes (top names from systematic_stock_screen.py, change screen):
  long  (Trump up -> up)  : crypto miners MARA/RIOT/CLSK, exchange COIN, MSTR,
                            prison GEO, broker IBKR, media DJT/RUM
  short (Trump up -> down): solar FSLR/RUN/CSIQ, utility AES/NEE, housing DHI/FND,
                            solar ETF TAN

Compares several universes so out-of-sample tracking/cointegration picks, not a
low ADF on a noisy basket (corr is the honest tracking metric).

INPUT   yfinance (daily) ; 1. data/polymarket_trump_2024_daily.csv
        1. data/kalshi/kalshi/trades/trades_*
OUTPUT  methodB_screened_stocks_results.txt
================================================================================
"""
import os
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.vector_ar.vecm import coint_johansen
import duckdb
import yfinance as yf

HERE = os.path.dirname(os.path.abspath(__file__))
# Walk up until the folder containing "1. data" is found, so the script runs
# from any depth without hard-coded relative hops.
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "1. data")):
    ROOT = os.path.dirname(ROOT)
DATA = os.path.join(ROOT, "1. data")
PM = os.path.join(DATA, "polymarket_trump_2024_daily.csv")
TRADES_GLOB = os.path.join(DATA, "kalshi", "kalshi", "trades", "trades_*.parquet")

ETFS = ["VAW", "VCR", "VDC", "VDE", "VFH", "VGT", "VHT", "VIS", "VNQ", "VOX", "VPU"]
LONG = ["MARA", "RIOT", "CLSK", "COIN", "MSTR", "GEO", "IBKR", "DJT", "RUM"]
SHORT = ["FSLR", "RUN", "CSIQ", "AES", "NEE", "DHI", "FND", "TAN"]
BASE_ADDS = ["DJT", "COIN", "TAN", "GEO"]
LEADERS = ["MARA", "COIN", "GEO", "IBKR", "FSLR", "RUN", "DHI", "TAN"]      # compact, both directions

EST_START, EST_END = "2024-06-01", "2024-09-30"
TEST_START, TEST_END = "2024-10-04", "2024-11-06"
Q0, Q1 = 0.447, 1.0


def _adf_p(x):
    return adfuller(pd.Series(x).dropna().values, autolag="AIC")[1]


def load_kalshi_daily():
    q = f"""
    WITH t AS (SELECT (created_time AT TIME ZONE 'America/New_York') AS et, yes_price
      FROM read_parquet('{TRADES_GLOB}') WHERE ticker='PRES-2024-DJT')
    SELECT et::date AS d, last(yes_price ORDER BY et)/100.0 AS prob FROM t
    WHERE et::date BETWEEN DATE '{TEST_START}' AND DATE '{TEST_END}' AND et::time<=TIME '16:00:00'
    GROUP BY d ORDER BY d
    """
    k = duckdb.sql(q).df(); k["d"] = pd.to_datetime(k["d"])
    return k.set_index("d")["prob"]


def evaluate(panel, kal, cols):
    cols = [c for c in cols if c in panel.columns]
    est = panel.loc[EST_START:EST_END, cols + ["prob"]].dropna()
    reg = sm.OLS(est["prob"].values, sm.add_constant(est[cols].values)).fit()
    w = reg.params[1:]
    test = panel.loc[TEST_START:TEST_END]
    B = test[cols].values @ w
    implied = Q0 + (B - B[0]) * (Q1 - Q0) / (B[-1] - B[0])
    d = pd.DataFrame({"i": implied, "k": kal.reindex(test.index).ffill().values}, index=test.index).dropna()
    ip, m = d["i"].values, d["k"].values
    s = ip - m
    eg = sm.OLS(ip, sm.add_constant(m)).fit()
    joh = coint_johansen(np.column_stack([ip, m]), det_order=0, k_ar_diff=1)
    return len(cols), d["i"].corr(d["k"]), np.sqrt((s ** 2).mean()), _adf_p(s), _adf_p(eg.resid), joh.lr1[0]


def main():
    tickers = sorted(set(ETFS + LONG + SHORT + BASE_ADDS + LEADERS))
    px = yf.download(tickers, start="2024-01-01", end="2024-11-07", auto_adjust=True, progress=False)["Close"]
    have = [t for t in tickers if t in px and px[t].notna().sum() > 100]
    missing = [t for t in tickers if t not in have]
    pm = pd.read_csv(PM, parse_dates=["date"]).set_index("date")["prob"]
    panel = px[have].join(pm, how="left")
    kal = load_kalshi_daily()

    universes = {
        "baseline: 11ETF + DJT+COIN+TAN+GEO": ETFS + BASE_ADDS,
        "screened stocks only (long+short)": LONG + SHORT,
        "11ETF + screened stocks": ETFS + LONG + SHORT,
        "compact leaders only (8)": LEADERS,
        "11ETF + compact leaders": ETFS + LEADERS,
    }
    out = ["METHOD B -- CHANGE-screen-selected thematic stocks, Method-B build, Oct-Nov vs Kalshi",
           "fetched: %s" % ", ".join(have),
           "missing: %s" % (", ".join(missing) or "none"),
           "corr = honest tracking; cointegration: ADF/EG p<0.05 or Johansen>15.49", "",
           f"  {'universe':38s} {'k':>3s} {'corr':>6s} {'RMSE':>6s} {'ADF':>6s} {'EG':>6s} {'Johan':>6s}",
           "  " + "-" * 76]
    for name, cols in universes.items():
        k, c, r, a, e, j = evaluate(panel, kal, cols)
        out.append(f"  {name:38s} {k:3d} {c:6.2f} {r:6.3f} {a:6.3f} {e:6.3f} {j:6.2f}")
    out += ["", "Read: prefer HIGH corr AND passing tests. A basket of many meme/crypto",
            "names can have election beta yet track poorly (idiosyncratic noise); the",
            "sector-ETF base plus a few theme names is usually the steadier tracker."]
    txt = "\n".join(out)
    with open(os.path.join(HERE, "methodB_screened_stocks_results.txt"), "w") as f:
        f.write(txt + "\n")
    print(txt)
    print("\nwritten -> methodB_screened_stocks_results.txt")


if __name__ == "__main__":
    main()
