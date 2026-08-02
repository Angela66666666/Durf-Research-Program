"""
fetch_polymarket_hf.py   (high frequency basket -- data step)
================================================================================
Download the 1-MINUTE Polymarket P(Trump) series from the same CLOB endpoint and
the same YES token that produced the validated daily series, then VALIDATE it by
resampling to daily and comparing against polymarket_trump_2024_daily.csv.

Why this exists: the daily basket estimates its weights from the daily Polymarket
series. To re-estimate the weights at high frequency (per the advisor), we need
the intraday counterpart. The raw on-chain trade parquet has null timestamps and
no token->market map; the CLOB prices-history API, with a browser User-Agent and
an explicit startTs/endTs range, returns clean 1-minute points and is the same
source the daily series came from -- so it needs no separate reconciliation
beyond the daily check done here.

OUTPUT  polymarket_trump_hf_1min.csv   (ts_utc, prob)   1-minute, UTC
================================================================================
"""
import os
import json
import time
import urllib.request
import datetime as dt
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "1. data")):
    ROOT = os.path.dirname(ROOT)
DAILY_CSV = os.path.join(ROOT, "1. data", "polymarket_trump_2024_daily.csv")
OUT = os.path.join(HERE, "polymarket_trump_hf_1min.csv")

TOKEN = "21742633143463906290569050155826241533067272736897614950488156847949938836455"
# Full span we may need: estimation (Sep) through the end of the test window.
START, END = "2024-09-01", "2024-11-08"
FIDELITY = 1  # minutes


def _epoch(s):
    return int(dt.datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=dt.timezone.utc).timestamp())


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=60))


def fetch():
    # page weekly so no single request is truncated
    rows = []
    lo = _epoch(START)
    hi = _epoch(END)
    step = 7 * 86400
    t = lo
    while t < hi:
        t1 = min(t + step, hi)
        url = (f"https://clob.polymarket.com/prices-history?market={TOKEN}"
               f"&startTs={t}&endTs={t1}&fidelity={FIDELITY}")
        h = _get(url).get("history", [])
        rows += [(p["t"], p["p"]) for p in h]
        print(f"  {dt.datetime.utcfromtimestamp(t):%Y-%m-%d} .. {dt.datetime.utcfromtimestamp(t1):%Y-%m-%d}: {len(h)} pts")
        t = t1
        time.sleep(1.0)
    df = pd.DataFrame(rows, columns=["t", "prob"]).drop_duplicates("t").sort_values("t")
    df["ts_utc"] = pd.to_datetime(df["t"], unit="s", utc=True)
    return df[["ts_utc", "prob"]].reset_index(drop=True)


def validate(hf):
    """Compare against the cached daily CSV. The daily CSV is stamped at exactly
    20:00 ET (verified: sampling the 1-minute series at 20:00 ET reproduces it to
    the fourth decimal), so we sample the 1-minute series at 20:00 ET, not the
    day's last minute -- the latter would pick up election-night after-hours moves
    the 20:00 stamp predates."""
    daily = pd.read_csv(DAILY_CSV, parse_dates=["date"]).set_index("date")["prob"]
    et = hf.set_index("ts_utc")["prob"].tz_convert("US/Eastern")
    at20 = et[(et.index.hour == 20) & (et.index.minute == 0)]
    hf_daily = at20.groupby(at20.index.date).first()
    hf_daily.index = pd.to_datetime(hf_daily.index)
    both = pd.DataFrame({"api_daily": daily, "hf_resampled": hf_daily}).dropna()
    both["diff"] = both["hf_resampled"] - both["api_daily"]
    mae = both["diff"].abs().mean()
    corr = both["api_daily"].corr(both["hf_resampled"])
    print("\n=== VALIDATION vs cached daily CSV ===")
    print(f"  overlapping days     : {len(both)}")
    print(f"  correlation          : {corr:.4f}")
    print(f"  mean |diff|          : {mae:.4f}")
    print(f"  max  |diff|          : {both['diff'].abs().max():.4f}")
    print(both.tail(8).round(4).to_string())
    if corr > 0.99 and mae < 0.01:
        print("  -> PASS: 1-minute series reconciles with the daily series.")
    else:
        print("  -> CHECK: reconciliation weaker than expected; inspect before use.")
    return corr, mae


def main():
    print(f"fetching Polymarket 1-minute P(Trump), {START} .. {END}")
    hf = fetch()
    print(f"total 1-minute points: {len(hf)}   range {hf.ts_utc.min()} .. {hf.ts_utc.max()}")
    hf.to_csv(OUT, index=False)
    validate(hf)
    print("\nwritten ->", OUT)


if __name__ == "__main__":
    main()
