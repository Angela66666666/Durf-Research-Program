"""
build_panels.py   (high frequency basket -- data step)
================================================================================
Build BOTH 1-minute panels this folder needs, self-contained (no dependency on
the sibling folder), for the 20-asset basket = 11 sector ETFs + 8 election adds
+ FXI. FXI (China large-caps) is an a-priori election-sensitive name -- a Trump
win means tariffs, which move Chinese equities -- and adding it lets the basket
cointegrate with Kalshi at 1 minute at the 5% level (Engle-Granger), which the
19-asset basket only reaches at 10%.

  estim_panel_1min.csv   Sep 3 - Oct 3   20 assets + Polymarket P(Trump)
                         -> used to ESTIMATE the weights (pre-test, out of sample)
  test_panel_1min.csv    Oct 4 - Nov 6   20 assets + Kalshi PRES-2024-DJT
                         -> used to TEST (cointegration gate + price discovery)

Same sources, RTH filter (09:30-16:00 ET) and within-day forward-fill for both,
so estimation and test differ only in venue (Polymarket vs Kalshi) and period.

INPUT   1. data/etf_hf/*_hf.parquet          11 sector ETFs (UTC NBBO ticks)
        1. data/etf/nbbo_addtl_tics.parquet  the 8 adds + FXI (ET NBBO ticks)
        1. data/kalshi/kalshi/trades/*        Kalshi PRES-2024-DJT
        polymarket_trump_hf_1min.csv          from fetch_polymarket_hf.py
OUTPUT  estim_panel_1min.csv, test_panel_1min.csv
================================================================================
"""
import os
import glob
import numpy as np
import pandas as pd
import duckdb

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "1. data")):
    ROOT = os.path.dirname(ROOT)
DATA = os.path.join(ROOT, "1. data")
ETF_GLOB = os.path.join(DATA, "etf_hf", "*_hf.parquet")
ADD_FILE = os.path.join(DATA, "etf", "nbbo_addtl_tics.parquet")
TRADES_GLOB = os.path.join(DATA, "kalshi", "kalshi", "trades", "trades_*.parquet")
PM_CSV = os.path.join(HERE, "polymarket_trump_hf_1min.csv")

ETFS = ["VAW", "VCR", "VDC", "VDE", "VFH", "VGT", "VHT", "VIS", "VNQ", "VOX", "VPU"]
ADDS = ["MARA", "COIN", "GEO", "IBKR", "FSLR", "RUN", "DHI", "TAN", "FXI"]   # +FXI hedge
COLS = ETFS + ADDS

ESTIM_START, ESTIM_END = "2024-09-03", "2024-10-03"      # pre-test, Polymarket
TEST_START, TEST_END = "2024-10-04", "2024-11-06"        # test, Kalshi
RTH_OPEN, RTH_CLOSE = "09:30:00", "16:00:00"


def _etf_files():
    return [f for f in glob.glob(ETF_GLOB) if not os.path.basename(f).startswith("._")]


def _etf_minutes(con, d0, d1):
    files = "[" + ", ".join("'%s'" % f for f in _etf_files()) + "]"
    q = f"""
    WITH t AS (
      SELECT (timestamp_utc AT TIME ZONE 'UTC') AT TIME ZONE 'America/New_York' AS et,
             regexp_extract(filename, '([A-Z]+)_hf\\.parquet', 1) AS sym, mid, timestamp_utc
      FROM read_parquet({files}, filename=true) WHERE mid IS NOT NULL)
    SELECT date_trunc('minute', et) AS m, sym, last(mid ORDER BY timestamp_utc) AS px
    FROM t WHERE et::date BETWEEN DATE '{d0}' AND DATE '{d1}'
      AND et::time BETWEEN TIME '{RTH_OPEN}' AND TIME '{RTH_CLOSE}' GROUP BY m, sym
    """
    return con.sql(q).df()


def _add_minutes(con, d0, d1):
    syms = ", ".join("'%s'" % s for s in ADDS)
    q = f"""
    WITH t AS (
      SELECT CAST(DATE AS DATE) + TIME_M AS et, SYM_ROOT AS sym, (BEST_BID + BEST_ASK) / 2.0 AS mid
      FROM read_parquet('{ADD_FILE}')
      WHERE SYM_ROOT IN ({syms}) AND BEST_BID > 0 AND BEST_ASK > 0
        AND CAST(DATE AS DATE) BETWEEN DATE '{d0}' AND DATE '{d1}'
        AND TIME_M BETWEEN TIME '{RTH_OPEN}' AND TIME '{RTH_CLOSE}')
    SELECT date_trunc('minute', et) AS m, sym, last(mid ORDER BY et) AS px FROM t GROUP BY m, sym
    """
    return con.sql(q).df()


def _kalshi_minutes(con, d0, d1):
    q = f"""
    WITH t AS (SELECT (created_time AT TIME ZONE 'America/New_York') AS et, yes_price
      FROM read_parquet('{TRADES_GLOB}') WHERE ticker = 'PRES-2024-DJT')
    SELECT date_trunc('minute', et) AS m, last(yes_price ORDER BY et) / 100.0 AS kalshi
    FROM t WHERE et::date BETWEEN DATE '{d0}' AND DATE '{d1}'
      AND et::time BETWEEN TIME '{RTH_OPEN}' AND TIME '{RTH_CLOSE}' GROUP BY m
    """
    return con.sql(q).df()


def _polymarket_minutes(d0, d1):
    pm = pd.read_csv(PM_CSV, parse_dates=["ts_utc"])
    et = pm.set_index("ts_utc")["prob"].tz_convert("US/Eastern")
    et = et[(et.index.date >= pd.Timestamp(d0).date()) & (et.index.date <= pd.Timestamp(d1).date())]
    tt = et.index.time
    et = et[(tt >= pd.Timestamp(RTH_OPEN).time()) & (tt <= pd.Timestamp(RTH_CLOSE).time())]
    m = et.index.tz_localize(None).floor("min")
    return pd.Series(et.values, index=m).groupby(level=0).last().rename("prob")


def _assemble(con, d0, d1, target_name, target_series):
    etf = _etf_minutes(con, d0, d1)
    add = _add_minutes(con, d0, d1)
    long = pd.concat([etf, add], ignore_index=True)
    long["m"] = pd.to_datetime(long["m"])
    wide = long.pivot(index="m", columns="sym", values="px").sort_index()
    panel = wide.join(target_series.rename(target_name), how="outer").sort_index()

    days = sorted(pd.Series(wide.index.date).unique())
    grid = pd.DatetimeIndex(np.concatenate(
        [pd.date_range(f"{d} {RTH_OPEN}", f"{d} {RTH_CLOSE}", freq="1min").values for d in days]))
    panel = panel.reindex(grid).groupby(lambda x: x.date(), group_keys=False).ffill()

    missing = [c for c in COLS if c not in panel.columns]
    if missing:
        raise SystemExit("missing assets: %s" % missing)
    complete = panel[COLS + [target_name]].dropna()
    complete.index.name = "minute"
    return complete, len(days)


def main():
    con = duckdb.connect()
    print("building 1-minute panels for the 20-asset basket (11 ETF + 8 adds + FXI)\n")

    pm = _polymarket_minutes(ESTIM_START, ESTIM_END)
    estim, ndE = _assemble(con, ESTIM_START, ESTIM_END, "prob", pm)
    estim.to_csv(os.path.join(HERE, "estim_panel_1min.csv"))
    print("  estim_panel_1min.csv : %5d complete minutes, %d days (%s..%s, Polymarket)"
          % (len(estim), ndE, ESTIM_START, ESTIM_END))

    kal = _kalshi_minutes(con, TEST_START, TEST_END).set_index("m")["kalshi"]
    kal.index = pd.to_datetime(kal.index)
    test, ndT = _assemble(con, TEST_START, TEST_END, "kalshi", kal)
    test.to_csv(os.path.join(HERE, "test_panel_1min.csv"))
    print("  test_panel_1min.csv  : %5d complete minutes, %d days (%s..%s, Kalshi)"
          % (len(test), ndT, TEST_START, TEST_END))


if __name__ == "__main__":
    main()
