PAIR ANALYSIS    —    Rank 18 / 48
================================================================================================
AAAGASM-24OCT31-US-3.15   x   VPU
Contract : "Will average **gas prices** be above $3.15?"
Sector relevance : VDE (Energy)
Window : 2024-10-02 to 2024-10-31     Kalshi trades : 58     primary bar : 10min     daily-screen R^2 : 0.20

>>> RELIABILITY:  Very-low-info   <<<   (see section 5; unreliable pairs still get figures, but read their problems in section 8)

DEFINITIONS
   xₜ₋ₖ = Kalshi yes-probability change, k bars before t   (1 bar = 10min)
   yₜ   = ETF log return over bar t
   calendar = full market-hours grid: x=0 in bars with no Kalshi trade (not dropped).
   k>0 => Kalshi leads ETF ;  k<0 => ETF leads Kalshi ;  k=0 => contemporaneous

1. CALENDAR-TIME REGRESSION (clock-time lags, full RTH grid)
   Full model:  yₜ = α + Σ(k=-3..3) βₖ·xₜ₋ₖ + φ₁·yₜ₋₁ + Σ(d=1..11) γ_d·Day_d
      where  ADL ETF self-lags p=1 (BIC-chosen): φ₁·yₜ₋₁;  day-FE: 11 day dummies over 12 trading days (first day = baseline).
      controls counted (so you can see the total at a glance):  7 lead/lag x-terms + 1 ETF self-lag(s) + 11 day-FE dummies + 1 intercept = 20 RHS regressors  (model n_params=20).
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₋₃·xₜ₊₃ + β₋₁·xₜ₊₁ + β₊₀·xₜ + β₊₁·xₜ₋₁
   where:
      β₋₃ = +2.240e-05   (t/z=+1.50, p=1.3e-01, p_fdr=2.3e-01)    [ETF leads]
      β₋₁ = -1.077e-04   (t/z=-4.15, p=3.4e-05, p_fdr=1.2e-04) ***   [ETF leads]
      β₊₀ = -1.557e-04   (t/z=-8.66, p=4.8e-18, p_fdr=3.4e-17) ***   [contemporaneous]
      β₊₁ = -8.570e-05   (t/z=-2.21, p=2.7e-02, p_fdr=6.3e-02) *   [Kalshi leads]
   Lean by count of significant lags: ETF-leads  (k>0:1, k<0:2).

2. EVENT-TIME REGRESSION (event-count lags)
   Full model:  yₜ = α + Σ(k) βₖ·xₜ₋ₖ + (ADL self-lags) + (day fixed effects)
   -> no regression result (insufficient data).

3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)
      k |       calendar b (FDR) |          event b (FDR)
   ------------------------------------------------------
     -3 |          +2.24e-05     |                     --
     -2 |          -1.53e-05     |                     --
     -1 |          -1.08e-04 *** |                     --
     +0 |          -1.56e-04 *** |                     --
     +1 |          -8.57e-05 *   |                     --
     +2 |          -5.85e-05     |                     --
     +3 |          -5.57e-06     |                     --
   (stars = BH-FDR corrected:  *** p_fdr<.01  ** <.05  * <.10)

4. DIRECTIONAL TEST (probit, ETF up/down)
   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k
   calendar: n/a
   event: n/a
   -> no significant directional predictability either mode (raw p<0.15).

5. DATA RELIABILITY (statistical, not a trade-count cutoff)
   Tier: Very-low-info
   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)
   calendar(full RTH grid): n_active=10  n_obs=271  n_days=12  K=3  params=20  df=251  median_SE=2.60e-05  sig(FDR)=2
   event: not estimable (insufficient data)
   => Very low info: even 'significant' coefficients are untrustworthy (huge SE, possibly spurious significance).

6. COARSE-FREQUENCY ROBUSTNESS (re-run calendar at 30min / 60min)
    30min: not estimable (n_obs=14 < minimum) -- coarser bars have even fewer observations
    60min: not estimable (n_obs=13 < minimum) -- coarser bars have even fewer observations

7. VERDICT
   Only one time-axis significant (ETF-leads) -- weak / single-mode evidence.
   (Note: this pair lacks the data to support reliable inference; the verdict above is descriptive only -- do not put it in the conclusions.)

8. FIGURE CAVEATS — figures are still drawn, but know their problems
   - Very low info (only 10 bars with an actual Kalshi move, < 15): even 'significant' coefficients are untrustworthy (huge SE, possibly spurious significance).
   - Most of the chart is flat no-trade lines; only a handful of bars carry real variation, so the lead calls in leadglance/segments are not robust.
   - Mixed coefficient signs across lags -- relationship not monotone.
   - Kalshi updates only on trades (flat line = no trade, NOT 'no change'); ETF mid refreshes continuously.

------------------------------------------------------------------------------------------------
Conventions: ET | 09:30-16:00 (forward windows capped to 16:00) | ETF in log return | median causal bars | full RTH grid | day-grouped lags (no overnight) | ADL self-control | significance = BH-FDR corrected.
Figures for this pair follow on the next page.