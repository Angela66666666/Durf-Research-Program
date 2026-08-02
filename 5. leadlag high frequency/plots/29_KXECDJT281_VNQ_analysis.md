PAIR ANALYSIS    —    Rank 9 / 48
================================================================================================
KXECDJT281   x   VNQ
Contract : "Will Trump win 281-257 - AZ, GA, NC, PA?"
Sector relevance : Election outcome (all sectors)
Window : 2024-11-04 to 2024-11-25     Kalshi trades : 308     primary bar : 5min     daily-screen R^2 : 0.43

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
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₋₃·xₜ₊₃ + β₋₂·xₜ₊₂ + β₋₁·xₜ₊₁ + β₊₁·xₜ₋₁
   where:
      β₋₃ = -2.984e-05   (t/z=-2.60, p=9.4e-03, p_fdr=3.5e-02) **   [ETF leads]
      β₋₂ = +8.799e-05   (t/z=+5.07, p=4.0e-07, p_fdr=4.3e-06) ***   [ETF leads]
      β₋₁ = +1.114e-04   (t/z=+2.25, p=2.5e-02, p_fdr=6.8e-02) *   [ETF leads]
      β₊₁ = +8.854e-05   (t/z=+3.65, p=2.6e-04, p_fdr=1.4e-03) ***   [Kalshi leads]
   Lean by count of significant lags: ETF-leads  (k>0:1, k<0:3).

2. EVENT-TIME REGRESSION (event-count lags)
   Full model:  yₜ = α + Σ(k=-5..5) βₖ·xₜ₋ₖ + Σ(d=1..2) γ_d·Day_d
      where  ADL ETF self-lags p=0 (BIC chose none -> no ETF self-lag term);  day-FE: 2 day dummies over 3 trading days (first day = baseline).
      controls counted (so you can see the total at a glance):  11 lead/lag x-terms + 0 ETF self-lag(s) + 2 day-FE dummies + 1 intercept = 14 RHS regressors  (model n_params=14).
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₋₄·xₜ₊₄ + β₋₃·xₜ₊₃ + β₊₁·xₜ₋₁ + β₊₂·xₜ₋₂ + β₊₄·xₜ₋₄
   where:
      β₋₄ = -1.020e-04   (t/z=-2.30, p=2.1e-02, p_fdr=5.8e-02) *   [ETF leads]
      β₋₃ = -1.100e-04   (t/z=-3.88, p=1.0e-04, p_fdr=1.2e-03) ***   [ETF leads]
      β₊₁ = +2.788e-04   (t/z=+3.31, p=9.2e-04, p_fdr=3.4e-03) ***   [Kalshi leads]
      β₊₂ = +3.501e-04   (t/z=+1.64, p=1.0e-01, p_fdr=2.2e-01)    [Kalshi leads]
      β₊₄ = +8.416e-05   (t/z=+3.68, p=2.3e-04, p_fdr=1.3e-03) ***   [Kalshi leads]
   Lean by count of significant lags: Kalshi-leads  (k>0:3, k<0:2).

3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)
      k |       calendar b (FDR) |          event b (FDR)
   ------------------------------------------------------
     -5 |          -2.56e-06     |          -8.13e-05    
     -4 |          -1.21e-05     |          -1.02e-04 *  
     -3 |          -2.98e-05 **  |          -1.10e-04 ***
     -2 |          +8.80e-05 *** |          -1.96e-04    
     -1 |          +1.11e-04 *   |          +1.84e-04    
     +0 |          -1.06e-05     |          +5.84e-05    
     +1 |          +8.85e-05 *** |          +2.79e-04 ***
     +2 |          +1.14e-05     |          +3.50e-04    
     +3 |          +3.53e-05     |          +2.06e-04    
     +4 |          +5.40e-06     |          +8.42e-05 ***
     +5 |          +1.62e-05     |          +1.11e-04    
   (stars = BH-FDR corrected:  *** p_fdr<.01  ** <.05  * <.10)

4. DIRECTIONAL TEST (probit, ETF up/down)
   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k
   calendar: β₋₅=+1.07e-01, β₋₂=+1.82e-01, β₊₀=-3.53e-01, β₊₂=-2.10e-01, β₊₅=-1.68e-01
   event: β₋₃=+1.43e-01, β₋₁=+8.75e-02, β₊₀=-7.71e-02

5. DATA RELIABILITY (statistical, not a trade-count cutoff)
   Tier: Adequate
   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)
   calendar(full RTH grid): n_active=53  n_obs=492  n_days=11  K=5  params=23  df=469  median_SE=2.10e-05  sig(FDR)=3
   event: n_active=37  n_obs=60  n_days=3  K=5  params=14  df=46  median_SE=8.41e-05  sig(FDR)=3

6. COARSE-FREQUENCY ROBUSTNESS (re-run calendar at 30min / 60min)
    30min: n_obs=32 df=16 K=5  sig=3 (Kalshi-leads 1 / ETF-leads 1) -> Balanced/mixed
    60min: n_obs=18 df=4 K=4  sig=1 (Kalshi-leads 0 / ETF-leads 1) -> ETF-leads

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