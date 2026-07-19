"""
Convert raw TAQ NBBO parquet files to clean high-frequency ETF quote data.

Input:  ../taq_vgd_etfs/SYM_ROOT=<ETF>/*.parquet
        Columns: DATE (SAS days since 1960-01-01), TIME_M (seconds since midnight ET),
                 BEST_BID, BEST_ASK

Output: etf_hf/<ETF>_hf.parquet
        Columns: timestamp_utc, best_bid, best_ask, mid

Transformations:
  - DATE + TIME_M → tz-aware UTC timestamp (via America/New_York localization)
  - Filter to regular NYSE trading hours: 09:30–16:00 ET
  - mid = (best_bid + best_ask) / 2
  - Drop rows where both bid and ask are NaN
"""

from pathlib import Path
import pandas as pd

SAS_EPOCH = pd.Timestamp("1960-01-01")

# NYSE regular session: 9:30 AM – 4:00 PM ET (in seconds since midnight)
MARKET_OPEN_SEC  = 9 * 3600 + 30 * 60   # 34200
MARKET_CLOSE_SEC = 16 * 3600             # 57600

HERE    = Path(__file__).parent
TAQ_DIR = HERE / ".." / "taq_vgd_etfs"
OUT_DIR = HERE / "etf_hf"
OUT_DIR.mkdir(exist_ok=True)

etf_dirs = sorted(TAQ_DIR.glob("SYM_ROOT=*"))
print(f"Found {len(etf_dirs)} ETFs in {TAQ_DIR.resolve()}\n")

for etf_dir in etf_dirs:
    etf = etf_dir.name.split("=")[1]
    files = sorted(etf_dir.glob("*.parquet"))

    chunks = [pd.read_parquet(f, columns=["DATE", "TIME_M", "BEST_BID", "BEST_ASK"])
              for f in files]
    df = pd.concat(chunks, ignore_index=True)

    # --- filter to market hours first (TIME_M in seconds) ---
    df = df[(df["TIME_M"] >= MARKET_OPEN_SEC) & (df["TIME_M"] <= MARKET_CLOSE_SEC)]

    # --- build naive ET datetime: date-part + time-part ---
    date_part = SAS_EPOCH + pd.to_timedelta(df["DATE"].astype(int), unit="D")
    time_part = pd.to_timedelta(df["TIME_M"], unit="s")
    ts_naive  = date_part.values + time_part.values

    ts_et = pd.DatetimeIndex(ts_naive).tz_localize(
        "America/New_York",
        ambiguous="NaT",   # clocks fall back Nov 3 2024; ambiguous ticks → NaT
        nonexistent="NaT",
    )
    ts_utc = ts_et.tz_convert("UTC")

    df = df.copy()
    df["timestamp_utc"] = ts_utc.values

    # --- mid price and cleanup ---
    df["mid"] = (df["BEST_BID"] + df["BEST_ASK"]) / 2
    df = df.rename(columns={"BEST_BID": "best_bid", "BEST_ASK": "best_ask"})

    result = (
        df[["timestamp_utc", "best_bid", "best_ask", "mid"]]
        .dropna(subset=["timestamp_utc"])
        .dropna(subset=["best_bid", "best_ask"], how="all")
        .sort_values("timestamp_utc")
        .reset_index(drop=True)
    )

    out_path = OUT_DIR / f"{etf}_hf.parquet"
    result.to_parquet(out_path, index=False)

    date_min = pd.Timestamp(result["timestamp_utc"].min()).date()
    date_max = pd.Timestamp(result["timestamp_utc"].max()).date()
    print(f"{etf}: {len(result):>9,} rows  |  {date_min} → {date_max}  →  {out_path.name}")

print(f"\nDone. Output in: {OUT_DIR.resolve()}")
