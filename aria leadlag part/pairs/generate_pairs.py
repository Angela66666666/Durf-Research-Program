"""
从 significant_pairs.csv 生成 pair_etf.csv 和 pair_contract.csv
逻辑（按"共享上下文"配对，而不是全组合）：
  - pair_etf.csv：     同一个 contract_ticker 匹配到的多个 ETF，两两配对
  - pair_contract.csv：同一个 etf 匹配到的多个 contract，两两配对
日期范围用两行各自 date_start/date_end 的【交集】（更保守，避免用没有共同重叠
的窗口去跑回归）。如果两行根本没有重叠日期，这一对会被跳过并打印提示。
"""
import pandas as pd
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).parent
SIG_PAIRS_CSV = HERE / ".." / "regression" / "significant_pairs.csv"
OUT_PAIR_ETF      = HERE / "pair_etf.csv"
OUT_PAIR_CONTRACT = HERE / "pair_contract.csv"

sig = pd.read_csv(SIG_PAIRS_CSV)
sig["date_start"] = pd.to_datetime(sig["date_start"])
sig["date_end"]   = pd.to_datetime(sig["date_end"])


def overlap_dates(row_a, row_b):
    """两行日期窗口的交集；没有重叠返回 None。"""
    start = max(row_a["date_start"], row_b["date_start"])
    end   = min(row_a["date_end"], row_b["date_end"])
    if start > end:
        return None
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


# ---------- pair_etf.csv: 同一合约关联的多个ETF两两配对 ----------
etf_pairs = []
skipped_etf = 0
for ticker, grp in sig.groupby("contract_ticker"):
    grp = grp.drop_duplicates(subset=["etf"])
    if len(grp) < 2:
        continue
    rows = grp.to_dict("records")
    for r1, r2 in combinations(rows, 2):
        if r1["etf"] == r2["etf"]:
            continue
        ov = overlap_dates(r1, r2)
        if ov is None:
            skipped_etf += 1
            continue
        ds, de = ov
        etf_pairs.append({
            "etf_x": r1["etf"], "etf_y": r2["etf"],
            "date_start": ds, "date_end": de,
            "shared_contract": ticker,
        })

df_etf_pairs = pd.DataFrame(etf_pairs).drop_duplicates(subset=["etf_x", "etf_y", "date_start", "date_end"])
df_etf_pairs.to_csv(OUT_PAIR_ETF, index=False)
print(f"pair_etf.csv 生成完毕: {len(df_etf_pairs)} 对 (跳过无重叠日期的: {skipped_etf})  -> {OUT_PAIR_ETF}")


# ---------- pair_contract.csv: 同一ETF关联的多个合约两两配对 ----------
contract_pairs = []
skipped_contract = 0
for etf, grp in sig.groupby("etf"):
    grp = grp.drop_duplicates(subset=["contract_ticker"])
    if len(grp) < 2:
        continue
    rows = grp.to_dict("records")
    for r1, r2 in combinations(rows, 2):
        if r1["contract_ticker"] == r2["contract_ticker"]:
            continue
        ov = overlap_dates(r1, r2)
        if ov is None:
            skipped_contract += 1
            continue
        ds, de = ov
        contract_pairs.append({
            "ticker_x": r1["contract_ticker"], "ticker_y": r2["contract_ticker"],
            "date_start": ds, "date_end": de,
            "shared_etf": etf,
        })

df_contract_pairs = pd.DataFrame(contract_pairs).drop_duplicates(
    subset=["ticker_x", "ticker_y", "date_start", "date_end"]
)
df_contract_pairs.to_csv(OUT_PAIR_CONTRACT, index=False)
print(f"pair_contract.csv 生成完毕: {len(df_contract_pairs)} 对 (跳过无重叠日期的: {skipped_contract})  -> {OUT_PAIR_CONTRACT}")
