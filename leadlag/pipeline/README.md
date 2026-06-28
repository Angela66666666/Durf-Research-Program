# `leadlag/pipeline/` — File Overview

Main pipeline for the lead-lag analysis: high-frequency joint-lag regressions of
Kalshi prediction-market contracts against Vanguard sector ETFs.

**All project-wide conventions are defined once in [`leadlag_common.py`](leadlag_common.py):**
timezone always ET, ETF always in log return, keep only 09:30–16:00 ET regular hours,
outliers absorbed by resample + per-bar median, bar size and lag order K chosen by
contract activity, significance corrected with BH-FDR.

Run order is at the bottom ("Dependencies & run order").

---

## 1. Core (single source of truth)

| File | What it does |
|---|---|
| **`leadlag_common.py`** | Shared core, imported by every script. Timezone conversion, market-hours filter, outlier cleaning, bar/K selection, data loading (`load_kalshi`/`load_etf`), causal bar construction (`build_unified_xy`/`causal_bars`, right-edge median, no look-ahead), the joint-lag regression engine (`run_joint_lag_regression`, day fixed effects + day-clustered SE + ADL self-lag control), and BH-FDR correction (`add_fdr`). **Change this one file to change conventions globally.** |

## 2. Three main analyses (Kalshi → ETF)

| File | What it does | Output CSV |
|---|---|---|
| **`leadlag_calendar_time.py`** | **Calendar-time** axis: resample both series to fixed clock bars on a full regular-hours grid (quiet bars Δx=0); lag k = k×bar of real wall-clock time. Primary bar chosen by activity + full grid as robustness. | `leadlag_calendar_kalshi_etf.csv` |
| **`leadlag_event_time.py`** | **Event-time** axis: same unified construction as calendar (x=Δprob, y=ETF log return over the same pair of timepoints), but timepoints are only the bars where Kalshi traded (active events), so lag k = k events earlier. Runs in parallel with calendar; differs from it only in which timepoints count. | `leadlag_event_kalshi_etf.csv` |
| **`leadlag_probit.py`** | **Direction test**: reduce "can Kalshi predict ETF" to up/down only. One probit per lag, `Pr(ETF↑)=Φ(α+β·Δprob_{t-k})`; β>0 significant at k>0 = Kalshi leads directionally. Calendar + event both. | `leadlag_probit_kalshi_etf.csv` |

## 3. Robustness / auxiliary

| File | What it does | Output |
|---|---|---|
| **`leadlag_coarse_freq.py`** | Coarse-frequency robustness: re-run calendar at 30min/60min bars for all 48 pairs, answering "did we just not try low frequency?". | `leadlag_coarse_freq.csv` |
| **`leadlag_reliability.py`** | Judge each pair's reliability from statistics (effective N, residual df, median coefficient SE) into tiers (cannot-estimate / very-low / low / adequate), replacing the arbitrary trade-count cutoff. | `leadlag_reliability.csv` |

## 4. Classification (conclusion layer)

| File | What it does | Output |
|---|---|---|
| **`leadlag_classification.py`** | Group all 48 pairs by contract type / ETF sector / event kind / reliability tier and tally "who leads" per group, answering whether any directional lead concentrates in a category. | `leadlag_classification.csv`, `leadlag_classification_summary.md`, `plots/classification_summary.png` |
| **`leadlag_classification_summary.md`** | Editable summary tables + text conclusion. **Headline: no clean single-direction lead; of 48 pairs only 12 have adequate df, within which Kalshi-leads 1 / ETF-leads 4.** | — |

## 5. Figures / report

| File | What it does | Output |
|---|---|---|
| **`make_pair_plots.py`** | Base figures for all 48 pairs (two-line time series, lag-coefficient plot b_j vs j) + a "most-illustrative-first" ranking table. | `plots/{tag}_timeseries.png`/`_lagcoef.png`, `plots/pair_ranking.csv` |
| **`make_enhanced_plots.py`** | Four enhanced figures: session-bridged zoom (colored by rolling cross-correlation, red=Kalshi leads / blue=ETF leads), per-day segments, event-index view, and a "who-moves-first" glance. | `plots/{tag}_zoom2.png`/`_segments.png`/`_event.png`/`_leadglance.png` |
| **`make_pair_text.py`** | Data-driven text analysis per pair (expanded regression formulas, coefficient table, probit, verdict, reliability, verified real-world events). **`plots/{tag}_analysis.md` is the editable source**; do not re-run after finalizing (it overwrites manual edits). | `plots/{tag}_analysis.md`/`_text.png` |
| **`build_pdf.py`** | Assemble all 48 pairs into one ranked PDF (text page + figure page each; text pages rendered as vectors from the `.md`). | `leadlag_pairs_report.pdf` (96 pages) |

## 6. Subfolders

| Path | What it does |
|---|---|
| **`merge/`** | Merging similar contracts. `merge_leadlag.py` pools the 19 contracts into 4 **sign-aligned super-signals** (Trump-favorability / FOMC-easing / gas-above / approval-strength), pooling each member's own Δprob (**never concatenating price levels**) and re-running calendar+event+probit against the union of relevant ETFs to recover degrees of freedom. Pooled regression uses per-member fixed effects + day-clustered SE; lags are shifted within member-day only. Outputs `leadlag_merged_*.csv`. |
| **`plots/`** | All figure outputs (48 pairs × several figures + editable `.md` + ranking table + summary figure). |

## 7. Output CSV quick reference

| CSV | Row meaning | Rows |
|---|---|---|
| `leadlag_calendar_kalshi_etf.csv` | pair × candidate bar × lag | 1409 |
| `leadlag_event_kalshi_etf.csv` | pair × lag | 274 |
| `leadlag_probit_kalshi_etf.csv` | pair × mode × lag | 440 |
| `leadlag_classification.csv` | one row per pair (labels + lean) | 48 |
| `leadlag_reliability.csv` | one row per pair (reliability tier) | 48 |
| `leadlag_coarse_freq.csv` | pair × coarse frequency | — |
| `merge/leadlag_merged_*.csv` | super-signal group × ETF × … | (new) |

## 8. Dependencies & run order

```
significant_pairs.csv (in ../../regression/, main input: list of 48 pairs)
        │
        ▼
leadlag_common.py  ← core imported by every script
        │
        ├─ leadlag_calendar_time.py ─┐
        ├─ leadlag_event_time.py ────┤  three main analyses (can run in parallel)
        ├─ leadlag_probit.py ────────┘
        ├─ leadlag_coarse_freq.py  (robustness)
        │
        ▼
leadlag_reliability.py        (reads calendar/event CSVs → assigns reliability tier)
        ▼
leadlag_classification.py     (reads calendar/event/probit/reliability → grouped tally)
        ▼
make_pair_plots.py → make_enhanced_plots.py → make_pair_text.py   (figures + text)
        ▼
build_pdf.py                  (assembles leadlag_pairs_report.pdf)

merge/merge_leadlag.py        (independent branch: merge contracts, re-run the three)
```

> Conventions and the three research disciplines: timezone/units/bar unified project-wide
> (edit `leadlag_common.py`); real-world events must be WebSearch-verified with URLs;
> sample choices such as event-zoom windows must serve the research question. The old
> hand-made `pair_analyses/` has been archived to `../archive/pair_analyses_handmade/`
> (it contained a fabricated narrative and misaligned dates) and is superseded by this
> pipeline's auto-generated pages.
