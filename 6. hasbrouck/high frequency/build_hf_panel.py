"""
build_hf_panel.py   (attempt2 -- STEP 4 groundwork)
================================================================================
Build ONE aligned 1-MINUTE panel for the high-frequency Hasbrouck step: the 11
sector ETFs, the 8 election-driven adds, and the Kalshi contract, all on a
single New-York-time minute grid over the Oct-Nov test window.

Why this file exists: the daily pair has only 24 observations, which is far too
thin for a VECM / information share (the daily run gives an unstable, sometimes
degenerate price-discovery direction). At 1-minute frequency the same window
yields ~9,000 observations, which is what the Hasbrouck machinery needs.

THREE SOURCES, THREE DIFFERENT TIME CONVENTIONS -- the whole point of this file
is to reconcile them:

  ETFs    1. data/etf_hf/<SYM>_hf.parquet   NBBO ticks, column `timestamp_utc`
                                            (UTC)   -> converted to ET here
  stocks  1. data/etf/nbbo_addtl_tics.parquet  NBBO ticks, DATE (timestamp) +
                                            TIME_M (time), already ET
  Kalshi  .../kalshi/trades/trades_*.parquet  trades, `created_time` (UTC-ish
                                            timestamptz) -> converted to ET

Conversions use DuckDB's `AT TIME ZONE 'America/New_York'` rather than a fixed
offset, because the test window straddles the 2024-11-03 DST change (EDT -> EST);
a hard-coded -4h or -5h would misalign one side by an hour after that date.

DESIGN CHOICES, stated so they are reviewable:
  - REGULAR HOURS ONLY (09:30-16:00 ET). Kalshi trades around the clock while
    the ETFs are closed; comparing them on a 24h clock would leave the equity
    side frozen while Kalshi keeps moving, which manufactures a spurious
    "Kalshi leads" result. Restricting to the hours when BOTH sides are live is
    the same logic as sampling the daily series at the 16:00 ET close.
  - MID PRICE, not trade price, on the equity side: (bid+ask)/2, and only where
    BOTH sides are present (the raw NBBO feed contains one-sided rows).
  - Bar = LAST observation within each minute (not mean), so the panel is a
    snapshot of the prevailing quote at each minute mark.
  - Gaps are forward-filled WITHIN a trading day only, never across the
    overnight boundary, so no overnight jump is smeared into the next session.

INPUT   1. data/etf_hf/*_hf.parquet
        1. data/etf/nbbo_addtl_tics.parquet
        1. data/kalshi/kalshi/trades/trades_*.parquet
OUTPUT  hf_panel_1min.csv    minute, <one column per asset>, kalshi
================================================================================
"""
import os
import numpy as np
import pandas as pd
import duckdb

HERE = os.path.dirname(os.path.abspath(__file__))
# Walk up until the folder containing "1. data" is found, so the script runs
# from any depth without hard-coded relative hops.
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "1. data")):
    ROOT = os.path.dirname(ROOT)
DATA = os.path.join(ROOT, "1. data")

ETF_GLOB = os.path.join(DATA, "etf_hf", "*_hf.parquet")
ADD_FILE = os.path.join(DATA, "etf", "nbbo_addtl_tics.parquet")
TRADES_GLOB = os.path.join(DATA, "kalshi", "kalshi", "trades", "trades_*.parquet")
OUT = os.path.join(HERE, "hf_panel_1min.csv")

ETFS = ["VAW", "VCR", "VDC", "VDE", "VFH", "VGT", "VHT", "VIS", "VNQ", "VOX", "VPU"]
ADDS = ["MARA", "COIN", "GEO", "IBKR", "FSLR", "RUN", "DHI", "TAN"]
CONTRACT = "PRES-2024-DJT"

# Same test window as the daily Method B, so daily and 1-min results are
# directly comparable. The adds' HF data starts 2024-09-03, which is after the
# Jun-Sep weight-estimation window -- fine, because the weights are estimated on
# DAILY Polymarket data and only APPLIED here.
TEST_START, TEST_END = "2024-10-04", "2024-11-06"
RTH_OPEN, RTH_CLOSE = "09:30:00", "16:00:00"


def etf_minutes(con):
    """11 sector ETFs: UTC ticks -> ET minute bars of the last mid."""
    q = f"""
    WITH t AS (
      SELECT
        (timestamp_utc AT TIME ZONE 'UTC') AT TIME ZONE 'America/New_York' AS et,
        regexp_extract(filename, '([A-Z]+)_hf\\.parquet', 1) AS sym,
        mid, timestamp_utc
      FROM read_parquet('{ETF_GLOB}', filename=true)
      WHERE mid IS NOT NULL
    )
    SELECT date_trunc('minute', et) AS m, sym,
           last(mid ORDER BY timestamp_utc) AS px
    FROM t
    WHERE et::date BETWEEN DATE '{TEST_START}' AND DATE '{TEST_END}'
      AND et::time BETWEEN TIME '{RTH_OPEN}' AND TIME '{RTH_CLOSE}'
    GROUP BY m, sym
    """
    return con.sql(q).df()


def add_minutes(con):
    """8 election-driven adds: ET ticks -> minute bars of the last two-sided mid."""
    syms = ", ".join("'%s'" % s for s in ADDS)
    q = f"""
    WITH t AS (
      SELECT CAST(DATE AS DATE) + TIME_M AS et, SYM_ROOT AS sym,
             (BEST_BID + BEST_ASK) / 2.0 AS mid, TIME_M
      FROM read_parquet('{ADD_FILE}')
      WHERE SYM_ROOT IN ({syms})
        AND BEST_BID IS NOT NULL AND BEST_ASK IS NOT NULL
        AND BEST_BID > 0 AND BEST_ASK > 0
        AND CAST(DATE AS DATE) BETWEEN DATE '{TEST_START}' AND DATE '{TEST_END}'
        AND TIME_M BETWEEN TIME '{RTH_OPEN}' AND TIME '{RTH_CLOSE}'
    )
    SELECT date_trunc('minute', et) AS m, sym, last(mid ORDER BY et) AS px
    FROM t GROUP BY m, sym
    """
    return con.sql(q).df()


def kalshi_minutes(con):
    """Kalshi contract: trades -> minute bars of the last traded probability."""
    q = f"""
    WITH t AS (
      SELECT (created_time AT TIME ZONE 'America/New_York') AS et, yes_price
      FROM read_parquet('{TRADES_GLOB}')
      WHERE ticker = '{CONTRACT}'
    )
    SELECT date_trunc('minute', et) AS m,
           last(yes_price ORDER BY et) / 100.0 AS kalshi
    FROM t
    WHERE et::date BETWEEN DATE '{TEST_START}' AND DATE '{TEST_END}'
      AND et::time BETWEEN TIME '{RTH_OPEN}' AND TIME '{RTH_CLOSE}'
    GROUP BY m
    """
    return con.sql(q).df()


def main():
    con = duckdb.connect()
    print("reading high-frequency sources (this scans a few GB, ~1 min)...\n")

    etf = etf_minutes(con)
    add = add_minutes(con)
    kal = kalshi_minutes(con)
    print("  ETF  minute-bars: %8d rows, %d symbols" % (len(etf), etf["sym"].nunique()))
    print("  add  minute-bars: %8d rows, %d symbols" % (len(add), add["sym"].nunique()))
    print("  Kalshi minute-bars: %6d rows" % len(kal))

    # ---- long -> wide, on one shared minute index -------------------------
    long = pd.concat([etf, add], ignore_index=True)
    long["m"] = pd.to_datetime(long["m"])
    wide = long.pivot(index="m", columns="sym", values="px").sort_index()

    kal["m"] = pd.to_datetime(kal["m"])
    panel = wide.join(kal.set_index("m")["kalshi"], how="outer").sort_index()

    # ---- reindex onto the complete RTH minute grid ------------------------
    # Build the grid from the trading days actually present in the ETF data, so
    # market holidays are excluded automatically rather than hard-coded.
    days = sorted(pd.Series(wide.index.date).unique())
    grid = []
    for d in days:
        grid.append(pd.date_range(f"{d} {RTH_OPEN}", f"{d} {RTH_CLOSE}", freq="1min"))
    grid = pd.DatetimeIndex(np.concatenate([g.values for g in grid]))
    panel = panel.reindex(grid)

    # ---- forward-fill inside each trading day only ------------------------
    # A quote that has not refreshed this minute is still the prevailing price,
    # so filling within the session is correct; filling ACROSS the overnight
    # break would carry a stale price through a gap where real news arrived.
    panel = panel.groupby(panel.index.date, group_keys=False).ffill()

    cols = ETFS + ADDS
    missing = [c for c in cols if c not in panel.columns]
    if missing:
        raise SystemExit("missing assets in HF sources: %s" % missing)
    panel = panel[cols + ["kalshi"]]

    complete = panel.dropna()
    print("\n  grid minutes            : %6d  (%d trading days)" % (len(panel), len(days)))
    print("  minutes with ALL assets : %6d  (%.1f%% of grid)"
          % (len(complete), 100.0 * len(complete) / len(panel)))

    print("\n  per-asset coverage on the grid:")
    for c in cols + ["kalshi"]:
        n = panel[c].notna().sum()
        print("    %-8s %6d  (%.1f%%)" % (c, n, 100.0 * n / len(panel)))

    complete.index.name = "minute"
    complete.to_csv(OUT)
    print("\n  first minute: %s   last minute: %s" % (complete.index[0], complete.index[-1]))
    print("written -> hf_panel_1min.csv  (%d rows x %d cols)" % complete.shape)


if __name__ == "__main__":
    main()
