PAIR ANALYSIS    —    Rank 12 / 48
================================================================================================
KXECDJT281   x   VCR
Contract : "Will Trump win 281-257 - AZ, GA, NC, PA?"
Sector relevance : Election outcome (all sectors)
Window : 2024-11-04 to 2024-11-25     Kalshi trades : 294     primary bar : 5min     daily-screen R^2 : 0.28

>>> RELIABILITY:  Adequate   <<<   (see section 5; unreliable pairs still get figures, but read their problems in section 8)

DEFINITIONS
   xₜ₋ₖ = Kalshi yes-probability change, k bars before t   (1 bar = 5min)
   yₜ   = ETF log return over bar t
   calendar = full market-hours grid: x=0 in bars with no Kalshi trade (not dropped).
   k>0 => Kalshi leads ETF ;  k<0 => ETF leads Kalshi ;  k=0 => contemporaneous

1. CALENDAR-TIME REGRESSION (clock-time lags, full RTH grid)
   Full model:  yₜ = α + Σ(k=-5..5) βₖ·xₜ₋ₖ + φ₁·yₜ₋₁ + Σ(d=1..7) γ_d·Day_d
      where  ADL ETF self-lags p=1 (BIC-chosen): φ₁·yₜ₋₁;  day-FE: 7 day dummies over 8 trading days (first day = baseline).
      controls counted (so you can see the total at a glance):  11 lead/lag x-terms + 1 ETF self-lag(s) + 7 day-FE dummies + 1 intercept = 20 RHS regressors  (model n_params=20).
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₋₂·xₜ₊₂
   where:
      β₋₂ = +3.263e-05   (t/z=+2.23, p=2.6e-02, p_fdr=2.9e-01)    [ETF leads]
   Lean by count of significant lags: ETF-leads  (k>0:0, k<0:1).

2. EVENT-TIME REGRESSION (event-count lags)
   Full model:  yₜ = α + Σ(k=-5..5) βₖ·xₜ₋ₖ + Σ(d=1..1) γ_d·Day_d
      where  ADL ETF self-lags p=0 (BIC chose none -> no ETF self-lag term);  day-FE: 1 day dummies over 2 trading days (first day = baseline).
      controls counted (so you can see the total at a glance):  11 lead/lag x-terms + 0 ETF self-lag(s) + 1 day-FE dummies + 1 intercept = 13 RHS regressors  (model n_params=13).
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₋₅·xₜ₊₅ + β₊₁·xₜ₋₁
   where:
      β₋₅ = -1.116e-04   (t/z=-2.29, p=2.2e-02, p_fdr=1.2e-01)    [ETF leads]
      β₊₁ = -7.434e-05   (t/z=-4.11, p=4.0e-05, p_fdr=4.4e-04) ***   [Kalshi leads]
   Lean by count of significant lags: balanced/no clear side  (k>0:1, k<0:1).

3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)
      k |       calendar b (FDR) |          event b (FDR)
   ------------------------------------------------------
     -5 |          -1.32e-05     |          -1.12e-04    
     -4 |          +1.02e-05     |          +1.30e-05    
     -3 |          +3.84e-05     |          -3.38e-05    
     -2 |          +3.26e-05     |          +2.21e-05    
     -1 |          +5.73e-06     |          +1.09e-04    
     +0 |          -8.70e-06     |          -7.26e-05    
     +1 |          -6.63e-06     |          -7.43e-05 ***
     +2 |          -1.21e-06     |          +4.15e-05    
     +3 |          +1.87e-05     |          -1.95e-04    
     +4 |          +3.03e-05     |          -5.81e-05    
     +5 |          -2.25e-06     |          +1.19e-04    
   (stars = BH-FDR corrected:  *** p_fdr<.01  ** <.05  * <.10)

4. DIRECTIONAL TEST (probit, ETF up/down)
   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k
   calendar: β₊₁=-7.74e-02
   event: β₊₁=-1.12e-01, β₊₃=-8.98e-02

5. DATA RELIABILITY (statistical, not a trade-count cutoff)
   Tier: Adequate
   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)
   calendar(full RTH grid): n_active=51  n_obs=385  n_days=8  K=5  params=20  df=365  median_SE=2.77e-05  sig(FDR)=0
   event: n_active=35  n_obs=58  n_days=2  K=5  params=13  df=45  median_SE=1.19e-04  sig(FDR)=1

6. COARSE-FREQUENCY ROBUSTNESS (re-run calendar at 30min / 60min)
    30min: n_obs=31 df=15 K=5  sig=7 (Kalshi-leads 4 / ETF-leads 2) -> Kalshi-leads
    60min: n_obs=18 df=4 K=4  sig=0 (Kalshi-leads 0 / ETF-leads 0) -> No-sig

7. VERDICT
   Calendar leans ETF-leads but Event leans balanced -- NOT robust across time-axis; no clean lead.

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