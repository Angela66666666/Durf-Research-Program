PAIR ANALYSIS    —    Rank 18 / 48
================================================================================================
KXECKH276   x   VOX
Contract : "Will Harris win 276-262 - PA, NV, MI, WI?"
Sector relevance : Election outcome (all sectors)
Window : 2024-11-04 to 2024-11-26     Kalshi trades : 37     primary bar : 10min     daily-screen R^2 : 0.59

>>> RELIABILITY:  Very-low-info   <<<   (see section 5; unreliable pairs still get figures, but read their problems in section 8)

DEFINITIONS
   xₜ₋ₖ = Kalshi yes-probability change, k bars before t   (1 bar = 10min)
   yₜ   = ETF log return over bar t
   calendar = full market-hours grid: x=0 in bars with no Kalshi trade (not dropped).
   k>0 => Kalshi leads ETF ;  k<0 => ETF leads Kalshi ;  k=0 => contemporaneous

1. CALENDAR-TIME REGRESSION (clock-time lags, full RTH grid)
   Full model:  yₜ = α + Σ(k=-3..3) βₖ·xₜ₋ₖ + φ₁·yₜ₋₁ + Σ(d=1..2) γ_d·Day_d
      where  ADL ETF self-lags p=1 (BIC-chosen): φ₁·yₜ₋₁;  day-FE: 2 day dummies over 3 trading days (first day = baseline).
      controls counted (so you can see the total at a glance):  7 lead/lag x-terms + 1 ETF self-lag(s) + 2 day-FE dummies + 1 intercept = 11 RHS regressors  (model n_params=11).
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₋₃·xₜ₊₃ + β₋₂·xₜ₊₂ + β₋₁·xₜ₊₁ + β₊₂·xₜ₋₂ + β₊₃·xₜ₋₃
   where:
      β₋₃ = +1.134e-04   (t/z=+7.06, p=1.7e-12, p_fdr=1.2e-11) ***   [ETF leads]
      β₋₂ = -6.332e-05   (t/z=-4.37, p=1.2e-05, p_fdr=4.3e-05) ***   [ETF leads]
      β₋₁ = +5.085e-05   (t/z=+2.44, p=1.5e-02, p_fdr=2.6e-02) **   [ETF leads]
      β₊₂ = -6.967e-05   (t/z=-2.12, p=3.4e-02, p_fdr=4.8e-02) **   [Kalshi leads]
      β₊₃ = +1.643e-04   (t/z=+3.38, p=7.3e-04, p_fdr=1.7e-03) ***   [Kalshi leads]
   Lean by count of significant lags: ETF-leads  (k>0:2, k<0:3).

2. EVENT-TIME REGRESSION (event-count lags)
   Full model:  yₜ = α + Σ(k=-3..3) βₖ·xₜ₋ₖ + φ₁·yₜ₋₁ + φ₂·yₜ₋₂ + φ₃·yₜ₋₃
      where  ADL ETF self-lags p=3 (BIC-chosen): φ₁·yₜ₋₁ + φ₂·yₜ₋₂ + φ₃·yₜ₋₃;  day-FE: none (single trading day -> clustered SE degrades to HC3).
      controls counted (so you can see the total at a glance):  7 lead/lag x-terms + 3 ETF self-lag(s) + 0 day-FE dummies + 1 intercept = 11 RHS regressors  (model n_params=11).
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₋₃·xₜ₊₃ + β₋₂·xₜ₊₂ + β₋₁·xₜ₊₁ + β₊₀·xₜ + β₊₁·xₜ₋₁ + β₊₂·xₜ₋₂
   where:
      β₋₃ = -5.791e-03   (t/z=-2.36, p=1.8e-02, p_fdr=7.7e-02) *   [ETF leads]
      β₋₂ = -7.145e-03   (t/z=-2.28, p=2.3e-02, p_fdr=7.7e-02) *   [ETF leads]
      β₋₁ = -6.871e-03   (t/z=-2.02, p=4.4e-02, p_fdr=7.7e-02) *   [ETF leads]
      β₊₀ = -7.890e-03   (t/z=-2.07, p=3.9e-02, p_fdr=7.7e-02) *   [contemporaneous]
      β₊₁ = -5.256e-03   (t/z=-1.82, p=6.9e-02, p_fdr=9.7e-02) *   [Kalshi leads]
      β₊₂ = -2.614e-03   (t/z=-1.51, p=1.3e-01, p_fdr=1.5e-01)    [Kalshi leads]
   Lean by count of significant lags: ETF-leads  (k>0:2, k<0:3).

3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)
      k |       calendar b (FDR) |          event b (FDR)
   ------------------------------------------------------
     -3 |          +1.13e-04 *** |          -5.79e-03 *  
     -2 |          -6.33e-05 *** |          -7.14e-03 *  
     -1 |          +5.08e-05 **  |          -6.87e-03 *  
     +0 |          -5.39e-05     |          -7.89e-03 *  
     +1 |          +4.98e-05     |          -5.26e-03 *  
     +2 |          -6.97e-05 **  |          -2.61e-03    
     +3 |          +1.64e-04 *** |          -2.21e-04    
   (stars = BH-FDR corrected:  *** p_fdr<.01  ** <.05  * <.10)

4. DIRECTIONAL TEST (probit, ETF up/down)
   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k
   calendar: n/a
   event: n/a
   -> no significant directional predictability either mode (raw p<0.15).

5. DATA RELIABILITY (statistical, not a trade-count cutoff)
   Tier: Very-low-info
   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)
   calendar(full RTH grid): n_active=8  n_obs=59  n_days=3  K=3  params=11  df=48  median_SE=3.29e-05  sig(FDR)=5
   event: n_active=7  n_obs=12  n_days=1  K=3  params=11  df=1  median_SE=2.89e-03  sig(FDR)=0
   => Very low info: even 'significant' coefficients are untrustworthy (huge SE, possibly spurious significance).

6. COARSE-FREQUENCY ROBUSTNESS (re-run calendar at 30min / 60min)
    30min: not estimable (n_obs=11 < minimum) -- coarser bars have even fewer observations
    60min: not estimable (n_obs=6 < minimum) -- coarser bars have even fewer observations

7. VERDICT
   Both time-axes lean ETF-leads (relatively robust; see strongest single term).
   (Note: this pair lacks the data to support reliable inference; the verdict above is descriptive only -- do not put it in the conclusions.)

8. FIGURE CAVEATS — figures are still drawn, but know their problems
   - Very low info (only 8 bars with an actual Kalshi move, < 15): even 'significant' coefficients are untrustworthy (huge SE, possibly spurious significance).
   - Most of the chart is flat no-trade lines; only a handful of bars carry real variation, so the lead calls in leadglance/segments are not robust.
   - Mixed coefficient signs across lags -- relationship not monotone.
   - Kalshi updates only on trades (flat line = no trade, NOT 'no change'); ETF mid refreshes continuously.

9. REAL-WORLD CONTEXT (WebSearch-verified; see URLs)
   - 2024 US presidential election held Tue Nov 5, 2024; ballots counted overnight Nov 5-6.
   - AP called the race for Trump ~5:34-5:37 AM ET on Wed Nov 6, 2024 (Wisconsin pushed him past 270) -- this is PRE-MARKET, so the regular-hours equity reaction shows up at the Nov 6 open.
   - Final electoral result: Trump 312, Harris 226.
   - Sources: en.wikipedia.org/wiki/2024_United_States_presidential_election ; spectrumlocalnews.com/us/snplus/news/2024/11/06/trump-wins-ap-projection-2024-election

------------------------------------------------------------------------------------------------
Conventions: ET | 09:30-16:00 (forward windows capped to 16:00) | ETF in log return | median causal bars | full RTH grid | day-grouped lags (no overnight) | ADL self-control | significance = BH-FDR corrected.
Figures for this pair follow on the next page.