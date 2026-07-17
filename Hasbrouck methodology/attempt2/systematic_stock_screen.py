"""
systematic_stock_screen.py   (attempt2)
================================================================================
Systematic, hindsight-free candidate screen over every liquid US stock, on
PRE-TEST data (Jun-Sep 2024, Polymarket). Two rankings, because selection should
match how the basket is built:

  CHANGE screen (Method A logic): corr( daily return , d P(Trump) ), as a t-stat.
      Differencing removes the common summer up-trend, so it isolates genuine
      election sensitivity -- robust, but not the level object Method B uses.

  LEVEL / cointegration screen (Method B logic): regress the P(Trump) LEVEL on
      the price LEVEL and ADF-test the residual (single-stock Engle-Granger).
      This matches Method B (levels), but raw level correlation is spurious
      (everything that rose in summer correlates with a rising prob), so we rank
      by residual stationarity (cointegration), not by level correlation.

Reassurance against multiple testing (~1300 names): trust names that cluster
into coherent economic themes; validate out of sample (Oct-Nov) before trusting.

INPUT   ../../etf_data/stock_prices.parquet
        ../attempt1/step1_step2/polymarket_trump_2024_daily.csv
OUTPUT  systematic_stock_screen.csv   full table, both rankings
        systematic_stock_screen.txt   readable summary
================================================================================
"""
import os
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
import duckdb

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
STOCKS = os.path.join(ROOT, "etf_data", "stock_prices.parquet")
PM = os.path.join(HERE, "..", "attempt1", "step1_step2", "polymarket_trump_2024_daily.csv")

EST_START, EST_END = "2024-06-01", "2024-09-30"
PAD_START = "2024-05-28"
MIN_PRICE, MIN_VOL, MIN_DAYS, MIN_OBS = 5.0, 1_000_000, 60, 50
OUR_PICKS = ["GEO", "DJT", "COIN"]


def _adf_p(x):
    x = np.asarray(x, float)
    if len(x) < 12 or np.std(x) == 0:
        return np.nan
    try:
        return adfuller(x, autolag="AIC")[1]
    except Exception:
        return np.nan


def main():
    px = duckdb.sql(f"""
        SELECT symbol, CAST(report_date AS DATE) d, close, volume
        FROM read_parquet('{STOCKS}')
        WHERE CAST(report_date AS DATE) BETWEEN DATE '{PAD_START}' AND DATE '{EST_END}'
    """).df()
    px["d"] = pd.to_datetime(px["d"])
    pm = pd.read_csv(PM, parse_dates=["date"]).set_index("date")["prob"]

    liq = px.groupby("symbol").agg(n=("close", "size"), ac=("close", "mean"), av=("volume", "mean"))
    keep = liq[(liq.n >= MIN_DAYS) & (liq.ac >= MIN_PRICE) & (liq.av >= MIN_VOL)].index
    px = px[px.symbol.isin(keep)].sort_values(["symbol", "d"])
    px["ret"] = px.groupby("symbol")["close"].pct_change()

    prob = pm.reindex(pd.to_datetime(sorted(px["d"].unique())))
    dprob = prob.diff()

    rows = []
    for sym, s in px.groupby("symbol"):
        s = s.set_index("d")
        # CHANGE screen: return vs dprob
        c = pd.concat([s["ret"], dprob.rename("dp")], axis=1).dropna()
        if len(c) < MIN_OBS:
            continue
        rc = np.corrcoef(c["ret"], c["dp"])[0, 1]
        if not np.isfinite(rc) or abs(rc) >= 1:
            continue
        t_chg = rc * np.sqrt((len(c) - 2) / (1 - rc ** 2))
        # LEVEL screen: prob level vs price level, cointegration residual
        L = pd.concat([s["close"], prob.rename("p")], axis=1).dropna()
        lvl_corr = L["close"].corr(L["p"])
        eg = sm.OLS(L["p"].values, sm.add_constant(L["close"].values)).fit()
        eg_p = _adf_p(eg.resid)
        rows.append((sym, rc, t_chg, lvl_corr, eg_p, len(c)))

    R = pd.DataFrame(rows, columns=["symbol", "chg_corr", "chg_t", "lvl_corr", "lvl_coint_p", "n"])
    R["rank_chg"] = R["chg_t"].rank(ascending=False).astype(int)
    R["rank_lvl_coint"] = R["lvl_coint_p"].rank(ascending=True)   # float; NaN where coint p is NaN
    R.sort_values("chg_t", ascending=False).to_csv(os.path.join(HERE, "systematic_stock_screen.csv"), index=False)

    def fmt(df, cols):
        return df[cols].to_string(index=False, formatters={
            "chg_t": "{:+.2f}".format, "chg_corr": "{:+.2f}".format,
            "lvl_corr": "{:+.2f}".format, "lvl_coint_p": "{:.3f}".format})

    out = [f"SYSTEMATIC SCREEN  window {EST_START}..{EST_END}  (liquid names: {len(R)})", ""]
    out += ["=== CHANGE screen (Method A): return ~ dP(Trump), by t ===",
            "TOP POSITIVE:", fmt(R.sort_values("chg_t", ascending=False).head(12), ["symbol", "chg_t", "chg_corr"]),
            "TOP NEGATIVE:", fmt(R.sort_values("chg_t").head(8), ["symbol", "chg_t", "chg_corr"]), ""]
    out += ["=== LEVEL screen (Method B): price level cointegrates with P(Trump) level ===",
            "(ranked by cointegration residual ADF p -- smaller = price level tracks prob level)",
            fmt(R.sort_values("lvl_coint_p").head(15), ["symbol", "lvl_coint_p", "lvl_corr", "chg_t"]), ""]
    out += ["Where the hand-picked names land:"]
    for tk in OUR_PICKS:
        if tk in R.symbol.values:
            r = R[R.symbol == tk].iloc[0]
            lvl_rk = "n/a" if pd.isna(r["rank_lvl_coint"]) else "%d" % int(r["rank_lvl_coint"])
            out.append("  %-5s change-rank %d/%d (t=%+.2f) | level-coint-rank %s/%d (resid ADF p=%.3f)"
                       % (tk, r["rank_chg"], len(R), r["chg_t"], lvl_rk, len(R), r["lvl_coint_p"]))
    out += ["", "Note: CHANGE screen isolates election sensitivity (differencing kills the",
            "common summer up-trend). LEVEL raw correlation is spurious (co-trending), so",
            "the level screen ranks by cointegration, matching Method B. Validate out of",
            "sample (Oct-Nov) before trusting any single name."]
    txt = "\n".join(out)
    with open(os.path.join(HERE, "systematic_stock_screen.txt"), "w") as f:
        f.write(txt + "\n")
    print(txt)
    print("\nwritten -> systematic_stock_screen.csv, systematic_stock_screen.txt")


if __name__ == "__main__":
    main()
