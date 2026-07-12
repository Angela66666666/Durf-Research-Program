"""
step3_build_basket.py
================================================================================
WHAT THIS FILE DOES  (Step 3 only -- build the basket level series)
  Steps 1-2 produced three weight vectors (plans A/B/C) that turn the eleven
  sector ETFs into one election-factor basket. Step 3 turns each weight vector
  into an intraday LEVEL series:

      bar return   b_t = w' r_t          (r_t = the 11 ETF log-returns over the bar)
      level        B_t = cumulative sum of b_t

  Nothing else. The level is in return units, NOT a probability. Kalshi is not
  touched here: putting B_t on a [0,1] probability scale, aligning it with the
  market, and any cointegration / VECM / Hasbrouck inference all belong to Step 4.

CONVENTIONS (reused from the pipeline so the series is directly comparable)
  - causal_bars(): right-edge median 1-min bars, look-ahead-free.
  - market hours: 09:30-16:00 ET only.
  - returns are bar-to-bar and INCLUDE the overnight close-to-open gap as the
    first bar return of each day, so B_t is the continuous value of holding the
    basket. This matters because the election outcome move happens overnight
    (Nov 5 close -> Nov 6 open); a within-day-only level would not see it, while
    Step 4's two-point probability calibration anchors on election night. The gap
    uses only the prior close and the current open, so it stays look-ahead-free.
  - complete case across all eleven ETFs, so every bar carries a full basket.

INPUTS
  etf_election_beta_polymarket.csv          the three weight vectors
  ../leadlag/etf_hf/<TICKER>_hf.parquet     1-min ETF mids
  ../leadlag/pipeline/leadlag_common.py     causal_bars() bar builder

OUTPUTS (written next to this file)
  step3_basket_levels.csv        one row per bar: date, ts_et, and one level per plan
  step3_construction_summary.txt what was built (bars, days, terminal levels)
================================================================================
"""
import os
import sys
import numpy as np
import pandas as pd

# ---------------- configuration ----------------
# MODE = "high_frequency" -> 1-min bars (intraday).
# MODE = "daily"          -> one close-to-close observation per trading day, which
#                            keeps the overnight gaps (where the election signal is)
#                            and drops the intraday minute noise.
MODE = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in ("high_frequency", "daily") else "high_frequency"

FREQ = "1min"                    # bar size used to build both; daily then collapses to the close
WIN_START = "2024-10-04"
WIN_END = "2024-11-06"

RTH_START = (9, 30)
RTH_END = (16, 0)

ETFS = ["VAW", "VCR", "VDC", "VDE", "VFH", "VGT", "VHT", "VIS", "VNQ", "VOX", "VPU"]
PLANS = {
    "A_sign_equal":    "weight_plan_a_sign_equal",
    "B_beta_weighted": "weight_plan_b_beta_weighted",
    "C_min_variance":  "weight_plan_c_min_variance",
}

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))          # repo root (this file lives in Hasbrouck methodology/step3)
WEIGHTS_CSV = os.path.join(HERE, "..", "step1_step2", "etf_election_beta_polymarket.csv")
ETF_HF_DIR = os.path.join(ROOT, "leadlag", "etf_hf")

sys.path.insert(0, os.path.join(ROOT, "leadlag", "pipeline"))
from leadlag_common import causal_bars  # noqa: E402


def load_weights():
    df = pd.read_csv(WEIGHTS_CSV).set_index("ticker").reindex(ETFS)
    if df.isna().any().any():
        raise ValueError("weights CSV is missing one of the eleven ETFs")
    return df


def _to_et_rth(df, tcol):
    """Naive-UTC timestamps -> ET, keep only 09:30-16:00 ET on the window. Adds the
    ts_et/date columns that causal_bars() expects."""
    et = pd.to_datetime(df[tcol]).dt.tz_localize("UTC").dt.tz_convert("US/Eastern")
    df = df.assign(ts_et=et)
    lo = pd.Timestamp(WIN_START, tz="US/Eastern")
    hi = pd.Timestamp(WIN_END, tz="US/Eastern") + pd.Timedelta(days=1)
    df = df[(df["ts_et"] >= lo) & (df["ts_et"] < hi)]
    h, m = df["ts_et"].dt.hour, df["ts_et"].dt.minute
    after_open = (h > RTH_START[0]) | ((h == RTH_START[0]) & (m >= RTH_START[1]))
    before_close = (h < RTH_END[0]) | ((h == RTH_END[0]) & (m == 0))
    df = df[after_open & before_close].copy()
    df["date"] = df["ts_et"].dt.date
    return df


def load_etf_bars():
    """Wide frame of per-ETF bar mids indexed by ts_et, complete case across all
    eleven ETFs so every bar carries a full basket."""
    cols = {}
    for tk in ETFS:
        raw = pd.read_parquet(os.path.join(ETF_HF_DIR, f"{tk}_hf.parquet"),
                              columns=["timestamp_utc", "mid"])
        bars = causal_bars(_to_et_rth(raw, "timestamp_utc"), "mid", FREQ)
        cols[tk] = bars.set_index("ts_et")["mid"]
        print(f"  {tk}: {len(bars)} bars")
    wide = pd.DataFrame(cols).dropna()
    wide["date"] = wide.index.normalize().date
    print(f"  common bars (all 11 ETFs present): {len(wide)}")
    return wide


def build_levels(etf_wide, W):
    """Continuous cumulative basket level B_t per plan. Bar-to-bar log returns are
    taken over the whole time-sorted series, so the first bar of each day carries
    the overnight close-to-open gap; B_t is then one continuous buy-and-hold NAV
    starting at 0."""
    g = etf_wide.sort_index()
    dates = g["date"].values
    mids = g.drop(columns="date")
    dret = np.diff(np.log(mids.values), axis=0)           # bar-to-bar, incl. overnight gap
    out = pd.DataFrame(index=mids.index)
    out["date"] = dates
    for plan, wcol in PLANS.items():
        bret = dret @ W[wcol].values
        out[f"B_{plan}"] = np.concatenate([[0.0], np.cumsum(bret)])
    return out


def main():
    print(f"MODE = {MODE}")
    print("loading Step-2 weights ...")
    W = load_weights()
    print("building ETF 1-min bars ...")
    etf_wide = load_etf_bars()
    if MODE == "daily":
        # collapse to one close-to-close observation per day: keep each day's last bar
        # (the 16:00 close). build_levels then differences close-to-close, so each daily
        # return spans one overnight + one trading day, and the intraday minute noise is
        # gone. This is the frequency where the election signal actually lives.
        etf_wide = etf_wide.groupby("date").tail(1)
        print(f"  collapsed to daily closes: {len(etf_wide)} days")
    print("cumulating basket levels ...")
    levels = build_levels(etf_wide, W)

    out = levels.reset_index().rename(columns={"index": "ts_et"})
    # write ts_et as a naive ET wall-clock string (drop the -04:00/-05:00 offset) so
    # a spreadsheet/CSV viewer does not silently convert it to the reader's local
    # timezone -- keeping it on the same ET calendar day as the `date` column.
    out["ts_et"] = out["ts_et"].dt.tz_localize(None)
    cols = ["date", "ts_et"] + [f"B_{p}" for p in PLANS]
    out = out[cols]
    out_csv = os.path.join(HERE, f"step3_basket_levels_{MODE}.csv")
    out.to_csv(out_csv, index=False)

    n_bars = len(out)
    n_days = out["date"].nunique()
    grain = "1-min bars" if MODE == "high_frequency" else "daily close-to-close"
    detail = ("Each B is the cumulative basket return w'(ETF log-returns), bar to bar,\n"
              "including the overnight close-to-open gap (a continuous buy-and-hold NAV).\n"
              if MODE == "high_frequency" else
              "Each B is the cumulative basket return w'(ETF log-returns), one observation\n"
              "per trading day (close-to-close), so each step spans one overnight plus one\n"
              "trading day; intraday minute noise is dropped.\n")
    summary = (
        f"STEP 3 [{MODE}] - ETF BASKET LEVEL SERIES (construction only, no probability)\n"
        + "=" * 78 + "\n"
        f"window        = {WIN_START} to {WIN_END}   (RTH 09:30-16:00 ET, {grain})\n"
        f"observations  = {n_bars}   over {n_days} trading days\n"
        f"basket plans  = {', '.join(PLANS)}\n\n"
        + detail +
        "The level is in return units; Step 4 calibrates it onto a [0,1] probability\n"
        "scale and aligns it with Kalshi.\n\n"
        "Terminal level B (window end minus window start):\n"
        + "".join(f"  plan {p:16s} {out[f'B_{p}'].iloc[-1] - out[f'B_{p}'].iloc[0]:+.4f}\n"
                 for p in PLANS)
    )
    with open(os.path.join(HERE, f"step3_construction_summary_{MODE}.txt"), "w") as f:
        f.write(summary)

    print("\n" + summary)
    print("written ->", out_csv)


if __name__ == "__main__":
    main()
