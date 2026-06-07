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
IN_CSV  = os.path.join(HERE, "regression_screen_results.csv")
OUT_CSV = os.path.join(HERE, "significant_pairs.csv")

P_THRESHOLD = 0.05


def extract_family(ticker: str) -> str:
    t = ticker
    if t.startswith("KX"):
        t = t[2:]
    m = re.match(r"^([A-Z]+)", t)
    return m.group(1) if m else t.split("-")[0]


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

deduped.to_csv(OUT_CSV, index=False)

print(f"Input:  {len(sig)} significant pairs (p < {P_THRESHOLD})")
print(f"Output: {len(deduped)} pairs after deduplication")
print(f"Saved to: {OUT_CSV}")
