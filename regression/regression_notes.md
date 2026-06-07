# Regression Screening Notes

Design decisions, methodology, and changelog for `regression.py`.

---

## 1. Objective

This project studies the **lead-lag relationship** between Kalshi prediction market contracts and Vanguard sector ETFs, using the 2024 U.S. Presidential Election as the main event.

This script is the **first-pass screening tool**: across 295 contracts × 11 ETFs, it identifies which (contract × ETF) pairs exhibit strong **contemporaneous co-movement**, filtering out irrelevant contracts and surfacing candidates worth deeper analysis.

## 2. Data

| File | Key columns | Description |
|---|---|---|
| `contract_daily_prices.csv` | `ticker`, `trade_date`, `close_yes_price`, `sector_relevance` | Daily data for 295 contracts; `close_yes_price` is in cents (0–100), i.e. probability × 100 |
| `../etf_data/vanguard_sector_etf_total_returns.csv` | `ticker`, `date`, `daily_total_return` | Daily total returns for 11 Vanguard sector ETFs |

Both datasets start from 2024-09 and are aligned by date.

## 3. Method

For each (contract × ETF) pair, run OLS:

- **X (independent)** = daily change in contract probability: `Δ(close_yes_price / 100)` (day-over-day diff within each contract)
- **Y (dependent)** = ETF `daily_total_return` on the same day
- Specification (contemporaneous only): `etf_return(t) ~ prob_change(t)`
- Output: `coef`, `abs_coef`, `std_coef` (standardized), `t_stat`, `p_value`, `r_squared`, `n_obs`
- **Ranked by `r_squared` (co-movement strength), descending**; printed summary filtered to p < 0.05

### Key parameters
- `MIN_OBS = 10`: pairs with fewer than 10 overlapping trading days are skipped.
- `P_THRESHOLD = 0.05`: only significant pairs are printed in the summary.

## 4. Key Methodological Decisions

### Why not rank by raw |coefficient|?

Each contract's `prob_change` has a different variance. A contract whose probability barely moves will mechanically produce a **large coefficient** to explain the same ETF movement — but has no real explanatory power (typical symptom: large coef, insignificant p-value).

**Solution:**
1. Add **standardized coefficient `std_coef = coef × std(X)/std(Y)`** to make coefficients comparable across contracts.
2. **Rank by `r_squared`** as the measure of co-movement strength (in single-regressor OLS, `R² = std_coef² = correlation²`). Do not rank by raw |coef|.
3. **Filter by `p_value < 0.05`** before printing the summary, to remove noise pairs.
4. All results (including insignificant) are still written to `regression_screen_results.csv` for downstream filtering.

### Minimum observation threshold

Many contracts in the raw data have only 2–5 days of records. Without a floor, the output is dominated by spurious results from tiny samples with artificially inflated coefficients. Hence `MIN_OBS = 10`.

---

## 5. Changelog

### v1 — Initial placeholder (inherited from repo)
- Read a non-existent `merged_data.csv` with non-existent columns `trump_prob_change` / `xle_return` (XLE is a SPDR energy ETF not present in this dataset; the energy ETF here is Vanguard's **VDE**).
- **Status: not runnable, pure placeholder.**

### v2 — Full pairwise contemporaneous screening
- **Change:** Use `contract_daily_prices.csv` + ETF returns directly; run contemporaneous OLS for all 295 contracts × 11 ETFs; rank by |coef|; save to `regression_screen_results.csv`.
- **Rationale:** The actual goal is screening for high-signal contracts, not running a single regression.
- **Added `MIN_OBS = 10`:** Exclude pairs with too few observations.
- **Problem found:** Top-ranked pairs were Fed rate contracts with large coefficients but insignificant p-values — ranking by raw |coef| is misleading.

### v3 — Add standardized coefficient, significance filter, lag-1
- **Change 1:** Add `std_coef` to make coefficients comparable across contracts.
- **Change 2:** Filter summary by `p_value < 0.05` before ranking; full results still saved to CSV.
- **Change 3:** Add lag-1 specification (`etf_return(t) ~ prob_change(t-1)`) alongside contemporaneous, to test whether prediction markets lead ETFs.
- **Finding:** Significant lag-1 pairs (12 out of 550) were fewer than chance (~27 expected), suggesting virtually no lead signal at daily frequency. Contemporaneous co-movement, however, was real and strong.

### v4 — Focus on contemporaneous screening, switch to R² ranking (current version)
- **Clarified role:** This regression is purely a "co-movement screener." Use daily contemporaneous regression to identify strongly co-moving (contract × ETF) pairs, then **download high-frequency data for those pairs only** to study actual lead-lag direction. Lead-lag is not determined here.
- **Change 1: Remove lag-1.** Lead-lag analysis belongs to the high-frequency stage; keeping it here is only a distraction.
- **Change 2: Switch ranking from `abs_coef` to `r_squared`.** In single-regressor OLS, `|std_coef| = √R² = |correlation|`, so co-movement strength is properly measured by R² (= std_coef²). Raw |coef| conflates signal strength with each contract's probability volatility — the wrong ranking dimension.
- **Keep short-lived contracts (`MIN_OBS=10` unchanged):** Contracts with only ~10 days around an event are retained — if that is all the daily data available, the corresponding high-frequency data will typically also cover only those days, and remains usable.

---

## 6. How to Run

```bash
cd regression/
python regression.py
```

Completes in a few seconds. Output: terminal prints the top significant pairs; full results saved to `regression_screen_results.csv`.
