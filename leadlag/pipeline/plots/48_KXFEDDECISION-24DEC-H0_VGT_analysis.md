PAIR ANALYSIS    —    Rank 3 / 48
================================================================================================
KXFEDDECISION-24DEC-H0   x   VGT
Contract : "Will the Federal Reserve Hike rates by 0bps at their December 2024 meeting?"
Sector relevance : VFH_VNQ_VPU (Rate-sensitive: Financials / Real Estate / Utilities)
Window : 2024-10-31 to 2024-12-18     Kalshi trades : 1326     primary bar : 10min     daily-screen R^2 : 0.12

>>> RELIABILITY:  Adequate   <<<   (see section 5; unreliable pairs still get figures, but read their problems in section 8)

DEFINITIONS
   xₜ₋ₖ = Kalshi yes-probability change, k bars before t   (1 bar = 10min)
   yₜ   = ETF log return over bar t
   calendar = full market-hours grid: x=0 in bars with no Kalshi trade (not dropped).
   k>0 => Kalshi leads ETF ;  k<0 => ETF leads Kalshi ;  k=0 => contemporaneous

1. CALENDAR-TIME REGRESSION (clock-time lags, full RTH grid)
   Full model:  yₜ = α + Σ(k=-8..8) βₖ·xₜ₋ₖ + Σ(d=1..30) γ_d·Day_d
      where  ADL ETF self-lags p=0 (BIC chose none -> no ETF self-lag term);  day-FE: 30 day dummies over 31 trading days (first day = baseline).
      controls counted (so you can see the total at a glance):  17 lead/lag x-terms + 0 ETF self-lag(s) + 30 day-FE dummies + 1 intercept = 48 RHS regressors  (model n_params=48).
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₊₅·xₜ₋₅
   where:
      β₊₅ = +3.663e-05   (t/z=+2.01, p=4.4e-02, p_fdr=7.5e-01)    [Kalshi leads]
   Lean by count of significant lags: Kalshi-leads  (k>0:1, k<0:0).

2. EVENT-TIME REGRESSION (event-count lags)
   Full model:  yₜ = α + Σ(k=-8..8) βₖ·xₜ₋ₖ + φ₁·yₜ₋₁ + φ₂·yₜ₋₂ + φ₃·yₜ₋₃ + Σ(d=1..8) γ_d·Day_d
      where  ADL ETF self-lags p=3 (BIC-chosen): φ₁·yₜ₋₁ + φ₂·yₜ₋₂ + φ₃·yₜ₋₃;  day-FE: 8 day dummies over 9 trading days (first day = baseline).
      controls counted (so you can see the total at a glance):  17 lead/lag x-terms + 3 ETF self-lag(s) + 8 day-FE dummies + 1 intercept = 29 RHS regressors  (model n_params=29).
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₋₈·xₜ₊₈ + β₋₇·xₜ₊₇ + β₋₆·xₜ₊₆ + β₋₄·xₜ₊₄ + β₋₃·xₜ₊₃ + β₋₂·xₜ₊₂ + β₊₈·xₜ₋₈
   where:
      β₋₈ = -1.152e-03   (t/z=-2.72, p=6.5e-03, p_fdr=3.7e-02) **   [ETF leads]
      β₋₇ = -1.199e-03   (t/z=-3.03, p=2.4e-03, p_fdr=2.4e-02) **   [ETF leads]
      β₋₆ = -2.168e-03   (t/z=-2.99, p=2.8e-03, p_fdr=2.4e-02) **   [ETF leads]
      β₋₄ = -1.633e-03   (t/z=-2.54, p=1.1e-02, p_fdr=4.7e-02) **   [ETF leads]
      β₋₃ = -1.175e-03   (t/z=-1.66, p=9.7e-02, p_fdr=2.7e-01)    [ETF leads]
      β₋₂ = -8.088e-04   (t/z=-1.49, p=1.4e-01, p_fdr=3.2e-01)    [ETF leads]
      β₊₈ = -7.510e-04   (t/z=-1.76, p=7.9e-02, p_fdr=2.7e-01)    [Kalshi leads]
   Lean by count of significant lags: ETF-leads  (k>0:1, k<0:6).

3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)
      k |       calendar b (FDR) |          event b (FDR)
   ------------------------------------------------------
     -8 |          +2.08e-05     |          -1.15e-03 ** 
     -7 |          +1.21e-05     |          -1.20e-03 ** 
     -6 |          +3.07e-05     |          -2.17e-03 ** 
     -5 |          +2.79e-05     |          -1.09e-03    
     -4 |          +6.13e-06     |          -1.63e-03 ** 
     -3 |          -1.12e-05     |          -1.17e-03    
     -2 |          +1.62e-06     |          -8.09e-04    
     -1 |          -1.28e-05     |          -1.14e-03    
     +0 |          +2.48e-05     |          -3.71e-04    
     +1 |          +2.48e-05     |          -9.15e-04    
     +2 |          +3.06e-05     |          -2.06e-04    
     +3 |          -3.38e-05     |          -5.61e-04    
     +4 |          +2.63e-05     |          -8.59e-05    
     +5 |          +3.66e-05     |          -7.00e-04    
     +6 |          -3.86e-06     |          -2.81e-04    
     +7 |          +1.16e-05     |          -2.42e-04    
     +8 |          +3.04e-05     |          -7.51e-04    
   (stars = BH-FDR corrected:  *** p_fdr<.01  ** <.05  * <.10)

4. DIRECTIONAL TEST (probit, ETF up/down)
   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k
   calendar: β₋₆=+1.49e-01, β₊₀=-9.52e-02, β₊₄=+6.68e-02, β₊₆=+1.13e-01
   event: β₊₆=+1.06e-01

5. DATA RELIABILITY (statistical, not a trade-count cutoff)
   Tier: Adequate
   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)
   calendar(full RTH grid): n_active=126  n_obs=586  n_days=31  K=8  params=48  df=538  median_SE=3.19e-05  sig(FDR)=0
   event: n_active=26  n_obs=45  n_days=9  K=8  params=29  df=16  median_SE=6.42e-04  sig(FDR)=4

6. COARSE-FREQUENCY ROBUSTNESS (re-run calendar at 30min / 60min)
    30min: n_obs=210 df=164 K=8  sig=0 (Kalshi-leads 0 / ETF-leads 0) -> No-sig
    60min: n_obs=131 df=88 K=6  sig=1 (Kalshi-leads 1 / ETF-leads 0) -> Kalshi-leads

7. VERDICT
   Calendar leans Kalshi-leads but Event leans ETF-leads -- NOT robust across time-axis; no clean lead.

8. FIGURE CAVEATS — figures are still drawn, but know their problems
   - Adequate info: figures and regression are mutually readable; note that flat Kalshi segments still mean 'no trade', not 'no change'.
   - Mixed coefficient signs across lags -- relationship not monotone.
   - Kalshi updates only on trades (flat line = no trade, NOT 'no change'); ETF mid refreshes continuously.

------------------------------------------------------------------------------------------------
Conventions: ET | 09:30-16:00 (forward windows capped to 16:00) | ETF in log return | median causal bars | full RTH grid | day-grouped lags (no overnight) | ADL self-control | significance = BH-FDR corrected.
Figures for this pair follow on the next page.