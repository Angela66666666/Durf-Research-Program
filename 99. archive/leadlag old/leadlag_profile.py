"""
Event-driven lead-lag profile: dense second-level impulse response.

Same event-driven structure as leadlag_event.py, but tests every 5 seconds
from 5 to 600 s, giving a full profile of β_k vs k (impulse response function).

For each Kalshi trade at time t, two directions:
  (A) Kalshi leads ETF : regress etf_return(t → t+k)   on prob_change(t)
  (B) ETF leads Kalshi : regress etf_return(t-k → t)   on prob_change(t)
      where significant β means prior ETF move predicts this Kalshi trade

Output: leadlag/leadlag_profile_results.csv
        one row per (pair, direction, horizon_sec)
"""

import duckdb
import pandas as pd
import numpy as np
import statsmodels.api as sm
from pathlib import Path
from typing import Optional

HERE          = Path(__file__).parent
CACHE_PATH    = HERE / "kalshi_hf_cache.parquet"
ETF_HF_DIR    = HERE / "etf_hf"
SIG_PAIRS_CSV = HERE / ".." / "regression" / "significant_pairs.csv"
OUT_CSV       = HERE / "leadlag_profile_results.csv"

# Dense horizons: every 5 s from 5 → 600 s (120 points per direction)
HORIZONS_SEC = list(range(5, 605, 5))
MIN_EVENTS   = 10
MAX_GAP_SEC  = 120

con = duckdb.connect()
sig = pd.read_csv(SIG_PAIRS_CSV)


def load_kalshi_trades(ticker: str, date_start: str, date_end: str) -> pd.DataFrame:
    q = f"""
    SELECT
        (created_time AT TIME ZONE 'UTC')::TIMESTAMP AS ts_utc,
        yes_price
    FROM read_parquet('{CACHE_PATH}')
    WHERE ticker       = '{ticker}'
      AND created_time >= TIMESTAMPTZ '{date_start} 00:00:00+00'
      AND created_time <= TIMESTAMPTZ '{date_end} 23:59:59+00'
    ORDER BY 1
    """
    df = con.execute(q).df()
    df["ts_utc"]      = pd.to_datetime(df["ts_utc"])
    df["prob"]        = df["yes_price"] / 100.0
    df["prob_change"] = df["prob"].diff()
    return df.dropna(subset=["prob_change"]).reset_index(drop=True)


def load_etf_ticks(etf: str, date_start: str, date_end: str) -> pd.DataFrame:
    etf_path = str(ETF_HF_DIR / f"{etf}_hf.parquet")
    q = f"""
    SELECT timestamp_utc AS ts_utc, mid
    FROM   read_parquet('{etf_path}')
    WHERE  timestamp_utc >= TIMESTAMP '{date_start} 00:00:00'
      AND  timestamp_utc <= TIMESTAMP '{date_end} 23:59:59'
    ORDER BY 1
    """
    df = con.execute(q).df()
    df["ts_utc"] = pd.to_datetime(df["ts_utc"])
    return df.dropna(subset=["mid"]).reset_index(drop=True)


def lookup_etf_mid(etf_ns: np.ndarray, etf_mid: np.ndarray,
                   query_ns: np.ndarray) -> np.ndarray:
    max_gap_ns = MAX_GAP_SEC * 1_000_000_000
    idx    = np.searchsorted(etf_ns, query_ns, side="right") - 1
    result = np.full(len(query_ns), np.nan)
    valid  = idx >= 0
    vi     = np.where(valid)[0]
    gaps   = query_ns[vi] - etf_ns[idx[vi]]
    close  = gaps <= max_gap_ns
    result[vi[close]] = etf_mid[idx[vi[close]]]
    return result


def ols_beta(y: np.ndarray, x: np.ndarray) -> Optional[dict]:
    df = pd.DataFrame({"y": y, "x": x}).replace([np.inf, -np.inf], np.nan).dropna()
    if len(df) < MIN_EVENTS or df["x"].nunique() < 2:
        return None
    m = sm.OLS(df["y"], sm.add_constant(df["x"])).fit()
    return {
        "n_events":  len(df),
        "coef":      m.params["x"],
        "t_stat":    m.tvalues["x"],
        "p_value":   m.pvalues["x"],
        "r_squared": m.rsquared,
    }


# ── main loop ──────────────────────────────────────────────────────────────────
rows = []

for i, pair in sig.iterrows():
    ticker     = pair["contract_ticker"]
    etf        = pair["etf"]
    date_start = str(pair["date_start"])
    date_end   = str(pair["date_end"])

    print(f"[{i+1}/{len(sig)}] {ticker} × {etf}", end="  ")

    kalshi    = load_kalshi_trades(ticker, date_start, date_end)
    etf_ticks = load_etf_ticks(etf, date_start, date_end)

    if len(kalshi) < MIN_EVENTS or etf_ticks.empty:
        print(f"skipped ({len(kalshi)} trades)")
        continue

    print(f"{len(kalshi)} trades, {len(etf_ticks):,} ETF ticks")

    etf_ns   = etf_ticks["ts_utc"].astype("datetime64[ns]").astype("int64").values
    etf_mid  = etf_ticks["mid"].values
    trade_ns = kalshi["ts_utc"].astype("datetime64[ns]").astype("int64").values
    prob_chg = kalshi["prob_change"].values

    etf_at_t = lookup_etf_mid(etf_ns, etf_mid, trade_ns)

    for delta_sec in HORIZONS_SEC:
        delta_ns = int(delta_sec * 1_000_000_000)

        # Direction A: Kalshi leads ETF
        etf_after        = lookup_etf_mid(etf_ns, etf_mid, trade_ns + delta_ns)
        etf_return_after = (etf_after - etf_at_t) / etf_at_t
        res_a = ols_beta(etf_return_after, prob_chg)
        if res_a:
            rows.append({
                "contract_ticker":  ticker,
                "etf":              etf,
                "direction":        "kalshi_leads_etf",
                "horizon_sec":      delta_sec,
                "n_kalshi_trades":  len(kalshi),
                **res_a,
                "r2_daily_screen":  pair["r_squared"],
                "contract_title":   pair["contract_title"],
            })

        # Direction B: ETF leads Kalshi
        etf_before        = lookup_etf_mid(etf_ns, etf_mid, trade_ns - delta_ns)
        etf_return_before = (etf_at_t - etf_before) / etf_before
        res_b = ols_beta(prob_chg, etf_return_before)
        if res_b:
            rows.append({
                "contract_ticker":  ticker,
                "etf":              etf,
                "direction":        "etf_leads_kalshi",
                "horizon_sec":      delta_sec,
                "n_kalshi_trades":  len(kalshi),
                **res_b,
                "r2_daily_screen":  pair["r_squared"],
                "contract_title":   pair["contract_title"],
            })

# ── save ───────────────────────────────────────────────────────────────────────
cols = [
    "contract_ticker", "etf", "direction", "horizon_sec",
    "n_kalshi_trades", "n_events", "coef", "t_stat", "p_value", "r_squared",
    "r2_daily_screen", "contract_title",
]
out = pd.DataFrame(rows)[cols]
out.to_csv(OUT_CSV, index=False)

print(f"\nTotal regressions: {len(out)}")
print(f"Saved → {OUT_CSV}\n")

# ── summary: for each (pair, direction), show the horizon with lowest p-value ─
print("Best horizon per pair × direction (sorted by p-value, all pairs included):\n")
peak = (
    out.loc[out.groupby(["contract_ticker", "etf", "direction"])["p_value"].idxmin()]
    .sort_values("p_value")
    .reset_index(drop=True)
)
show = ["contract_ticker", "etf", "direction", "horizon_sec", "n_kalshi_trades",
        "coef", "t_stat", "p_value"]
with pd.option_context("display.width", 220, "display.max_colwidth", 50):
    print(peak[show].to_string(index=False))
