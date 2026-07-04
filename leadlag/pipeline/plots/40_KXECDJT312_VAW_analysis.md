PAIR ANALYSIS    —    Rank 13 / 48
================================================================================================
KXECDJT312   x   VAW
Contract : "Will Trump win 312-226 - swing state sweep?"
Sector relevance : Election outcome (all sectors)
Window : 2024-11-04 to 2024-12-12     Kalshi trades : 232     primary bar : 10min     daily-screen R^2 : 0.31

>>> RELIABILITY:  Adequate   <<<   (see section 5; unreliable pairs still get figures, but read their problems in section 8)

DEFINITIONS
   xₜ₋ₖ = Kalshi yes-probability change, k bars before t   (1 bar = 10min)
   yₜ   = ETF log return over bar t
   calendar = full market-hours grid: x=0 in bars with no Kalshi trade (not dropped).
   k>0 => Kalshi leads ETF ;  k<0 => ETF leads Kalshi ;  k=0 => contemporaneous

1. CALENDAR-TIME REGRESSION (clock-time lags, full RTH grid)
   Full model:  yₜ = α + Σ(k=-5..5) βₖ·xₜ₋ₖ + φ₁·yₜ₋₁ + Σ(d=1..16) γ_d·Day_d
      where  ADL ETF self-lags p=1 (BIC-chosen): φ₁·yₜ₋₁;  day-FE: 16 day dummies over 17 trading days (first day = baseline).
      controls counted (so you can see the total at a glance):  11 lead/lag x-terms + 1 ETF self-lag(s) + 16 day-FE dummies + 1 intercept = 29 RHS regressors  (model n_params=29).
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₋₅·xₜ₊₅ + β₋₄·xₜ₊₄ + β₋₂·xₜ₊₂ + β₋₁·xₜ₊₁ + β₊₅·xₜ₋₅
   where:
      β₋₅ = +7.038e-05   (t/z=+3.30, p=9.8e-04, p_fdr=7.6e-03) ***   [ETF leads]
      β₋₄ = +6.325e-05   (t/z=+3.20, p=1.4e-03, p_fdr=7.6e-03) ***   [ETF leads]
      β₋₂ = -5.317e-05   (t/z=-2.48, p=1.3e-02, p_fdr=4.8e-02) **   [ETF leads]
      β₋₁ = +1.731e-05   (t/z=+1.56, p=1.2e-01, p_fdr=3.3e-01)    [ETF leads]
      β₊₅ = -5.190e-05   (t/z=-1.45, p=1.5e-01, p_fdr=3.3e-01)    [Kalshi leads]
   Lean by count of significant lags: ETF-leads  (k>0:1, k<0:4).

2. EVENT-TIME REGRESSION (event-count lags)
   Full model:  yₜ = α + Σ(k=-5..5) βₖ·xₜ₋ₖ + Σ(d=1..3) γ_d·Day_d
      where  ADL ETF self-lags p=0 (BIC chose none -> no ETF self-lag term);  day-FE: 3 day dummies over 4 trading days (first day = baseline).
      controls counted (so you can see the total at a glance):  11 lead/lag x-terms + 0 ETF self-lag(s) + 3 day-FE dummies + 1 intercept = 15 RHS regressors  (model n_params=15).
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₊₁·xₜ₋₁ + β₊₄·xₜ₋₄
   where:
      β₊₁ = -1.337e-03   (t/z=-1.48, p=1.4e-01, p_fdr=5.2e-01)    [Kalshi leads]
      β₊₄ = -1.916e-03   (t/z=-2.17, p=3.0e-02, p_fdr=3.3e-01)    [Kalshi leads]
   Lean by count of significant lags: Kalshi-leads  (k>0:2, k<0:0).

3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)
      k |       calendar b (FDR) |          event b (FDR)
   ------------------------------------------------------
     -5 |          +7.04e-05 *** |          +2.04e-05    
     -4 |          +6.33e-05 *** |          -1.17e-04    
     -3 |          -3.44e-05     |          -1.16e-04    
     -2 |          -5.32e-05 **  |          -8.20e-04    
     -1 |          +1.73e-05     |          -8.72e-04    
     +0 |          +8.22e-06     |          -9.70e-04    
     +1 |          -2.25e-05     |          -1.34e-03    
     +2 |          +7.00e-07     |          -9.33e-04    
     +3 |          +5.61e-06     |          -1.59e-03    
     +4 |          -1.83e-05     |          -1.92e-03    
     +5 |          -5.19e-05     |          -6.04e-04    
   (stars = BH-FDR corrected:  *** p_fdr<.01  ** <.05  * <.10)

4. DIRECTIONAL TEST (probit, ETF up/down)
   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k
   calendar: β₋₄=-1.63e-01**, β₋₁=+1.38e-01, β₊₄=-2.38e-01
   event: β₋₄=-2.86e-01**, β₋₁=+2.92e-01**, β₊₄=-3.08e-01**

5. DATA RELIABILITY (statistical, not a trade-count cutoff)
   Tier: Adequate
   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)
   calendar(full RTH grid): n_active=40  n_obs=301  n_days=17  K=5  params=29  df=272  median_SE=2.86e-05  sig(FDR)=3
   event: n_active=22  n_obs=28  n_days=4  K=5  params=15  df=13  median_SE=9.05e-04  sig(FDR)=0

6. COARSE-FREQUENCY ROBUSTNESS (re-run calendar at 30min / 60min)
    30min: n_obs=37 df=20 K=5  sig=0 (Kalshi-leads 0 / ETF-leads 0) -> No-sig
    60min: n_obs=22 df=7 K=4  sig=3 (Kalshi-leads 0 / ETF-leads 3) -> ETF-leads

7. VERDICT
   Calendar leans ETF-leads but Event leans Kalshi-leads -- NOT robust across time-axis; no clean lead.

8. FIGURE CAVEATS — figures are still drawn, but know their problems
   - Adequate info: figures and regression are mutually readable; note that flat Kalshi segments still mean 'no trade', not 'no change'.
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