"""
Event-driven lead-lag analysis: Kalshi prediction market vs Vanguard sector ETFs.

For each Kalshi trade at time t, we test two directions:

  (A) Kalshi leads ETF:
        Regress  etf_return(t → t+Δ)  on  kalshi_prob_change(t)
        Significant β > 0  →  Kalshi moves predict subsequent ETF moves

  (B) ETF leads Kalshi:
        Regress  kalshi_prob_change(t)  on  etf_return(t-Δ → t)
        Significant γ > 0  →  Prior ETF moves predict Kalshi trades

Tested for Δ = 5, 10, 30, 60, 120, 300 seconds.

Data
----
  Kalshi : leadlag/kalshi_hf_cache.parquet   (built on first run)
  ETF    : leadlag/etf_hf/<ETF>_hf.parquet   (built by process_taq.py)

Output
------
  leadlag/leadlag_event_results.csv
"""

import duckdb
import pandas as pd
import numpy as np
import statsmodels.api as sm
from pathlib import Path
from typing import Optional

# ── paths ──────────────────────────────────────────────────────────────────────
HERE          = Path(__file__).parent
KALSHI_GLOB   = str(HERE / ".." / "prediction-market-analysis" / "data" / "kalshi" / "trades" / "*.parquet")
CACHE_PATH    = HERE / "kalshi_hf_cache.parquet"
ETF_HF_DIR    = HERE / "etf_hf"
SIG_PAIRS_CSV = HERE / ".." / "regression" / "significant_pairs.csv"
OUT_CSV       = HERE / "leadlag_event_results.csv"

# ── parameters ─────────────────────────────────────────────────────────────────
HORIZONS_SEC = [5, 10, 30, 60, 120, 300]   # time windows to test (seconds)
MIN_EVENTS   = 10                            # min Kalshi trades to run regression
MAX_GAP_SEC  = 120                           # if no ETF tick within this gap → NaN

# ── setup ──────────────────────────────────────────────────────────────────────
con = duckdb.connect()
sig = pd.read_csv(SIG_PAIRS_CSV)
tickers = sig["contract_ticker"].unique().tolist()

# ── Step 0: build Kalshi cache once (scan 7,214 files) ─────────────────────────
if not CACHE_PATH.exists():
    ticker_list = ", ".join(f"'{t}'" for t in tickers)
    print("Building Kalshi cache (one-time scan)…")
    con.execute(f"""
        COPY (
            SELECT ticker, created_time, yes_price
            FROM   read_parquet('{KALSHI_GLOB}')
            WHERE  ticker IN ({ticker_list})
        ) TO '{CACHE_PATH}' (FORMAT PARQUET)
    """)
    print(f"  Saved → {CACHE_PATH}\n")
else:
    print(f"Using existing Kalshi cache: {CACHE_PATH}\n")


# ── data loaders ───────────────────────────────────────────────────────────────
def load_kalshi_trades(ticker: str, date_start: str, date_end: str) -> pd.DataFrame:
    """Individual Kalshi trades for one contract, with prob_change computed."""
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
    """ETF NBBO mid-price ticks for the event window."""
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


# ── core lookup ────────────────────────────────────────────────────────────────
def lookup_etf_mid(etf_ns: np.ndarray, etf_mid: np.ndarray,
                   query_ns: np.ndarray) -> np.ndarray:
    """
    For each query time, return the last ETF mid price at or before that time.
    Returns NaN if the nearest preceding tick is more than MAX_GAP_SEC away.
    """
    max_gap_ns = MAX_GAP_SEC * 1_000_000_000
    idx    = np.searchsorted(etf_ns, query_ns, side="right") - 1
    result = np.full(len(query_ns), np.nan)
    valid  = idx >= 0
    vi     = np.where(valid)[0]
    gaps   = query_ns[vi] - etf_ns[idx[vi]]
    close  = gaps <= max_gap_ns
    result[vi[close]] = etf_mid[idx[vi[close]]]
    return result


# ── regression helper ──────────────────────────────────────────────────────────
def ols_stats(y: np.ndarray, x: np.ndarray) -> Optional[dict]:
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

    print(f"[{i+1}/{len(sig)}] {ticker} × {etf}  ({date_start} → {date_end})", end="  ")

    kalshi    = load_kalshi_trades(ticker, date_start, date_end)
    etf_ticks = load_etf_ticks(etf, date_start, date_end)

    if len(kalshi) < MIN_EVENTS or etf_ticks.empty:
        print(f"skipped ({len(kalshi)} Kalshi trades)")
        continue

    print(f"{len(kalshi)} Kalshi trades, {len(etf_ticks):,} ETF ticks")

    # Convert timestamps to int64 nanoseconds for fast vectorised lookup
    etf_ns   = etf_ticks["ts_utc"].astype("datetime64[ns]").astype("int64").values
    etf_mid  = etf_ticks["mid"].values
    trade_ns = kalshi["ts_utc"].astype("datetime64[ns]").astype("int64").values
    prob_chg = kalshi["prob_change"].values

    # ETF mid at the exact moment of each Kalshi trade (reference price)
    etf_at_t = lookup_etf_mid(etf_ns, etf_mid, trade_ns)

    for delta_sec in HORIZONS_SEC:
        delta_ns = int(delta_sec * 1_000_000_000)

        # ── Direction A: Kalshi leads ETF ──────────────────────────────────
        # ETF return in the Δ seconds AFTER each Kalshi trade
        etf_after        = lookup_etf_mid(etf_ns, etf_mid, trade_ns + delta_ns)
        etf_return_after = (etf_after - etf_at_t) / etf_at_t

        res_a = ols_stats(etf_return_after, prob_chg)
        if res_a:
            rows.append({
                "contract_ticker": ticker,
                "etf":             etf,
                "direction":       "kalshi_leads_etf",
                "horizon_sec":     delta_sec,
                **res_a,
                "r2_daily_screen": pair["r_squared"],
                "contract_title":  pair["contract_title"],
            })

        # ── Direction B: ETF leads Kalshi ──────────────────────────────────
        # ETF return in the Δ seconds BEFORE each Kalshi trade
        etf_before        = lookup_etf_mid(etf_ns, etf_mid, trade_ns - delta_ns)
        etf_return_before = (etf_at_t - etf_before) / etf_before

        res_b = ols_stats(prob_chg, etf_return_before)
        if res_b:
            rows.append({
                "contract_ticker": ticker,
                "etf":             etf,
                "direction":       "etf_leads_kalshi",
                "horizon_sec":     delta_sec,
                **res_b,
                "r2_daily_screen": pair["r_squared"],
                "contract_title":  pair["contract_title"],
            })

# ── save & summarise ───────────────────────────────────────────────────────────
cols = [
    "contract_ticker", "etf", "direction", "horizon_sec",
    "n_events", "coef", "t_stat", "p_value", "r_squared", "r2_daily_screen",
    "contract_title",
]
out = pd.DataFrame(rows)[cols]
out.to_csv(OUT_CSV, index=False)

print(f"\nTotal regressions: {len(out)}")
print(f"Saved → {OUT_CSV}\n")

sig_out = out[out["p_value"] < 0.05].sort_values("r_squared", ascending=False)
print(f"Significant (p < 0.05): {len(sig_out)} of {len(out)}")

show = ["contract_ticker", "etf", "direction", "horizon_sec", "n_events", "r_squared", "p_value"]
with pd.option_context("display.width", 180, "display.max_colwidth", 50):
    print(sig_out.head(30)[show].to_string(index=False))
