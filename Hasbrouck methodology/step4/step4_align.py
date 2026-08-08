"""
step4_align.py
================================================================================
STEP 4, PART 2a -- ALIGN THE CALIBRATED BASKET WITH KALSHI
  Puts the market (Kalshi PRES-2024-DJT) and the calibrated basket implied
  probabilities on the same bar grid, so the cointegration / VECM / Hasbrouck
  stage has one aligned pair per plan.

  This is the first place Kalshi enters Step 4. Two facts drive the handling:
    - The ETF basket moves essentially every bar (dense).
    - Kalshi trades sparsely (only ~71% of RTH bars have a trade over the window,
      and only ~46% in the first two weeks).
  So the market must be forward-filled onto the grid, and every bar is flagged
  `market_fresh` = True when a real Kalshi trade fell in that bar, False when the
  value was carried forward. The forward fill uses ALL trades including overnight,
  so a day's first bar reflects the overnight move (matching the basket, whose
  level already includes the overnight gap). Only past trades are carried
  forward, never future -- look-ahead-free.

INPUT   step4_implied_prob.csv                      the calibrated basket grid
        ../prediction-market-analysis/.../trades_*  PRES-2024-DJT trades
OUTPUT  step4_pair.csv   date, ts_et, kalshi_prob, market_fresh, implied_p_<plan>
================================================================================
"""
import os
import sys
import pandas as pd
import duckdb

MODE = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in ("high_frequency", "daily") else "high_frequency"

CONTRACT = "PRES-2024-DJT"
FREQ = "1min"
WIN_START = "2024-10-04"
WIN_END = "2024-11-06"

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))          # repo root (this file lives in Hasbrouck methodology/step4)
IMPLIED = os.path.join(HERE, f"step4_implied_prob_{MODE}.csv")
TRADES_GLOB = os.path.join(ROOT, "prediction-market-analysis", "data", "kalshi", "trades", "trades_*.parquet")

sys.path.insert(0, os.path.join(ROOT, "leadlag", "pipeline"))
from leadlag_common import causal_bars  # noqa: E402


def load_kalshi_bars():
    """1-min causal prob bars over ALL hours (overnight kept), naive ET index."""
    q = f"""
    SELECT created_time AS ts_utc, yes_price / 100.0 AS prob
    FROM   read_parquet('{TRADES_GLOB}')
    WHERE  ticker = '{CONTRACT}'
      AND  (created_time AT TIME ZONE 'America/New_York')::date
             BETWEEN DATE '{WIN_START}' AND DATE '{WIN_END}'
    ORDER  BY ts_utc
    """
    df = duckdb.sql(q).df()
    # UTC -> ET wall clock, drop tz so it matches the naive-ET grid in the CSV
    et = pd.to_datetime(df["ts_utc"], utc=True).dt.tz_convert("US/Eastern").dt.tz_localize(None)
    df = pd.DataFrame({"ts_et": et, "prob": df["prob"].values})
    df["date"] = df["ts_et"].dt.date
    bars = causal_bars(df, "prob", FREQ)          # right-edge median bars, per date, incl. overnight
    return bars.set_index("ts_et")["prob"].sort_index()


def main():
    grid_df = pd.read_csv(IMPLIED, parse_dates=["ts_et"])
    grid = pd.DatetimeIndex(grid_df["ts_et"])     # naive ET

    ks = load_kalshi_bars()
    # value on the grid: last Kalshi bar at or before each grid point (ffill; captures
    # overnight for a day's first/only bar). Never uses a future trade -> look-ahead-free.
    filled = ks.reindex(grid.union(ks.index)).sort_index().ffill().reindex(grid).values
    if MODE == "high_frequency":
        # fresh = a real trade fell in this exact 1-min bar
        fresh = ks.reindex(grid).notna().values
    else:
        # daily: one obs per day; fresh = the contract traded that day (always true here)
        traded_days = set(pd.DatetimeIndex(ks.index).normalize().date)
        fresh = pd.Series(grid).dt.date.isin(traded_days).values

    out = grid_df.copy()
    out.insert(2, "kalshi_prob", filled)
    out.insert(3, "market_fresh", fresh)

    out_csv = os.path.join(HERE, f"step4_pair_{MODE}.csv")
    out.to_csv(out_csv, index=False)

    n = len(out)
    print(f"aligned {n} bars over {out['date'].nunique()} trading days")
    print(f"Kalshi fresh bars: {out['market_fresh'].mean() * 100:.1f}% overall")
    print(f"kalshi_prob range: {out['kalshi_prob'].min():.3f} .. {out['kalshi_prob'].max():.3f}")
    print("written ->", out_csv)


if __name__ == "__main__":
    main()
