# Why this folder was archived (2026-06-27)

These four hand-made pair deep-dives were **superseded by `leadlag/pipeline/`**, which
regenerates all 48 pairs (including these two Fed pairs) under the corrected, project-wide
methodology: ET timezone, ETF **log return** (not mid price), 09:30–16:00 ET market-hours
filter, resample+median outlier handling, calendar+event parallel with activity-chosen K,
probit direction test, BH-FDR, and df-based reliability tiering.

Auto-generated replacements live in `leadlag/pipeline/plots/`:
- `01_fed_nov_h0__vde/`  → `45_FEDDECISION-24NOV-H0_VDE_*`
- `04_fed_dec_c25__vis/` → `47_KXFEDDECISION-24DEC-C25_VIS_*`

Two specific defects in the archived versions (do not reuse their prose/figures):
1. `01_fed_nov_h0__vde/plot_fed_nov_vde.py` contained a **fabricated** "Fed-speak digestion"
   narrative for 2024-10-17 — no Fed official spoke that day (this was caught and corrected).
2. `01` and `04` event-zoom dates were **misaligned** with the contract's underlying event
   (zoomed weeks before the Nov 6-7 / Dec 17-18 FOMC).

Kept for provenance only.
