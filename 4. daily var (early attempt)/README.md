# 4. Daily VAR (early attempt)

## What this folder is

This is an **early, superseded attempt** to answer the project's main question —
does the prediction market *lead* the sector ETF? — using **daily** data. It did
not work, and that failure is the whole point of keeping it: it is the reason the
study moved to high-frequency data (folders `5. leadlag high frequency` and
`6. hasbrouck`).

Read the results here as a **negative result**, not as a finding. In particular,
`var_RESULTS.txt` reports a Granger p-value of 0.47 ("not significant") — that
number does **not** mean "the prediction market does not lead the ETF." It means
the daily test has no power to tell (see below).

## What the two scripts do

Both take the significant pairs from `3. daily screen` and test lead-lag on
**daily** bars.

| Script | Method | Result |
|---|---|---|
| `var.py` | Fits a 2-variable VAR(2) on the single strongest pair (`KXECKH276` × VFH) and runs a Granger-causality test (contract → ETF). | Granger **p = 0.474, not significant** — and estimated from only **8 observations**. Writes `var_RESULTS.txt`. |
| `Lead lag.py` | For every significant pair, runs a lag-1 OLS in **both** directions (does yesterday's contract move predict today's ETF return, and vice versa). | Of 32 pairs: contract-leads-ETF significant in **3**, ETF-leads-contract in **6** — both near what pure chance would give, with no asymmetry. Writes `LEAD_LAG_FINAL_RESULT.csv`. |

Inputs (auto-located from the project root): `3. daily screen/regression_screen_results.csv`,
`3. daily screen/contract_daily_prices.csv`, `1. data/etf/vanguard_sector_etf_total_returns.csv`.

---

## Why the daily result cannot show anything

This is the important part. The daily test is not "a test that came back
negative" — it is a test that **could not have detected the effect even if the
effect is real and strong**, for four reasons:

1. **The timescale is wrong — this is the core problem.** The hypothesis is that
   the prediction market absorbs news *minutes to hours* before the ETF does. A
   **daily** bar collapses the entire trading day into one number, so the
   market's move and the ETF's response fall inside the **same** daily
   observation. At daily resolution you simply cannot see which one moved first
   within the day. A daily lag-1 test instead asks "does today's contract move
   predict *tomorrow's* ETF return" — a full day later — which is not the
   hypothesis and is exactly the kind of overnight predictability that would be
   arbitraged away. So a null here is expected regardless of the truth.

2. **The sample is far too small to estimate anything.** The VAR had **8
   observations** to fit a model with 10 coefficients — that is essentially
   unidentified; the standard errors are meaningless. The lag-1 pairs had only
   ~20–25 days each. A Granger p = 0.47 on n = 8 means "we have no information,"
   not "no effect."

3. **The contracts barely exist in daily terms.** Most contracts trade only a
   handful of days around their event, so the daily series is inherently too
   short to ever carry statistical power — no method applied at daily frequency
   could fix this.

4. **The output is noise, and reading direction into it would be wrong.**
   Contract-leads showed up in 3 of 32 pairs and ETF-leads in 6 of 32 — both at
   roughly the chance rate, with no systematic asymmetry. This is the signature
   of "nothing detectable at this frequency," and it is emphatically **not**
   evidence that the ETF leads the market.

---

## Why we moved to high frequency

To detect a lead measured in minutes, you have to look at minutes. The
high-frequency stage fixes every problem above:

- **Resolution:** 1-minute bars can actually separate "the market moved, then the
  ETF followed" *within* a trading day — the exact thing daily bars erase.
- **Power:** the same test window that gives ~10–25 daily points gives
  **thousands** of intraday observations, which is what a VECM / Granger /
  information-share estimator needs to produce stable, testable results.
- **Where it lives:** `5. leadlag high frequency` (high-frequency Granger, which
  *does* find a one-directional Kalshi → ETF lead that survives multiple-testing
  correction) and `6. hasbrouck` (Hasbrouck information shares). Those are the
  real tests; this folder only documents why they were necessary.

---

## File reference

| File | Role |
|---|---|
| `var.py` | VAR(2) + Granger on the strongest pair → `var_RESULTS.txt` |
| `Lead lag.py` | Lag-1 OLS both directions on all significant pairs → `LEAD_LAG_FINAL_RESULT.csv` |
| `var_RESULTS.txt` | VAR output (Granger p = 0.474, not significant) |
| `LEAD_LAG_FINAL_RESULT.csv` | Per-pair lag-1 lead-lag results (32 pairs) |

## How to run

```bash
python "var.py"
python "Lead lag.py"
```

Each finishes in a few seconds. Both write their output into this folder.
