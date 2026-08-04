# 5. Lead-Lag (high frequency)

## Goal of this folder

For the 48 candidate pairs found in `3. daily screen` (`significant_pairs.csv`),
pull **intraday** data for each Kalshi contract and its matched sector ETF and
test, at high frequency, **which side moves first** — does the prediction market
lead the ETF, or the other way around? Folder 4 already showed that daily data
has no power to answer this; this folder is where the question is actually
settled, on 1-minute-scale bars.

The question is attacked with several methods on two time axes, cross-checked,
tiered by data reliability, and assembled into reports.

Inputs (auto-located from the project root, which every script finds by walking
up to the folder containing `1. data/`):

- `3. daily screen/significant_pairs.csv` — the 48 pairs (contract × ETF + window)
- `1. data/kalshi/kalshi/trades/trades_*.parquet` — Kalshi trades
- `1. data/etf_hf/*_hf.parquet` — ETF high-frequency NBBO mids

---

## Conventions (defined once, in `engine/leadlag_common.py`)

Every script imports `leadlag_common.py`; changing it changes the whole project.

- **Timezone**: always America/New_York (ET); DST handled by DuckDB.
- **Regular hours only**: keep `09:30 ≤ t < 16:00` ET. Kalshi trades around the
  clock while ETFs are closed; comparing on a 24h clock would let Kalshi move
  while the ETF is frozen and manufacture a spurious "Kalshi leads".
- **Signals**: `x = Δprob` (Kalshi probability change = yes_price/100, differenced
  within a trading day) and `y = ETF log return = ln(mid_t) − ln(mid_{t-1})`.
- **Bars**: resample to a fixed bar, take the **median** inside each bar (right-edge,
  right-closed, so a bar labelled `t` summarizes `(t−Δ, t]` and uses only data ≤ t —
  causal, no look-ahead). Median absorbs one-tick spikes without deleting points.
- **Bar size and lag order K**: chosen per contract by its trading cadence
  (busier → finer bar, larger K).
- **Significance**: Benjamini–Hochberg FDR correction within each regression family.

---

## The three core formulas (all in `leadlag_common.py`)

**1. Per-coefficient joint-lag / ADL regression** (`run_joint_lag_regression`) —
the descriptive lead-lag: reports every lag coefficient individually.

```
y_t = a + Σ_{j=-K..+K} b_j·x_{t-j} + Σ_{i=1..p} φ_i·y_{t-i} + day_FE + ε_t

  b_j significant at j>0  → x's PAST predicts y   → Kalshi leads ETF
  b_j significant at j<0  → x's FUTURE            → ETF leads Kalshi
  j=0 = contemporaneous
  Σ φ_i·y_{t-i} = the effect's OWN lags (ADL), order p chosen by BIC — nets out
                  the ETF's own momentum so autocorrelation isn't mistaken for a lead
  x standardized; SE clustered by day (HC3 on single-day pairs)
```

**2. Standard Granger joint-Wald test** (`run_granger_direction`) — the **headline**.
One direction = one regression + one joint test = one p-value.

```
Kalshi → ETF:  etfret_t = a + Σ_{i=1..p} φ_i·etfret_{t-i}     (ETF's own past)
                            + Σ_{j=1..K} b_j·Δprob_{t-j}       (only the PAST of Δprob)
                            + day_FE + ε
               H0: b_1 = b_2 = … = b_K = 0   → reject ⇒ Kalshi Granger-leads ETF
ETF → Kalshi:  swap cause and effect, run again
```

Only the cause's **past** enters (j ≥ 1): the contemporaneous term j=0 (can't tell
direction) and future terms j<0 (that's the other direction) are excluded — this is
the textbook Granger test, and the joint Wald replaces counting 2K+1 separate
t-tests. **Standard errors use `hac-panel` (panel Newey–West, banded by K, blocked
per trading day)**, not day-clustering: many event contracts have only 1–few days
of data, where a day-clustered covariance is rank-deficient and the joint Wald
breaks (spurious p≈0); hac-panel is full-rank on single-day pairs and computes
Newey–West *within* each day (no overnight bleed). Because `x` and `y` are already
differenced (stationary), this is VAR-style Granger — **no cointegration/VECM
needed** (that is the separate Hasbrouck route in folder 6).

**3. Probit direction test** (`run_granger_probit`) — robustness: predict only
up/down, which is robust to outliers/magnitude.

```
Pr(ETF_up_t = 1) = Φ( α + Σ_{i=1..p} φ_i·up_{t-i} + Σ_{j=1..K} b_j·Δprob_{t-j} )
   up = 1[etfret > 0],  H0: b_1 = … = b_K = 0   (joint Wald, hac-panel)
```

---

## What each subfolder does

### `engine/` — the main pipeline

`leadlag_common.py` is the **engine** (the machinery above); it runs no analysis by
itself. The other files are **drivers**: each picks a time axis and/or method, loops
the 48 pairs, and writes one result CSV. Four of them run regressions; two only
summarize.

| Script | What it varies | Output (in `engine/`) |
|---|---|---|
| `leadlag_calendar_time.py` | **Clock-time axis** (lag k = k×bar of wall-clock); 5 candidate bars for robustness | `leadlag_calendar_kalshi_etf.csv` |
| `leadlag_event_time.py` | **Event axis** (lag k = k Kalshi-trade events earlier) | `leadlag_event_kalshi_etf.csv` |
| `leadlag_granger.py` ⭐ | **Joint Granger** (formula 2 + 3), calendar & event, both directions | `leadlag_granger_pairs.csv` |
| `leadlag_probit.py` | **Direction-only** probit per lag | `leadlag_probit_kalshi_etf.csv` |
| `leadlag_coarse_freq.py` | Re-runs calendar at **30min/60min** ("did we just not try low frequency?") | `leadlag_coarse_freq.csv` |
| `leadlag_reliability.py` | No regression — tiers each pair by effective sample size | `leadlag_reliability.csv` |
| `leadlag_classification.py` | No regression — groups pairs by type/sector/reliability; tallies who-leads both by per-coefficient counting **and** by the Granger joint-Wald verdict | `leadlag_classification.csv`, `leadlag_classification_summary.md` |

### `cross market/` — benchmark / placebo (standalone)

`generate_pairs.py` builds ETF↔ETF and contract↔contract pairing tables; then
`leadlag_cross_market.py` runs the same joint-lag idea on **ETF↔ETF**, **contract↔
contract**, and each series' **own autocorrelation** (Model B/C + self). Purpose:
context for the Kalshi→ETF result (e.g. how strong is generic co-movement /
self-persistence). Note: this branch uses its **own** regression code (not
`leadlag_common`), its output CSVs are an **older per-coefficient version**, and
**nothing downstream reads them** — it is a side investigation, not part of the
main report chain.

### `merge/` — pooled super-signals

To recover degrees of freedom, the 19 contracts are pooled into **4 sign-aligned
super-signals** (Trump-favorability / FOMC-easing / gas-above / approval-strength).
**Only each member's own Δprob is pooled** (never the price levels — different
thresholds aren't comparable); reverse contracts (Harris wins, hold, below) are
multiplied by −1 so `+Δ` means the same direction. The same calendar/event/probit
and Granger tests are re-run on the pool, with **per-member fixed effects**, lags
shifted **within (member × day)**, and day-clustered / hac-panel SEs.
`merge_leadlag.py` → the `leadlag_merged_*.csv`; `merge_granger.py` →
`leadlag_merged_granger.csv`; `dump_merge_pool.py` dumps the pooled panel.

### `reports/` + `plots/` — figures and the two reports

**Figure / text generators** (all figures go to `plots/`, merge figures to
`merge/plots/`): `make_pair_plots.py` (base figures + `plots/pair_ranking.csv`, the
most-data-first ordering everything uses), `make_enhanced_plots.py` (4 enhanced
figures per pair), `make_pair_text.py` (per-pair text pages), `make_granger_plots.py`
(the two Granger heatmaps).

**Two report builders, each producing ONE Markdown report (no PDF):**

| Builder | Report | Content |
|---|---|---|
| `build_granger_report.py` | **`leadlag_granger_report.md`** | the joint-Wald **headline** |
| `build_md.py` | **`leadlag_pairs_report.md`** | the **per-coefficient / probit** companion (also absorbs the pooled-signal per-coefficient section) |

Both reports share one layout: **method → core statistics & conclusion → MERGE
(pooled) → per-pair detail (most-data-first)**. `leadlag_classification.py` writes an
intermediate `leadlag_classification_summary.md` (kept in `engine/`) that the
per-coefficient report embeds; the two obsolete PDF builders are in `99. archive/`.

---

## Run order

```
3. daily screen/significant_pairs.csv   (48 pairs, the input)
        │
        ▼
engine/leadlag_common.py                (engine, imported by all)
        ├─ leadlag_calendar_time.py ─┐
        ├─ leadlag_event_time.py     │  four analyses (parallel)
        ├─ leadlag_granger.py  ⭐    │
        ├─ leadlag_probit.py ────────┘
        ├─ leadlag_coarse_freq.py       (robustness)
        ▼
   leadlag_reliability.py               (reads calendar/event → reliability tier)
        ▼
   leadlag_classification.py            (reads all → grouped tally)
        ▼
reports/ make_pair_plots → make_enhanced_plots → make_pair_text   (per-pair figures + text)
         make_granger_plots                                      (two heatmaps)
         build_md.py             → leadlag_pairs_report.md        (per-coefficient report)
         build_granger_report.py → leadlag_granger_report.md      (Granger headline report)

merge/merge_leadlag.py → merge_granger.py     (independent pooled branch)
cross market/  (independent benchmark branch — not wired into the reports)
```

---

## Key statistics & results

All direction verdicts below come from the **Granger joint-Wald** test (the headline
statistic); per-coefficient ADL and probit are descriptive backup only. `n_active` =
number of bars where the Kalshi side actually moved (the real identifying sample); a
joint test needs `n_active ≥ 11` even to run.

### Coverage — how many pairs are testable

| level | tested | Granger-estimable (calendar) | not estimable |
|---|---|---|---|
| single pairs | 48 | **27** | 21 — Kalshi barely traded (<11 active bars) |
| pooled signals × ETF | 37 | **37** | 0 |

### Single-pair Granger — direction counts by threshold (count = pairs)

| axis (pool) | cutoff | Kalshi→ETF | ETF→Kalshi |
|---|---|---|---|
| **calendar** (27) | raw p<0.05 | 8 | 1 |
| | raw p<0.10 | 10 | 1 |
| | raw p<0.15 | 11 | 1 |
| | **FDR p<0.05** | **7** | **0** |
| | FDR p<0.15 | 8 | 0 |
| **event** (21) | raw p<0.05 | 9 | 7 |
| | **FDR p<0.05** | **8** | **4** |
| | FDR p<0.15 | 9 | 7 |

→ Calendar is cleanly one-directional (**7 : 0**); the event axis is close to balanced.

### Single-pair Granger (calendar, FDR<0.05) × data reliability — **the caveat**

| reliability tier | # pairs | Kalshi-leads | ETF-leads | no-sig |
|---|---|---|---|---|
| Adequate (n_active ≥ 40) | 13 | **0** | 0 | 13 |
| Low-info | 1 | 0 | 0 | 1 |
| Very-low-info (n_active < 15) | 13 | **7** | 0 | 6 |
| Cannot-estimate | 21 | — | — | — |

→ **Every** Kalshi-lead sits in the very-low-info tier; 6 of the 7 are one contract
(`KXECKH276`, Harris 276 EV, **7 intraday moves**) × 5 correlated ETFs — one
observation replicated, not 5 confirmations. **The adequate-data single pairs show no
lead.**

### Merge (pooled super-signals) Granger — calendar, FDR<0.05

Pooling the 19 contracts into 4 sign-aligned super-signals recovers degrees of freedom.

| super-signal | ETFs tested | median n_active | Kalshi-leads | ETF-leads |
|---|---|---|---|---|
| ELECTION_trump_fav | 9 | **137** (adequate) | 2 — VFH, VDC | 0 |
| FOMC_easing | 9 | **654** (adequate) | 1 — VPU | 0 |
| GAS_above | 11 | 20 (thin) | 6 | 0 |
| APPROVAL_strength | 8 | 12 (very thin) | 0 | 0 |
| **total** | **37** | | **9** | **0** |

→ Strictly one-directional (**9 : 0**), and this time some of it is on **adequate**
data (ELECTION, FOMC) — so once enough data is pooled, the lead does **not** vanish.

## Bottom line (two layers)

1. **Single contracts** — the only Kalshi→ETF leads are on very-sparsely-traded
   contracts (dominated by one with 7 intraday moves); adequately-sampled single
   pairs show nothing. Per-contract evidence is untrustworthy on its own.
2. **Pooled super-signals** — pooling recovers adequate data, and there the Granger
   lead is still strictly one-directional (9 Kalshi-leads, **0** ETF-leads),
   including on adequate-data signals (ELECTION, FOMC).

Net: **weak but directionally consistent** evidence of a Kalshi→ETF lead — and never
the reverse. Report it as *suggestive*, always paired with the sparse single-pair
caveat, never as a decisive "prediction markets lead stock markets" claim. Sources:
single pairs `engine/leadlag_granger_pairs.csv`, pooled `merge/leadlag_merged_granger.csv`.
