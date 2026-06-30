PAIR ANALYSIS    —    Rank 11 / 48
================================================================================================
KXECDJT281   x   VGT
Contract : "Will Trump win 281-257 - AZ, GA, NC, PA?"
Sector relevance : Election outcome (all sectors)
Window : 2024-11-04 to 2024-11-25     Kalshi trades : 294     primary bar : 5min     daily-screen R^2 : 0.32

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
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₋₁·xₜ₊₁ + β₊₃·xₜ₋₃
   where:
      β₋₁ = -3.137e-05   (t/z=-3.09, p=2.0e-03, p_fdr=2.2e-02) **   [ETF leads]
      β₊₃ = -1.916e-05   (t/z=-2.55, p=1.1e-02, p_fdr=5.8e-02) *   [Kalshi leads]
   Lean by count of significant lags: balanced/no clear side  (k>0:1, k<0:1).

2. EVENT-TIME REGRESSION (event-count lags)
   Full model:  yₜ = α + Σ(k=-5..5) βₖ·xₜ₋ₖ + Σ(d=1..1) γ_d·Day_d
      where  ADL ETF self-lags p=0 (BIC chose none -> no ETF self-lag term);  day-FE: 1 day dummies over 2 trading days (first day = baseline).
      controls counted (so you can see the total at a glance):  11 lead/lag x-terms + 0 ETF self-lag(s) + 1 day-FE dummies + 1 intercept = 13 RHS regressors  (model n_params=13).
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₋₁·xₜ₊₁ + β₊₀·xₜ + β₊₅·xₜ₋₅
   where:
      β₋₁ = -7.252e-05   (t/z=-2.38, p=1.8e-02, p_fdr=6.4e-02) *   [ETF leads]
      β₊₀ = -2.397e-04   (t/z=-4.20, p=2.7e-05, p_fdr=2.9e-04) ***   [contemporaneous]
      β₊₅ = +1.775e-04   (t/z=+3.51, p=4.5e-04, p_fdr=2.5e-03) ***   [Kalshi leads]
   Lean by count of significant lags: balanced/no clear side  (k>0:1, k<0:1).

3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)
      k |       calendar b (FDR) |          event b (FDR)
   ------------------------------------------------------
     -5 |          -1.77e-05     |          -6.46e-05    
     -4 |          +1.84e-05     |          +3.11e-05    
     -3 |          -3.68e-06     |          -3.83e-06    
     -2 |          +2.40e-05     |          -3.19e-05    
     -1 |          -3.14e-05 **  |          -7.25e-05 *  
     +0 |          -2.38e-05     |          -2.40e-04 ***
     +1 |          -1.24e-05     |          -1.11e-04    
     +2 |          +1.38e-05     |          +4.91e-05    
     +3 |          -1.92e-05 *   |          +1.26e-05    
     +4 |          -1.02e-05     |          +5.54e-05    
     +5 |          -5.11e-05     |          +1.78e-04 ***
   (stars = BH-FDR corrected:  *** p_fdr<.01  ** <.05  * <.10)

4. DIRECTIONAL TEST (probit, ETF up/down)
   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k
   calendar: β₋₆=-1.62e-01, β₊₁=-1.20e-01
   event: β₋₆=-1.11e-01

5. DATA RELIABILITY (statistical, not a trade-count cutoff)
   Tier: Adequate
   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)
   calendar(full RTH grid): n_active=51  n_obs=385  n_days=8  K=5  params=20  df=365  median_SE=2.48e-05  sig(FDR)=1
   event: n_active=35  n_obs=58  n_days=2  K=5  params=13  df=45  median_SE=6.81e-05  sig(FDR)=2

6. COARSE-FREQUENCY ROBUSTNESS (re-run calendar at 30min / 60min)
    30min: n_obs=31 df=15 K=5  sig=6 (Kalshi-leads 3 / ETF-leads 2) -> Kalshi-leads
    60min: n_obs=18 df=4 K=4  sig=1 (Kalshi-leads 0 / ETF-leads 1) -> ETF-leads

7. VERDICT
   Both time-axes balanced -- no clean directional lead.

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