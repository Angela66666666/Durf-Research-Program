PAIR ANALYSIS    —    Rank 8 / 48
================================================================================================
KXECKH276   x   VGT
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
   Full model: yₜ = α + Σₖ βₖ·xₜ₋ₖ + Σᵢ φᵢ·yₜ₋ᵢ (ADL self-control) + day-FE
   Significant terms (BH-FDR) expanded:  yₜ = α + β₋₂·xₜ₊₂ + β₋₁·xₜ₊₁ + β₊₂·xₜ₋₂
   where:
      β₋₂ = -1.618e-04   (t/z=-5.23, p=1.7e-07, p_fdr=3.9e-07) ***   [ETF leads]
      β₋₁ = -7.145e-05   (t/z=-5.75, p=9.2e-09, p_fdr=3.2e-08) ***   [ETF leads]
      β₊₂ = -2.388e-04   (t/z=-10.16, p=3.0e-24, p_fdr=2.1e-23) ***   [Kalshi leads]
   Lean by count of significant lags: ETF-leads  (k>0:1, k<0:2).

2. EVENT-TIME REGRESSION (event-count lags)
   Full model: yₜ = α + Σₖ βₖ·xₜ₋ₖ + Σᵢ φᵢ·yₜ₋ᵢ (ADL self-control) + day-FE
   -> 9 coefficients tested, NONE significant after BH-FDR (p_fdr<0.05).

3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)
      k |       calendar b (FDR) |          event b (FDR)
   ------------------------------------------------------
     -4 |                     -- |          -2.65e-04    
     -3 |          +4.30e-05     |          -2.02e-04    
     -2 |          -1.62e-04 *** |          -5.71e-05    
     -1 |          -7.14e-05 *** |          -2.58e-05    
     +0 |          -1.24e-04     |          +2.09e-04    
     +1 |          -1.40e-04 *   |          +5.79e-04    
     +2 |          -2.39e-04 *** |          +4.56e-04    
     +3 |          +2.97e-05     |          +8.09e-04    
     +4 |                     -- |          +6.80e-04    
   (stars = BH-FDR corrected:  *** p_fdr<.01  ** <.05  * <.10)

4. DIRECTIONAL TEST (probit, ETF up/down)
   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k
   calendar: n/a
   event: n/a
   -> no significant directional predictability either mode (BH-FDR).

5. DATA RELIABILITY (statistical, not a trade-count cutoff)
   Tier: Very-low-info
   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)
   calendar(full RTH grid): n_active=7  n_obs=53  n_days=3  K=3  params=15  df=38  median_SE=3.09e-05  sig(FDR)=3
   event: n_active=7  n_obs=17  n_days=1  K=4  params=15  df=2  median_SE=1.07e-03  sig(FDR)=0
   => Very low info: even 'significant' coefficients are untrustworthy (huge SE, possibly spurious significance).

6. COARSE-FREQUENCY ROBUSTNESS (re-run calendar at 30min / 60min)
    30min: not estimable (n_obs=11 < minimum) -- coarser bars have even fewer observations
    60min: not estimable (n_obs=6 < minimum) -- coarser bars have even fewer observations

7. VERDICT
   Only one time-axis significant (ETF-leads) -- weak / single-mode evidence.
   (Note: this pair lacks the data to support reliable inference; the verdict above is descriptive only -- do not put it in the conclusions.)

8. FIGURE CAVEATS — figures are still drawn, but know their problems
   - Very low info (only 7 bars with an actual Kalshi move, < 15): even 'significant' coefficients are untrustworthy (huge SE, possibly spurious significance).
   - Most of the chart is flat no-trade lines; only a handful of bars carry real variation, so the lead calls in leadglance/segments are not robust.
   - Kalshi updates only on trades (flat line = no trade, NOT 'no change'); ETF mid refreshes continuously.

9. REAL-WORLD CONTEXT (WebSearch-verified; see URLs)
   - 2024 US presidential election held Tue Nov 5, 2024; ballots counted overnight Nov 5-6.
   - AP called the race for Trump ~5:34-5:37 AM ET on Wed Nov 6, 2024 (Wisconsin pushed him past 270) -- this is PRE-MARKET, so the regular-hours equity reaction shows up at the Nov 6 open.
   - Final electoral result: Trump 312, Harris 226.
   - Sources: en.wikipedia.org/wiki/2024_United_States_presidential_election ; spectrumlocalnews.com/us/snplus/news/2024/11/06/trump-wins-ap-projection-2024-election

------------------------------------------------------------------------------------------------
Conventions: ET | 09:30-16:00 (forward windows capped to 16:00) | ETF in log return | median causal bars | full RTH grid | day-grouped lags (no overnight) | ADL self-control | significance = BH-FDR corrected.
Figures for this pair follow on the next page.