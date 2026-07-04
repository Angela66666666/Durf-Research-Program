PAIR ANALYSIS    —    Rank 10 / 48
================================================================================================
KXECDJT281   x   VOX
Contract : "Will Trump win 281-257 - AZ, GA, NC, PA?"
Sector relevance : Election outcome (all sectors)
Window : 2024-11-04 to 2024-11-25     Kalshi trades : 308     primary bar : 5min     daily-screen R^2 : 0.33

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
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₋₃·xₜ₊₃ + β₋₂·xₜ₊₂ + β₋₁·xₜ₊₁ + β₊₃·xₜ₋₃
   where:
      β₋₃ = +2.976e-05   (t/z=+2.71, p=6.7e-03, p_fdr=2.5e-02) **   [ETF leads]
      β₋₂ = +5.158e-05   (t/z=+3.38, p=7.3e-04, p_fdr=4.0e-03) ***   [ETF leads]
      β₋₁ = +1.609e-05   (t/z=+1.63, p=1.0e-01, p_fdr=2.8e-01)    [ETF leads]
      β₊₃ = +3.848e-05   (t/z=+4.81, p=1.5e-06, p_fdr=1.6e-05) ***   [Kalshi leads]
   Lean by count of significant lags: ETF-leads  (k>0:1, k<0:3).

2. EVENT-TIME REGRESSION (event-count lags)
   Full model:  yₜ = α + Σ(k=-5..5) βₖ·xₜ₋ₖ + Σ(d=1..2) γ_d·Day_d
      where  ADL ETF self-lags p=0 (BIC chose none -> no ETF self-lag term);  day-FE: 2 day dummies over 3 trading days (first day = baseline).
      controls counted (so you can see the total at a glance):  11 lead/lag x-terms + 0 ETF self-lag(s) + 2 day-FE dummies + 1 intercept = 14 RHS regressors  (model n_params=14).
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₋₁·xₜ₊₁ + β₊₂·xₜ₋₂
   where:
      β₋₁ = +1.916e-04   (t/z=+2.31, p=2.1e-02, p_fdr=1.2e-01)    [ETF leads]
      β₊₂ = +2.670e-04   (t/z=+2.89, p=3.8e-03, p_fdr=4.2e-02) **   [Kalshi leads]
   Lean by count of significant lags: balanced/no clear side  (k>0:1, k<0:1).

3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)
      k |       calendar b (FDR) |          event b (FDR)
   ------------------------------------------------------
     -5 |          +1.42e-05     |          -1.80e-06    
     -4 |          +6.85e-06     |          -2.90e-05    
     -3 |          +2.98e-05 **  |          -1.26e-05    
     -2 |          +5.16e-05 *** |          -1.69e-05    
     -1 |          +1.61e-05     |          +1.92e-04    
     +0 |          +2.51e-05     |          +1.99e-05    
     +1 |          -6.10e-07     |          +5.99e-05    
     +2 |          +2.38e-05     |          +2.67e-04 ** 
     +3 |          +3.85e-05 *** |          +2.84e-05    
     +4 |          -3.12e-06     |          +7.27e-05    
     +5 |          -2.99e-05     |          +1.27e-04    
   (stars = BH-FDR corrected:  *** p_fdr<.01  ** <.05  * <.10)

4. DIRECTIONAL TEST (probit, ETF up/down)
   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k
   calendar: β₋₁=+2.70e-01***, β₊₅=+6.16e-02, β₊₆=+1.18e-01
   event: β₋₄=+1.80e-01*, β₋₁=+1.13e-01*, β₊₀=+1.24e-01, β₊₃=-1.86e-01

5. DATA RELIABILITY (statistical, not a trade-count cutoff)
   Tier: Adequate
   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)
   calendar(full RTH grid): n_active=53  n_obs=492  n_days=11  K=5  params=23  df=469  median_SE=1.44e-05  sig(FDR)=3
   event: n_active=37  n_obs=60  n_days=3  K=5  params=14  df=46  median_SE=8.88e-05  sig(FDR)=1

6. COARSE-FREQUENCY ROBUSTNESS (re-run calendar at 30min / 60min)
    30min: n_obs=32 df=16 K=5  sig=4 (Kalshi-leads 2 / ETF-leads 2) -> Balanced/mixed
    60min: n_obs=18 df=4 K=4  sig=2 (Kalshi-leads 2 / ETF-leads 0) -> Kalshi-leads

7. VERDICT
   Calendar leans ETF-leads but Event leans balanced -- NOT robust across time-axis; no clean lead.

8. FIGURE CAVEATS — figures are still drawn, but know their problems
   - Adequate info: figures and regression are mutually readable; note that flat Kalshi segments still mean 'no trade', not 'no change'.
   - Kalshi updates only on trades (flat line = no trade, NOT 'no change'); ETF mid refreshes continuously.

9. REAL-WORLD CONTEXT (WebSearch-verified; see URLs)
   - 2024 US presidential election held Tue Nov 5, 2024; ballots counted overnight Nov 5-6.
   - AP called the race for Trump ~5:34-5:37 AM ET on Wed Nov 6, 2024 (Wisconsin pushed him past 270) -- this is PRE-MARKET, so the regular-hours equity reaction shows up at the Nov 6 open.
   - Final electoral result: Trump 312, Harris 226.
   - Sources: en.wikipedia.org/wiki/2024_United_States_presidential_election ; spectrumlocalnews.com/us/snplus/news/2024/11/06/trump-wins-ap-projection-2024-election

------------------------------------------------------------------------------------------------
Conventions: ET | 09:30-16:00 (forward windows capped to 16:00) | ETF in log return | median causal bars | full RTH grid | day-grouped lags (no overnight) | ADL self-control | significance = BH-FDR corrected.
Figures for this pair follow on the next page.