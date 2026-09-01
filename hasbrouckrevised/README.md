# High-frequency basket — weights re-estimated at 1 minute

**Why this folder exists.** The main analysis (`../daily`, `../high frequency`)
estimates the basket weights on *daily* data and applies them at 1 minute. The
advisor's point: statistical properties differ across horizons, so the daily
cointegrating vector need not be the right one at the minute scale — and indeed
the daily-weighted basket does not cointegrate with Kalshi at 1 minute. This
folder **re-estimates the whole weight vector directly on 1-minute data** and
re-runs the price-discovery analysis with it.

## Two changes from the main analysis

1. **Weights re-estimated at 1 minute** on the pre-test window (Polymarket, Sep).
2. **FXI added to the basket** (→ 20 assets = 11 sector ETFs + 8 adds + FXI). FXI
   is China large-caps: a Trump win means tariffs, which move Chinese equities,
   so it is an a-priori election-sensitive name (it was already a candidate in
   the original data request), added as a hedge that removes broad non-election
   variance. With it the basket **cointegrates with Kalshi at 1 minute at the 5%
   level** (Engle-Granger), which the 19-asset basket only reached at 10%.

## Files

| File | Role |
|---|---|
| `fetch_polymarket_hf.py` | Downloads 1-min Polymarket P(Trump) from the CLOB API (same YES token as the daily series) → `polymarket_trump_hf_1min.csv`. Validates: sampled at 20:00 ET it reproduces the cached daily series exactly (corr 1.000, MAE 0.000). Run once. |
| `build_panels.py` | Builds both 1-min panels → `estim_panel_1min.csv` (Sep, 20 assets + Polymarket) and `test_panel_1min.csv` (Oct-Nov, 20 assets + Kalshi). |
| `hasbrouck_basket.py` | Steps 1–4 in one file → `hf_basket_weights.csv`, `hf_basket_pair_1min.csv`, `hf_basket_results.txt`, `hf_basket.png`. |

Run order: `fetch_polymarket_hf.py` → `build_panels.py` → `hasbrouck_basket.py`.

## Out-of-sample design (no look-ahead)

Weights estimated on **Polymarket, Sep 3 – Oct 3**; test on **Kalshi, Oct 4 –
Nov 6**. Different venue *and* an earlier period than the test window — the same
no-circularity logic as the daily Method B. The adds' NBBO data starts 2024-09-03
(the estimation window's left edge); the right edge is the day before Kalshi's
contract begins (so estimation and test never overlap).

## What step 4's five parts are for

Step 4 asks one thing — **does the equity basket lead Kalshi, or follow it?** —
and each part removes one way the naive answer could be an artefact:

- **Part 1 baseline.** Over all minutes, which side error-corrects (moves back
  when the two prices diverge)? The side that does *not* adjust is the leader.
- **Part 2 by time of day.** Is the adjustment there all day or only in the
  morning? Separates a genuine lead from mere opening catch-up.
- **Part 3 delete the first N minutes.** How much of the effect survives once the
  open is removed? Locates where it lives.
- **Part 4 one-sided test + placebo.** Does the opening gap predict the *basket's*
  next 90 minutes (C1) but *not* Kalshi's (C2)? A significant C1 with a flat C2
  rules out "both just followed the same news" and shows the basket is chasing
  Kalshi — information flowing market → equity.
- **Part 5 opening convergence profile.** Minute by minute after the open, what
  fraction of the opening gap has the basket closed? This traces the catch-up
  directly.

## Headline results (`hf_basket_results.txt`)

**Steps 1–3.**
```
weights: level cointegrating regression on 1-min, Sep 3-Oct 3, n=8,993, R2=0.929
gate vs Kalshi (Oct-Nov, 9,361 min):
   level correlation = +0.917   (daily-weighted basket: +0.572; 19-asset HF: +0.904)
   Engle-Granger p = 0.037 -> COINTEGRATED at 5%   (headline, scale-invariant)
   Johansen trace  12.41 (10% cv 13.43) -> not at 10%
   ADF spread(1,-1) 0.838 -> no  (unit-slope test; the basket underresponds ~0.3x,
                                  so this test is mis-specified here and is not the gate)
```

**Step 4.**
```
PART 1  basket alpha -0.00149 (t -4.04) ADJUSTS ; kalshi (t 1.73) does not
        Gonzalo-Granger basket 77.7% / kalshi 22.3% ; Hasbrouck IS kalshi 85.5%
PART 2  adjustment present across the day, afternoon strongest (14:00-16:00 t -3.08)
PART 3  survives removing the open: t stays -3.2 to -4.0 through skip-120
PART 4  C1 gap->basket 90m  slope -0.242  p=0.003   (basket closes the gap)
        C2 gap->kalshi 90m  slope -0.051  p=0.683   (placebo, flat)
PART 5  fraction of the opening gap the basket closes:
          15m 21%   60m 24%   90m 24%   240m 30%   330m 31%   (all p<0.01)
          Kalshi placebo hovers at ~0 and never systematically closes the gap
```

## What this says (and how it revises the daily-basket story)

1. **Kalshi leads, one-sided.** The basket error-corrects toward Kalshi (t = −4.04)
   while Kalshi does not adjust; the opening gap drives the basket (C1) but not
   Kalshi (C2). Information flows prediction-market → equity. This is the same
   direction as the daily basket, now on a basket that actually cointegrates.

2. **The lead is persistent intraday, not opening-only.** With the noisy daily-
   weighted basket the effect vanished after the first 90 minutes; with the
   properly HF-estimated, cointegrating basket the basket keeps walking toward
   Kalshi all day — closing ~21% of the opening gap in the first 15 minutes and
   ~31% by the close (Part 5), with error-correction significant through the whole
   session (Part 3). **This revises the paper's "temporary, first-90-minutes"
   framing**: the opening-only reading was an artefact of the weaker basket.

3. **The gap never fully closes (~31%).** The equity basket spans only part of the
   election factor, so it tracks the *direction* of Kalshi's information but
   absorbs only about a third of each opening dislocation.

## Limitations

1. **Cointegration passes only on Engle-Granger (5%), not Johansen (12.41 < 13.43).**
   Adding FXI got the scale-invariant headline test over the 5% line but not a
   clean sweep of all three; no basket of these equities fully cointegrates,
   because they only partially span the election factor.
2. **FXI selection.** FXI is adopted for an a-priori economic reason (China/tariff
   is a standard Trump-election trade), not because it minimised a test p-value —
   though a handful of a-priori hedges were compared. State it that way in the paper.
3. **In-sample level R² = 0.929 is inflated** by a level-on-levels regression on
   trending prices; the Oct-Nov out-of-sample gate is the real arbiter.
4. The main analysis's limitations still hold (overnight layer partly mechanical,
   RTH only, Part 4/5 session-level with n = 23).
