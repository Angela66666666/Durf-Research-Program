# 3. Daily Screen

## Goal of this folder

Take the 295 contracts selected in `2. contract selection`, build a daily price
panel for them, and find which **(contract × sector-ETF)** pairs co-move most
strongly on the same day. This is a **screener**, not the lead-lag test itself:
its output is the short list of pairs worth pulling high-frequency data for. The
actual lead-lag direction is decided later, in `5. leadlag high frequency`.

Why only a screener, and why same-day co-movement rather than lead-lag here? A
daily lag-1 test was run and found **no lead signal at daily frequency** (12 of
550 lag-1 pairs significant — fewer than the ~27 expected by chance). Same-day
co-movement, on the other hand, is real and strong. So the daily data is used
only to *rank* co-movement strength and pick candidates; whether the prediction
market leads or lags is a question for intraday data.

The pipeline is three steps:

```
2. contract selection/selected_contracts.csv  (295 contracts)
        │
        ▼
  extract_contract_trades.py ──▶ contract_daily_prices.csv   (295 contracts × day, 3998 rows)
        │                               │
        │   1. data/etf/…returns.csv ───┤
        ▼                               ▼
                     regression.py ──▶ regression_screen_results.csv   (all 594 regressions)
                            │
                            ▼
              build_significant_pairs.py ──▶ significant_pairs.csv   (48 pairs → handed to folder 5)
```

All scripts locate the project root automatically by walking up until they find
`1. data/`, so they run from any working directory.

---

## Step 1 — Build the daily price panel

**Script:** `extract_contract_trades.py`
**Reads:** `2. contract selection/selected_contracts.csv` (the 295 tickers) +
`1. data/kalshi/kalshi/trades/*.parquet`
**Writes:** `contract_daily_prices.csv`

For each of the 295 contracts it aggregates every individual trade to one row per
day. The core aggregation:

```python
daily = con.execute(f"""
    SELECT ticker,
           DATE_TRUNC('day', created_time AT TIME ZONE 'UTC') AS trade_date,
           SUM(yes_price * count) / SUM(count)   AS vwap_yes_price,
           LAST(yes_price  ORDER BY created_time) AS close_yes_price,
           FIRST(yes_price ORDER BY created_time) AS open_yes_price,
           SUM(count)  AS daily_volume,
           COUNT(*)    AS n_trades
    FROM '{trades_glob}'
    WHERE ticker IN ({ticker_list})
    GROUP BY ticker, DATE_TRUNC('day', created_time AT TIME ZONE 'UTC')
""").df()
```

`yes_price` is quoted in cents (0–100), so the market-implied probability is
`close_yes_price / 100` (e.g. 72 → 0.72). **Output: `contract_daily_prices.csv` —
daily open / close / VWAP / volume for the 295 contracts (3,998 rows).**

---

## Step 2 — Regression screen

**Script:** `regression.py`
**Reads:** `contract_daily_prices.csv` +
`1. data/etf/vanguard_sector_etf_total_returns.csv`
**Writes:** `regression_screen_results.csv`

For every (contract × ETF) pair it fits one contemporaneous OLS:

```
etf_return(t)  ~  const + prob_change(t)
```

where `prob_change(t)` is the day-over-day change in the contract's implied
probability (`Δ(close_yes_price / 100)`) and `etf_return(t)` is the ETF's daily
total return that same day. With 295 contracts × 11 ETFs and a minimum-overlap
filter, this produces **594 regressions**, all saved to
`regression_screen_results.csv` (significant or not).

**Two methodology choices, both to avoid being misled:**

- **Rank by R², not raw |coef|.** Each contract's `prob_change` has a different
  variance, so a contract whose probability barely moves mechanically gets a
  *large* coefficient to explain the same ETF move — large coef, insignificant p.
  In a one-regressor OLS `|std_coef| = √R² = |correlation|`, so R² is the honest
  measure of co-movement strength. A standardized `std_coef` is also reported so
  coefficients are comparable across contracts.
- **`MIN_OBS = 10`.** Many contracts have only 2–5 days of data; without a floor
  the ranking fills up with spurious tiny-sample fits. Pairs with fewer than 10
  overlapping trading days are skipped. (Contracts with ~10 days around an event
  are kept — the matching high-frequency data usually covers those same days.)

---

## Step 3 — Deduplicate to significant pairs

**Script:** `build_significant_pairs.py`
**Reads:** `regression_screen_results.csv` (+ `contract_daily_prices.csv` and the
ETF returns, to attach each pair's date range)
**Writes:** `significant_pairs.csv`

Two filters:

1. Keep only **p < 0.05** → 110 pairs.
2. **Deduplicate by contract family × ETF**: many contracts are the *same event
   in different outcome scenarios* (e.g. `KXECDJT312`, `KXECDJT322`, `KXECDJT270`
   are all "Trump wins by margin X" and move in near-lockstep). A "family" is the
   ticker's uppercase alphabetic prefix after stripping the leading `KX`
   (`KXECDJT312 → ECDJT`, `KXFEDDECISION-24DEC-C25 → FEDDECISION`, and
   `538APPROVEMAX-…`, which starts with a digit, is kept as-is). Within each
   (family × ETF) group only the **highest-R²** row is kept.

| Stage | Rows |
|---|---|
| All regression pairs | 594 |
| After p < 0.05 | 110 |
| After family deduplication | **48** |

**Output: `significant_pairs.csv` — 48 pairs, 19 contracts, 7 ticker families**
(election electoral-vote `ECDJT`/`ECKH`, Fed decisions `FEDDECISION`/`RATECUT`,
gas prices `AAAGASM`, approval ratings `538APPROVEMAX`/`538APPROVEMIN`). Top pair:
**`KXECKH276` (Harris wins 276–262) × VFH, R² = 0.88.** This file is the handoff
to `5. leadlag high frequency`, which pulls intraday data for each of these pairs
to test lead-lag direction.

---

## File reference

| File | Role | Reads | Writes |
|---|---|---|---|
| `extract_contract_trades.py` | Step 1 — daily price panel | `2. contract selection/selected_contracts.csv`, `1. data/kalshi/kalshi/trades/*.parquet` | `contract_daily_prices.csv` |
| `regression.py` | Step 2 — contemporaneous screen | `contract_daily_prices.csv`, `1. data/etf/vanguard_sector_etf_total_returns.csv` | `regression_screen_results.csv` |
| `build_significant_pairs.py` | Step 3 — filter + dedup | `regression_screen_results.csv` | `significant_pairs.csv` |
| `contract_daily_prices.csv` | Step 1 output / Steps 2–3 input | — | — |
| `regression_screen_results.csv` | Step 2 output (all 594 regressions) | — | — |
| `significant_pairs.csv` | Step 3 output — the 48 candidate pairs (handed to folder 5) | — | — |

## How to run

```bash
python "extract_contract_trades.py"     # rebuilds contract_daily_prices.csv
python "regression.py"                   # rebuilds regression_screen_results.csv
python "build_significant_pairs.py"      # rebuilds significant_pairs.csv
```

Runs in a few seconds each (Step 1 scans the trades parquet and takes ~1 minute).
