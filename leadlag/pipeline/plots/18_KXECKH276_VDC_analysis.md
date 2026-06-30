PAIR ANALYSIS    —    Rank 21 / 48
================================================================================================
KXECKH276   x   VDC
Contract : "Will Harris win 276-262 - PA, NV, MI, WI?"
Sector relevance : Election outcome (all sectors)
Window : 2024-11-04 to 2024-11-26     Kalshi trades : 37     primary bar : 10min     daily-screen R^2 : 0.53

>>> RELIABILITY:  Very-low-info   <<<   (see section 5; unreliable pairs still get figures, but read their problems in section 8)

DEFINITIONS
   xₜ₋ₖ = Kalshi yes-probability change, k bars before t   (1 bar = 10min)
   yₜ   = ETF log return over bar t
   calendar = full market-hours grid: x=0 in bars with no Kalshi trade (not dropped).
   k>0 => Kalshi leads ETF ;  k<0 => ETF leads Kalshi ;  k=0 => contemporaneous

1. CALENDAR-TIME REGRESSION (clock-time lags, full RTH grid)
   Full model:  yₜ = α + Σ(k=-3..3) βₖ·xₜ₋ₖ + Σ(d=1..2) γ_d·Day_d
      where  ADL ETF self-lags p=0 (BIC chose none -> no ETF self-lag term);  day-FE: 2 day dummies over 3 trading days (first day = baseline).
      controls counted (so you can see the total at a glance):  7 lead/lag x-terms + 0 ETF self-lag(s) + 2 day-FE dummies + 1 intercept = 10 RHS regressors  (model n_params=10).
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₋₃·xₜ₊₃ + β₋₂·xₜ₊₂ + β₋₁·xₜ₊₁ + β₊₀·xₜ + β₊₁·xₜ₋₁ + β₊₂·xₜ₋₂ + β₊₃·xₜ₋₃
   where:
      β₋₃ = -2.984e-05   (t/z=-4.12, p=3.8e-05, p_fdr=4.4e-05) ***   [ETF leads]
      β₋₂ = -6.707e-05   (t/z=-2.68, p=7.3e-03, p_fdr=7.3e-03) ***   [ETF leads]
      β₋₁ = -1.092e-04   (t/z=-10.24, p=1.3e-24, p_fdr=2.3e-24) ***   [ETF leads]
      β₊₀ = -1.199e-04   (t/z=-4.67, p=3.0e-06, p_fdr=4.3e-06) ***   [contemporaneous]
      β₊₁ = -1.178e-04   (t/z=-11.37, p=6.0e-30, p_fdr=1.4e-29) ***   [Kalshi leads]
      β₊₂ = -6.792e-05   (t/z=-21.59, p=2.1e-103, p_fdr=7.4e-103) ***   [Kalshi leads]
      β₊₃ = +7.161e-05   (t/z=+89.03, p=0.0e+00, p_fdr=0.0e+00) ***   [Kalshi leads]
   Lean by count of significant lags: balanced/no clear side  (k>0:3, k<0:3).

2. EVENT-TIME REGRESSION (event-count lags)
   Full model:  yₜ = α + Σ(k=-3..3) βₖ·xₜ₋ₖ + φ₁·yₜ₋₁ + φ₂·yₜ₋₂ + φ₃·yₜ₋₃
      where  ADL ETF self-lags p=3 (BIC-chosen): φ₁·yₜ₋₁ + φ₂·yₜ₋₂ + φ₃·yₜ₋₃;  day-FE: none (single trading day -> clustered SE degrades to HC3).
      controls counted (so you can see the total at a glance):  7 lead/lag x-terms + 3 ETF self-lag(s) + 0 day-FE dummies + 1 intercept = 11 RHS regressors  (model n_params=11).
   -> 7 coefficients tested, NONE significant at raw p<0.15.

3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)
      k |       calendar b (FDR) |          event b (FDR)
   ------------------------------------------------------
     -3 |          -2.98e-05 *** |          +4.03e-04    
     -2 |          -6.71e-05 *** |          +9.02e-04    
     -1 |          -1.09e-04 *** |          +1.23e-03    
     +0 |          -1.20e-04 *** |          +8.58e-04    
     +1 |          -1.18e-04 *** |          +1.07e-03    
     +2 |          -6.79e-05 *** |          +5.34e-04    
     +3 |          +7.16e-05 *** |          -2.61e-04    
   (stars = BH-FDR corrected:  *** p_fdr<.01  ** <.05  * <.10)

4. DIRECTIONAL TEST (probit, ETF up/down)
   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k
   calendar: n/a
   event: n/a
   -> no significant directional predictability either mode (raw p<0.15).

5. DATA RELIABILITY (statistical, not a trade-count cutoff)
   Tier: Very-low-info
   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)
   calendar(full RTH grid): n_active=8  n_obs=59  n_days=3  K=3  params=10  df=49  median_SE=1.04e-05  sig(FDR)=7
   event: n_active=7  n_obs=12  n_days=1  K=3  params=11  df=1  median_SE=7.35e-03  sig(FDR)=0
   => Very low info: even 'significant' coefficients are untrustworthy (huge SE, possibly spurious significance).

6. COARSE-FREQUENCY ROBUSTNESS (re-run calendar at 30min / 60min)
    30min: not estimable (n_obs=11 < minimum) -- coarser bars have even fewer observations
    60min: not estimable (n_obs=6 < minimum) -- coarser bars have even fewer observations

7. VERDICT
   Only one time-axis significant (balanced) -- weak / single-mode evidence.
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