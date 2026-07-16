"""
fetch_and_screen_election_assets.py
================================================================================
Purpose (rework, does NOT touch the existing Step 1-4 code)
  1. Download daily prices for a candidate list of "election-driven" assets that
     could be added to the basket (Prof's suggestion: include names like DJT that
     are more election driven than broad sector ETFs).
  2. Screen each candidate for how election-driven it actually is, by regressing
     its daily return on the daily change in Polymarket P(Trump), over the same
     event window Step 1 uses (2024-06-20..07-31) and over a longer window.
     Reports beta, t, and R^2 so the universe can be pruned on evidence.

  This only gathers data and ranks candidates; it does not build any basket.

INPUT   ../step1_step2/polymarket_trump_2024_daily.csv   (date, prob)
OUTPUT  election_assets_daily.csv    daily close/adj-close for every candidate
        (prints the ranked screen table)
================================================================================
"""
import os
import numpy as np
import pandas as pd
import statsmodels.api as sm
import yfinance as yf

HERE = os.path.dirname(os.path.abspath(__file__))
PM = os.path.join(HERE, "..", "attempt1", "step1_step2", "polymarket_trump_2024_daily.csv")

# Candidate universe. side = expected direction of the election beta.
# "confirmed" = named as a Trump-trade mover in press coverage of the 2024 result;
# "verify"    = commonly cited theme name, kept for the screen to judge.
CANDIDATES = {
    "DJT":     ("Trump Media (Truth Social)",        "long",  "confirmed"),
    "MSTR":    ("MicroStrategy (bitcoin proxy)",     "long",  "confirmed"),
    "COIN":    ("Coinbase (crypto exchange)",        "long",  "confirmed"),
    "HOOD":    ("Robinhood (crypto/retail broker)",  "long",  "confirmed"),
    "XLF":     ("Financials sector (banks)",         "long",  "confirmed"),
    "BTC-USD": ("Bitcoin",                           "long",  "confirmed"),
    "GEO":     ("GEO Group (private prisons)",       "long",  "verify"),
    "CXW":     ("CoreCivic (private prisons)",       "long",  "verify"),
    "RGR":     ("Sturm Ruger (firearms)",            "long",  "verify"),
    "TAN":     ("Solar ETF",                         "short", "verify"),
    "ICLN":    ("Clean energy ETF",                  "short", "verify"),
    "FXI":     ("China large-cap (tariff-exposed)",  "short", "verify"),
}

EVENT_START, EVENT_END = "2024-06-20", "2024-07-31"   # Step 1's identification window
LONG_START,  LONG_END  = "2024-03-27", "2024-11-01"   # DJT listed 2024-03-26


def screen(ret, dprob, lo, hi):
    """OLS of daily return on daily change in P(Trump) over [lo, hi]."""
    d = pd.concat([ret.rename("r"), dprob.rename("dp")], axis=1).dropna()
    d = d[(d.index >= lo) & (d.index <= hi)]
    if len(d) < 5:
        return np.nan, np.nan, np.nan, len(d)
    m = sm.OLS(d["r"], sm.add_constant(d["dp"])).fit()
    return m.params["dp"], m.tvalues["dp"], m.rsquared, len(d)


def main():
    pm = pd.read_csv(PM, parse_dates=["date"]).set_index("date")["prob"]
    dprob = pm.diff()

    tickers = list(CANDIDATES)
    px = yf.download(tickers, start=LONG_START, end="2024-11-07",
                     progress=False, auto_adjust=True)["Close"]
    px.to_csv(os.path.join(HERE, "election_assets_daily.csv"))

    rows = []
    for tk in tickers:
        if tk not in px or px[tk].dropna().empty:
            rows.append((tk, *CANDIDATES[tk], np.nan, np.nan, np.nan, 0, np.nan, np.nan, np.nan, 0))
            continue
        ret = px[tk].pct_change()
        eb, et, er2, en = screen(ret, dprob, EVENT_START, EVENT_END)
        lb, lt, lr2, ln = screen(ret, dprob, LONG_START, LONG_END)
        rows.append((tk, *CANDIDATES[tk], eb, et, er2, en, lb, lt, lr2, ln))

    cols = ["ticker", "name", "side", "status",
            "beta_evt", "t_evt", "R2_evt", "n_evt",
            "beta_long", "t_long", "R2_long", "n_long"]
    res = pd.DataFrame(rows, columns=cols).sort_values("R2_long", ascending=False)

    pd.set_option("display.width", 200, "display.max_columns", 20)
    print("\nELECTION-DRIVEN CANDIDATE SCREEN (return regressed on change in Polymarket P(Trump))")
    print("event window = %s..%s   long window = %s..%s\n" % (EVENT_START, EVENT_END, LONG_START, LONG_END))
    print(res.to_string(index=False,
          formatters={"beta_evt": "{:+.3f}".format, "t_evt": "{:+.2f}".format, "R2_evt": "{:.3f}".format,
                      "beta_long": "{:+.3f}".format, "t_long": "{:+.2f}".format, "R2_long": "{:.3f}".format}))
    print("\nsaved prices -> election_assets_daily.csv")


if __name__ == "__main__":
    main()
