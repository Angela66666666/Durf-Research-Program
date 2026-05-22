# ETF Data Pipeline Notes

## Objective

Extract daily returns for 11 Vanguard Sector ETFs over **2024-09-01 to 2024-12-31** (covering the 2024 U.S. Presidential Election and its aftermath), to be used in a lead-lag analysis between Kalshi prediction market contracts and sector ETF returns.

ETFs covered:
VOX (Communication Services), VCR (Consumer Discretionary), VDC (Consumer Staples), VDE (Energy), VFH (Financials), VHT (Health Care), VIS (Industrials), VGT (Information Technology), VAW (Materials), VNQ (Real Estate), VPU (Utilities)

---

## Original Plan vs. What Actually Happened

### Original Plan

`data_explore_example(1).py` was designed as a single-step pipeline: use DuckDB's `httpfs` plugin to read parquet files directly from HuggingFace, filter to the target ETFs and date range, and compute returns.

**Original data sources:**
- Prices: `https://huggingface.co/datasets/bwzheng2010/yahoo-finance-data`
- Dividends / splits: `https://huggingface.co/datasets/defeatbeta/yahoo-finance-data`

### Why it was split into two steps (Attempt 1)

HuggingFace returned **HTTP 429 Too Many Requests**, blocking direct remote reads. The workaround was to manually download the parquet files via `curl` and update the script to read from local paths instead.

### Why the approach changed entirely (Attempt 2)

After switching to local files, the script produced **0 rows**. Investigation showed that the `bwzheng2010/yahoo-finance-data` dataset contains only individual stocks — it does not include ETFs. Querying for all 11 Vanguard ETFs returned nothing.

**Final decision:** drop the HuggingFace data source entirely and use `yfinance` to download the target ETFs directly from Yahoo Finance.

| | Original | Final |
|---|---|---|
| Data source | HuggingFace parquet (full market) | Yahoo Finance via yfinance |
| Download scope | All stocks, all history — filter locally | Only the 11 target ETFs, target date range |
| Dependencies | duckdb + httpfs | yfinance + pandas |
| Output format | Same CSV schema | Same CSV schema |

The three downloaded parquet files in `etf_data/` are kept for reference but are no longer part of this pipeline.

---

## Steps (Final Version)

### Step 1: Install dependency

```bash
pip install yfinance
```

### Step 2: Run the script

```bash
cd /Users/liu/Desktop/Durf/etf_data
python download_etf_returns.py
```

Output is saved to `etf_data/vanguard_sector_etf_total_returns.csv` regardless of which directory the script is run from.

### Output schema

| Column | Description |
|--------|-------------|
| `ticker` | ETF symbol |
| `date` | Trading date |
| `close` | Closing price |
| `dividend` | Dividend paid that day (0 if none) |
| `lag_close` | Previous day's closing price |
| `daily_price_return` | Price-only daily return |
| `daily_total_return` | Total return including dividends |
| `dividend_return_component` | Dividend contribution to return |

**Result:** 902 rows, 11 ETFs, 22 dividend events (2 per ETF, clustered around late September and mid-December)
