"""
Unified lead-lag regression — professor's specification:

    r_{i,t} = α + Σ_{k=-K}^{K} β_k Δς(p_{t-k}) + γ'X_t + ε_{i,t}

  r_{i,t}     : ETF 1-minute log return at minute t
  Δς(p_{t-k}) : Kalshi probability change at minute t-k
                (0 at non-trade minutes; via ffill → diff)
  k > 0       : past prob changes — significant β → Kalshi leads ETF
  k < 0       : future prob changes — significant β → ETF leads Kalshi
  k = 0       : contemporaneous
  X_t         : day fixed effects

Data
----
  Kalshi : leadlag/kalshi_hf_cache.parquet
  ETF    : leadlag/etf_hf/<ETF>_hf.parquet

Output
------
  leadlag/leadlag_unified_results.csv
"""

import duckdb
import pandas as pd
import numpy as np
import statsmodels.api as sm
from pathlib import Path

HERE          = Path(__file__).parent
CACHE_PATH    = HERE / "kalshi_hf_cache.parquet"
ETF_HF_DIR    = HERE / "etf_hf"
SIG_PAIRS_CSV = HERE / ".." / "regression" / "significant_pairs.csv"
OUT_CSV       = HERE / "leadlag_unified_results.csv"

K       = 5    # lags/leads in minutes
MIN_OBS = 50   # minimum rows after building lag matrix

con = duckdb.connect()
sig = pd.read_csv(SIG_PAIRS_CSV)


def make_col(k: int) -> str:
    if k < 0:
        return f"lag_m{abs(k)}"
    if k > 0:
        return f"lag_p{k}"
    return "lag_0"


def load_kalshi_minute(ticker: str, date_start: str, date_end: str) -> pd.Series:
    q = f"""
    SELECT
        DATE_TRUNC('minute', (created_time AT TIME ZONE 'UTC')::TIMESTAMP) AS minute_utc,
        ARG_MAX(yes_price, created_time) AS last_price
    FROM read_parquet('{CACHE_PATH}')
    WHERE ticker = '{ticker}'
      AND created_time >= TIMESTAMPTZ '{date_start} 00:00:00+00'
      AND created_time <= TIMESTAMPTZ '{date_end} 23:59:59+00'
    GROUP BY 1
    ORDER BY 1
    """
    df = con.execute(q).df()
    df["minute_utc"] = pd.to_datetime(df["minute_utc"])
    return (df.set_index("minute_utc")["last_price"] / 100.0).rename("prob")


def load_etf_minute(etf: str, date_start: str, date_end: str) -> pd.Series:
    etf_path = str(ETF_HF_DIR / f"{etf}_hf.parquet")
    q = f"""
    SELECT
        DATE_TRUNC('minute', timestamp_utc) AS minute_utc,
        ARG_MAX(mid, timestamp_utc) AS last_mid
    FROM read_parquet('{etf_path}')
    WHERE timestamp_utc >= TIMESTAMP '{date_start} 00:00:00'
      AND timestamp_utc <= TIMESTAMP '{date_end} 23:59:59'
    GROUP BY 1
    ORDER BY 1
    """
    df = con.execute(q).df()
    df["minute_utc"] = pd.to_datetime(df["minute_utc"])
    return df.set_index("minute_utc")["last_mid"].rename("etf_mid")


# ── main loop ──────────────────────────────────────────────────────────────────
rows = []

for i, pair in sig.iterrows():
    ticker     = pair["contract_ticker"]
    etf        = pair["etf"]
    date_start = str(pair["date_start"])
    date_end   = str(pair["date_end"])

    print(f"[{i+1}/{len(sig)}] {ticker} × {etf}  ({date_start} → {date_end})", end="  ")

    kalshi_s = load_kalshi_minute(ticker, date_start, date_end)
    etf_s    = load_etf_minute(etf, date_start, date_end)

    # Dense minute grid from ETF (market hours only), Kalshi joined sparsely
    df = etf_s.to_frame().join(kalshi_s, how="left")

    # Forward-fill Kalshi prob; diff gives 0 at non-trade minutes
    df["prob"]        = df["prob"].ffill()
    df["prob_change"] = df["prob"].diff().fillna(0)
    df["etf_return"]  = np.log(df["etf_mid"]).diff()
    df["date"]        = df.index.date

    df = df.dropna(subset=["etf_return"])

    if df["prob_change"].abs().sum() < 1e-8:
        print("skipped (no Kalshi activity)")
        continue

    # Build lag/lead columns
    # shift(+k) → value k steps in the past  (k>0: past Kalshi → ETF now → Kalshi leads)
    # shift(-k) → value k steps in the future (k<0: future Kalshi → ETF leads Kalshi)
    lag_cols = [make_col(k) for k in range(-K, K + 1)]
    for k in range(-K, K + 1):
        df[make_col(k)] = df["prob_change"].shift(k)

    df = df.dropna(subset=lag_cols)

    if len(df) < MIN_OBS:
        print(f"skipped ({len(df)} obs after lags)")
        continue

    print(f"{len(df):,} obs")

    day_dummies = pd.get_dummies(df["date"], prefix="d", drop_first=True, dtype=float)
    X = sm.add_constant(pd.concat([df[lag_cols].astype(float), day_dummies], axis=1))
    y = df["etf_return"].astype(float)

    try:
        m = sm.OLS(y, X).fit(cov_type="HC3")
    except Exception as e:
        print(f"  OLS failed: {e}")
        continue

    for k in range(-K, K + 1):
        col = make_col(k)
        if col not in m.params:
            continue
        direction = "kalshi_leads_etf" if k > 0 else ("contemp" if k == 0 else "etf_leads_kalshi")
        rows.append({
            "contract_ticker": ticker,
            "etf":             etf,
            "k":               k,
            "direction":       direction,
            "coef":            m.params[col],
            "t_stat":          m.tvalues[col],
            "p_value":         m.pvalues[col],
            "r_squared":       m.rsquared,
            "n_obs":           int(len(df)),
            "r2_daily_screen": pair["r_squared"],
            "contract_title":  pair["contract_title"],
        })

# ── save & summarise ───────────────────────────────────────────────────────────
out = pd.DataFrame(rows)
out.to_csv(OUT_CSV, index=False)

print(f"\nTotal coefficients estimated: {len(out)}")
print(f"Saved → {OUT_CSV}\n")

sig_out = out[out["p_value"] < 0.05].sort_values("p_value")
print(f"Significant (p < 0.05): {len(sig_out)} of {len(out)}")

show = ["contract_ticker", "etf", "k", "direction", "coef", "t_stat", "p_value", "n_obs"]
with pd.option_context("display.width", 200, "display.max_colwidth", 50):
    print(sig_out.head(40)[show].to_string(index=False))
