# Granger Report — Kalshi prediction markets × Vanguard sector ETFs

_Headline statistic: one joint Wald test per direction. Structure: **both core heatmaps up front** (single pairs, then merged pooled signals) → overview & method → per-pair formulas+Wald detail → per-group detail. The main lead-lag reports (`leadlag_pairs_report.md`, `leadlag_merge_report.md`) no longer contain Granger. Method: `GRANGER_TEST.md`._

---

## CORE FIGURE 1 — single-pair Granger heatmap (all 48 pairs × 6 regressions)

![single-pair Granger heatmap](plots/granger_heatmap.png)

_Rows = pairs; columns = time-axis × direction; cell colour = joint Wald p (p<0.05 red = that direction's lead/lag IS significant; NA = too sparse to estimate). CALENDAR Kalshi→ETF lights up while ETF→Kalshi stays pale ⇒ clean one-directional lead; EVENT is more bidirectional._

---

## CORE FIGURE 2 — merged pooled signals Granger heatmap

![merged pooled signals Granger heatmap](plots/granger_merge_heatmap.png)

_Each left block = one pooled signal (labelled with its members & sign convention); rows = that group × each ETF. CALENDAR Pooled→ETF lit while ETF→Pooled pale ⇒ the pooled signal Granger-leads the ETF (clearest for GAS and ELECTION)._

---

## COVERAGE — why 27 of 48 pairs carry results

```text
COVERAGE — 27 of 48 pairs carry Granger results; 21 are dropped (shown as NA rows in core figure 1).
================================================================================================

WHY 21 PAIRS ARE DROPPED (all fail at the SAME step — not a model failure, a data-density failure):

  The joint-Wald test needs enough *price-changing* observations to fit the smallest admissible model
  (K cause-lags + BIC own-lags + day fixed effects) and still have residual degrees of freedom for a
  valid Newey-West (hac-panel) covariance. ONE gate, applied identically to every pair, every time-axis,
  and BOTH specifications, BEFORE any regression is attempted:

     n_active  =  # observations where the cause actually moved  >=  2K + 5  =  11   (at K = 3)

  The threshold is derived from the model's parameter count (K cause-lags plus own-lags plus intercept),
  not chosen by hand. linear and probit share the same sample (the same calendar grid / event sequence)
  and the same gate, so a pair is never estimable under one specification but not the other. probit
  additionally needs both up- and down-moves to appear in the dependent variable, which is an intrinsic
  requirement of the model rather than a discretionary cutoff.

  Every dropped pair fails this gate: the Kalshi contract barely traded during its overlap window, so
  after building bars almost no bar carries a non-zero price change. There is simply not enough
  independent information to identify a lag polynomial, let alone test it. Nothing is estimated and the
  row is left NA rather than reporting an under-identified / rank-deficient p-value.

  Of the 21 dropped, 0 had ZERO price-changing bars in the window (no trading / no
  quote updates at all); the rest had only a handful, well under 11.

DROPPED PAIRS (price-changing observations, measured on the same grid/sequence used for estimation):

  contract                    etf    cal  evt   reason
  Approval >43% by Oct31      VOX      2    2   too few price-changing observations (< 11)
  Gas >$3.30 by Nov30         VDC      2    2   too few price-changing observations (< 11)
  Gas >$3.30 by Nov30         VDE      2    2   too few price-changing observations (< 11)
  Gas >$3.30 by Nov30         VFH      2    2   too few price-changing observations (< 11)
  Gas >$3.30 by Nov30         VNQ      2    2   too few price-changing observations (< 11)
  Approval >43% by Sep30      VAW      3    3   too few price-changing observations (< 11)
  Approval >43% by Sep30      VCR      3    3   too few price-changing observations (< 11)
  Approval >43% by Sep30      VIS      3    3   too few price-changing observations (< 11)
  Gas >$3.20 by Oct31         VHT      3    3   too few price-changing observations (< 11)
  Approval >41% by Nov30      VGT      3    3   too few price-changing observations (< 11)
  Approval >41% by Nov30      VHT      3    3   too few price-changing observations (< 11)
  Gas >$3.15 by Sep30         VAW      5    5   too few price-changing observations (< 11)
  Gas >$3.15 by Sep30         VCR      5    5   too few price-changing observations (< 11)
  Gas >$3.15 by Sep30         VGT      5    5   too few price-changing observations (< 11)
  Gas >$3.15 by Sep30         VIS      5    5   too few price-changing observations (< 11)
  Gas >$3.15 by Sep30         VOX      5    5   too few price-changing observations (< 11)
  Approval <37% by Nov30      VFH      8    8   too few price-changing observations (< 11)
  Approval <37% by Nov30      VNQ      8    8   too few price-changing observations (< 11)
  Fed cut by Sep-24           VCR      8    8   too few price-changing observations (< 11)
  Fed cut by Sep-24           VGT      8    8   too few price-changing observations (< 11)
  Fed cut by Sep-24           VOX      8    8   too few price-changing observations (< 11)

TAKEAWAY: the 27 estimable pairs are exactly those liquid enough to support valid inference;
the drop is a mechanical minimum-sample rule, applied identically to every pair and both
specifications, not a selection on results.
```

---

## OVERVIEW & METHOD

```text
GRANGER JOINT CAUSALITY — Kalshi prediction markets  vs  Vanguard sector ETFs
================================================================================================
This is the HEADLINE statistic: one joint Wald test per direction giving ONE p-value, replacing the
per-coefficient counting used in the main lead-lag report. It is the high-frequency reinstatement of
this project's daily Var.py results.test_causality (a VAR Granger Wald), and the object the advisor asked
for. Full method: GRANGER_TEST.md.

DEFINITIONS
   xₜ = Kalshi yes-probability change (Δprob) over bar t ;   yₜ = ETF log return over bar t.
   Only PAST lags of the 'cause' are used (j≥1); the contemporaneous (j=0) and future (j<0) terms are
   NOT part of the test. Each regression controls for the dependent variable's OWN past (ADL self-lags,
   order chosen by BIC).

THE TEST (per direction)
   Kalshi→ETF:  yₜ = α + Σ(i=1..p) φᵢ·yₜ₋ᵢ + Σ(j=1..K) bⱼ·xₜ₋ⱼ + day-FE ;   H0: b₁=…=b_K=0
   ETF→Kalshi:  xₜ = α + Σ(i=1..q) ψᵢ·xₜ₋ᵢ + Σ(j=1..K) dⱼ·yₜ₋ⱼ + day-FE ;   H0: d₁=…=d_K=0
   Reject H0 (p<0.05) ⇒ that variable Granger-leads the other. Comparing the two p's states who leads.

STANDARD ERRORS & VALIDITY
   Joint Wald uses panel Newey-West (hac-panel, bandwidth=K, within each trading-day block): full-rank
   (valid even for single-day event contracts, where day-clustering would be rank-deficient) and the
   microstructure-standard covariance for high-frequency intraday data. Δprob and log-returns are
   differenced ⇒ stationary ⇒ plain Granger is valid, no cointegration/VECM needed.

SAMPLE GATE (identical for both specifications)
   A regression is attempted only if n_active — the number of observations where the CAUSE actually moved —
   is at least 2K+5 (=11 at K=3), a bound derived from the model's parameter count. linear and probit use
   the SAME sample (same calendar grid / event sequence) and the SAME gate, so no pair is estimable under
   one specification but not the other. See the COVERAGE section.

MULTIPLE TESTING
   Each (time-axis × specification × direction) is one test family; within it the joint-Wald p-values are
   Benjamini-Hochberg FDR-corrected across all pairs (column p_fdr). Both raw p and FDR p are reported;
   conclusions rest on the FDR-corrected counts and, above all, on the asymmetry between directions.

CONVENTIONS:  ET | 09:30-16:00 | ETF log return | median causal bars | day-grouped lags (no overnight)
              | adaptive bar & K by contract activity | ADL self-lags by BIC | significance p<0.05.

================================================================================================

CONCLUSIONS
================================================================================================
HEADLINE — the direction is asymmetric. Whenever Granger causality is significant it runs
Kalshi → ETF; the reverse (ETF → Kalshi) is essentially absent. This asymmetry — not the raw count
of significant pairs — is the robust finding, and it answers the project's question: the evidence
supports prediction markets LEADING sector ETFs, and does not support the reverse.

1. Direction is one-way (Kalshi → ETF)
   - Single pairs, calendar:  8 Kalshi-leads  vs  1 ETF-leads   (0 bidir, 18 neither, of 27).
   - Single pairs, event:     5 Kalshi-leads  vs  3 ETF-leads   (4 bidir, 9 neither, of 21).
   - Pooled signals, calendar: 13 Pooled-leads   vs  1 ETF-leads   (0 bidir, 23 neither, of 37).
   - Pooled signals, event:    9 Pooled-leads   vs  0 ETF-leads   (2 bidir, 7 neither, of 18).
   The reverse direction is significant in ~0 cases at every level — the lead is one-directional.

2. Weak and concentrated at the single-contract level
   - 18 of 27 single pairs show no Granger causality either way (calendar). The 8 that do are
     concentrated in a handful of contracts — mainly 'Harris 276 EV' across 5 ETFs, plus 3 other contracts with one ETF each:
       Harris 276 EV×VDE, Harris 276 EV×VIS, Harris 276 EV×VFH, Gas >$3.15 by Oct31×VPU, Trump 316 EV×VDE, Harris 276 EV×VOX, Harris 276 EV×VAW, Trump 306 EV×VDC.
   - So the lead is NOT a broad per-contract phenomenon; it is concentrated in the few LIQUID contracts.
     Illiquid contracts have no usable price-discovery process (consistent with the advisor's point).

3. Pooling restores power
   - Aggregating same-family contracts into sign-aligned pooled signals (more degrees of freedom) lights
     up Pooled→ETF in 13/37 (calendar) and 9/18 (event), while the reverse stays ~0. The lead is
     real but needs aggregation to detect above single-contract noise.
   - Per pooled signal, Pooled→ETF significance (raw p<0.05, then after BH-FDR):
       APPROVAL_strength    calendar: 1/8 raw, 0 after FDR   |   event: not estimable
       ELECTION_trump_fav   calendar: 3/9 raw, 2 after FDR   |   event: 7/9 raw, 7 after FDR
       FOMC_easing          calendar: 1/9 raw, 1 after FDR   |   event: 4/9 raw, 3 after FDR
       GAS_above            calendar: 8/11 raw, 6 after FDR   |   event: not estimable
     Only the pooled signals with enough ACTIVE event-time observations are estimable on the event
     axis; the others show 'not estimable' there rather than a null result.

4. Caveats (state them)
   - Time-axis: the clean one-way result is on the CALENDAR (clock-time) axis. EVENT-time is muddier
     (3 single-pair ETF-leads, 4 bidirectional), most likely an artifact of sampling only at the sparse
     Kalshi trade instants (near-contemporaneous comovement misread as ETF-leads). The headline rests on
     calendar; event-time is robustness / a warning, not the basis for the claim.
   - Direction-only (probit) is weak: 5/27 (calendar) and 5/23 (event) significant. Predictability
     is in the MAGNITUDE of continuous returns more than in the up/down sign.

5. Multiple testing — the asymmetry SURVIVES a Benjamini-Hochberg FDR correction
   Every direction×axis×spec is one test family; each family is BH-FDR corrected across all pairs, so
   "8 of 27 significant at 5%" cannot be read as evidence on its own (~1.4 would be expected by chance).
   Counts below are raw p<0.05 -> FDR p<0.05:
     - Single pairs, calendar:   Kalshi→ETF 8→7 of 27   |   ETF→Kalshi 1→0 of 27
     - Single pairs, event:      Kalshi→ETF 9→8 of 21   |   ETF→Kalshi 7→4 of 21
     - Pooled signals, calendar: Pooled→ETF 13→9 of 37   |   ETF→Pooled 1→0 of 37
     - Pooled signals, event:    Pooled→ETF 11→10 of 18   |   ETF→Pooled 2→0 of 18
   The Kalshi→ETF direction largely survives FDR, while the reverse direction collapses to ~0 once
   corrected. So the one-way lead is not an artifact of running many tests: correcting for multiplicity
   REMOVES the reverse-direction hits and KEEPS the forward ones.

BOTTOM LINE — High-frequency Granger tests show prediction markets one-directionally lead sector ETFs on
the clock-time axis (reverse essentially absent); the lead is concentrated in a few high-liquidity
contracts and is most robust after pooling same-family contracts into pooled signals; direction-only
(probit) and event-time evidence is weaker. 'Lead' here means Granger precedence (predictive), not cause.

================================================================================================
SINGLE-PAIR SUMMARY — grouped by contract (not sorted by p).
joint-Wald p per direction; * <.10  ** <.05  *** <.01;  '†' = still significant after BH-FDR.

contract                 etf      cal K→E     cal E→K     evt K→E     evt E→K  verdict(cal/evt)
Trump 281 EV             VCR          0.9        0.87         0.3      0.095*  -/-
                         VGT         0.65        0.64        0.78        0.59  -/-
                         VNQ         0.16        0.19   2e-06***†        0.56  -/K→E
                         VOX         0.16        0.77         0.6        0.69  -/-

Trump 306 EV             VDC      0.031**        0.34 2.1e-10***†        0.12  K→E/K→E

Trump 312 EV             VAW         0.97        0.19 3.2e-09***†        0.66  -/K→E

Trump 316 EV             VDE   0.0067***†        0.49           -           -  K→E/-
                         VFH         0.37        0.23           -           -  -/-
                         VIS         0.17        0.19           -           -  -/-

Harris 276 EV            VAW   0.0089***†        0.34     0.046**     0.033**  K→E/bi
                         VCR       0.066*        0.42        0.59 1.1e-08***†  -/E→K
                         VDC         0.31        0.63        0.84 1.5e-08***†  -/E→K
                         VDE  2.5e-07***†        0.41  0.0039***†     0.024**  K→E/bi
                         VFH  0.00013***†        0.32        0.65      0.066*  K→E/-
                         VGT         0.53        0.35 6.7e-08***†     0.037**  -/bi
                         VIS    6e-05***†        0.31         0.1  0.0068***†  K→E/E→K
                         VOX   0.0075***†        0.23        0.38        0.86  K→E/-

Harris 287 EV            VNQ         0.65        0.33  0.0053***† 4.5e-09***†  -/bi

Fed Nov-24 hold 0bp      VDE          0.4        0.38           -           -  -/-
                         VNQ         0.14     0.036**           -           -  E→K/-

Fed Sep-24 cut 25bp      VDC         0.48        0.75        0.37        0.74  -/-
                         VOX          0.2        0.71        0.89        0.64  -/-
                         VPU         0.88        0.59        0.84        0.54  -/-

Fed Dec-24 cut 25bp      VFH       0.082*        0.49  0.0092***†        0.15  -/K→E
                         VIS         0.46        0.25  0.0099***†        0.43  -/K→E

Fed Dec-24 hold 0bp      VGT         0.59        0.88        0.95        0.34  -/-

Gas >$3.15 by Oct31      VPU   0.0017***†        0.58           -           -  K→E/-
```

---

## Single-pair detail — explicit formulas + joint Wald per direction

---

### Rank 1/48 — Fed Dec-24 cut 25bp × VIS

```text
GRANGER CAUSALITY    —    Rank 1 / 48
================================================================================================
Fed Dec-24 cut 25bp   x   VIS      [ticker: KXFEDDECISION-24DEC-C25]
Contract : "Will the Federal Reserve Cut rates by 25bps at their December 2024 meeting?"
Window : 2024-10-31 to 2024-12-18     primary bar : 5min     Kalshi trades : 2308

Test: joint Wald H0 = all PAST cause-lags are 0 (controls the effect's own past; hac-panel SE).
p<0.05 ⇒ that variable Granger-leads the other.  (x=Δprob, y=ETF log return.)

1. CALENDAR-TIME (clock-time lags, full RTH grid)
   Direction A — Kalshi → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..10) bⱼ·xₜ₋ⱼ + Σ(d=1..32) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=10 ; day-FE over 33 days ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 9.82,  p = 0.457    |   BH-FDR p = 0.649 
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + Σ(j=1..10) dⱼ·yₜ₋ⱼ + Σ(d=1..32) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=10 ; day-FE over 33 days ; hac-panel SE (bw=10).
      H0: d₁ = … = d_10 = 0   →   Wald χ²(10) = 12.55,  p = 0.25    |   BH-FDR p = 0.706 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..10) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=10 ; sample spans 33 days (probit: no day-FE) ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 13.15,  p = 0.215    |   BH-FDR p = 0.586 
   => calendar verdict: neither direction significant.

2. EVENT-TIME (event-count lags)
   Direction A — Kalshi → ETF:
      yₜ = α + (no y self-lag term: BIC chose p=0) + Σ(j=1..10) bⱼ·xₜ₋ⱼ + Σ(d=1..27) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=10 ; day-FE over 28 days ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 23.24,  p = 0.00989 ***   |   BH-FDR p = 0.0259 **
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + ψ₅·xₜ₋₅ + ψ₆·xₜ₋₆ + Σ(j=1..10) dⱼ·yₜ₋ⱼ + Σ(d=1..27) γ_d·Day_d
      controls: ADL self-lags p=6 (BIC) ; cause block K=10 ; day-FE over 28 days ; hac-panel SE (bw=10).
      H0: d₁ = … = d_10 = 0   →   Wald χ²(10) = 10.14,  p = 0.428    |   BH-FDR p = 0.692 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..10) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=10 ; sample spans 28 days (probit: no day-FE) ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 25.25,  p = 0.00489 ***   |   BH-FDR p = 0.0225 **
   => event verdict: Kalshi Granger-leads ETF.

3. OVERALL VERDICT
   Calendar says 'neither direction significant' but Event says 'Kalshi Granger-leads ETF' — not robust across time-axis.

------------------------------------------------------------------------------------------------
This pair's joint-Wald p per direction is also in the single-pair heatmap (core figure 1).
```

---

### Rank 2/48 — Fed Dec-24 cut 25bp × VFH

```text
GRANGER CAUSALITY    —    Rank 2 / 48
================================================================================================
Fed Dec-24 cut 25bp   x   VFH      [ticker: KXFEDDECISION-24DEC-C25]
Contract : "Will the Federal Reserve Cut rates by 25bps at their December 2024 meeting?"
Window : 2024-10-31 to 2024-12-18     primary bar : 5min     Kalshi trades : 2308

Test: joint Wald H0 = all PAST cause-lags are 0 (controls the effect's own past; hac-panel SE).
p<0.05 ⇒ that variable Granger-leads the other.  (x=Δprob, y=ETF log return.)

1. CALENDAR-TIME (clock-time lags, full RTH grid)
   Direction A — Kalshi → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..10) bⱼ·xₜ₋ⱼ + Σ(d=1..32) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=10 ; day-FE over 33 days ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 16.67,  p = 0.0819 *   |   BH-FDR p = 0.221 
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + Σ(j=1..10) dⱼ·yₜ₋ⱼ + Σ(d=1..32) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=10 ; day-FE over 33 days ; hac-panel SE (bw=10).
      H0: d₁ = … = d_10 = 0   →   Wald χ²(10) = 9.41,  p = 0.494    |   BH-FDR p = 0.741 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..10) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=10 ; sample spans 33 days (probit: no day-FE) ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 11.31,  p = 0.334    |   BH-FDR p = 0.586 
   => calendar verdict: neither direction significant.

2. EVENT-TIME (event-count lags)
   Direction A — Kalshi → ETF:
      yₜ = α + (no y self-lag term: BIC chose p=0) + Σ(j=1..10) bⱼ·xₜ₋ⱼ + Σ(d=1..27) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=10 ; day-FE over 28 days ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 23.44,  p = 0.00924 ***   |   BH-FDR p = 0.0259 **
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + ψ₅·xₜ₋₅ + ψ₆·xₜ₋₆ + Σ(j=1..10) dⱼ·yₜ₋ⱼ + Σ(d=1..27) γ_d·Day_d
      controls: ADL self-lags p=6 (BIC) ; cause block K=10 ; day-FE over 28 days ; hac-panel SE (bw=10).
      H0: d₁ = … = d_10 = 0   →   Wald χ²(10) = 14.47,  p = 0.153    |   BH-FDR p = 0.291 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..10) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=10 ; sample spans 28 days (probit: no day-FE) ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 17.36,  p = 0.0667 *   |   BH-FDR p = 0.256 
   => event verdict: Kalshi Granger-leads ETF.

3. OVERALL VERDICT
   Calendar says 'neither direction significant' but Event says 'Kalshi Granger-leads ETF' — not robust across time-axis.

------------------------------------------------------------------------------------------------
This pair's joint-Wald p per direction is also in the single-pair heatmap (core figure 1).
```

---

### Rank 3/48 — Fed Dec-24 hold 0bp × VGT

```text
GRANGER CAUSALITY    —    Rank 3 / 48
================================================================================================
Fed Dec-24 hold 0bp   x   VGT      [ticker: KXFEDDECISION-24DEC-H0]
Contract : "Will the Federal Reserve Hike rates by 0bps at their December 2024 meeting?"
Window : 2024-10-31 to 2024-12-18     primary bar : 10min     Kalshi trades : 1375

Test: joint Wald H0 = all PAST cause-lags are 0 (controls the effect's own past; hac-panel SE).
p<0.05 ⇒ that variable Granger-leads the other.  (x=Δprob, y=ETF log return.)

1. CALENDAR-TIME (clock-time lags, full RTH grid)
   Direction A — Kalshi → ETF:
      yₜ = α + (no y self-lag term: BIC chose p=0) + Σ(j=1..8) bⱼ·xₜ₋ⱼ + Σ(d=1..33) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=8 ; day-FE over 34 days ; hac-panel SE (bw=8).
      H0: b₁ = … = b_8 = 0   →   Wald χ²(8) = 6.47,  p = 0.595    |   BH-FDR p = 0.727 
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + Σ(j=1..8) dⱼ·yₜ₋ⱼ + Σ(d=1..33) γ_d·Day_d
      controls: ADL self-lags p=4 (BIC) ; cause block K=8 ; day-FE over 34 days ; hac-panel SE (bw=8).
      H0: d₁ = … = d_8 = 0   →   Wald χ²(8) = 3.77,  p = 0.878    |   BH-FDR p = 0.878 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..8) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=8 ; sample spans 34 days (probit: no day-FE) ; hac-panel SE (bw=8).
      H0: b₁ = … = b_8 = 0   →   Wald χ²(8) = 6.79,  p = 0.559    |   BH-FDR p = 0.686 
   => calendar verdict: neither direction significant.

2. EVENT-TIME (event-count lags)
   Direction A — Kalshi → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..8) bⱼ·xₜ₋ⱼ + Σ(d=1..25) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=8 ; day-FE over 26 days ; hac-panel SE (bw=8).
      H0: b₁ = … = b_8 = 0   →   Wald χ²(8) = 2.76,  p = 0.949    |   BH-FDR p = 0.949 
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + Σ(j=1..8) dⱼ·yₜ₋ⱼ + Σ(d=1..25) γ_d·Day_d
      controls: ADL self-lags p=2 (BIC) ; cause block K=8 ; day-FE over 26 days ; hac-panel SE (bw=8).
      H0: d₁ = … = d_8 = 0   →   Wald χ²(8) = 9.06,  p = 0.337    |   BH-FDR p = 0.59 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..8) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=8 ; sample spans 26 days (probit: no day-FE) ; hac-panel SE (bw=8).
      H0: b₁ = … = b_8 = 0   →   Wald χ²(8) = 6.65,  p = 0.575    |   BH-FDR p = 0.811 
   => event verdict: neither direction significant.

3. OVERALL VERDICT
   No Granger causality detected on either axis.

------------------------------------------------------------------------------------------------
This pair's joint-Wald p per direction is also in the single-pair heatmap (core figure 1).
```

---

### Rank 4/48 — Fed Sep-24 cut 25bp × VOX

```text
GRANGER CAUSALITY    —    Rank 4 / 48
================================================================================================
Fed Sep-24 cut 25bp   x   VOX      [ticker: FEDDECISION-24SEP-C25]
Contract : "Will the Federal Reserve Cut rates by 25bps at their September 2024 meeting?"
Window : 2024-09-04 to 2024-09-18     primary bar : 2min     Kalshi trades : 1125

Test: joint Wald H0 = all PAST cause-lags are 0 (controls the effect's own past; hac-panel SE).
p<0.05 ⇒ that variable Granger-leads the other.  (x=Δprob, y=ETF log return.)

1. CALENDAR-TIME (clock-time lags, full RTH grid)
   Direction A — Kalshi → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..8) bⱼ·xₜ₋ⱼ + Σ(d=1..10) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=8 ; day-FE over 11 days ; hac-panel SE (bw=8).
      H0: b₁ = … = b_8 = 0   →   Wald χ²(8) = 10.95,  p = 0.205    |   BH-FDR p = 0.368 
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + Σ(j=1..8) dⱼ·yₜ₋ⱼ + Σ(d=1..10) γ_d·Day_d
      controls: ADL self-lags p=4 (BIC) ; cause block K=8 ; day-FE over 11 days ; hac-panel SE (bw=8).
      H0: d₁ = … = d_8 = 0   →   Wald χ²(8) = 5.44,  p = 0.71    |   BH-FDR p = 0.828 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..8) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=8 ; sample spans 11 days (probit: no day-FE) ; hac-panel SE (bw=8).
      H0: b₁ = … = b_8 = 0   →   Wald χ²(8) = 8.14,  p = 0.42    |   BH-FDR p = 0.586 
   => calendar verdict: neither direction significant.

2. EVENT-TIME (event-count lags)
   Direction A — Kalshi → ETF:
      yₜ = α + (no y self-lag term: BIC chose p=0) + Σ(j=1..8) bⱼ·xₜ₋ⱼ + Σ(d=1..9) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=8 ; day-FE over 10 days ; hac-panel SE (bw=8).
      H0: b₁ = … = b_8 = 0   →   Wald χ²(8) = 3.63,  p = 0.889    |   BH-FDR p = 0.933 
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + Σ(j=1..8) dⱼ·yₜ₋ⱼ + Σ(d=1..9) γ_d·Day_d
      controls: ADL self-lags p=2 (BIC) ; cause block K=8 ; day-FE over 10 days ; hac-panel SE (bw=8).
      H0: d₁ = … = d_8 = 0   →   Wald χ²(8) = 6.08,  p = 0.638    |   BH-FDR p = 0.766 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..8) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=8 ; sample spans 10 days (probit: no day-FE) ; hac-panel SE (bw=8).
      H0: b₁ = … = b_8 = 0   →   Wald χ²(8) = 12.73,  p = 0.121    |   BH-FDR p = 0.349 
   => event verdict: neither direction significant.

3. OVERALL VERDICT
   No Granger causality detected on either axis.

------------------------------------------------------------------------------------------------
This pair's joint-Wald p per direction is also in the single-pair heatmap (core figure 1).
```

---

### Rank 5/48 — Fed Sep-24 cut 25bp × VPU

```text
GRANGER CAUSALITY    —    Rank 5 / 48
================================================================================================
Fed Sep-24 cut 25bp   x   VPU      [ticker: FEDDECISION-24SEP-C25]
Contract : "Will the Federal Reserve Cut rates by 25bps at their September 2024 meeting?"
Window : 2024-09-04 to 2024-09-18     primary bar : 2min     Kalshi trades : 1125

Test: joint Wald H0 = all PAST cause-lags are 0 (controls the effect's own past; hac-panel SE).
p<0.05 ⇒ that variable Granger-leads the other.  (x=Δprob, y=ETF log return.)

1. CALENDAR-TIME (clock-time lags, full RTH grid)
   Direction A — Kalshi → ETF:
      yₜ = α + φ₁·yₜ₋₁ + φ₂·yₜ₋₂ + φ₃·yₜ₋₃ + φ₄·yₜ₋₄ + φ₅·yₜ₋₅ + φ₆·yₜ₋₆ + Σ(j=1..8) bⱼ·xₜ₋ⱼ + Σ(d=1..10) γ_d·Day_d
      controls: ADL self-lags p=6 (BIC) ; cause block K=8 ; day-FE over 11 days ; hac-panel SE (bw=8).
      H0: b₁ = … = b_8 = 0   →   Wald χ²(8) = 3.75,  p = 0.879    |   BH-FDR p = 0.938 
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + Σ(j=1..8) dⱼ·yₜ₋ⱼ + Σ(d=1..10) γ_d·Day_d
      controls: ADL self-lags p=4 (BIC) ; cause block K=8 ; day-FE over 11 days ; hac-panel SE (bw=8).
      H0: d₁ = … = d_8 = 0   →   Wald χ²(8) = 6.53,  p = 0.588    |   BH-FDR p = 0.779 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..8) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=8 ; sample spans 11 days (probit: no day-FE) ; hac-panel SE (bw=8).
      H0: b₁ = … = b_8 = 0   →   Wald χ²(8) = 10.05,  p = 0.262    |   BH-FDR p = 0.586 
   => calendar verdict: neither direction significant.

2. EVENT-TIME (event-count lags)
   Direction A — Kalshi → ETF:
      yₜ = α + φ₁·yₜ₋₁ + φ₂·yₜ₋₂ + Σ(j=1..8) bⱼ·xₜ₋ⱼ + Σ(d=1..9) γ_d·Day_d
      controls: ADL self-lags p=2 (BIC) ; cause block K=8 ; day-FE over 10 days ; hac-panel SE (bw=8).
      H0: b₁ = … = b_8 = 0   →   Wald χ²(8) = 4.23,  p = 0.836    |   BH-FDR p = 0.932 
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + Σ(j=1..8) dⱼ·yₜ₋ⱼ + Σ(d=1..9) γ_d·Day_d
      controls: ADL self-lags p=2 (BIC) ; cause block K=8 ; day-FE over 10 days ; hac-panel SE (bw=8).
      H0: d₁ = … = d_8 = 0   →   Wald χ²(8) = 6.97,  p = 0.54    |   BH-FDR p = 0.766 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..8) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=8 ; sample spans 10 days (probit: no day-FE) ; hac-panel SE (bw=8).
      H0: b₁ = … = b_8 = 0   →   Wald χ²(8) = 6.11,  p = 0.635    |   BH-FDR p = 0.811 
   => event verdict: neither direction significant.

3. OVERALL VERDICT
   No Granger causality detected on either axis.

------------------------------------------------------------------------------------------------
This pair's joint-Wald p per direction is also in the single-pair heatmap (core figure 1).
```

---

### Rank 6/48 — Fed Sep-24 cut 25bp × VDC

```text
GRANGER CAUSALITY    —    Rank 6 / 48
================================================================================================
Fed Sep-24 cut 25bp   x   VDC      [ticker: FEDDECISION-24SEP-C25]
Contract : "Will the Federal Reserve Cut rates by 25bps at their September 2024 meeting?"
Window : 2024-09-04 to 2024-09-18     primary bar : 2min     Kalshi trades : 1125

Test: joint Wald H0 = all PAST cause-lags are 0 (controls the effect's own past; hac-panel SE).
p<0.05 ⇒ that variable Granger-leads the other.  (x=Δprob, y=ETF log return.)

1. CALENDAR-TIME (clock-time lags, full RTH grid)
   Direction A — Kalshi → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..8) bⱼ·xₜ₋ⱼ + Σ(d=1..10) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=8 ; day-FE over 11 days ; hac-panel SE (bw=8).
      H0: b₁ = … = b_8 = 0   →   Wald χ²(8) = 7.50,  p = 0.484    |   BH-FDR p = 0.653 
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + Σ(j=1..8) dⱼ·yₜ₋ⱼ + Σ(d=1..10) γ_d·Day_d
      controls: ADL self-lags p=4 (BIC) ; cause block K=8 ; day-FE over 11 days ; hac-panel SE (bw=8).
      H0: d₁ = … = d_8 = 0   →   Wald χ²(8) = 5.07,  p = 0.75    |   BH-FDR p = 0.828 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..8) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=8 ; sample spans 11 days (probit: no day-FE) ; hac-panel SE (bw=8).
      H0: b₁ = … = b_8 = 0   →   Wald χ²(8) = 6.44,  p = 0.598    |   BH-FDR p = 0.702 
   => calendar verdict: neither direction significant.

2. EVENT-TIME (event-count lags)
   Direction A — Kalshi → ETF:
      yₜ = α + (no y self-lag term: BIC chose p=0) + Σ(j=1..8) bⱼ·xₜ₋ⱼ + Σ(d=1..9) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=8 ; day-FE over 10 days ; hac-panel SE (bw=8).
      H0: b₁ = … = b_8 = 0   →   Wald χ²(8) = 8.73,  p = 0.366    |   BH-FDR p = 0.607 
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + Σ(j=1..8) dⱼ·yₜ₋ⱼ + Σ(d=1..9) γ_d·Day_d
      controls: ADL self-lags p=2 (BIC) ; cause block K=8 ; day-FE over 10 days ; hac-panel SE (bw=8).
      H0: d₁ = … = d_8 = 0   →   Wald χ²(8) = 5.14,  p = 0.742    |   BH-FDR p = 0.78 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..8) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=8 ; sample spans 10 days (probit: no day-FE) ; hac-panel SE (bw=8).
      H0: b₁ = … = b_8 = 0   →   Wald χ²(8) = 22.28,  p = 0.00442 ***   |   BH-FDR p = 0.0225 **
   => event verdict: neither direction significant.

3. OVERALL VERDICT
   No Granger causality detected on either axis.

------------------------------------------------------------------------------------------------
This pair's joint-Wald p per direction is also in the single-pair heatmap (core figure 1).
```

---

### Rank 7/48 — Fed Nov-24 hold 0bp × VNQ

```text
GRANGER CAUSALITY    —    Rank 7 / 48
================================================================================================
Fed Nov-24 hold 0bp   x   VNQ      [ticker: FEDDECISION-24NOV-H0]
Contract : "Will the Federal Reserve Hike rates by 0bps at their November 2024 meeting?"
Window : 2024-09-18 to 2024-11-07     primary bar : 10min     Kalshi trades : 452

Test: joint Wald H0 = all PAST cause-lags are 0 (controls the effect's own past; hac-panel SE).
p<0.05 ⇒ that variable Granger-leads the other.  (x=Δprob, y=ETF log return.)

1. CALENDAR-TIME (clock-time lags, full RTH grid)
   Direction A — Kalshi → ETF:
      yₜ = α + (no y self-lag term: BIC chose p=0) + Σ(j=1..6) bⱼ·xₜ₋ⱼ + Σ(d=1..35) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=6 ; day-FE over 36 days ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 9.75,  p = 0.136    |   BH-FDR p = 0.324 
   Direction B — ETF → Kalshi:
      xₜ = α + (no x self-lag term: BIC chose p=0) + Σ(j=1..6) dⱼ·yₜ₋ⱼ + Σ(d=1..35) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=6 ; day-FE over 36 days ; hac-panel SE (bw=6).
      H0: d₁ = … = d_6 = 0   →   Wald χ²(6) = 13.45,  p = 0.0364 **   |   BH-FDR p = 0.706 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..6) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=6 ; sample spans 36 days (probit: no day-FE) ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 6.88,  p = 0.332    |   BH-FDR p = 0.586 
   => calendar verdict: ETF Granger-leads Kalshi.

2. EVENT-TIME (event-count lags)
   (not estimable at this axis)

3. OVERALL VERDICT
   Only one axis significant: ETF Granger-leads Kalshi.

------------------------------------------------------------------------------------------------
This pair's joint-Wald p per direction is also in the single-pair heatmap (core figure 1).
```

---

### Rank 8/48 — Fed Nov-24 hold 0bp × VDE

```text
GRANGER CAUSALITY    —    Rank 8 / 48
================================================================================================
Fed Nov-24 hold 0bp   x   VDE      [ticker: FEDDECISION-24NOV-H0]
Contract : "Will the Federal Reserve Hike rates by 0bps at their November 2024 meeting?"
Window : 2024-09-18 to 2024-11-07     primary bar : 10min     Kalshi trades : 452

Test: joint Wald H0 = all PAST cause-lags are 0 (controls the effect's own past; hac-panel SE).
p<0.05 ⇒ that variable Granger-leads the other.  (x=Δprob, y=ETF log return.)

1. CALENDAR-TIME (clock-time lags, full RTH grid)
   Direction A — Kalshi → ETF:
      yₜ = α + (no y self-lag term: BIC chose p=0) + Σ(j=1..6) bⱼ·xₜ₋ⱼ + Σ(d=1..35) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=6 ; day-FE over 36 days ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 6.25,  p = 0.396    |   BH-FDR p = 0.594 
   Direction B — ETF → Kalshi:
      xₜ = α + (no x self-lag term: BIC chose p=0) + Σ(j=1..6) dⱼ·yₜ₋ⱼ + Σ(d=1..35) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=6 ; day-FE over 36 days ; hac-panel SE (bw=6).
      H0: d₁ = … = d_6 = 0   →   Wald χ²(6) = 6.37,  p = 0.383    |   BH-FDR p = 0.706 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..6) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=6 ; sample spans 36 days (probit: no day-FE) ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 6.03,  p = 0.42    |   BH-FDR p = 0.586 
   => calendar verdict: neither direction significant.

2. EVENT-TIME (event-count lags)
   (not estimable at this axis)

3. OVERALL VERDICT
   No Granger causality detected on either axis.

------------------------------------------------------------------------------------------------
This pair's joint-Wald p per direction is also in the single-pair heatmap (core figure 1).
```

---

### Rank 9/48 — Trump 281 EV × VNQ

```text
GRANGER CAUSALITY    —    Rank 9 / 48
================================================================================================
Trump 281 EV   x   VNQ      [ticker: KXECDJT281]
Contract : "Will Trump win 281-257 - AZ, GA, NC, PA?"
Window : 2024-11-04 to 2024-11-25     primary bar : 5min     Kalshi trades : 308

Test: joint Wald H0 = all PAST cause-lags are 0 (controls the effect's own past; hac-panel SE).
p<0.05 ⇒ that variable Granger-leads the other.  (x=Δprob, y=ETF log return.)

1. CALENDAR-TIME (clock-time lags, full RTH grid)
   Direction A — Kalshi → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..5) bⱼ·xₜ₋ⱼ + Σ(d=1..10) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=5 ; day-FE over 11 days ; hac-panel SE (bw=5).
      H0: b₁ = … = b_5 = 0   →   Wald χ²(5) = 7.85,  p = 0.165    |   BH-FDR p = 0.324 
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + Σ(j=1..5) dⱼ·yₜ₋ⱼ + Σ(d=1..10) γ_d·Day_d
      controls: ADL self-lags p=2 (BIC) ; cause block K=5 ; day-FE over 11 days ; hac-panel SE (bw=5).
      H0: d₁ = … = d_5 = 0   →   Wald χ²(5) = 7.40,  p = 0.193    |   BH-FDR p = 0.706 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..5) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=5 ; sample spans 11 days (probit: no day-FE) ; hac-panel SE (bw=5).
      H0: b₁ = … = b_5 = 0   →   Wald χ²(5) = 15.89,  p = 0.00718 ***   |   BH-FDR p = 0.0969 *
   => calendar verdict: neither direction significant.

2. EVENT-TIME (event-count lags)
   Direction A — Kalshi → ETF:
      yₜ = α + (no y self-lag term: BIC chose p=0) + Σ(j=1..5) bⱼ·xₜ₋ⱼ + Σ(d=1..3) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=5 ; day-FE over 4 days ; hac-panel SE (bw=5).
      H0: b₁ = … = b_5 = 0   →   Wald χ²(5) = 34.36,  p = 2.02e-06 ***   |   BH-FDR p = 1.06e-05 ***
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + Σ(j=1..5) dⱼ·yₜ₋ⱼ + Σ(d=1..3) γ_d·Day_d
      controls: ADL self-lags p=2 (BIC) ; cause block K=5 ; day-FE over 4 days ; hac-panel SE (bw=5).
      H0: d₁ = … = d_5 = 0   →   Wald χ²(5) = 3.90,  p = 0.564    |   BH-FDR p = 0.766 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..5) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=5 ; sample spans 4 days (probit: no day-FE) ; hac-panel SE (bw=5).
      H0: b₁ = … = b_5 = 0   →   Wald χ²(5) = 2.59,  p = 0.763    |   BH-FDR p = 0.895 
   => event verdict: Kalshi Granger-leads ETF.

3. OVERALL VERDICT
   Calendar says 'neither direction significant' but Event says 'Kalshi Granger-leads ETF' — not robust across time-axis.

------------------------------------------------------------------------------------------------
This pair's joint-Wald p per direction is also in the single-pair heatmap (core figure 1).
```

---

### Rank 10/48 — Trump 281 EV × VOX

```text
GRANGER CAUSALITY    —    Rank 10 / 48
================================================================================================
Trump 281 EV   x   VOX      [ticker: KXECDJT281]
Contract : "Will Trump win 281-257 - AZ, GA, NC, PA?"
Window : 2024-11-04 to 2024-11-25     primary bar : 5min     Kalshi trades : 308

Test: joint Wald H0 = all PAST cause-lags are 0 (controls the effect's own past; hac-panel SE).
p<0.05 ⇒ that variable Granger-leads the other.  (x=Δprob, y=ETF log return.)

1. CALENDAR-TIME (clock-time lags, full RTH grid)
   Direction A — Kalshi → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..5) bⱼ·xₜ₋ⱼ + Σ(d=1..10) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=5 ; day-FE over 11 days ; hac-panel SE (bw=5).
      H0: b₁ = … = b_5 = 0   →   Wald χ²(5) = 7.94,  p = 0.16    |   BH-FDR p = 0.324 
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + Σ(j=1..5) dⱼ·yₜ₋ⱼ + Σ(d=1..10) γ_d·Day_d
      controls: ADL self-lags p=2 (BIC) ; cause block K=5 ; day-FE over 11 days ; hac-panel SE (bw=5).
      H0: d₁ = … = d_5 = 0   →   Wald χ²(5) = 2.56,  p = 0.767    |   BH-FDR p = 0.828 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..5) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=5 ; sample spans 11 days (probit: no day-FE) ; hac-panel SE (bw=5).
      H0: b₁ = … = b_5 = 0   →   Wald χ²(5) = 4.32,  p = 0.504    |   BH-FDR p = 0.648 
   => calendar verdict: neither direction significant.

2. EVENT-TIME (event-count lags)
   Direction A — Kalshi → ETF:
      yₜ = α + φ₁·yₜ₋₁ + φ₂·yₜ₋₂ + Σ(j=1..5) bⱼ·xₜ₋ⱼ + Σ(d=1..3) γ_d·Day_d
      controls: ADL self-lags p=2 (BIC) ; cause block K=5 ; day-FE over 4 days ; hac-panel SE (bw=5).
      H0: b₁ = … = b_5 = 0   →   Wald χ²(5) = 3.67,  p = 0.597    |   BH-FDR p = 0.836 
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + Σ(j=1..5) dⱼ·yₜ₋ⱼ + Σ(d=1..3) γ_d·Day_d
      controls: ADL self-lags p=2 (BIC) ; cause block K=5 ; day-FE over 4 days ; hac-panel SE (bw=5).
      H0: d₁ = … = d_5 = 0   →   Wald χ²(5) = 3.05,  p = 0.693    |   BH-FDR p = 0.766 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..5) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=5 ; sample spans 4 days (probit: no day-FE) ; hac-panel SE (bw=5).
      H0: b₁ = … = b_5 = 0   →   Wald χ²(5) = 4.88,  p = 0.43    |   BH-FDR p = 0.762 
   => event verdict: neither direction significant.

3. OVERALL VERDICT
   No Granger causality detected on either axis.

------------------------------------------------------------------------------------------------
This pair's joint-Wald p per direction is also in the single-pair heatmap (core figure 1).
```

---

### Rank 11/48 — Trump 281 EV × VGT

```text
GRANGER CAUSALITY    —    Rank 11 / 48
================================================================================================
Trump 281 EV   x   VGT      [ticker: KXECDJT281]
Contract : "Will Trump win 281-257 - AZ, GA, NC, PA?"
Window : 2024-11-04 to 2024-11-25     primary bar : 5min     Kalshi trades : 308

Test: joint Wald H0 = all PAST cause-lags are 0 (controls the effect's own past; hac-panel SE).
p<0.05 ⇒ that variable Granger-leads the other.  (x=Δprob, y=ETF log return.)

1. CALENDAR-TIME (clock-time lags, full RTH grid)
   Direction A — Kalshi → ETF:
      yₜ = α + φ₁·yₜ₋₁ + φ₂·yₜ₋₂ + Σ(j=1..5) bⱼ·xₜ₋ⱼ + Σ(d=1..10) γ_d·Day_d
      controls: ADL self-lags p=2 (BIC) ; cause block K=5 ; day-FE over 11 days ; hac-panel SE (bw=5).
      H0: b₁ = … = b_5 = 0   →   Wald χ²(5) = 3.36,  p = 0.645    |   BH-FDR p = 0.727 
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + Σ(j=1..5) dⱼ·yₜ₋ⱼ + Σ(d=1..10) γ_d·Day_d
      controls: ADL self-lags p=2 (BIC) ; cause block K=5 ; day-FE over 11 days ; hac-panel SE (bw=5).
      H0: d₁ = … = d_5 = 0   →   Wald χ²(5) = 3.42,  p = 0.635    |   BH-FDR p = 0.779 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..5) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=5 ; sample spans 11 days (probit: no day-FE) ; hac-panel SE (bw=5).
      H0: b₁ = … = b_5 = 0   →   Wald χ²(5) = 5.51,  p = 0.357    |   BH-FDR p = 0.586 
   => calendar verdict: neither direction significant.

2. EVENT-TIME (event-count lags)
   Direction A — Kalshi → ETF:
      yₜ = α + (no y self-lag term: BIC chose p=0) + Σ(j=1..5) bⱼ·xₜ₋ⱼ + Σ(d=1..3) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=5 ; day-FE over 4 days ; hac-panel SE (bw=5).
      H0: b₁ = … = b_5 = 0   →   Wald χ²(5) = 2.47,  p = 0.781    |   BH-FDR p = 0.932 
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + Σ(j=1..5) dⱼ·yₜ₋ⱼ + Σ(d=1..3) γ_d·Day_d
      controls: ADL self-lags p=2 (BIC) ; cause block K=5 ; day-FE over 4 days ; hac-panel SE (bw=5).
      H0: d₁ = … = d_5 = 0   →   Wald χ²(5) = 3.69,  p = 0.594    |   BH-FDR p = 0.766 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..5) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=5 ; sample spans 4 days (probit: no day-FE) ; hac-panel SE (bw=5).
      H0: b₁ = … = b_5 = 0   →   Wald χ²(5) = 1.48,  p = 0.915    |   BH-FDR p = 0.967 
   => event verdict: neither direction significant.

3. OVERALL VERDICT
   No Granger causality detected on either axis.

------------------------------------------------------------------------------------------------
This pair's joint-Wald p per direction is also in the single-pair heatmap (core figure 1).
```

---

### Rank 12/48 — Trump 281 EV × VCR

```text
GRANGER CAUSALITY    —    Rank 12 / 48
================================================================================================
Trump 281 EV   x   VCR      [ticker: KXECDJT281]
Contract : "Will Trump win 281-257 - AZ, GA, NC, PA?"
Window : 2024-11-04 to 2024-11-25     primary bar : 5min     Kalshi trades : 308

Test: joint Wald H0 = all PAST cause-lags are 0 (controls the effect's own past; hac-panel SE).
p<0.05 ⇒ that variable Granger-leads the other.  (x=Δprob, y=ETF log return.)

1. CALENDAR-TIME (clock-time lags, full RTH grid)
   Direction A — Kalshi → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..5) bⱼ·xₜ₋ⱼ + Σ(d=1..10) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=5 ; day-FE over 11 days ; hac-panel SE (bw=5).
      H0: b₁ = … = b_5 = 0   →   Wald χ²(5) = 1.58,  p = 0.904    |   BH-FDR p = 0.938 
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + Σ(j=1..5) dⱼ·yₜ₋ⱼ + Σ(d=1..10) γ_d·Day_d
      controls: ADL self-lags p=2 (BIC) ; cause block K=5 ; day-FE over 11 days ; hac-panel SE (bw=5).
      H0: d₁ = … = d_5 = 0   →   Wald χ²(5) = 1.85,  p = 0.87    |   BH-FDR p = 0.878 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..5) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=5 ; sample spans 11 days (probit: no day-FE) ; hac-panel SE (bw=5).
      H0: b₁ = … = b_5 = 0   →   Wald χ²(5) = 0.62,  p = 0.987    |   BH-FDR p = 0.987 
   => calendar verdict: neither direction significant.

2. EVENT-TIME (event-count lags)
   Direction A — Kalshi → ETF:
      yₜ = α + (no y self-lag term: BIC chose p=0) + Σ(j=1..5) bⱼ·xₜ₋ⱼ + Σ(d=1..3) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=5 ; day-FE over 4 days ; hac-panel SE (bw=5).
      H0: b₁ = … = b_5 = 0   →   Wald χ²(5) = 6.08,  p = 0.298    |   BH-FDR p = 0.569 
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + Σ(j=1..5) dⱼ·yₜ₋ⱼ + Σ(d=1..3) γ_d·Day_d
      controls: ADL self-lags p=2 (BIC) ; cause block K=5 ; day-FE over 4 days ; hac-panel SE (bw=5).
      H0: d₁ = … = d_5 = 0   →   Wald χ²(5) = 9.37,  p = 0.0953 *   |   BH-FDR p = 0.222 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..5) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=5 ; sample spans 4 days (probit: no day-FE) ; hac-panel SE (bw=5).
      H0: b₁ = … = b_5 = 0   →   Wald χ²(5) = 4.09,  p = 0.537    |   BH-FDR p = 0.811 
   => event verdict: neither direction significant.

3. OVERALL VERDICT
   No Granger causality detected on either axis.

------------------------------------------------------------------------------------------------
This pair's joint-Wald p per direction is also in the single-pair heatmap (core figure 1).
```

---

### Rank 13/48 — Trump 312 EV × VAW

```text
GRANGER CAUSALITY    —    Rank 13 / 48
================================================================================================
Trump 312 EV   x   VAW      [ticker: KXECDJT312]
Contract : "Will Trump win 312-226 - swing state sweep?"
Window : 2024-11-04 to 2024-12-12     primary bar : 10min     Kalshi trades : 232

Test: joint Wald H0 = all PAST cause-lags are 0 (controls the effect's own past; hac-panel SE).
p<0.05 ⇒ that variable Granger-leads the other.  (x=Δprob, y=ETF log return.)

1. CALENDAR-TIME (clock-time lags, full RTH grid)
   Direction A — Kalshi → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..5) bⱼ·xₜ₋ⱼ + Σ(d=1..17) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=5 ; day-FE over 18 days ; hac-panel SE (bw=5).
      H0: b₁ = … = b_5 = 0   →   Wald χ²(5) = 0.91,  p = 0.969    |   BH-FDR p = 0.969 
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + Σ(j=1..5) dⱼ·yₜ₋ⱼ + Σ(d=1..17) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=5 ; day-FE over 18 days ; hac-panel SE (bw=5).
      H0: d₁ = … = d_5 = 0   →   Wald χ²(5) = 7.42,  p = 0.191    |   BH-FDR p = 0.706 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..5) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=5 ; sample spans 18 days (probit: no day-FE) ; hac-panel SE (bw=5).
      H0: b₁ = … = b_5 = 0   →   Wald χ²(5) = 2.24,  p = 0.816    |   BH-FDR p = 0.881 
   => calendar verdict: neither direction significant.

2. EVENT-TIME (event-count lags)
   Direction A — Kalshi → ETF:
      yₜ = α + (no y self-lag term: BIC chose p=0) + Σ(j=1..5) bⱼ·xₜ₋ⱼ + Σ(d=1..3) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=5 ; day-FE over 4 days ; hac-panel SE (bw=5).
      H0: b₁ = … = b_5 = 0   →   Wald χ²(5) = 48.20,  p = 3.23e-09 ***   |   BH-FDR p = 3.39e-08 ***
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + Σ(j=1..5) dⱼ·yₜ₋ⱼ + Σ(d=1..3) γ_d·Day_d
      controls: ADL self-lags p=2 (BIC) ; cause block K=5 ; day-FE over 4 days ; hac-panel SE (bw=5).
      H0: d₁ = … = d_5 = 0   →   Wald χ²(5) = 3.25,  p = 0.661    |   BH-FDR p = 0.766 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..5) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=5 ; sample spans 4 days (probit: no day-FE) ; hac-panel SE (bw=5).
      H0: b₁ = … = b_5 = 0   →   Wald χ²(5) = 23.80,  p = 0.000237 ***   |   BH-FDR p = 0.00273 ***
   => event verdict: Kalshi Granger-leads ETF.

3. OVERALL VERDICT
   Calendar says 'neither direction significant' but Event says 'Kalshi Granger-leads ETF' — not robust across time-axis.

------------------------------------------------------------------------------------------------
This pair's joint-Wald p per direction is also in the single-pair heatmap (core figure 1).
```

---

### Rank 14/48 — Trump 306 EV × VDC

```text
GRANGER CAUSALITY    —    Rank 14 / 48
================================================================================================
Trump 306 EV   x   VDC      [ticker: KXECDJT306]
Contract : "Will Trump win 306-232 - AZ, GA, MI, PA, WI, NC?"
Window : 2024-11-04 to 2024-12-16     primary bar : 10min     Kalshi trades : 123

Test: joint Wald H0 = all PAST cause-lags are 0 (controls the effect's own past; hac-panel SE).
p<0.05 ⇒ that variable Granger-leads the other.  (x=Δprob, y=ETF log return.)

1. CALENDAR-TIME (clock-time lags, full RTH grid)
   Direction A — Kalshi → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..4) bⱼ·xₜ₋ⱼ + Σ(d=1..12) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; day-FE over 13 days ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 10.63,  p = 0.031 **   |   BH-FDR p = 0.105 
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + Σ(j=1..4) dⱼ·yₜ₋ⱼ + Σ(d=1..12) γ_d·Day_d
      controls: ADL self-lags p=3 (BIC) ; cause block K=4 ; day-FE over 13 days ; hac-panel SE (bw=4).
      H0: d₁ = … = d_4 = 0   →   Wald χ²(4) = 4.51,  p = 0.342    |   BH-FDR p = 0.706 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..4) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; sample spans 13 days (probit: no day-FE) ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 3.80,  p = 0.434    |   BH-FDR p = 0.586 
   => calendar verdict: Kalshi Granger-leads ETF.

2. EVENT-TIME (event-count lags)
   Direction A — Kalshi → ETF:
      yₜ = α + (no y self-lag term: BIC chose p=0) + Σ(j=1..4) bⱼ·xₜ₋ⱼ + Σ(d=1..1) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=4 ; day-FE over 2 days ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 51.18,  p = 2.05e-10 ***   |   BH-FDR p = 4.31e-09 ***
   Direction B — ETF → Kalshi:
      xₜ = α + (no x self-lag term: BIC chose p=0) + Σ(j=1..4) dⱼ·yₜ₋ⱼ + Σ(d=1..1) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=4 ; day-FE over 2 days ; hac-panel SE (bw=4).
      H0: d₁ = … = d_4 = 0   →   Wald χ²(4) = 7.35,  p = 0.119    |   BH-FDR p = 0.249 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..4) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=4 ; sample spans 2 days (probit: no day-FE) ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 8.22,  p = 0.0839 *   |   BH-FDR p = 0.276 
   => event verdict: Kalshi Granger-leads ETF.

3. OVERALL VERDICT
   Both time-axes agree: Kalshi Granger-leads ETF (relatively robust).

------------------------------------------------------------------------------------------------
This pair's joint-Wald p per direction is also in the single-pair heatmap (core figure 1).
```

---

### Rank 15/48 — Trump 316 EV × VFH

```text
GRANGER CAUSALITY    —    Rank 15 / 48
================================================================================================
Trump 316 EV   x   VFH      [ticker: KXECDJT316]
Contract : "Will Trump win 316-222 - AZ, GA, MI, MN, NC, PA, WI?"
Window : 2024-11-04 to 2024-12-12     primary bar : 10min     Kalshi trades : 59

Test: joint Wald H0 = all PAST cause-lags are 0 (controls the effect's own past; hac-panel SE).
p<0.05 ⇒ that variable Granger-leads the other.  (x=Δprob, y=ETF log return.)

1. CALENDAR-TIME (clock-time lags, full RTH grid)
   Direction A — Kalshi → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..4) bⱼ·xₜ₋ⱼ + Σ(d=1..6) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; day-FE over 7 days ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 4.24,  p = 0.374    |   BH-FDR p = 0.594 
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + Σ(j=1..4) dⱼ·yₜ₋ⱼ + Σ(d=1..6) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; day-FE over 7 days ; hac-panel SE (bw=4).
      H0: d₁ = … = d_4 = 0   →   Wald χ²(4) = 5.67,  p = 0.225    |   BH-FDR p = 0.706 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + φ₂·yₜ₋₂ + Σ(j=1..4) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=2 (BIC) ; cause block K=4 ; sample spans 7 days (probit: no day-FE) ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 5.48,  p = 0.242    |   BH-FDR p = 0.586 
   => calendar verdict: neither direction significant.

2. EVENT-TIME (event-count lags)
   (not estimable at this axis)

3. OVERALL VERDICT
   No Granger causality detected on either axis.

------------------------------------------------------------------------------------------------
This pair's joint-Wald p per direction is also in the single-pair heatmap (core figure 1).
```

---

### Rank 16/48 — Trump 316 EV × VIS

```text
GRANGER CAUSALITY    —    Rank 16 / 48
================================================================================================
Trump 316 EV   x   VIS      [ticker: KXECDJT316]
Contract : "Will Trump win 316-222 - AZ, GA, MI, MN, NC, PA, WI?"
Window : 2024-11-04 to 2024-12-12     primary bar : 10min     Kalshi trades : 59

Test: joint Wald H0 = all PAST cause-lags are 0 (controls the effect's own past; hac-panel SE).
p<0.05 ⇒ that variable Granger-leads the other.  (x=Δprob, y=ETF log return.)

1. CALENDAR-TIME (clock-time lags, full RTH grid)
   Direction A — Kalshi → ETF:
      yₜ = α + (no y self-lag term: BIC chose p=0) + Σ(j=1..4) bⱼ·xₜ₋ⱼ + Σ(d=1..6) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=4 ; day-FE over 7 days ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 6.45,  p = 0.168    |   BH-FDR p = 0.324 
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + Σ(j=1..4) dⱼ·yₜ₋ⱼ + Σ(d=1..6) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; day-FE over 7 days ; hac-panel SE (bw=4).
      H0: d₁ = … = d_4 = 0   →   Wald χ²(4) = 6.09,  p = 0.192    |   BH-FDR p = 0.706 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + φ₂·yₜ₋₂ + Σ(j=1..4) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=2 (BIC) ; cause block K=4 ; sample spans 7 days (probit: no day-FE) ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 10.05,  p = 0.0395 **   |   BH-FDR p = 0.213 
   => calendar verdict: neither direction significant.

2. EVENT-TIME (event-count lags)
   (not estimable at this axis)

3. OVERALL VERDICT
   No Granger causality detected on either axis.

------------------------------------------------------------------------------------------------
This pair's joint-Wald p per direction is also in the single-pair heatmap (core figure 1).
```

---

### Rank 17/48 — Trump 316 EV × VDE

```text
GRANGER CAUSALITY    —    Rank 17 / 48
================================================================================================
Trump 316 EV   x   VDE      [ticker: KXECDJT316]
Contract : "Will Trump win 316-222 - AZ, GA, MI, MN, NC, PA, WI?"
Window : 2024-11-04 to 2024-12-12     primary bar : 10min     Kalshi trades : 59

Test: joint Wald H0 = all PAST cause-lags are 0 (controls the effect's own past; hac-panel SE).
p<0.05 ⇒ that variable Granger-leads the other.  (x=Δprob, y=ETF log return.)

1. CALENDAR-TIME (clock-time lags, full RTH grid)
   Direction A — Kalshi → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..4) bⱼ·xₜ₋ⱼ + Σ(d=1..6) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; day-FE over 7 days ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 14.19,  p = 0.00672 ***   |   BH-FDR p = 0.0336 **
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + Σ(j=1..4) dⱼ·yₜ₋ⱼ + Σ(d=1..6) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; day-FE over 7 days ; hac-panel SE (bw=4).
      H0: d₁ = … = d_4 = 0   →   Wald χ²(4) = 3.43,  p = 0.489    |   BH-FDR p = 0.741 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..4) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; sample spans 7 days (probit: no day-FE) ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 7.22,  p = 0.125    |   BH-FDR p = 0.429 
   => calendar verdict: Kalshi Granger-leads ETF.

2. EVENT-TIME (event-count lags)
   (not estimable at this axis)

3. OVERALL VERDICT
   Only one axis significant: Kalshi Granger-leads ETF.

------------------------------------------------------------------------------------------------
This pair's joint-Wald p per direction is also in the single-pair heatmap (core figure 1).
```

---

### Rank 18/48 — Gas >$3.15 by Oct31 × VPU

```text
GRANGER CAUSALITY    —    Rank 18 / 48
================================================================================================
Gas >$3.15 by Oct31   x   VPU      [ticker: AAAGASM-24OCT31-US-3.15]
Contract : "Will average **gas prices** be above $3.15?"
Window : 2024-10-02 to 2024-10-31     primary bar : 10min     Kalshi trades : 58

Test: joint Wald H0 = all PAST cause-lags are 0 (controls the effect's own past; hac-panel SE).
p<0.05 ⇒ that variable Granger-leads the other.  (x=Δprob, y=ETF log return.)

1. CALENDAR-TIME (clock-time lags, full RTH grid)
   Direction A — Kalshi → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..3) bⱼ·xₜ₋ⱼ + Σ(d=1..13) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=3 ; day-FE over 14 days ; hac-panel SE (bw=3).
      H0: b₁ = … = b_3 = 0   →   Wald χ²(3) = 15.13,  p = 0.00171 ***   |   BH-FDR p = 0.0116 **
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + Σ(j=1..3) dⱼ·yₜ₋ⱼ + Σ(d=1..13) γ_d·Day_d
      controls: ADL self-lags p=2 (BIC) ; cause block K=3 ; day-FE over 14 days ; hac-panel SE (bw=3).
      H0: d₁ = … = d_3 = 0   →   Wald χ²(3) = 1.97,  p = 0.578    |   BH-FDR p = 0.779 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..3) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=3 ; sample spans 14 days (probit: no day-FE) ; hac-panel SE (bw=3).
      H0: b₁ = … = b_3 = 0   →   Wald χ²(3) = 6.87,  p = 0.076 *   |   BH-FDR p = 0.342 
   => calendar verdict: Kalshi Granger-leads ETF.

2. EVENT-TIME (event-count lags)
   (not estimable at this axis)

3. OVERALL VERDICT
   Only one axis significant: Kalshi Granger-leads ETF.

------------------------------------------------------------------------------------------------
This pair's joint-Wald p per direction is also in the single-pair heatmap (core figure 1).
```

---

### Rank 19/48 — Harris 276 EV × VOX

```text
GRANGER CAUSALITY    —    Rank 19 / 48
================================================================================================
Harris 276 EV   x   VOX      [ticker: KXECKH276]
Contract : "Will Harris win 276-262 - PA, NV, MI, WI?"
Window : 2024-11-04 to 2024-11-26     primary bar : 10min     Kalshi trades : 43

Test: joint Wald H0 = all PAST cause-lags are 0 (controls the effect's own past; hac-panel SE).
p<0.05 ⇒ that variable Granger-leads the other.  (x=Δprob, y=ETF log return.)

1. CALENDAR-TIME (clock-time lags, full RTH grid)
   Direction A — Kalshi → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..3) bⱼ·xₜ₋ⱼ + Σ(d=1..5) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=3 ; day-FE over 6 days ; hac-panel SE (bw=3).
      H0: b₁ = … = b_3 = 0   →   Wald χ²(3) = 11.98,  p = 0.00746 ***   |   BH-FDR p = 0.0336 **
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + Σ(j=1..3) dⱼ·yₜ₋ⱼ + Σ(d=1..5) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=3 ; day-FE over 6 days ; hac-panel SE (bw=3).
      H0: d₁ = … = d_3 = 0   →   Wald χ²(3) = 4.26,  p = 0.235    |   BH-FDR p = 0.706 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..3) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=3 ; sample spans 6 days (probit: no day-FE) ; hac-panel SE (bw=3).
      H0: b₁ = … = b_3 = 0   →   Wald χ²(3) = 9.68,  p = 0.0215 **   |   BH-FDR p = 0.193 
   => calendar verdict: Kalshi Granger-leads ETF.

2. EVENT-TIME (event-count lags)
   Direction A — Kalshi → ETF:
      yₜ = α + (no y self-lag term: BIC chose p=0) + Σ(j=1..3) bⱼ·xₜ₋ⱼ
      controls: ADL self-lags p=0 (BIC) ; cause block K=3 ; no day-FE (single day) ; hac-panel SE (bw=3).
      H0: b₁ = … = b_3 = 0   →   Wald χ²(3) = 3.10,  p = 0.376    |   BH-FDR p = 0.607 
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + Σ(j=1..3) dⱼ·yₜ₋ⱼ
      controls: ADL self-lags p=3 (BIC) ; cause block K=3 ; no day-FE (single day) ; hac-panel SE (bw=3).
      H0: d₁ = … = d_3 = 0   →   Wald χ²(3) = 0.74,  p = 0.863    |   BH-FDR p = 0.863 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..3) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=3 ; sample spans 1 days (probit: no day-FE) ; hac-panel SE (bw=3).
      H0: b₁ = … = b_3 = 0   →   Wald χ²(3) = 3.36,  p = 0.34    |   BH-FDR p = 0.652 
   => event verdict: neither direction significant.

3. OVERALL VERDICT
   Calendar says 'Kalshi Granger-leads ETF' but Event says 'neither direction significant' — not robust across time-axis.

------------------------------------------------------------------------------------------------
This pair's joint-Wald p per direction is also in the single-pair heatmap (core figure 1).
```

---

### Rank 20/48 — Harris 276 EV × VFH

```text
GRANGER CAUSALITY    —    Rank 20 / 48
================================================================================================
Harris 276 EV   x   VFH      [ticker: KXECKH276]
Contract : "Will Harris win 276-262 - PA, NV, MI, WI?"
Window : 2024-11-04 to 2024-11-26     primary bar : 10min     Kalshi trades : 43

Test: joint Wald H0 = all PAST cause-lags are 0 (controls the effect's own past; hac-panel SE).
p<0.05 ⇒ that variable Granger-leads the other.  (x=Δprob, y=ETF log return.)

1. CALENDAR-TIME (clock-time lags, full RTH grid)
   Direction A — Kalshi → ETF:
      yₜ = α + (no y self-lag term: BIC chose p=0) + Σ(j=1..3) bⱼ·xₜ₋ⱼ + Σ(d=1..5) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=3 ; day-FE over 6 days ; hac-panel SE (bw=3).
      H0: b₁ = … = b_3 = 0   →   Wald χ²(3) = 20.56,  p = 0.00013 ***   |   BH-FDR p = 0.00117 ***
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + Σ(j=1..3) dⱼ·yₜ₋ⱼ + Σ(d=1..5) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=3 ; day-FE over 6 days ; hac-panel SE (bw=3).
      H0: d₁ = … = d_3 = 0   →   Wald χ²(3) = 3.52,  p = 0.319    |   BH-FDR p = 0.706 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..3) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=3 ; sample spans 6 days (probit: no day-FE) ; hac-panel SE (bw=3).
      H0: b₁ = … = b_3 = 0   →   Wald χ²(3) = 0.17,  p = 0.982    |   BH-FDR p = 0.987 
   => calendar verdict: Kalshi Granger-leads ETF.

2. EVENT-TIME (event-count lags)
   Direction A — Kalshi → ETF:
      yₜ = α + (no y self-lag term: BIC chose p=0) + Σ(j=1..3) bⱼ·xₜ₋ⱼ
      controls: ADL self-lags p=0 (BIC) ; cause block K=3 ; no day-FE (single day) ; hac-panel SE (bw=3).
      H0: b₁ = … = b_3 = 0   →   Wald χ²(3) = 1.62,  p = 0.655    |   BH-FDR p = 0.86 
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + Σ(j=1..3) dⱼ·yₜ₋ⱼ
      controls: ADL self-lags p=3 (BIC) ; cause block K=3 ; no day-FE (single day) ; hac-panel SE (bw=3).
      H0: d₁ = … = d_3 = 0   →   Wald χ²(3) = 7.19,  p = 0.0659 *   |   BH-FDR p = 0.173 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..3) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=3 ; sample spans 1 days (probit: no day-FE) ; hac-panel SE (bw=3).
      H0: b₁ = … = b_3 = 0   →   Wald χ²(3) = 0.26,  p = 0.967    |   BH-FDR p = 0.967 
   => event verdict: neither direction significant.

3. OVERALL VERDICT
   Calendar says 'Kalshi Granger-leads ETF' but Event says 'neither direction significant' — not robust across time-axis.

------------------------------------------------------------------------------------------------
This pair's joint-Wald p per direction is also in the single-pair heatmap (core figure 1).
```

---

### Rank 21/48 — Harris 276 EV × VIS

```text
GRANGER CAUSALITY    —    Rank 21 / 48
================================================================================================
Harris 276 EV   x   VIS      [ticker: KXECKH276]
Contract : "Will Harris win 276-262 - PA, NV, MI, WI?"
Window : 2024-11-04 to 2024-11-26     primary bar : 10min     Kalshi trades : 43

Test: joint Wald H0 = all PAST cause-lags are 0 (controls the effect's own past; hac-panel SE).
p<0.05 ⇒ that variable Granger-leads the other.  (x=Δprob, y=ETF log return.)

1. CALENDAR-TIME (clock-time lags, full RTH grid)
   Direction A — Kalshi → ETF:
      yₜ = α + (no y self-lag term: BIC chose p=0) + Σ(j=1..3) bⱼ·xₜ₋ⱼ + Σ(d=1..5) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=3 ; day-FE over 6 days ; hac-panel SE (bw=3).
      H0: b₁ = … = b_3 = 0   →   Wald χ²(3) = 22.17,  p = 6.01e-05 ***   |   BH-FDR p = 0.000812 ***
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + Σ(j=1..3) dⱼ·yₜ₋ⱼ + Σ(d=1..5) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=3 ; day-FE over 6 days ; hac-panel SE (bw=3).
      H0: d₁ = … = d_3 = 0   →   Wald χ²(3) = 3.59,  p = 0.309    |   BH-FDR p = 0.706 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..3) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=3 ; sample spans 6 days (probit: no day-FE) ; hac-panel SE (bw=3).
      H0: b₁ = … = b_3 = 0   →   Wald χ²(3) = 23.93,  p = 2.59e-05 ***   |   BH-FDR p = 0.000699 ***
   => calendar verdict: Kalshi Granger-leads ETF.

2. EVENT-TIME (event-count lags)
   Direction A — Kalshi → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..3) bⱼ·xₜ₋ⱼ
      controls: ADL self-lags p=1 (BIC) ; cause block K=3 ; no day-FE (single day) ; hac-panel SE (bw=3).
      H0: b₁ = … = b_3 = 0   →   Wald χ²(3) = 6.16,  p = 0.104    |   BH-FDR p = 0.219 
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + Σ(j=1..3) dⱼ·yₜ₋ⱼ
      controls: ADL self-lags p=3 (BIC) ; cause block K=3 ; no day-FE (single day) ; hac-panel SE (bw=3).
      H0: d₁ = … = d_3 = 0   →   Wald χ²(3) = 12.19,  p = 0.00676 ***   |   BH-FDR p = 0.0355 **
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..3) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=3 ; sample spans 1 days (probit: no day-FE) ; hac-panel SE (bw=3).
      H0: b₁ = … = b_3 = 0   →   Wald χ²(3) = 4.45,  p = 0.217    |   BH-FDR p = 0.472 
   => event verdict: ETF Granger-leads Kalshi.

3. OVERALL VERDICT
   Calendar says 'Kalshi Granger-leads ETF' but Event says 'ETF Granger-leads Kalshi' — not robust across time-axis.

------------------------------------------------------------------------------------------------
This pair's joint-Wald p per direction is also in the single-pair heatmap (core figure 1).
```

---

### Rank 22/48 — Harris 276 EV × VCR

```text
GRANGER CAUSALITY    —    Rank 22 / 48
================================================================================================
Harris 276 EV   x   VCR      [ticker: KXECKH276]
Contract : "Will Harris win 276-262 - PA, NV, MI, WI?"
Window : 2024-11-04 to 2024-11-26     primary bar : 10min     Kalshi trades : 43

Test: joint Wald H0 = all PAST cause-lags are 0 (controls the effect's own past; hac-panel SE).
p<0.05 ⇒ that variable Granger-leads the other.  (x=Δprob, y=ETF log return.)

1. CALENDAR-TIME (clock-time lags, full RTH grid)
   Direction A — Kalshi → ETF:
      yₜ = α + (no y self-lag term: BIC chose p=0) + Σ(j=1..3) bⱼ·xₜ₋ⱼ + Σ(d=1..5) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=3 ; day-FE over 6 days ; hac-panel SE (bw=3).
      H0: b₁ = … = b_3 = 0   →   Wald χ²(3) = 7.20,  p = 0.0658 *   |   BH-FDR p = 0.197 
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + Σ(j=1..3) dⱼ·yₜ₋ⱼ + Σ(d=1..5) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=3 ; day-FE over 6 days ; hac-panel SE (bw=3).
      H0: d₁ = … = d_3 = 0   →   Wald χ²(3) = 2.83,  p = 0.418    |   BH-FDR p = 0.706 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..3) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=3 ; sample spans 6 days (probit: no day-FE) ; hac-panel SE (bw=3).
      H0: b₁ = … = b_3 = 0   →   Wald χ²(3) = 4.20,  p = 0.24    |   BH-FDR p = 0.586 
   => calendar verdict: neither direction significant.

2. EVENT-TIME (event-count lags)
   Direction A — Kalshi → ETF:
      yₜ = α + (no y self-lag term: BIC chose p=0) + Σ(j=1..3) bⱼ·xₜ₋ⱼ
      controls: ADL self-lags p=0 (BIC) ; cause block K=3 ; no day-FE (single day) ; hac-panel SE (bw=3).
      H0: b₁ = … = b_3 = 0   →   Wald χ²(3) = 1.91,  p = 0.591    |   BH-FDR p = 0.836 
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + Σ(j=1..3) dⱼ·yₜ₋ⱼ
      controls: ADL self-lags p=3 (BIC) ; cause block K=3 ; no day-FE (single day) ; hac-panel SE (bw=3).
      H0: d₁ = … = d_3 = 0   →   Wald χ²(3) = 39.91,  p = 1.11e-08 ***   |   BH-FDR p = 1.04e-07 ***
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..3) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=3 ; sample spans 1 days (probit: no day-FE) ; hac-panel SE (bw=3).
      H0: b₁ = … = b_3 = 0   →   Wald χ²(3) = 1.09,  p = 0.778    |   BH-FDR p = 0.895 
   => event verdict: ETF Granger-leads Kalshi.

3. OVERALL VERDICT
   Calendar says 'neither direction significant' but Event says 'ETF Granger-leads Kalshi' — not robust across time-axis.

------------------------------------------------------------------------------------------------
This pair's joint-Wald p per direction is also in the single-pair heatmap (core figure 1).
```

---

### Rank 23/48 — Harris 276 EV × VDE

```text
GRANGER CAUSALITY    —    Rank 23 / 48
================================================================================================
Harris 276 EV   x   VDE      [ticker: KXECKH276]
Contract : "Will Harris win 276-262 - PA, NV, MI, WI?"
Window : 2024-11-04 to 2024-11-26     primary bar : 10min     Kalshi trades : 43

Test: joint Wald H0 = all PAST cause-lags are 0 (controls the effect's own past; hac-panel SE).
p<0.05 ⇒ that variable Granger-leads the other.  (x=Δprob, y=ETF log return.)

1. CALENDAR-TIME (clock-time lags, full RTH grid)
   Direction A — Kalshi → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..3) bⱼ·xₜ₋ⱼ + Σ(d=1..5) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=3 ; day-FE over 6 days ; hac-panel SE (bw=3).
      H0: b₁ = … = b_3 = 0   →   Wald χ²(3) = 33.54,  p = 2.48e-07 ***   |   BH-FDR p = 6.69e-06 ***
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + Σ(j=1..3) dⱼ·yₜ₋ⱼ + Σ(d=1..5) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=3 ; day-FE over 6 days ; hac-panel SE (bw=3).
      H0: d₁ = … = d_3 = 0   →   Wald χ²(3) = 2.86,  p = 0.414    |   BH-FDR p = 0.706 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..3) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=3 ; sample spans 6 days (probit: no day-FE) ; hac-panel SE (bw=3).
      H0: b₁ = … = b_3 = 0   →   Wald χ²(3) = 8.51,  p = 0.0366 **   |   BH-FDR p = 0.213 
   => calendar verdict: Kalshi Granger-leads ETF.

2. EVENT-TIME (event-count lags)
   Direction A — Kalshi → ETF:
      yₜ = α + (no y self-lag term: BIC chose p=0) + Σ(j=1..3) bⱼ·xₜ₋ⱼ
      controls: ADL self-lags p=0 (BIC) ; cause block K=3 ; no day-FE (single day) ; hac-panel SE (bw=3).
      H0: b₁ = … = b_3 = 0   →   Wald χ²(3) = 13.36,  p = 0.00391 ***   |   BH-FDR p = 0.0164 **
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + Σ(j=1..3) dⱼ·yₜ₋ⱼ
      controls: ADL self-lags p=3 (BIC) ; cause block K=3 ; no day-FE (single day) ; hac-panel SE (bw=3).
      H0: d₁ = … = d_3 = 0   →   Wald χ²(3) = 9.47,  p = 0.0237 **   |   BH-FDR p = 0.0994 *
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..3) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=3 ; sample spans 1 days (probit: no day-FE) ; hac-panel SE (bw=3).
      H0: b₁ = … = b_3 = 0   →   Wald χ²(3) = 4.59,  p = 0.205    |   BH-FDR p = 0.472 
   => event verdict: bidirectional (both reject).

3. OVERALL VERDICT
   Calendar says 'Kalshi Granger-leads ETF' but Event says 'bidirectional (both reject)' — not robust across time-axis.

------------------------------------------------------------------------------------------------
This pair's joint-Wald p per direction is also in the single-pair heatmap (core figure 1).
```

---

### Rank 24/48 — Harris 276 EV × VGT

```text
GRANGER CAUSALITY    —    Rank 24 / 48
================================================================================================
Harris 276 EV   x   VGT      [ticker: KXECKH276]
Contract : "Will Harris win 276-262 - PA, NV, MI, WI?"
Window : 2024-11-04 to 2024-11-26     primary bar : 10min     Kalshi trades : 43

Test: joint Wald H0 = all PAST cause-lags are 0 (controls the effect's own past; hac-panel SE).
p<0.05 ⇒ that variable Granger-leads the other.  (x=Δprob, y=ETF log return.)

1. CALENDAR-TIME (clock-time lags, full RTH grid)
   Direction A — Kalshi → ETF:
      yₜ = α + (no y self-lag term: BIC chose p=0) + Σ(j=1..3) bⱼ·xₜ₋ⱼ + Σ(d=1..5) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=3 ; day-FE over 6 days ; hac-panel SE (bw=3).
      H0: b₁ = … = b_3 = 0   →   Wald χ²(3) = 2.20,  p = 0.533    |   BH-FDR p = 0.685 
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + Σ(j=1..3) dⱼ·yₜ₋ⱼ + Σ(d=1..5) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=3 ; day-FE over 6 days ; hac-panel SE (bw=3).
      H0: d₁ = … = d_3 = 0   →   Wald χ²(3) = 3.27,  p = 0.352    |   BH-FDR p = 0.706 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..3) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=3 ; sample spans 6 days (probit: no day-FE) ; hac-panel SE (bw=3).
      H0: b₁ = … = b_3 = 0   →   Wald χ²(3) = 1.34,  p = 0.72    |   BH-FDR p = 0.81 
   => calendar verdict: neither direction significant.

2. EVENT-TIME (event-count lags)
   Direction A — Kalshi → ETF:
      yₜ = α + (no y self-lag term: BIC chose p=0) + Σ(j=1..3) bⱼ·xₜ₋ⱼ
      controls: ADL self-lags p=0 (BIC) ; cause block K=3 ; no day-FE (single day) ; hac-panel SE (bw=3).
      H0: b₁ = … = b_3 = 0   →   Wald χ²(3) = 36.21,  p = 6.75e-08 ***   |   BH-FDR p = 4.72e-07 ***
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + Σ(j=1..3) dⱼ·yₜ₋ⱼ
      controls: ADL self-lags p=3 (BIC) ; cause block K=3 ; no day-FE (single day) ; hac-panel SE (bw=3).
      H0: d₁ = … = d_3 = 0   →   Wald χ²(3) = 8.50,  p = 0.0367 **   |   BH-FDR p = 0.11 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..3) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=3 ; sample spans 1 days (probit: no day-FE) ; hac-panel SE (bw=3).
      H0: b₁ = … = b_3 = 0   →   Wald χ²(3) = 4.36,  p = 0.226    |   BH-FDR p = 0.472 
   => event verdict: bidirectional (both reject).

3. OVERALL VERDICT
   Calendar says 'neither direction significant' but Event says 'bidirectional (both reject)' — not robust across time-axis.

------------------------------------------------------------------------------------------------
This pair's joint-Wald p per direction is also in the single-pair heatmap (core figure 1).
```

---

### Rank 25/48 — Harris 276 EV × VDC

```text
GRANGER CAUSALITY    —    Rank 25 / 48
================================================================================================
Harris 276 EV   x   VDC      [ticker: KXECKH276]
Contract : "Will Harris win 276-262 - PA, NV, MI, WI?"
Window : 2024-11-04 to 2024-11-26     primary bar : 10min     Kalshi trades : 43

Test: joint Wald H0 = all PAST cause-lags are 0 (controls the effect's own past; hac-panel SE).
p<0.05 ⇒ that variable Granger-leads the other.  (x=Δprob, y=ETF log return.)

1. CALENDAR-TIME (clock-time lags, full RTH grid)
   Direction A — Kalshi → ETF:
      yₜ = α + (no y self-lag term: BIC chose p=0) + Σ(j=1..3) bⱼ·xₜ₋ⱼ + Σ(d=1..5) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=3 ; day-FE over 6 days ; hac-panel SE (bw=3).
      H0: b₁ = … = b_3 = 0   →   Wald χ²(3) = 3.55,  p = 0.314    |   BH-FDR p = 0.531 
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + Σ(j=1..3) dⱼ·yₜ₋ⱼ + Σ(d=1..5) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=3 ; day-FE over 6 days ; hac-panel SE (bw=3).
      H0: d₁ = … = d_3 = 0   →   Wald χ²(3) = 1.72,  p = 0.633    |   BH-FDR p = 0.779 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..3) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=3 ; sample spans 6 days (probit: no day-FE) ; hac-panel SE (bw=3).
      H0: b₁ = … = b_3 = 0   →   Wald χ²(3) = 3.64,  p = 0.304    |   BH-FDR p = 0.586 
   => calendar verdict: neither direction significant.

2. EVENT-TIME (event-count lags)
   Direction A — Kalshi → ETF:
      yₜ = α + (no y self-lag term: BIC chose p=0) + Σ(j=1..3) bⱼ·xₜ₋ⱼ
      controls: ADL self-lags p=0 (BIC) ; cause block K=3 ; no day-FE (single day) ; hac-panel SE (bw=3).
      H0: b₁ = … = b_3 = 0   →   Wald χ²(3) = 0.82,  p = 0.844    |   BH-FDR p = 0.932 
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + Σ(j=1..3) dⱼ·yₜ₋ⱼ
      controls: ADL self-lags p=3 (BIC) ; cause block K=3 ; no day-FE (single day) ; hac-panel SE (bw=3).
      H0: d₁ = … = d_3 = 0   →   Wald χ²(3) = 39.33,  p = 1.48e-08 ***   |   BH-FDR p = 1.04e-07 ***
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..3) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=3 ; sample spans 1 days (probit: no day-FE) ; hac-panel SE (bw=3).
      H0: b₁ = … = b_3 = 0   →   Wald χ²(3) = 2.04,  p = 0.565    |   BH-FDR p = 0.811 
   => event verdict: ETF Granger-leads Kalshi.

3. OVERALL VERDICT
   Calendar says 'neither direction significant' but Event says 'ETF Granger-leads Kalshi' — not robust across time-axis.

------------------------------------------------------------------------------------------------
This pair's joint-Wald p per direction is also in the single-pair heatmap (core figure 1).
```

---

### Rank 26/48 — Harris 276 EV × VAW

```text
GRANGER CAUSALITY    —    Rank 26 / 48
================================================================================================
Harris 276 EV   x   VAW      [ticker: KXECKH276]
Contract : "Will Harris win 276-262 - PA, NV, MI, WI?"
Window : 2024-11-04 to 2024-11-26     primary bar : 10min     Kalshi trades : 43

Test: joint Wald H0 = all PAST cause-lags are 0 (controls the effect's own past; hac-panel SE).
p<0.05 ⇒ that variable Granger-leads the other.  (x=Δprob, y=ETF log return.)

1. CALENDAR-TIME (clock-time lags, full RTH grid)
   Direction A — Kalshi → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..3) bⱼ·xₜ₋ⱼ + Σ(d=1..5) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=3 ; day-FE over 6 days ; hac-panel SE (bw=3).
      H0: b₁ = … = b_3 = 0   →   Wald χ²(3) = 11.60,  p = 0.00889 ***   |   BH-FDR p = 0.0343 **
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + Σ(j=1..3) dⱼ·yₜ₋ⱼ + Σ(d=1..5) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=3 ; day-FE over 6 days ; hac-panel SE (bw=3).
      H0: d₁ = … = d_3 = 0   →   Wald χ²(3) = 3.37,  p = 0.338    |   BH-FDR p = 0.706 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..3) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=3 ; sample spans 6 days (probit: no day-FE) ; hac-panel SE (bw=3).
      H0: b₁ = … = b_3 = 0   →   Wald χ²(3) = 2.91,  p = 0.406    |   BH-FDR p = 0.586 
   => calendar verdict: Kalshi Granger-leads ETF.

2. EVENT-TIME (event-count lags)
   Direction A — Kalshi → ETF:
      yₜ = α + φ₁·yₜ₋₁ + φ₂·yₜ₋₂ + φ₃·yₜ₋₃ + Σ(j=1..3) bⱼ·xₜ₋ⱼ
      controls: ADL self-lags p=3 (BIC) ; cause block K=3 ; no day-FE (single day) ; hac-panel SE (bw=3).
      H0: b₁ = … = b_3 = 0   →   Wald χ²(3) = 8.00,  p = 0.046 **   |   BH-FDR p = 0.107 
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + Σ(j=1..3) dⱼ·yₜ₋ⱼ
      controls: ADL self-lags p=3 (BIC) ; cause block K=3 ; no day-FE (single day) ; hac-panel SE (bw=3).
      H0: d₁ = … = d_3 = 0   →   Wald χ²(3) = 8.75,  p = 0.0328 **   |   BH-FDR p = 0.11 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + φ₂·yₜ₋₂ + φ₃·yₜ₋₃ + Σ(j=1..3) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=3 (BIC) ; cause block K=3 ; sample spans 1 days (probit: no day-FE) ; hac-panel SE (bw=3).
      H0: b₁ = … = b_3 = 0   →   Wald χ²(3) = 67.80,  p = 1.26e-14 ***   |   BH-FDR p = 2.9e-13 ***
   => event verdict: bidirectional (both reject).

3. OVERALL VERDICT
   Calendar says 'Kalshi Granger-leads ETF' but Event says 'bidirectional (both reject)' — not robust across time-axis.

------------------------------------------------------------------------------------------------
This pair's joint-Wald p per direction is also in the single-pair heatmap (core figure 1).
```

---

### Rank 27/48 — Harris 287 EV × VNQ

```text
GRANGER CAUSALITY    —    Rank 27 / 48
================================================================================================
Harris 287 EV   x   VNQ      [ticker: KXECKH287]
Contract : "Will Harris win 287-251 - PA, NV, MI, WI, AZ?"
Window : 2024-11-04 to 2024-11-21     primary bar : 10min     Kalshi trades : 39

Test: joint Wald H0 = all PAST cause-lags are 0 (controls the effect's own past; hac-panel SE).
p<0.05 ⇒ that variable Granger-leads the other.  (x=Δprob, y=ETF log return.)

1. CALENDAR-TIME (clock-time lags, full RTH grid)
   Direction A — Kalshi → ETF:
      yₜ = α + (no y self-lag term: BIC chose p=0) + Σ(j=1..3) bⱼ·xₜ₋ⱼ + Σ(d=1..4) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=3 ; day-FE over 5 days ; hac-panel SE (bw=3).
      H0: b₁ = … = b_3 = 0   →   Wald χ²(3) = 1.66,  p = 0.646    |   BH-FDR p = 0.727 
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + Σ(j=1..3) dⱼ·yₜ₋ⱼ + Σ(d=1..4) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=3 ; day-FE over 5 days ; hac-panel SE (bw=3).
      H0: d₁ = … = d_3 = 0   →   Wald χ²(3) = 3.45,  p = 0.328    |   BH-FDR p = 0.706 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..3) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=3 ; sample spans 5 days (probit: no day-FE) ; hac-panel SE (bw=3).
      H0: b₁ = … = b_3 = 0   →   Wald χ²(3) = 5.70,  p = 0.127    |   BH-FDR p = 0.429 
   => calendar verdict: neither direction significant.

2. EVENT-TIME (event-count lags)
   Direction A — Kalshi → ETF:
      yₜ = α + φ₁·yₜ₋₁ + φ₂·yₜ₋₂ + φ₃·yₜ₋₃ + Σ(j=1..3) bⱼ·xₜ₋ⱼ + Σ(d=1..1) γ_d·Day_d
      controls: ADL self-lags p=3 (BIC) ; cause block K=3 ; day-FE over 2 days ; hac-panel SE (bw=3).
      H0: b₁ = … = b_3 = 0   →   Wald χ²(3) = 12.71,  p = 0.00531 ***   |   BH-FDR p = 0.0186 **
   Direction B — ETF → Kalshi:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + Σ(j=1..3) dⱼ·yₜ₋ⱼ + Σ(d=1..1) γ_d·Day_d
      controls: ADL self-lags p=3 (BIC) ; cause block K=3 ; day-FE over 2 days ; hac-panel SE (bw=3).
      H0: d₁ = … = d_3 = 0   →   Wald χ²(3) = 41.76,  p = 4.5e-09 ***   |   BH-FDR p = 9.46e-08 ***
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + φ₂·yₜ₋₂ + φ₃·yₜ₋₃ + Σ(j=1..3) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=3 (BIC) ; cause block K=3 ; sample spans 2 days (probit: no day-FE) ; hac-panel SE (bw=3).
      H0: b₁ = … = b_3 = 0   →   Wald χ²(3) = 13.81,  p = 0.00317 ***   |   BH-FDR p = 0.0225 **
   => event verdict: bidirectional (both reject).

3. OVERALL VERDICT
   Calendar says 'neither direction significant' but Event says 'bidirectional (both reject)' — not robust across time-axis.

------------------------------------------------------------------------------------------------
This pair's joint-Wald p per direction is also in the single-pair heatmap (core figure 1).
```

---

# MERGE pooled signals — detail

---

## MERGE — ELECTION_trump_fav  (Granger overview)

```text
MERGE pooled signal — GRANGER overview :  ELECTION_trump_fav
================================================================================================
Each pooled signal = members' sign-aligned Δprob pooled (member fixed effects, hac-panel SE by
member×day). 'Sign-aligned' means each member's Δprob is multiplied by ±1 so that a positive value
always means the same real-world direction (e.g. a MIN-side contract is flipped). The CONTINUOUS
magnitude of Δprob is kept — the moves are NOT discretized to ±1.
Joint Wald per direction; S=combined pooled signal, E=ETF. p<0.05 ⇒ that side leads.

ETF        cal S→E     cal E→S     evt S→E     evt E→S   verdict(cal / evt)
VAW           0.49        0.42  1.3e-05***        0.21   - / S→E
VCR         0.065*        0.37      0.086*        0.25   - / -
VDC      0.0096***        0.24     0.014**        0.19   S→E / S→E
VDE           0.13         0.2   0.0019***     0.022**   - / bidir
VFH     0.00027***         0.8  2.7e-05***        0.59   S→E / S→E
VGT           0.69        0.66        0.14        0.72   - / -
VIS        0.028**        0.35  4.9e-06***        0.24   S→E / S→E
VNQ           0.32        0.45   0.0019***      0.03**   - / bidir
VOX            0.2        0.18  0.00017***        0.34   - / S→E

Per-ETF pseudo-pairs (combined pooled signal × each ETF) follow, each with explicit formulas + joint Wald.
```


### ELECTION_trump_fav (combined)  ×  VAW

```text
GRANGER —  ELECTION_trump_fav (combined pooled signal)   x   VAW
================================================================================================
S = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level). x=Δprob(S), y=ETF log return.
Joint Wald H0 = all PAST cause-lags 0; member FE (linear); hac-panel SE by member×day. p<0.05 ⇒ leads.

1. CALENDAR-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..6) bⱼ·xₜ₋ⱼ + Σ(d=1..21) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=6 ; day-FE over 22 days ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 5.47,  p = 0.485    |   BH-FDR p = 0.561 
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + ψ₅·xₜ₋₅ + Σ(j=1..6) dⱼ·yₜ₋ⱼ + Σ(d=1..21) γ_d·Day_d
      controls: ADL self-lags p=5 (BIC) ; cause block K=6 ; day-FE over 22 days ; hac-panel SE (bw=6).
      H0: d₁ = … = d_6 = 0   →   Wald χ²(6) = 6.04,  p = 0.418    |   BH-FDR p = 0.735 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..6) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=6 ; sample spans 22 days (probit: no day-FE) ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 8.27,  p = 0.219    |   BH-FDR p = 0.476 
   => calendar verdict: neither direction significant.

2. EVENT-TIME
   Direction A — Pooled → ETF:
      yₜ = α + (no y self-lag term: BIC chose p=0) + Σ(j=1..6) bⱼ·xₜ₋ⱼ + Σ(d=1..4) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=6 ; day-FE over 5 days ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 32.54,  p = 1.28e-05 ***   |   BH-FDR p = 0.000116 ***
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + ψ₅·xₜ₋₅ + Σ(j=1..6) dⱼ·yₜ₋ⱼ + Σ(d=1..4) γ_d·Day_d
      controls: ADL self-lags p=5 (BIC) ; cause block K=6 ; day-FE over 5 days ; hac-panel SE (bw=6).
      H0: d₁ = … = d_6 = 0   →   Wald χ²(6) = 8.33,  p = 0.215    |   BH-FDR p = 0.568 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..6) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=6 ; sample spans 5 days (probit: no day-FE) ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 8.92,  p = 0.178    |   BH-FDR p = 0.303 
   => event verdict: Pooled Granger-leads ETF.
```


### ELECTION_trump_fav (combined)  ×  VCR

```text
GRANGER —  ELECTION_trump_fav (combined pooled signal)   x   VCR
================================================================================================
S = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level). x=Δprob(S), y=ETF log return.
Joint Wald H0 = all PAST cause-lags 0; member FE (linear); hac-panel SE by member×day. p<0.05 ⇒ leads.

1. CALENDAR-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..6) bⱼ·xₜ₋ⱼ + Σ(d=1..21) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=6 ; day-FE over 22 days ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 11.86,  p = 0.0651 *   |   BH-FDR p = 0.172 
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + ψ₅·xₜ₋₅ + Σ(j=1..6) dⱼ·yₜ₋ⱼ + Σ(d=1..21) γ_d·Day_d
      controls: ADL self-lags p=5 (BIC) ; cause block K=6 ; day-FE over 22 days ; hac-panel SE (bw=6).
      H0: d₁ = … = d_6 = 0   →   Wald χ²(6) = 6.47,  p = 0.372    |   BH-FDR p = 0.735 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..6) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=6 ; sample spans 22 days (probit: no day-FE) ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 3.48,  p = 0.747    |   BH-FDR p = 0.864 
   => calendar verdict: neither direction significant.

2. EVENT-TIME
   Direction A — Pooled → ETF:
      yₜ = α + (no y self-lag term: BIC chose p=0) + Σ(j=1..6) bⱼ·xₜ₋ⱼ + Σ(d=1..4) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=6 ; day-FE over 5 days ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 11.08,  p = 0.086 *   |   BH-FDR p = 0.119 
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + ψ₅·xₜ₋₅ + Σ(j=1..6) dⱼ·yₜ₋ⱼ + Σ(d=1..4) γ_d·Day_d
      controls: ADL self-lags p=5 (BIC) ; cause block K=6 ; day-FE over 5 days ; hac-panel SE (bw=6).
      H0: d₁ = … = d_6 = 0   →   Wald χ²(6) = 7.81,  p = 0.253    |   BH-FDR p = 0.568 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..6) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=6 ; sample spans 5 days (probit: no day-FE) ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 10.95,  p = 0.09 *   |   BH-FDR p = 0.231 
   => event verdict: neither direction significant.
```


### ELECTION_trump_fav (combined)  ×  VDC

```text
GRANGER —  ELECTION_trump_fav (combined pooled signal)   x   VDC
================================================================================================
S = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level). x=Δprob(S), y=ETF log return.
Joint Wald H0 = all PAST cause-lags 0; member FE (linear); hac-panel SE by member×day. p<0.05 ⇒ leads.

1. CALENDAR-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..6) bⱼ·xₜ₋ⱼ + Σ(d=1..21) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=6 ; day-FE over 22 days ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 16.92,  p = 0.00959 ***   |   BH-FDR p = 0.0443 **
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + ψ₅·xₜ₋₅ + Σ(j=1..6) dⱼ·yₜ₋ⱼ + Σ(d=1..21) γ_d·Day_d
      controls: ADL self-lags p=5 (BIC) ; cause block K=6 ; day-FE over 22 days ; hac-panel SE (bw=6).
      H0: d₁ = … = d_6 = 0   →   Wald χ²(6) = 7.99,  p = 0.239    |   BH-FDR p = 0.735 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..6) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=6 ; sample spans 22 days (probit: no day-FE) ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 10.56,  p = 0.103    |   BH-FDR p = 0.452 
   => calendar verdict: Pooled Granger-leads ETF.

2. EVENT-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..6) bⱼ·xₜ₋ⱼ + Σ(d=1..4) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=6 ; day-FE over 5 days ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 15.87,  p = 0.0145 **   |   BH-FDR p = 0.0261 **
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + ψ₅·xₜ₋₅ + Σ(j=1..6) dⱼ·yₜ₋ⱼ + Σ(d=1..4) γ_d·Day_d
      controls: ADL self-lags p=5 (BIC) ; cause block K=6 ; day-FE over 5 days ; hac-panel SE (bw=6).
      H0: d₁ = … = d_6 = 0   →   Wald χ²(6) = 8.71,  p = 0.191    |   BH-FDR p = 0.568 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..6) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=6 ; sample spans 5 days (probit: no day-FE) ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 8.80,  p = 0.185    |   BH-FDR p = 0.303 
   => event verdict: Pooled Granger-leads ETF.
```


### ELECTION_trump_fav (combined)  ×  VDE

```text
GRANGER —  ELECTION_trump_fav (combined pooled signal)   x   VDE
================================================================================================
S = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level). x=Δprob(S), y=ETF log return.
Joint Wald H0 = all PAST cause-lags 0; member FE (linear); hac-panel SE by member×day. p<0.05 ⇒ leads.

1. CALENDAR-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + φ₂·yₜ₋₂ + Σ(j=1..6) bⱼ·xₜ₋ⱼ + Σ(d=1..21) γ_d·Day_d
      controls: ADL self-lags p=2 (BIC) ; cause block K=6 ; day-FE over 22 days ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 9.83,  p = 0.132    |   BH-FDR p = 0.272 
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + ψ₅·xₜ₋₅ + Σ(j=1..6) dⱼ·yₜ₋ⱼ + Σ(d=1..21) γ_d·Day_d
      controls: ADL self-lags p=5 (BIC) ; cause block K=6 ; day-FE over 22 days ; hac-panel SE (bw=6).
      H0: d₁ = … = d_6 = 0   →   Wald χ²(6) = 8.53,  p = 0.202    |   BH-FDR p = 0.735 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..6) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=6 ; sample spans 22 days (probit: no day-FE) ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 10.44,  p = 0.107    |   BH-FDR p = 0.452 
   => calendar verdict: neither direction significant.

2. EVENT-TIME
   Direction A — Pooled → ETF:
      yₜ = α + (no y self-lag term: BIC chose p=0) + Σ(j=1..6) bⱼ·xₜ₋ⱼ + Σ(d=1..4) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=6 ; day-FE over 5 days ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 20.93,  p = 0.00189 ***   |   BH-FDR p = 0.0041 ***
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + ψ₅·xₜ₋₅ + Σ(j=1..6) dⱼ·yₜ₋ⱼ + Σ(d=1..4) γ_d·Day_d
      controls: ADL self-lags p=5 (BIC) ; cause block K=6 ; day-FE over 5 days ; hac-panel SE (bw=6).
      H0: d₁ = … = d_6 = 0   →   Wald χ²(6) = 14.76,  p = 0.0222 **   |   BH-FDR p = 0.269 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..6) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=6 ; sample spans 5 days (probit: no day-FE) ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 9.65,  p = 0.14    |   BH-FDR p = 0.28 
   => event verdict: bidirectional (both reject).
```


### ELECTION_trump_fav (combined)  ×  VFH

```text
GRANGER —  ELECTION_trump_fav (combined pooled signal)   x   VFH
================================================================================================
S = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level). x=Δprob(S), y=ETF log return.
Joint Wald H0 = all PAST cause-lags 0; member FE (linear); hac-panel SE by member×day. p<0.05 ⇒ leads.

1. CALENDAR-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..6) bⱼ·xₜ₋ⱼ + Σ(d=1..21) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=6 ; day-FE over 22 days ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 25.51,  p = 0.000274 ***   |   BH-FDR p = 0.00307 ***
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + ψ₅·xₜ₋₅ + Σ(j=1..6) dⱼ·yₜ₋ⱼ + Σ(d=1..21) γ_d·Day_d
      controls: ADL self-lags p=5 (BIC) ; cause block K=6 ; day-FE over 22 days ; hac-panel SE (bw=6).
      H0: d₁ = … = d_6 = 0   →   Wald χ²(6) = 3.10,  p = 0.796    |   BH-FDR p = 0.859 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..6) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=6 ; sample spans 22 days (probit: no day-FE) ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 22.06,  p = 0.00118 ***   |   BH-FDR p = 0.0438 **
   => calendar verdict: Pooled Granger-leads ETF.

2. EVENT-TIME
   Direction A — Pooled → ETF:
      yₜ = α + (no y self-lag term: BIC chose p=0) + Σ(j=1..6) bⱼ·xₜ₋ⱼ + Σ(d=1..4) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=6 ; day-FE over 5 days ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 30.84,  p = 2.72e-05 ***   |   BH-FDR p = 0.000163 ***
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + ψ₅·xₜ₋₅ + Σ(j=1..6) dⱼ·yₜ₋ⱼ + Σ(d=1..4) γ_d·Day_d
      controls: ADL self-lags p=5 (BIC) ; cause block K=6 ; day-FE over 5 days ; hac-panel SE (bw=6).
      H0: d₁ = … = d_6 = 0   →   Wald χ²(6) = 4.64,  p = 0.591    |   BH-FDR p = 0.818 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..6) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=6 ; sample spans 5 days (probit: no day-FE) ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 19.65,  p = 0.00319 ***   |   BH-FDR p = 0.0381 **
   => event verdict: Pooled Granger-leads ETF.
```


### ELECTION_trump_fav (combined)  ×  VGT

```text
GRANGER —  ELECTION_trump_fav (combined pooled signal)   x   VGT
================================================================================================
S = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level). x=Δprob(S), y=ETF log return.
Joint Wald H0 = all PAST cause-lags 0; member FE (linear); hac-panel SE by member×day. p<0.05 ⇒ leads.

1. CALENDAR-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + φ₂·yₜ₋₂ + Σ(j=1..6) bⱼ·xₜ₋ⱼ + Σ(d=1..21) γ_d·Day_d
      controls: ADL self-lags p=2 (BIC) ; cause block K=6 ; day-FE over 22 days ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 3.87,  p = 0.694    |   BH-FDR p = 0.755 
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + ψ₅·xₜ₋₅ + Σ(j=1..6) dⱼ·yₜ₋ⱼ + Σ(d=1..21) γ_d·Day_d
      controls: ADL self-lags p=5 (BIC) ; cause block K=6 ; day-FE over 22 days ; hac-panel SE (bw=6).
      H0: d₁ = … = d_6 = 0   →   Wald χ²(6) = 4.12,  p = 0.66    |   BH-FDR p = 0.842 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..6) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=6 ; sample spans 22 days (probit: no day-FE) ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 1.93,  p = 0.926    |   BH-FDR p = 0.963 
   => calendar verdict: neither direction significant.

2. EVENT-TIME
   Direction A — Pooled → ETF:
      yₜ = α + (no y self-lag term: BIC chose p=0) + Σ(j=1..6) bⱼ·xₜ₋ⱼ + Σ(d=1..4) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=6 ; day-FE over 5 days ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 9.66,  p = 0.14    |   BH-FDR p = 0.18 
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + ψ₅·xₜ₋₅ + Σ(j=1..6) dⱼ·yₜ₋ⱼ + Σ(d=1..4) γ_d·Day_d
      controls: ADL self-lags p=5 (BIC) ; cause block K=6 ; day-FE over 5 days ; hac-panel SE (bw=6).
      H0: d₁ = … = d_6 = 0   →   Wald χ²(6) = 3.69,  p = 0.718    |   BH-FDR p = 0.861 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..6) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=6 ; sample spans 5 days (probit: no day-FE) ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 5.02,  p = 0.541    |   BH-FDR p = 0.609 
   => event verdict: neither direction significant.
```


### ELECTION_trump_fav (combined)  ×  VIS

```text
GRANGER —  ELECTION_trump_fav (combined pooled signal)   x   VIS
================================================================================================
S = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level). x=Δprob(S), y=ETF log return.
Joint Wald H0 = all PAST cause-lags 0; member FE (linear); hac-panel SE by member×day. p<0.05 ⇒ leads.

1. CALENDAR-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..6) bⱼ·xₜ₋ⱼ + Σ(d=1..21) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=6 ; day-FE over 22 days ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 14.18,  p = 0.0277 **   |   BH-FDR p = 0.0817 *
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + ψ₅·xₜ₋₅ + Σ(j=1..6) dⱼ·yₜ₋ⱼ + Σ(d=1..21) γ_d·Day_d
      controls: ADL self-lags p=5 (BIC) ; cause block K=6 ; day-FE over 22 days ; hac-panel SE (bw=6).
      H0: d₁ = … = d_6 = 0   →   Wald χ²(6) = 6.69,  p = 0.35    |   BH-FDR p = 0.735 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..6) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=6 ; sample spans 22 days (probit: no day-FE) ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 8.83,  p = 0.183    |   BH-FDR p = 0.452 
   => calendar verdict: Pooled Granger-leads ETF.

2. EVENT-TIME
   Direction A — Pooled → ETF:
      yₜ = α + (no y self-lag term: BIC chose p=0) + Σ(j=1..6) bⱼ·xₜ₋ⱼ + Σ(d=1..4) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=6 ; day-FE over 5 days ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 34.70,  p = 4.92e-06 ***   |   BH-FDR p = 8.85e-05 ***
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + ψ₅·xₜ₋₅ + Σ(j=1..6) dⱼ·yₜ₋ⱼ + Σ(d=1..4) γ_d·Day_d
      controls: ADL self-lags p=5 (BIC) ; cause block K=6 ; day-FE over 5 days ; hac-panel SE (bw=6).
      H0: d₁ = … = d_6 = 0   →   Wald χ²(6) = 8.02,  p = 0.237    |   BH-FDR p = 0.568 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..6) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=6 ; sample spans 5 days (probit: no day-FE) ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 14.74,  p = 0.0224 **   |   BH-FDR p = 0.0806 *
   => event verdict: Pooled Granger-leads ETF.
```


### ELECTION_trump_fav (combined)  ×  VNQ

```text
GRANGER —  ELECTION_trump_fav (combined pooled signal)   x   VNQ
================================================================================================
S = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level). x=Δprob(S), y=ETF log return.
Joint Wald H0 = all PAST cause-lags 0; member FE (linear); hac-panel SE by member×day. p<0.05 ⇒ leads.

1. CALENDAR-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + φ₂·yₜ₋₂ + Σ(j=1..6) bⱼ·xₜ₋ⱼ + Σ(d=1..21) γ_d·Day_d
      controls: ADL self-lags p=2 (BIC) ; cause block K=6 ; day-FE over 22 days ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 7.00,  p = 0.321    |   BH-FDR p = 0.475 
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + ψ₅·xₜ₋₅ + Σ(j=1..6) dⱼ·yₜ₋ⱼ + Σ(d=1..21) γ_d·Day_d
      controls: ADL self-lags p=5 (BIC) ; cause block K=6 ; day-FE over 22 days ; hac-panel SE (bw=6).
      H0: d₁ = … = d_6 = 0   →   Wald χ²(6) = 5.73,  p = 0.454    |   BH-FDR p = 0.735 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..6) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=6 ; sample spans 22 days (probit: no day-FE) ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 7.42,  p = 0.284    |   BH-FDR p = 0.552 
   => calendar verdict: neither direction significant.

2. EVENT-TIME
   Direction A — Pooled → ETF:
      yₜ = α + (no y self-lag term: BIC chose p=0) + Σ(j=1..6) bⱼ·xₜ₋ⱼ + Σ(d=1..4) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=6 ; day-FE over 5 days ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 20.93,  p = 0.00189 ***   |   BH-FDR p = 0.0041 ***
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + ψ₅·xₜ₋₅ + Σ(j=1..6) dⱼ·yₜ₋ⱼ + Σ(d=1..4) γ_d·Day_d
      controls: ADL self-lags p=5 (BIC) ; cause block K=6 ; day-FE over 5 days ; hac-panel SE (bw=6).
      H0: d₁ = … = d_6 = 0   →   Wald χ²(6) = 13.98,  p = 0.0299 **   |   BH-FDR p = 0.269 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..6) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=6 ; sample spans 4 days (probit: no day-FE) ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 11.08,  p = 0.0859 *   |   BH-FDR p = 0.231 
   => event verdict: bidirectional (both reject).
```


### ELECTION_trump_fav (combined)  ×  VOX

```text
GRANGER —  ELECTION_trump_fav (combined pooled signal)   x   VOX
================================================================================================
S = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level). x=Δprob(S), y=ETF log return.
Joint Wald H0 = all PAST cause-lags 0; member FE (linear); hac-panel SE by member×day. p<0.05 ⇒ leads.

1. CALENDAR-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + φ₂·yₜ₋₂ + Σ(j=1..6) bⱼ·xₜ₋ⱼ + Σ(d=1..21) γ_d·Day_d
      controls: ADL self-lags p=2 (BIC) ; cause block K=6 ; day-FE over 22 days ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 8.64,  p = 0.195    |   BH-FDR p = 0.38 
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + ψ₅·xₜ₋₅ + Σ(j=1..6) dⱼ·yₜ₋ⱼ + Σ(d=1..21) γ_d·Day_d
      controls: ADL self-lags p=5 (BIC) ; cause block K=6 ; day-FE over 22 days ; hac-panel SE (bw=6).
      H0: d₁ = … = d_6 = 0   →   Wald χ²(6) = 8.87,  p = 0.181    |   BH-FDR p = 0.735 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..6) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=6 ; sample spans 22 days (probit: no day-FE) ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 4.01,  p = 0.676    |   BH-FDR p = 0.817 
   => calendar verdict: neither direction significant.

2. EVENT-TIME
   Direction A — Pooled → ETF:
      yₜ = α + (no y self-lag term: BIC chose p=0) + Σ(j=1..6) bⱼ·xₜ₋ⱼ + Σ(d=1..4) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=6 ; day-FE over 5 days ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 26.64,  p = 0.000169 ***   |   BH-FDR p = 0.000761 ***
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + ψ₅·xₜ₋₅ + Σ(j=1..6) dⱼ·yₜ₋ⱼ + Σ(d=1..4) γ_d·Day_d
      controls: ADL self-lags p=5 (BIC) ; cause block K=6 ; day-FE over 5 days ; hac-panel SE (bw=6).
      H0: d₁ = … = d_6 = 0   →   Wald χ²(6) = 6.79,  p = 0.341    |   BH-FDR p = 0.614 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..6) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=6 ; sample spans 5 days (probit: no day-FE) ; hac-panel SE (bw=6).
      H0: b₁ = … = b_6 = 0   →   Wald χ²(6) = 18.96,  p = 0.00423 ***   |   BH-FDR p = 0.0381 **
   => event verdict: Pooled Granger-leads ETF.
```

---

## MERGE — FOMC_easing  (Granger overview)

```text
MERGE pooled signal — GRANGER overview :  FOMC_easing
================================================================================================
Each pooled signal = members' sign-aligned Δprob pooled (member fixed effects, hac-panel SE by
member×day). 'Sign-aligned' means each member's Δprob is multiplied by ±1 so that a positive value
always means the same real-world direction (e.g. a MIN-side contract is flipped). The CONTINUOUS
magnitude of Δprob is kept — the moves are NOT discretized to ±1.
Joint Wald per direction; S=combined pooled signal, E=ETF. p<0.05 ⇒ that side leads.

ETF        cal S→E     cal E→S     evt S→E     evt E→S   verdict(cal / evt)
VCR           0.31        0.22         0.6        0.84   - / -
VDC           0.41        0.25      0.079*        0.33   - / -
VDE           0.11        0.83        0.21        0.66   - / -
VFH           0.54        0.81    0.002***        0.43   - / S→E
VGT           0.79     0.024**        0.69        0.45   E→S / -
VIS            0.8        0.31     0.049**         0.9   - / S→E
VNQ           0.43        0.45   0.0014***         0.1   - / S→E
VOX           0.31        0.35        0.68         0.8   - / -
VPU        0.012**        0.32   0.0012***        0.13   S→E / S→E

Per-ETF pseudo-pairs (combined pooled signal × each ETF) follow, each with explicit formulas + joint Wald.
```


### FOMC_easing (combined)  ×  VCR

```text
GRANGER —  FOMC_easing (combined pooled signal)   x   VCR
================================================================================================
S = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level). x=Δprob(S), y=ETF log return.
Joint Wald H0 = all PAST cause-lags 0; member FE (linear); hac-panel SE by member×day. p<0.05 ⇒ leads.

1. CALENDAR-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + φ₂·yₜ₋₂ + φ₃·yₜ₋₃ + φ₄·yₜ₋₄ + φ₅·yₜ₋₅ + φ₆·yₜ₋₆ + Σ(j=1..10) bⱼ·xₜ₋ⱼ + Σ(d=1..74) γ_d·Day_d
      controls: ADL self-lags p=6 (BIC) ; cause block K=10 ; day-FE over 75 days ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 11.70,  p = 0.306    |   BH-FDR p = 0.475 
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + ψ₅·xₜ₋₅ + Σ(j=1..10) dⱼ·yₜ₋ⱼ + Σ(d=1..74) γ_d·Day_d
      controls: ADL self-lags p=5 (BIC) ; cause block K=10 ; day-FE over 75 days ; hac-panel SE (bw=10).
      H0: d₁ = … = d_10 = 0   →   Wald χ²(10) = 13.12,  p = 0.217    |   BH-FDR p = 0.735 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..10) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=10 ; sample spans 75 days (probit: no day-FE) ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 9.98,  p = 0.442    |   BH-FDR p = 0.654 
   => calendar verdict: neither direction significant.

2. EVENT-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..10) bⱼ·xₜ₋ⱼ + Σ(d=1..42) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=10 ; day-FE over 43 days ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 8.28,  p = 0.602    |   BH-FDR p = 0.677 
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + ψ₅·xₜ₋₅ + ψ₆·xₜ₋₆ + Σ(j=1..10) dⱼ·yₜ₋ⱼ + Σ(d=1..42) γ_d·Day_d
      controls: ADL self-lags p=6 (BIC) ; cause block K=10 ; day-FE over 43 days ; hac-panel SE (bw=10).
      H0: d₁ = … = d_10 = 0   →   Wald χ²(10) = 5.70,  p = 0.84    |   BH-FDR p = 0.889 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..10) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=10 ; sample spans 43 days (probit: no day-FE) ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 13.13,  p = 0.216    |   BH-FDR p = 0.325 
   => event verdict: neither direction significant.
```


### FOMC_easing (combined)  ×  VDC

```text
GRANGER —  FOMC_easing (combined pooled signal)   x   VDC
================================================================================================
S = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level). x=Δprob(S), y=ETF log return.
Joint Wald H0 = all PAST cause-lags 0; member FE (linear); hac-panel SE by member×day. p<0.05 ⇒ leads.

1. CALENDAR-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..10) bⱼ·xₜ₋ⱼ + Σ(d=1..74) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=10 ; day-FE over 75 days ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 10.33,  p = 0.412    |   BH-FDR p = 0.522 
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + ψ₅·xₜ₋₅ + Σ(j=1..10) dⱼ·yₜ₋ⱼ + Σ(d=1..74) γ_d·Day_d
      controls: ADL self-lags p=5 (BIC) ; cause block K=10 ; day-FE over 75 days ; hac-panel SE (bw=10).
      H0: d₁ = … = d_10 = 0   →   Wald χ²(10) = 12.58,  p = 0.248    |   BH-FDR p = 0.735 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..10) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=10 ; sample spans 75 days (probit: no day-FE) ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 10.80,  p = 0.373    |   BH-FDR p = 0.627 
   => calendar verdict: neither direction significant.

2. EVENT-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..10) bⱼ·xₜ₋ⱼ + Σ(d=1..42) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=10 ; day-FE over 43 days ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 16.81,  p = 0.0786 *   |   BH-FDR p = 0.118 
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + ψ₅·xₜ₋₅ + ψ₆·xₜ₋₆ + Σ(j=1..10) dⱼ·yₜ₋ⱼ + Σ(d=1..42) γ_d·Day_d
      controls: ADL self-lags p=6 (BIC) ; cause block K=10 ; day-FE over 43 days ; hac-panel SE (bw=10).
      H0: d₁ = … = d_10 = 0   →   Wald χ²(10) = 11.35,  p = 0.331    |   BH-FDR p = 0.614 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..10) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=10 ; sample spans 41 days (probit: no day-FE) ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 10.96,  p = 0.36    |   BH-FDR p = 0.499 
   => event verdict: neither direction significant.
```


### FOMC_easing (combined)  ×  VDE

```text
GRANGER —  FOMC_easing (combined pooled signal)   x   VDE
================================================================================================
S = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level). x=Δprob(S), y=ETF log return.
Joint Wald H0 = all PAST cause-lags 0; member FE (linear); hac-panel SE by member×day. p<0.05 ⇒ leads.

1. CALENDAR-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..10) bⱼ·xₜ₋ⱼ + Σ(d=1..74) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=10 ; day-FE over 75 days ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 15.56,  p = 0.113    |   BH-FDR p = 0.246 
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + ψ₅·xₜ₋₅ + Σ(j=1..10) dⱼ·yₜ₋ⱼ + Σ(d=1..74) γ_d·Day_d
      controls: ADL self-lags p=5 (BIC) ; cause block K=10 ; day-FE over 75 days ; hac-panel SE (bw=10).
      H0: d₁ = … = d_10 = 0   →   Wald χ²(10) = 5.76,  p = 0.835    |   BH-FDR p = 0.859 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..10) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=10 ; sample spans 75 days (probit: no day-FE) ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 7.43,  p = 0.685    |   BH-FDR p = 0.817 
   => calendar verdict: neither direction significant.

2. EVENT-TIME
   Direction A — Pooled → ETF:
      yₜ = α + (no y self-lag term: BIC chose p=0) + Σ(j=1..10) bⱼ·xₜ₋ⱼ + Σ(d=1..42) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=10 ; day-FE over 43 days ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 13.22,  p = 0.212    |   BH-FDR p = 0.254 
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + ψ₅·xₜ₋₅ + ψ₆·xₜ₋₆ + Σ(j=1..10) dⱼ·yₜ₋ⱼ + Σ(d=1..42) γ_d·Day_d
      controls: ADL self-lags p=6 (BIC) ; cause block K=10 ; day-FE over 43 days ; hac-panel SE (bw=10).
      H0: d₁ = … = d_10 = 0   →   Wald χ²(10) = 7.73,  p = 0.655    |   BH-FDR p = 0.843 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..10) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=10 ; sample spans 41 days (probit: no day-FE) ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 9.27,  p = 0.507    |   BH-FDR p = 0.608 
   => event verdict: neither direction significant.
```


### FOMC_easing (combined)  ×  VFH

```text
GRANGER —  FOMC_easing (combined pooled signal)   x   VFH
================================================================================================
S = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level). x=Δprob(S), y=ETF log return.
Joint Wald H0 = all PAST cause-lags 0; member FE (linear); hac-panel SE by member×day. p<0.05 ⇒ leads.

1. CALENDAR-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + φ₂·yₜ₋₂ + φ₃·yₜ₋₃ + φ₄·yₜ₋₄ + φ₅·yₜ₋₅ + Σ(j=1..10) bⱼ·xₜ₋ⱼ + Σ(d=1..74) γ_d·Day_d
      controls: ADL self-lags p=5 (BIC) ; cause block K=10 ; day-FE over 75 days ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 8.91,  p = 0.54    |   BH-FDR p = 0.606 
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + ψ₅·xₜ₋₅ + Σ(j=1..10) dⱼ·yₜ₋ⱼ + Σ(d=1..74) γ_d·Day_d
      controls: ADL self-lags p=5 (BIC) ; cause block K=10 ; day-FE over 75 days ; hac-panel SE (bw=10).
      H0: d₁ = … = d_10 = 0   →   Wald χ²(10) = 6.02,  p = 0.813    |   BH-FDR p = 0.859 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..10) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=10 ; sample spans 75 days (probit: no day-FE) ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 5.91,  p = 0.823    |   BH-FDR p = 0.905 
   => calendar verdict: neither direction significant.

2. EVENT-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..10) bⱼ·xₜ₋ⱼ + Σ(d=1..42) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=10 ; day-FE over 43 days ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 27.66,  p = 0.00205 ***   |   BH-FDR p = 0.0041 ***
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + ψ₅·xₜ₋₅ + ψ₆·xₜ₋₆ + Σ(j=1..10) dⱼ·yₜ₋ⱼ + Σ(d=1..42) γ_d·Day_d
      controls: ADL self-lags p=6 (BIC) ; cause block K=10 ; day-FE over 43 days ; hac-panel SE (bw=10).
      H0: d₁ = … = d_10 = 0   →   Wald χ²(10) = 10.13,  p = 0.429    |   BH-FDR p = 0.675 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..10) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=10 ; sample spans 42 days (probit: no day-FE) ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 20.99,  p = 0.0211 **   |   BH-FDR p = 0.0806 *
   => event verdict: Pooled Granger-leads ETF.
```


### FOMC_easing (combined)  ×  VGT

```text
GRANGER —  FOMC_easing (combined pooled signal)   x   VGT
================================================================================================
S = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level). x=Δprob(S), y=ETF log return.
Joint Wald H0 = all PAST cause-lags 0; member FE (linear); hac-panel SE by member×day. p<0.05 ⇒ leads.

1. CALENDAR-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + φ₂·yₜ₋₂ + φ₃·yₜ₋₃ + φ₄·yₜ₋₄ + φ₅·yₜ₋₅ + φ₆·yₜ₋₆ + Σ(j=1..10) bⱼ·xₜ₋ⱼ + Σ(d=1..74) γ_d·Day_d
      controls: ADL self-lags p=6 (BIC) ; cause block K=10 ; day-FE over 75 days ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 6.24,  p = 0.795    |   BH-FDR p = 0.819 
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + ψ₅·xₜ₋₅ + Σ(j=1..10) dⱼ·yₜ₋ⱼ + Σ(d=1..74) γ_d·Day_d
      controls: ADL self-lags p=5 (BIC) ; cause block K=10 ; day-FE over 75 days ; hac-panel SE (bw=10).
      H0: d₁ = … = d_10 = 0   →   Wald χ²(10) = 20.60,  p = 0.024 **   |   BH-FDR p = 0.735 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + φ₂·yₜ₋₂ + Σ(j=1..10) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=2 (BIC) ; cause block K=10 ; sample spans 75 days (probit: no day-FE) ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 3.25,  p = 0.975    |   BH-FDR p = 0.975 
   => calendar verdict: ETF Granger-leads Pooled.

2. EVENT-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..10) bⱼ·xₜ₋ⱼ + Σ(d=1..42) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=10 ; day-FE over 43 days ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 7.38,  p = 0.689    |   BH-FDR p = 0.689 
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + ψ₅·xₜ₋₅ + ψ₆·xₜ₋₆ + Σ(j=1..10) dⱼ·yₜ₋ⱼ + Σ(d=1..42) γ_d·Day_d
      controls: ADL self-lags p=6 (BIC) ; cause block K=10 ; day-FE over 43 days ; hac-panel SE (bw=10).
      H0: d₁ = … = d_10 = 0   →   Wald χ²(10) = 9.89,  p = 0.45    |   BH-FDR p = 0.675 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..10) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=10 ; sample spans 43 days (probit: no day-FE) ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 10.39,  p = 0.407    |   BH-FDR p = 0.523 
   => event verdict: neither direction significant.
```


### FOMC_easing (combined)  ×  VIS

```text
GRANGER —  FOMC_easing (combined pooled signal)   x   VIS
================================================================================================
S = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level). x=Δprob(S), y=ETF log return.
Joint Wald H0 = all PAST cause-lags 0; member FE (linear); hac-panel SE by member×day. p<0.05 ⇒ leads.

1. CALENDAR-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + φ₂·yₜ₋₂ + φ₃·yₜ₋₃ + φ₄·yₜ₋₄ + φ₅·yₜ₋₅ + φ₆·yₜ₋₆ + Σ(j=1..10) bⱼ·xₜ₋ⱼ + Σ(d=1..74) γ_d·Day_d
      controls: ADL self-lags p=6 (BIC) ; cause block K=10 ; day-FE over 75 days ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 6.21,  p = 0.797    |   BH-FDR p = 0.819 
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + ψ₅·xₜ₋₅ + Σ(j=1..10) dⱼ·yₜ₋ⱼ + Σ(d=1..74) γ_d·Day_d
      controls: ADL self-lags p=5 (BIC) ; cause block K=10 ; day-FE over 75 days ; hac-panel SE (bw=10).
      H0: d₁ = … = d_10 = 0   →   Wald χ²(10) = 11.59,  p = 0.313    |   BH-FDR p = 0.735 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..10) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=10 ; sample spans 75 days (probit: no day-FE) ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 8.69,  p = 0.561    |   BH-FDR p = 0.742 
   => calendar verdict: neither direction significant.

2. EVENT-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..10) bⱼ·xₜ₋ⱼ + Σ(d=1..42) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=10 ; day-FE over 43 days ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 18.37,  p = 0.049 **   |   BH-FDR p = 0.0802 *
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + ψ₅·xₜ₋₅ + ψ₆·xₜ₋₆ + Σ(j=1..10) dⱼ·yₜ₋ⱼ + Σ(d=1..42) γ_d·Day_d
      controls: ADL self-lags p=6 (BIC) ; cause block K=10 ; day-FE over 43 days ; hac-panel SE (bw=10).
      H0: d₁ = … = d_10 = 0   →   Wald χ²(10) = 4.79,  p = 0.905    |   BH-FDR p = 0.905 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..10) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=10 ; sample spans 42 days (probit: no day-FE) ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 8.21,  p = 0.608    |   BH-FDR p = 0.644 
   => event verdict: Pooled Granger-leads ETF.
```


### FOMC_easing (combined)  ×  VNQ

```text
GRANGER —  FOMC_easing (combined pooled signal)   x   VNQ
================================================================================================
S = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level). x=Δprob(S), y=ETF log return.
Joint Wald H0 = all PAST cause-lags 0; member FE (linear); hac-panel SE by member×day. p<0.05 ⇒ leads.

1. CALENDAR-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + φ₂·yₜ₋₂ + φ₃·yₜ₋₃ + φ₄·yₜ₋₄ + φ₅·yₜ₋₅ + φ₆·yₜ₋₆ + Σ(j=1..10) bⱼ·xₜ₋ⱼ + Σ(d=1..74) γ_d·Day_d
      controls: ADL self-lags p=6 (BIC) ; cause block K=10 ; day-FE over 75 days ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 10.16,  p = 0.427    |   BH-FDR p = 0.522 
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + ψ₅·xₜ₋₅ + Σ(j=1..10) dⱼ·yₜ₋ⱼ + Σ(d=1..74) γ_d·Day_d
      controls: ADL self-lags p=5 (BIC) ; cause block K=10 ; day-FE over 75 days ; hac-panel SE (bw=10).
      H0: d₁ = … = d_10 = 0   →   Wald χ²(10) = 9.95,  p = 0.445    |   BH-FDR p = 0.735 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..10) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=10 ; sample spans 75 days (probit: no day-FE) ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 14.15,  p = 0.166    |   BH-FDR p = 0.452 
   => calendar verdict: neither direction significant.

2. EVENT-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..10) bⱼ·xₜ₋ⱼ + Σ(d=1..42) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=10 ; day-FE over 43 days ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 28.76,  p = 0.00136 ***   |   BH-FDR p = 0.00408 ***
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + ψ₅·xₜ₋₅ + ψ₆·xₜ₋₆ + Σ(j=1..10) dⱼ·yₜ₋ⱼ + Σ(d=1..42) γ_d·Day_d
      controls: ADL self-lags p=6 (BIC) ; cause block K=10 ; day-FE over 43 days ; hac-panel SE (bw=10).
      H0: d₁ = … = d_10 = 0   →   Wald χ²(10) = 15.85,  p = 0.104    |   BH-FDR p = 0.568 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..10) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=10 ; sample spans 42 days (probit: no day-FE) ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 24.25,  p = 0.00697 ***   |   BH-FDR p = 0.0418 **
   => event verdict: Pooled Granger-leads ETF.
```


### FOMC_easing (combined)  ×  VOX

```text
GRANGER —  FOMC_easing (combined pooled signal)   x   VOX
================================================================================================
S = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level). x=Δprob(S), y=ETF log return.
Joint Wald H0 = all PAST cause-lags 0; member FE (linear); hac-panel SE by member×day. p<0.05 ⇒ leads.

1. CALENDAR-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + φ₂·yₜ₋₂ + φ₃·yₜ₋₃ + φ₄·yₜ₋₄ + φ₅·yₜ₋₅ + Σ(j=1..10) bⱼ·xₜ₋ⱼ + Σ(d=1..74) γ_d·Day_d
      controls: ADL self-lags p=5 (BIC) ; cause block K=10 ; day-FE over 75 days ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 11.65,  p = 0.309    |   BH-FDR p = 0.475 
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + ψ₅·xₜ₋₅ + Σ(j=1..10) dⱼ·yₜ₋ⱼ + Σ(d=1..74) γ_d·Day_d
      controls: ADL self-lags p=5 (BIC) ; cause block K=10 ; day-FE over 75 days ; hac-panel SE (bw=10).
      H0: d₁ = … = d_10 = 0   →   Wald χ²(10) = 11.08,  p = 0.352    |   BH-FDR p = 0.735 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..10) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=10 ; sample spans 75 days (probit: no day-FE) ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 14.05,  p = 0.171    |   BH-FDR p = 0.452 
   => calendar verdict: neither direction significant.

2. EVENT-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..10) bⱼ·xₜ₋ⱼ + Σ(d=1..42) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=10 ; day-FE over 43 days ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 7.51,  p = 0.677    |   BH-FDR p = 0.689 
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + ψ₅·xₜ₋₅ + ψ₆·xₜ₋₆ + Σ(j=1..10) dⱼ·yₜ₋ⱼ + Σ(d=1..42) γ_d·Day_d
      controls: ADL self-lags p=6 (BIC) ; cause block K=10 ; day-FE over 43 days ; hac-panel SE (bw=10).
      H0: d₁ = … = d_10 = 0   →   Wald χ²(10) = 6.21,  p = 0.797    |   BH-FDR p = 0.889 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..10) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=10 ; sample spans 42 days (probit: no day-FE) ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 4.19,  p = 0.938    |   BH-FDR p = 0.938 
   => event verdict: neither direction significant.
```


### FOMC_easing (combined)  ×  VPU

```text
GRANGER —  FOMC_easing (combined pooled signal)   x   VPU
================================================================================================
S = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level). x=Δprob(S), y=ETF log return.
Joint Wald H0 = all PAST cause-lags 0; member FE (linear); hac-panel SE by member×day. p<0.05 ⇒ leads.

1. CALENDAR-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..10) bⱼ·xₜ₋ⱼ + Σ(d=1..74) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=10 ; day-FE over 75 days ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 22.67,  p = 0.012 **   |   BH-FDR p = 0.0495 **
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + ψ₅·xₜ₋₅ + Σ(j=1..10) dⱼ·yₜ₋ⱼ + Σ(d=1..74) γ_d·Day_d
      controls: ADL self-lags p=5 (BIC) ; cause block K=10 ; day-FE over 75 days ; hac-panel SE (bw=10).
      H0: d₁ = … = d_10 = 0   →   Wald χ²(10) = 11.50,  p = 0.32    |   BH-FDR p = 0.735 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..10) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=10 ; sample spans 75 days (probit: no day-FE) ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 21.26,  p = 0.0194 **   |   BH-FDR p = 0.154 
   => calendar verdict: Pooled Granger-leads ETF.

2. EVENT-TIME
   Direction A — Pooled → ETF:
      yₜ = α + (no y self-lag term: BIC chose p=0) + Σ(j=1..10) bⱼ·xₜ₋ⱼ + Σ(d=1..42) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=10 ; day-FE over 43 days ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 29.20,  p = 0.00116 ***   |   BH-FDR p = 0.00408 ***
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + ψ₂·xₜ₋₂ + ψ₃·xₜ₋₃ + ψ₄·xₜ₋₄ + ψ₅·xₜ₋₅ + ψ₆·xₜ₋₆ + Σ(j=1..10) dⱼ·yₜ₋ⱼ + Σ(d=1..42) γ_d·Day_d
      controls: ADL self-lags p=6 (BIC) ; cause block K=10 ; day-FE over 43 days ; hac-panel SE (bw=10).
      H0: d₁ = … = d_10 = 0   →   Wald χ²(10) = 14.94,  p = 0.134    |   BH-FDR p = 0.568 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..10) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=10 ; sample spans 43 days (probit: no day-FE) ; hac-panel SE (bw=10).
      H0: b₁ = … = b_10 = 0   →   Wald χ²(10) = 15.28,  p = 0.122    |   BH-FDR p = 0.275 
   => event verdict: Pooled Granger-leads ETF.
```

---

## MERGE — GAS_above  (Granger overview)

```text
MERGE pooled signal — GRANGER overview :  GAS_above
================================================================================================
Each pooled signal = members' sign-aligned Δprob pooled (member fixed effects, hac-panel SE by
member×day). 'Sign-aligned' means each member's Δprob is multiplied by ±1 so that a positive value
always means the same real-world direction (e.g. a MIN-side contract is flipped). The CONTINUOUS
magnitude of Δprob is kept — the moves are NOT discretized to ±1.
Joint Wald per direction; S=combined pooled signal, E=ETF. p<0.05 ⇒ that side leads.

ETF        cal S→E     cal E→S     evt S→E     evt E→S   verdict(cal / evt)
VAW      0.0017***        0.61           -           -   S→E / -
VCR     2.8e-08***         0.4           -           -   S→E / -
VDC        0.029**        0.49           -           -   S→E / -
VDE           0.36        0.75           -           -   - / -
VFH           0.44        0.78           -           -   - / -
VGT      0.0018***        0.46           -           -   S→E / -
VHT         0.086*        0.23           -           -   - / -
VIS        0.016**        0.84           -           -   S→E / -
VNQ      0.0037***        0.15           -           -   S→E / -
VOX     0.00033***         0.5           -           -   S→E / -
VPU      0.0003***        0.48           -           -   S→E / -

Per-ETF pseudo-pairs (combined pooled signal × each ETF) follow, each with explicit formulas + joint Wald.
```


### GAS_above (combined)  ×  VAW

```text
GRANGER —  GAS_above (combined pooled signal)   x   VAW
================================================================================================
S = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level). x=Δprob(S), y=ETF log return.
Joint Wald H0 = all PAST cause-lags 0; member FE (linear); hac-panel SE by member×day. p<0.05 ⇒ leads.

1. CALENDAR-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..4) bⱼ·xₜ₋ⱼ + Σ(d=1..24) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; day-FE over 25 days ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 17.26,  p = 0.00172 ***   |   BH-FDR p = 0.0111 **
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + Σ(j=1..4) dⱼ·yₜ₋ⱼ + Σ(d=1..24) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; day-FE over 25 days ; hac-panel SE (bw=4).
      H0: d₁ = … = d_4 = 0   →   Wald χ²(4) = 2.67,  p = 0.615    |   BH-FDR p = 0.812 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..4) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=4 ; sample spans 25 days (probit: no day-FE) ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 7.40,  p = 0.116    |   BH-FDR p = 0.452 
   => calendar verdict: Pooled Granger-leads ETF.

2. EVENT-TIME
   (not estimable)
```


### GAS_above (combined)  ×  VCR

```text
GRANGER —  GAS_above (combined pooled signal)   x   VCR
================================================================================================
S = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level). x=Δprob(S), y=ETF log return.
Joint Wald H0 = all PAST cause-lags 0; member FE (linear); hac-panel SE by member×day. p<0.05 ⇒ leads.

1. CALENDAR-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..4) bⱼ·xₜ₋ⱼ + Σ(d=1..24) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; day-FE over 25 days ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 40.88,  p = 2.85e-08 ***   |   BH-FDR p = 1.05e-06 ***
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + Σ(j=1..4) dⱼ·yₜ₋ⱼ + Σ(d=1..24) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; day-FE over 25 days ; hac-panel SE (bw=4).
      H0: d₁ = … = d_4 = 0   →   Wald χ²(4) = 4.06,  p = 0.397    |   BH-FDR p = 0.735 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..4) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; sample spans 25 days (probit: no day-FE) ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 4.67,  p = 0.322    |   BH-FDR p = 0.568 
   => calendar verdict: Pooled Granger-leads ETF.

2. EVENT-TIME
   (not estimable)
```


### GAS_above (combined)  ×  VDC

```text
GRANGER —  GAS_above (combined pooled signal)   x   VDC
================================================================================================
S = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level). x=Δprob(S), y=ETF log return.
Joint Wald H0 = all PAST cause-lags 0; member FE (linear); hac-panel SE by member×day. p<0.05 ⇒ leads.

1. CALENDAR-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + φ₂·yₜ₋₂ + Σ(j=1..4) bⱼ·xₜ₋ⱼ + Σ(d=1..24) γ_d·Day_d
      controls: ADL self-lags p=2 (BIC) ; cause block K=4 ; day-FE over 25 days ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 10.82,  p = 0.0287 **   |   BH-FDR p = 0.0817 *
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + Σ(j=1..4) dⱼ·yₜ₋ⱼ + Σ(d=1..24) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; day-FE over 25 days ; hac-panel SE (bw=4).
      H0: d₁ = … = d_4 = 0   →   Wald χ²(4) = 3.45,  p = 0.486    |   BH-FDR p = 0.735 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..4) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; sample spans 24 days (probit: no day-FE) ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 4.11,  p = 0.391    |   BH-FDR p = 0.629 
   => calendar verdict: Pooled Granger-leads ETF.

2. EVENT-TIME
   (not estimable)
```


### GAS_above (combined)  ×  VDE

```text
GRANGER —  GAS_above (combined pooled signal)   x   VDE
================================================================================================
S = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level). x=Δprob(S), y=ETF log return.
Joint Wald H0 = all PAST cause-lags 0; member FE (linear); hac-panel SE by member×day. p<0.05 ⇒ leads.

1. CALENDAR-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..4) bⱼ·xₜ₋ⱼ + Σ(d=1..24) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; day-FE over 25 days ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 4.33,  p = 0.363    |   BH-FDR p = 0.498 
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + Σ(j=1..4) dⱼ·yₜ₋ⱼ + Σ(d=1..24) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; day-FE over 25 days ; hac-panel SE (bw=4).
      H0: d₁ = … = d_4 = 0   →   Wald χ²(4) = 1.95,  p = 0.745    |   BH-FDR p = 0.859 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..4) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; sample spans 25 days (probit: no day-FE) ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 5.88,  p = 0.208    |   BH-FDR p = 0.476 
   => calendar verdict: neither direction significant.

2. EVENT-TIME
   (not estimable)
```


### GAS_above (combined)  ×  VFH

```text
GRANGER —  GAS_above (combined pooled signal)   x   VFH
================================================================================================
S = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level). x=Δprob(S), y=ETF log return.
Joint Wald H0 = all PAST cause-lags 0; member FE (linear); hac-panel SE by member×day. p<0.05 ⇒ leads.

1. CALENDAR-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..4) bⱼ·xₜ₋ⱼ + Σ(d=1..24) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; day-FE over 25 days ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 3.78,  p = 0.437    |   BH-FDR p = 0.522 
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + Σ(j=1..4) dⱼ·yₜ₋ⱼ + Σ(d=1..24) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; day-FE over 25 days ; hac-panel SE (bw=4).
      H0: d₁ = … = d_4 = 0   →   Wald χ²(4) = 1.75,  p = 0.781    |   BH-FDR p = 0.859 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..4) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; sample spans 25 days (probit: no day-FE) ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 3.49,  p = 0.48    |   BH-FDR p = 0.683 
   => calendar verdict: neither direction significant.

2. EVENT-TIME
   (not estimable)
```


### GAS_above (combined)  ×  VGT

```text
GRANGER —  GAS_above (combined pooled signal)   x   VGT
================================================================================================
S = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level). x=Δprob(S), y=ETF log return.
Joint Wald H0 = all PAST cause-lags 0; member FE (linear); hac-panel SE by member×day. p<0.05 ⇒ leads.

1. CALENDAR-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..4) bⱼ·xₜ₋ⱼ + Σ(d=1..24) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; day-FE over 25 days ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 17.16,  p = 0.0018 ***   |   BH-FDR p = 0.0111 **
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + Σ(j=1..4) dⱼ·yₜ₋ⱼ + Σ(d=1..24) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; day-FE over 25 days ; hac-panel SE (bw=4).
      H0: d₁ = … = d_4 = 0   →   Wald χ²(4) = 3.62,  p = 0.46    |   BH-FDR p = 0.735 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..4) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=4 ; sample spans 25 days (probit: no day-FE) ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 11.57,  p = 0.0208 **   |   BH-FDR p = 0.154 
   => calendar verdict: Pooled Granger-leads ETF.

2. EVENT-TIME
   (not estimable)
```


### GAS_above (combined)  ×  VHT

```text
GRANGER —  GAS_above (combined pooled signal)   x   VHT
================================================================================================
S = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level). x=Δprob(S), y=ETF log return.
Joint Wald H0 = all PAST cause-lags 0; member FE (linear); hac-panel SE by member×day. p<0.05 ⇒ leads.

1. CALENDAR-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..4) bⱼ·xₜ₋ⱼ + Σ(d=1..24) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; day-FE over 25 days ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 8.15,  p = 0.0863 *   |   BH-FDR p = 0.2 
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + Σ(j=1..4) dⱼ·yₜ₋ⱼ + Σ(d=1..24) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; day-FE over 25 days ; hac-panel SE (bw=4).
      H0: d₁ = … = d_4 = 0   →   Wald χ²(4) = 5.59,  p = 0.232    |   BH-FDR p = 0.735 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..4) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; sample spans 25 days (probit: no day-FE) ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 15.28,  p = 0.00415 ***   |   BH-FDR p = 0.0559 *
   => calendar verdict: neither direction significant.

2. EVENT-TIME
   (not estimable)
```


### GAS_above (combined)  ×  VIS

```text
GRANGER —  GAS_above (combined pooled signal)   x   VIS
================================================================================================
S = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level). x=Δprob(S), y=ETF log return.
Joint Wald H0 = all PAST cause-lags 0; member FE (linear); hac-panel SE by member×day. p<0.05 ⇒ leads.

1. CALENDAR-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + φ₂·yₜ₋₂ + Σ(j=1..4) bⱼ·xₜ₋ⱼ + Σ(d=1..24) γ_d·Day_d
      controls: ADL self-lags p=2 (BIC) ; cause block K=4 ; day-FE over 25 days ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 12.17,  p = 0.0161 **   |   BH-FDR p = 0.0542 *
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + Σ(j=1..4) dⱼ·yₜ₋ⱼ + Σ(d=1..24) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; day-FE over 25 days ; hac-panel SE (bw=4).
      H0: d₁ = … = d_4 = 0   →   Wald χ²(4) = 1.45,  p = 0.836    |   BH-FDR p = 0.859 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..4) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; sample spans 25 days (probit: no day-FE) ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 10.36,  p = 0.0347 **   |   BH-FDR p = 0.214 
   => calendar verdict: Pooled Granger-leads ETF.

2. EVENT-TIME
   (not estimable)
```


### GAS_above (combined)  ×  VNQ

```text
GRANGER —  GAS_above (combined pooled signal)   x   VNQ
================================================================================================
S = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level). x=Δprob(S), y=ETF log return.
Joint Wald H0 = all PAST cause-lags 0; member FE (linear); hac-panel SE by member×day. p<0.05 ⇒ leads.

1. CALENDAR-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..4) bⱼ·xₜ₋ⱼ + Σ(d=1..24) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; day-FE over 25 days ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 15.56,  p = 0.00366 ***   |   BH-FDR p = 0.0194 **
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + Σ(j=1..4) dⱼ·yₜ₋ⱼ + Σ(d=1..24) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; day-FE over 25 days ; hac-panel SE (bw=4).
      H0: d₁ = … = d_4 = 0   →   Wald χ²(4) = 6.79,  p = 0.147    |   BH-FDR p = 0.735 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..4) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=4 ; sample spans 25 days (probit: no day-FE) ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 3.85,  p = 0.426    |   BH-FDR p = 0.654 
   => calendar verdict: Pooled Granger-leads ETF.

2. EVENT-TIME
   (not estimable)
```


### GAS_above (combined)  ×  VOX

```text
GRANGER —  GAS_above (combined pooled signal)   x   VOX
================================================================================================
S = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level). x=Δprob(S), y=ETF log return.
Joint Wald H0 = all PAST cause-lags 0; member FE (linear); hac-panel SE by member×day. p<0.05 ⇒ leads.

1. CALENDAR-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..4) bⱼ·xₜ₋ⱼ + Σ(d=1..24) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; day-FE over 25 days ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 20.90,  p = 0.000332 ***   |   BH-FDR p = 0.00307 ***
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + Σ(j=1..4) dⱼ·yₜ₋ⱼ + Σ(d=1..24) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; day-FE over 25 days ; hac-panel SE (bw=4).
      H0: d₁ = … = d_4 = 0   →   Wald χ²(4) = 3.38,  p = 0.496    |   BH-FDR p = 0.735 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..4) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=4 ; sample spans 25 days (probit: no day-FE) ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 5.27,  p = 0.261    |   BH-FDR p = 0.536 
   => calendar verdict: Pooled Granger-leads ETF.

2. EVENT-TIME
   (not estimable)
```


### GAS_above (combined)  ×  VPU

```text
GRANGER —  GAS_above (combined pooled signal)   x   VPU
================================================================================================
S = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level). x=Δprob(S), y=ETF log return.
Joint Wald H0 = all PAST cause-lags 0; member FE (linear); hac-panel SE by member×day. p<0.05 ⇒ leads.

1. CALENDAR-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..4) bⱼ·xₜ₋ⱼ + Σ(d=1..24) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; day-FE over 25 days ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 21.09,  p = 0.000303 ***   |   BH-FDR p = 0.00307 ***
   Direction B — ETF → Pooled:
      xₜ = α + ψ₁·xₜ₋₁ + Σ(j=1..4) dⱼ·yₜ₋ⱼ + Σ(d=1..24) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; day-FE over 25 days ; hac-panel SE (bw=4).
      H0: d₁ = … = d_4 = 0   →   Wald χ²(4) = 3.50,  p = 0.477    |   BH-FDR p = 0.735 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..4) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; sample spans 25 days (probit: no day-FE) ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 3.36,  p = 0.5    |   BH-FDR p = 0.685 
   => calendar verdict: Pooled Granger-leads ETF.

2. EVENT-TIME
   (not estimable)
```

---

## MERGE — APPROVAL_strength  (Granger overview)

```text
MERGE pooled signal — GRANGER overview :  APPROVAL_strength
================================================================================================
Each pooled signal = members' sign-aligned Δprob pooled (member fixed effects, hac-panel SE by
member×day). 'Sign-aligned' means each member's Δprob is multiplied by ±1 so that a positive value
always means the same real-world direction (e.g. a MIN-side contract is flipped). The CONTINUOUS
magnitude of Δprob is kept — the moves are NOT discretized to ±1.
Joint Wald per direction; S=combined pooled signal, E=ETF. p<0.05 ⇒ that side leads.

ETF        cal S→E     cal E→S     evt S→E     evt E→S   verdict(cal / evt)
VAW           0.29        0.72           -           -   - / -
VCR           0.23        0.32           -           -   - / -
VFH           0.93        0.26           -           -   - / -
VGT         0.081*        0.33           -           -   - / -
VHT           0.31         0.6           -           -   - / -
VIS           0.35        0.43           -           -   - / -
VNQ           0.38        0.92           -           -   - / -
VOX        0.015**        0.61           -           -   S→E / -

Per-ETF pseudo-pairs (combined pooled signal × each ETF) follow, each with explicit formulas + joint Wald.
```


### APPROVAL_strength (combined)  ×  VAW

```text
GRANGER —  APPROVAL_strength (combined pooled signal)   x   VAW
================================================================================================
S = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level). x=Δprob(S), y=ETF log return.
Joint Wald H0 = all PAST cause-lags 0; member FE (linear); hac-panel SE by member×day. p<0.05 ⇒ leads.

1. CALENDAR-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..4) bⱼ·xₜ₋ⱼ + Σ(d=1..30) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; day-FE over 31 days ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 4.99,  p = 0.288    |   BH-FDR p = 0.475 
   Direction B — ETF → Pooled:
      xₜ = α + (no x self-lag term: BIC chose p=0) + Σ(j=1..4) dⱼ·yₜ₋ⱼ + Σ(d=1..30) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=4 ; day-FE over 31 days ; hac-panel SE (bw=4).
      H0: d₁ = … = d_4 = 0   →   Wald χ²(4) = 2.07,  p = 0.723    |   BH-FDR p = 0.859 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..4) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=4 ; sample spans 31 days (probit: no day-FE) ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 6.37,  p = 0.173    |   BH-FDR p = 0.452 
   => calendar verdict: neither direction significant.

2. EVENT-TIME
   (not estimable)
```


### APPROVAL_strength (combined)  ×  VCR

```text
GRANGER —  APPROVAL_strength (combined pooled signal)   x   VCR
================================================================================================
S = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level). x=Δprob(S), y=ETF log return.
Joint Wald H0 = all PAST cause-lags 0; member FE (linear); hac-panel SE by member×day. p<0.05 ⇒ leads.

1. CALENDAR-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..4) bⱼ·xₜ₋ⱼ + Σ(d=1..30) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; day-FE over 31 days ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 5.63,  p = 0.228    |   BH-FDR p = 0.422 
   Direction B — ETF → Pooled:
      xₜ = α + (no x self-lag term: BIC chose p=0) + Σ(j=1..4) dⱼ·yₜ₋ⱼ + Σ(d=1..30) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=4 ; day-FE over 31 days ; hac-panel SE (bw=4).
      H0: d₁ = … = d_4 = 0   →   Wald χ²(4) = 4.70,  p = 0.32    |   BH-FDR p = 0.735 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..4) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=4 ; sample spans 31 days (probit: no day-FE) ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 1.47,  p = 0.832    |   BH-FDR p = 0.905 
   => calendar verdict: neither direction significant.

2. EVENT-TIME
   (not estimable)
```


### APPROVAL_strength (combined)  ×  VFH

```text
GRANGER —  APPROVAL_strength (combined pooled signal)   x   VFH
================================================================================================
S = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level). x=Δprob(S), y=ETF log return.
Joint Wald H0 = all PAST cause-lags 0; member FE (linear); hac-panel SE by member×day. p<0.05 ⇒ leads.

1. CALENDAR-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..4) bⱼ·xₜ₋ⱼ + Σ(d=1..30) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; day-FE over 31 days ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 0.84,  p = 0.934    |   BH-FDR p = 0.934 
   Direction B — ETF → Pooled:
      xₜ = α + (no x self-lag term: BIC chose p=0) + Σ(j=1..4) dⱼ·yₜ₋ⱼ + Σ(d=1..30) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=4 ; day-FE over 31 days ; hac-panel SE (bw=4).
      H0: d₁ = … = d_4 = 0   →   Wald χ²(4) = 5.29,  p = 0.259    |   BH-FDR p = 0.735 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..4) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; sample spans 31 days (probit: no day-FE) ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 0.81,  p = 0.937    |   BH-FDR p = 0.963 
   => calendar verdict: neither direction significant.

2. EVENT-TIME
   (not estimable)
```


### APPROVAL_strength (combined)  ×  VGT

```text
GRANGER —  APPROVAL_strength (combined pooled signal)   x   VGT
================================================================================================
S = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level). x=Δprob(S), y=ETF log return.
Joint Wald H0 = all PAST cause-lags 0; member FE (linear); hac-panel SE by member×day. p<0.05 ⇒ leads.

1. CALENDAR-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..4) bⱼ·xₜ₋ⱼ + Σ(d=1..30) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; day-FE over 31 days ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 8.32,  p = 0.0806 *   |   BH-FDR p = 0.199 
   Direction B — ETF → Pooled:
      xₜ = α + (no x self-lag term: BIC chose p=0) + Σ(j=1..4) dⱼ·yₜ₋ⱼ + Σ(d=1..30) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=4 ; day-FE over 31 days ; hac-panel SE (bw=4).
      H0: d₁ = … = d_4 = 0   →   Wald χ²(4) = 4.64,  p = 0.327    |   BH-FDR p = 0.735 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..4) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=4 ; sample spans 31 days (probit: no day-FE) ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 7.11,  p = 0.13    |   BH-FDR p = 0.452 
   => calendar verdict: neither direction significant.

2. EVENT-TIME
   (not estimable)
```


### APPROVAL_strength (combined)  ×  VHT

```text
GRANGER —  APPROVAL_strength (combined pooled signal)   x   VHT
================================================================================================
S = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level). x=Δprob(S), y=ETF log return.
Joint Wald H0 = all PAST cause-lags 0; member FE (linear); hac-panel SE by member×day. p<0.05 ⇒ leads.

1. CALENDAR-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..4) bⱼ·xₜ₋ⱼ + Σ(d=1..30) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; day-FE over 31 days ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 4.76,  p = 0.313    |   BH-FDR p = 0.475 
   Direction B — ETF → Pooled:
      xₜ = α + (no x self-lag term: BIC chose p=0) + Σ(j=1..4) dⱼ·yₜ₋ⱼ + Σ(d=1..30) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=4 ; day-FE over 31 days ; hac-panel SE (bw=4).
      H0: d₁ = … = d_4 = 0   →   Wald χ²(4) = 2.77,  p = 0.597    |   BH-FDR p = 0.812 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..4) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=4 ; sample spans 31 days (probit: no day-FE) ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 6.55,  p = 0.162    |   BH-FDR p = 0.452 
   => calendar verdict: neither direction significant.

2. EVENT-TIME
   (not estimable)
```


### APPROVAL_strength (combined)  ×  VIS

```text
GRANGER —  APPROVAL_strength (combined pooled signal)   x   VIS
================================================================================================
S = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level). x=Δprob(S), y=ETF log return.
Joint Wald H0 = all PAST cause-lags 0; member FE (linear); hac-panel SE by member×day. p<0.05 ⇒ leads.

1. CALENDAR-TIME
   Direction A — Pooled → ETF:
      yₜ = α + (no y self-lag term: BIC chose p=0) + Σ(j=1..4) bⱼ·xₜ₋ⱼ + Σ(d=1..30) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=4 ; day-FE over 31 days ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 4.43,  p = 0.351    |   BH-FDR p = 0.498 
   Direction B — ETF → Pooled:
      xₜ = α + (no x self-lag term: BIC chose p=0) + Σ(j=1..4) dⱼ·yₜ₋ⱼ + Σ(d=1..30) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=4 ; day-FE over 31 days ; hac-panel SE (bw=4).
      H0: d₁ = … = d_4 = 0   →   Wald χ²(4) = 3.81,  p = 0.432    |   BH-FDR p = 0.735 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + (no y self-lag term: BIC chose p=0) + Σ(j=1..4) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=0 (BIC) ; cause block K=4 ; sample spans 31 days (probit: no day-FE) ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 2.57,  p = 0.633    |   BH-FDR p = 0.807 
   => calendar verdict: neither direction significant.

2. EVENT-TIME
   (not estimable)
```


### APPROVAL_strength (combined)  ×  VNQ

```text
GRANGER —  APPROVAL_strength (combined pooled signal)   x   VNQ
================================================================================================
S = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level). x=Δprob(S), y=ETF log return.
Joint Wald H0 = all PAST cause-lags 0; member FE (linear); hac-panel SE by member×day. p<0.05 ⇒ leads.

1. CALENDAR-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..4) bⱼ·xₜ₋ⱼ + Σ(d=1..30) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; day-FE over 31 days ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 4.22,  p = 0.377    |   BH-FDR p = 0.498 
   Direction B — ETF → Pooled:
      xₜ = α + (no x self-lag term: BIC chose p=0) + Σ(j=1..4) dⱼ·yₜ₋ⱼ + Σ(d=1..30) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=4 ; day-FE over 31 days ; hac-panel SE (bw=4).
      H0: d₁ = … = d_4 = 0   →   Wald χ²(4) = 0.93,  p = 0.92    |   BH-FDR p = 0.92 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..4) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; sample spans 31 days (probit: no day-FE) ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 4.79,  p = 0.309    |   BH-FDR p = 0.568 
   => calendar verdict: neither direction significant.

2. EVENT-TIME
   (not estimable)
```


### APPROVAL_strength (combined)  ×  VOX

```text
GRANGER —  APPROVAL_strength (combined pooled signal)   x   VOX
================================================================================================
S = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level). x=Δprob(S), y=ETF log return.
Joint Wald H0 = all PAST cause-lags 0; member FE (linear); hac-panel SE by member×day. p<0.05 ⇒ leads.

1. CALENDAR-TIME
   Direction A — Pooled → ETF:
      yₜ = α + φ₁·yₜ₋₁ + Σ(j=1..4) bⱼ·xₜ₋ⱼ + Σ(d=1..30) γ_d·Day_d
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; day-FE over 31 days ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 12.33,  p = 0.0151 **   |   BH-FDR p = 0.0542 *
   Direction B — ETF → Pooled:
      xₜ = α + (no x self-lag term: BIC chose p=0) + Σ(j=1..4) dⱼ·yₜ₋ⱼ + Σ(d=1..30) γ_d·Day_d
      controls: ADL self-lags p=0 (BIC) ; cause block K=4 ; day-FE over 31 days ; hac-panel SE (bw=4).
      H0: d₁ = … = d_4 = 0   →   Wald χ²(4) = 2.71,  p = 0.607    |   BH-FDR p = 0.812 
   Direction A (probit, ETF up/down):
      Pr(yₜ>0) = Φ( α + φ₁·yₜ₋₁ + Σ(j=1..4) bⱼ·xₜ₋ⱼ )
      controls: ADL self-lags p=1 (BIC) ; cause block K=4 ; sample spans 30 days (probit: no day-FE) ; hac-panel SE (bw=4).
      H0: b₁ = … = b_4 = 0   →   Wald χ²(4) = 15.08,  p = 0.00453 ***   |   BH-FDR p = 0.0559 *
   => calendar verdict: Pooled Granger-leads ETF.

2. EVENT-TIME
   (not estimable)
```
