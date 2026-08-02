PAIR ANALYSIS    —    Rank 11 / 48
================================================================================================
KXECDJT281   x   VGT
Contract : "Will Trump win 281-257 - AZ, GA, NC, PA?"
Sector relevance : Election outcome (all sectors)
Window : 2024-11-04 to 2024-11-25     Kalshi trades : 308     primary bar : 5min     daily-screen R^2 : 0.32

>>> RELIABILITY:  Adequate   <<<   (see section 5; unreliable pairs still get figures, but read their problems in section 8)

DEFINITIONS
   xₜ₋ₖ = Kalshi yes-probability change, k bars before t   (1 bar = 5min)
   yₜ   = ETF log return over bar t
   calendar = full market-hours grid: x=0 in bars with no Kalshi trade (not dropped).
   k>0 => Kalshi leads ETF ;  k<0 => ETF leads Kalshi ;  k=0 => contemporaneous

1. CALENDAR-TIME REGRESSION (clock-time lags, full RTH grid)
   Full model:  yₜ = α + Σ(k=-5..5) βₖ·xₜ₋ₖ + φ₁·yₜ₋₁ + φ₂·yₜ₋₂ + Σ(d=1..10) γ_d·Day_d
      where  ADL ETF self-lags p=2 (BIC-chosen): φ₁·yₜ₋₁ + φ₂·yₜ₋₂;  day-FE: 10 day dummies over 11 trading days (first day = baseline).
      controls counted (so you can see the total at a glance):  11 lead/lag x-terms + 2 ETF self-lag(s) + 10 day-FE dummies + 1 intercept = 24 RHS regressors  (model n_params=24).
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₋₁·xₜ₊₁
   where:
      β₋₁ = -2.456e-05   (t/z=-2.75, p=5.9e-03, p_fdr=6.5e-02) *   [ETF leads]
   Lean by count of significant lags: ETF-leads  (k>0:0, k<0:1).

2. EVENT-TIME REGRESSION (event-count lags)
   Full model:  yₜ = α + Σ(k=-5..5) βₖ·xₜ₋ₖ + Σ(d=1..2) γ_d·Day_d
      where  ADL ETF self-lags p=0 (BIC chose none -> no ETF self-lag term);  day-FE: 2 day dummies over 3 trading days (first day = baseline).
      controls counted (so you can see the total at a glance):  11 lead/lag x-terms + 0 ETF self-lag(s) + 2 day-FE dummies + 1 intercept = 14 RHS regressors  (model n_params=14).
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₋₁·xₜ₊₁ + β₊₀·xₜ + β₊₅·xₜ₋₅
   where:
      β₋₁ = -7.498e-05   (t/z=-3.08, p=2.0e-03, p_fdr=7.5e-03) ***   [ETF leads]
      β₊₀ = -2.400e-04   (t/z=-4.64, p=3.5e-06, p_fdr=3.8e-05) ***   [contemporaneous]
      β₊₅ = +1.702e-04   (t/z=+4.30, p=1.7e-05, p_fdr=9.3e-05) ***   [Kalshi leads]
   Lean by count of significant lags: balanced/no clear side  (k>0:1, k<0:1).

3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)
      k |       calendar b (FDR) |          event b (FDR)
   ------------------------------------------------------
     -5 |          -1.53e-05     |          -6.25e-05    
     -4 |          +1.67e-05     |          +2.96e-05    
     -3 |          -4.60e-06     |          -4.55e-06    
     -2 |          +2.89e-05     |          -3.39e-05    
     -1 |          -2.46e-05 *   |          -7.50e-05 ***
     +0 |          -1.64e-05     |          -2.40e-04 ***
     +1 |          -1.29e-05     |          -1.18e-04    
     +2 |          +8.52e-06     |          +5.15e-05    
     +3 |          -2.08e-05     |          +1.03e-05    
     +4 |          -9.49e-06     |          +5.25e-05    
     +5 |          -4.61e-05     |          +1.70e-04 ***
   (stars = BH-FDR corrected:  *** p_fdr<.01  ** <.05  * <.10)

4. DIRECTIONAL TEST (probit, ETF up/down)
   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k
   calendar: β₋₄=+1.44e-01, β₊₁=-1.09e-01
   event: β₋₆=-6.38e-02, β₋₄=+1.52e-01

5. DATA RELIABILITY (statistical, not a trade-count cutoff)
   Tier: Adequate
   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)
   calendar(full RTH grid): n_active=53  n_obs=492  n_days=11  K=5  params=24  df=468  median_SE=2.06e-05  sig(FDR)=0
   event: n_active=37  n_obs=60  n_days=3  K=5  params=14  df=46  median_SE=5.94e-05  sig(FDR)=3

6. COARSE-FREQUENCY ROBUSTNESS (re-run calendar at 30min / 60min)
    30min: n_obs=32 df=16 K=5  sig=4 (Kalshi-leads 2 / ETF-leads 2) -> Balanced/mixed
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