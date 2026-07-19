PAIR ANALYSIS    —    Rank 12 / 48
================================================================================================
KXECDJT281   x   VCR
Contract : "Will Trump win 281-257 - AZ, GA, NC, PA?"
Sector relevance : Election outcome (all sectors)
Window : 2024-11-04 to 2024-11-25     Kalshi trades : 308     primary bar : 5min     daily-screen R^2 : 0.28

>>> RELIABILITY:  Adequate   <<<   (see section 5; unreliable pairs still get figures, but read their problems in section 8)

DEFINITIONS
   xₜ₋ₖ = Kalshi yes-probability change, k bars before t   (1 bar = 5min)
   yₜ   = ETF log return over bar t
   calendar = full market-hours grid: x=0 in bars with no Kalshi trade (not dropped).
   k>0 => Kalshi leads ETF ;  k<0 => ETF leads Kalshi ;  k=0 => contemporaneous

1. CALENDAR-TIME REGRESSION (clock-time lags, full RTH grid)
   Full model:  yₜ = α + Σ(k=-5..5) βₖ·xₜ₋ₖ + φ₁·yₜ₋₁ + Σ(d=1..10) γ_d·Day_d
      where  ADL ETF self-lags p=1 (BIC-chosen): φ₁·yₜ₋₁;  day-FE: 10 day dummies over 11 trading days (first day = baseline).
      controls counted (so you can see the total at a glance):  11 lead/lag x-terms + 1 ETF self-lag(s) + 10 day-FE dummies + 1 intercept = 23 RHS regressors  (model n_params=23).
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₋₂·xₜ₊₂
   where:
      β₋₂ = +3.205e-05   (t/z=+2.11, p=3.5e-02, p_fdr=3.8e-01)    [ETF leads]
   Lean by count of significant lags: ETF-leads  (k>0:0, k<0:1).

2. EVENT-TIME REGRESSION (event-count lags)
   Full model:  yₜ = α + Σ(k=-5..5) βₖ·xₜ₋ₖ + Σ(d=1..2) γ_d·Day_d
      where  ADL ETF self-lags p=0 (BIC chose none -> no ETF self-lag term);  day-FE: 2 day dummies over 3 trading days (first day = baseline).
      controls counted (so you can see the total at a glance):  11 lead/lag x-terms + 0 ETF self-lag(s) + 2 day-FE dummies + 1 intercept = 14 RHS regressors  (model n_params=14).
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₋₅·xₜ₊₅ + β₊₃·xₜ₋₃ + β₊₅·xₜ₋₅
   where:
      β₋₅ = -1.127e-04   (t/z=-3.28, p=1.0e-03, p_fdr=1.1e-02) **   [ETF leads]
      β₊₃ = -1.859e-04   (t/z=-1.47, p=1.4e-01, p_fdr=4.4e-01)    [Kalshi leads]
      β₊₅ = +1.298e-04   (t/z=+1.52, p=1.3e-01, p_fdr=4.4e-01)    [Kalshi leads]
   Lean by count of significant lags: Kalshi-leads  (k>0:2, k<0:1).

3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)
      k |       calendar b (FDR) |          event b (FDR)
   ------------------------------------------------------
     -5 |          -1.38e-05     |          -1.13e-04 ** 
     -4 |          +9.43e-06     |          +1.57e-05    
     -3 |          +2.66e-05     |          -3.10e-05    
     -2 |          +3.20e-05     |          +2.90e-05    
     -1 |          +4.69e-06     |          +1.18e-04    
     +0 |          -6.89e-06     |          -5.92e-05    
     +1 |          -6.01e-06     |          -4.81e-05    
     +2 |          -7.80e-07     |          +3.16e-05    
     +3 |          +1.48e-05     |          -1.86e-04    
     +4 |          +2.47e-05     |          -5.16e-05    
     +5 |          -2.82e-06     |          +1.30e-04    
   (stars = BH-FDR corrected:  *** p_fdr<.01  ** <.05  * <.10)

4. DIRECTIONAL TEST (probit, ETF up/down)
   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k
   calendar: β₋₄=+3.60e-01, β₋₃=-9.30e-02, β₊₁=-6.42e-02, β₊₆=-7.91e-02
   event: β₊₁=-9.90e-02, β₊₃=-1.40e-01***, β₊₆=-5.98e-02*

5. DATA RELIABILITY (statistical, not a trade-count cutoff)
   Tier: Adequate
   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)
   calendar(full RTH grid): n_active=53  n_obs=492  n_days=11  K=5  params=23  df=469  median_SE=2.52e-05  sig(FDR)=0
   event: n_active=37  n_obs=60  n_days=3  K=5  params=14  df=46  median_SE=8.56e-05  sig(FDR)=1

6. COARSE-FREQUENCY ROBUSTNESS (re-run calendar at 30min / 60min)
    30min: n_obs=32 df=16 K=5  sig=7 (Kalshi-leads 4 / ETF-leads 2) -> Kalshi-leads
    60min: n_obs=18 df=4 K=4  sig=0 (Kalshi-leads 0 / ETF-leads 0) -> No-sig

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