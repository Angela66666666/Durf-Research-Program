"""
build_daily_panel.py   (attempt2)
================================================================================
Build ONE clean daily panel used by every attempt2 script: adjusted close for
the whole asset universe (11 sector ETFs + the election-driven adds) plus the
Polymarket P(Trump) series, over 2024. One source (yfinance, dividend-adjusted)
and one convention, so estimation (pre-election) and the test window (Oct-Nov)
are consistent.

Universe is edit-here. The election-driven adds default to DJT / COIN / TAN /
GEO (Trump Media, crypto exchange, solar short, private prisons) -- all normal
share prices so a fixed-share dollar basket is well behaved. Double-check /
change this list freely.

INPUT   1. data/polymarket_trump_2024_daily.csv   (date, prob)
OUTPUT  panel_daily.csv     date, <one column per asset>, prob
================================================================================
"""
import os
import pandas as pd
import yfinance as yf

HERE = os.path.dirname(os.path.abspath(__file__))
# Walk up until the folder containing "1. data" is found, so the script runs
# from any depth without hard-coded relative hops.
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "1. data")):
    ROOT = os.path.dirname(ROOT)
DATA = os.path.join(ROOT, "1. data")
PM = os.path.join(DATA, "polymarket_trump_2024_daily.csv")

ETFS = ["VAW", "VCR", "VDC", "VDE", "VFH", "VGT", "VHT", "VIS", "VNQ", "VOX", "VPU"]
ADDS = ["MARA", "COIN", "GEO", "IBKR", "FSLR", "RUN", "DHI", "TAN"]   # systematically-screened compact leaders
ASSETS = ETFS + ADDS

START, END = "2024-01-01", "2024-11-07"


def main():
    px = yf.download(ASSETS, start=START, end=END, auto_adjust=True, progress=False)["Close"]
    px = px[ASSETS]                                    # keep column order
    pm = pd.read_csv(PM, parse_dates=["date"]).set_index("date")["prob"]

    panel = px.join(pm, how="left")                    # prob aligned to trading days
    panel.index.name = "date"
    panel.to_csv(os.path.join(HERE, "panel_daily.csv"))

    print("panel:", panel.index.min().date(), "->", panel.index.max().date(), f"({len(panel)} trading days)")
    print("\nfirst valid date per asset (adjusted close):")
    for a in ASSETS:
        s = panel[a].dropna()
        print(f"  {a:8s} {s.index.min().date()}  n={len(s)}")
    print(f"\n  prob     {panel['prob'].dropna().index.min().date()}  n={panel['prob'].notna().sum()}")
    print("\nwritten -> panel_daily.csv")


if __name__ == "__main__":
    main()
