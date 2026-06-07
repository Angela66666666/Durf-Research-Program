"""
Builds significant_pairs.csv from regression_screen_results.csv.

Two-step filter:
  1. Keep only statistically significant pairs (p < 0.05).
  2. Deduplicate by contract family × ETF: within each group, keep the
     single highest-R² row.

"Contract family" = the uppercase alphabetic prefix of the ticker after
stripping a leading KX (Kalshi's naming prefix, not meaningful).

Examples:
  KXECDJT312  -> ECDJT   (Trump electoral-map contracts)
  KXECKH276   -> ECKH    (Harris electoral-map contracts)
  KXFEDDECISION-24DEC-C25 -> FEDDECISION
  FEDDECISION-24NOV-H0    -> FEDDECISION
  KXAAAGASM-24NOV30-US-3.30 -> AAAGASM
  AAAGASM-24SEP30-US-3.15   -> AAAGASM
  RATECUT-24SEP18         -> RATECUT
  538APPROVEMAX-24SEP30-T43 -> 538APPROVEMAX (starts with digit, kept as-is)
"""

import os
import re
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
IN_CSV       = os.path.join(HERE, "regression_screen_results.csv")
CONTRACT_CSV = os.path.join(HERE, "contract_daily_prices.csv")
ETF_CSV      = os.path.join(HERE, "..", "etf_data", "vanguard_sector_etf_total_returns.csv")
OUT_CSV      = os.path.join(HERE, "significant_pairs.csv")

P_THRESHOLD = 0.05


def extract_family(ticker: str) -> str:
    t = ticker
    if t.startswith("KX"):
        t = t[2:]
    m = re.match(r"^([A-Z]+)", t)
    return m.group(1) if m else t.split("-")[0]


# --- Step 1: load regression results and filter/deduplicate ---
df = pd.read_csv(IN_CSV)
sig = df[df["p_value"] < P_THRESHOLD].copy()
sig["contract_family"] = sig["contract_ticker"].apply(extract_family)

deduped = (
    sig.sort_values("r_squared", ascending=False)
    .drop_duplicates(subset=["contract_family", "etf"], keep="first")
    .drop(columns=["contract_family"])
    .sort_values("r_squared", ascending=False)
    .reset_index(drop=True)
)

# --- Step 2: compute date_start and date_end for each pair ---
contracts = pd.read_csv(CONTRACT_CSV, parse_dates=["trade_date"])
contracts = contracts.dropna(subset=["close_yes_price"])
contracts["prob"] = contracts["close_yes_price"] / 100
contracts["prob_change"] = contracts.groupby("ticker")["prob"].diff()

etf = pd.read_csv(ETF_CSV, parse_dates=["date"])
etf_wide = etf.pivot_table(index="date", columns="ticker", values="daily_total_return")

date_ranges = []
for _, row in deduped.iterrows():
    ticker = row["contract_ticker"]
    etf_ticker = row["etf"]

    c = contracts[contracts["ticker"] == ticker][["trade_date", "prob_change"]].dropna()
    c = c.rename(columns={"trade_date": "date"})

    if etf_ticker not in etf_wide.columns:
        date_ranges.append(("", ""))
        continue

    e = etf_wide[[etf_ticker]].dropna().reset_index()
    merged = pd.merge(c, e, on="date").dropna()
    merged = merged.sort_values("date")

    if merged.empty:
        date_ranges.append(("", ""))
    else:
        date_ranges.append((
            merged["date"].iloc[0].strftime("%Y-%m-%d"),
            merged["date"].iloc[-1].strftime("%Y-%m-%d"),
        ))

deduped["date_start"], deduped["date_end"] = zip(*date_ranges)

deduped.to_csv(OUT_CSV, index=False)

print(f"Input:  {len(sig)} significant pairs (p < {P_THRESHOLD})")
print(f"Output: {len(deduped)} pairs after deduplication")
print(f"Saved to: {OUT_CSV}")
