PAIR ANALYSIS    —    Rank 3 / 48
================================================================================================
KXFEDDECISION-24DEC-H0   x   VGT
Contract : "Will the Federal Reserve Hike rates by 0bps at their December 2024 meeting?"
Sector relevance : VFH_VNQ_VPU (Rate-sensitive: Financials / Real Estate / Utilities)
Window : 2024-10-31 to 2024-12-18     Kalshi trades : 1375     primary bar : 10min     daily-screen R^2 : 0.12

>>> RELIABILITY:  Adequate   <<<   (see section 5; unreliable pairs still get figures, but read their problems in section 8)

DEFINITIONS
   xₜ₋ₖ = Kalshi yes-probability change, k bars before t   (1 bar = 10min)
   yₜ   = ETF log return over bar t
   calendar = full market-hours grid: x=0 in bars with no Kalshi trade (not dropped).
   k>0 => Kalshi leads ETF ;  k<0 => ETF leads Kalshi ;  k=0 => contemporaneous

1. CALENDAR-TIME REGRESSION (clock-time lags, full RTH grid)
   Full model:  yₜ = α + Σ(k=-8..8) βₖ·xₜ₋ₖ + Σ(d=1..32) γ_d·Day_d
      where  ADL ETF self-lags p=0 (BIC chose none -> no ETF self-lag term);  day-FE: 32 day dummies over 33 trading days (first day = baseline).
      controls counted (so you can see the total at a glance):  17 lead/lag x-terms + 0 ETF self-lag(s) + 32 day-FE dummies + 1 intercept = 50 RHS regressors  (model n_params=50).
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₊₀·xₜ + β₊₅·xₜ₋₅
   where:
      β₊₀ = +3.995e-05   (t/z=+1.50, p=1.3e-01, p_fdr=6.7e-01)    [contemporaneous]
      β₊₅ = +2.608e-05   (t/z=+1.67, p=9.6e-02, p_fdr=6.7e-01)    [Kalshi leads]
   Lean by count of significant lags: Kalshi-leads  (k>0:1, k<0:0).

2. EVENT-TIME REGRESSION (event-count lags)
   Full model:  yₜ = α + Σ(k=-8..8) βₖ·xₜ₋ₖ + φ₁·yₜ₋₁ + Σ(d=1..8) γ_d·Day_d
      where  ADL ETF self-lags p=1 (BIC-chosen): φ₁·yₜ₋₁;  day-FE: 8 day dummies over 9 trading days (first day = baseline).
      controls counted (so you can see the total at a glance):  17 lead/lag x-terms + 1 ETF self-lag(s) + 8 day-FE dummies + 1 intercept = 27 RHS regressors  (model n_params=27).
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₋₈·xₜ₊₈ + β₋₇·xₜ₊₇ + β₋₆·xₜ₊₆ + β₋₃·xₜ₊₃ + β₋₂·xₜ₊₂ + β₋₁·xₜ₊₁ + β₊₁·xₜ₋₁ + β₊₂·xₜ₋₂ + β₊₃·xₜ₋₃ + β₊₄·xₜ₋₄
   where:
      β₋₈ = -7.682e-04   (t/z=-2.70, p=6.8e-03, p_fdr=7.4e-02) *   [ETF leads]
      β₋₇ = -7.839e-04   (t/z=-2.48, p=1.3e-02, p_fdr=7.4e-02) *   [ETF leads]
      β₋₆ = -1.090e-03   (t/z=-1.82, p=6.9e-02, p_fdr=1.8e-01)    [ETF leads]
      β₋₃ = -6.043e-04   (t/z=-1.64, p=1.0e-01, p_fdr=1.9e-01)    [ETF leads]
      β₋₂ = -7.290e-04   (t/z=-1.79, p=7.4e-02, p_fdr=1.8e-01)    [ETF leads]
      β₋₁ = -1.034e-03   (t/z=-2.51, p=1.2e-02, p_fdr=7.4e-02) *   [ETF leads]
      β₊₁ = -7.639e-04   (t/z=-1.67, p=9.5e-02, p_fdr=1.9e-01)    [Kalshi leads]
      β₊₂ = -3.685e-04   (t/z=-1.55, p=1.2e-01, p_fdr=2.1e-01)    [Kalshi leads]
      β₊₃ = -6.243e-04   (t/z=-1.83, p=6.7e-02, p_fdr=1.8e-01)    [Kalshi leads]
      β₊₄ = -2.431e-04   (t/z=-1.83, p=6.7e-02, p_fdr=1.8e-01)    [Kalshi leads]
   Lean by count of significant lags: ETF-leads  (k>0:4, k<0:6).

3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)
      k |       calendar b (FDR) |          event b (FDR)
   ------------------------------------------------------
     -8 |          +2.15e-05     |          -7.68e-04 *  
     -7 |          +1.39e-05     |          -7.84e-04 *  
     -6 |          +5.27e-05     |          -1.09e-03    
     -5 |          +2.61e-05     |          -4.80e-04    
     -4 |          +3.66e-06     |          -4.78e-04    
     -3 |          -2.09e-07     |          -6.04e-04    
     -2 |          +1.07e-05     |          -7.29e-04    
     -1 |          -5.85e-07     |          -1.03e-03 *  
     +0 |          +4.00e-05     |          -2.36e-04    
     +1 |          +2.80e-05     |          -7.64e-04    
     +2 |          +3.08e-05     |          -3.68e-04    
     +3 |          -3.24e-06     |          -6.24e-04    
     +4 |          +5.11e-05     |          -2.43e-04    
     +5 |          +2.61e-05     |          -2.57e-04    
     +6 |          -4.95e-06     |          -2.86e-05    
     +7 |          +2.02e-05     |          +1.40e-04    
     +8 |          +4.08e-05     |          -2.43e-04    
   (stars = BH-FDR corrected:  *** p_fdr<.01  ** <.05  * <.10)

4. DIRECTIONAL TEST (probit, ETF up/down)
   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k
   calendar: β₋₆=+1.57e-01, β₊₀=-9.61e-02
   event: β₋₈=-6.48e-02, β₋₆=+1.23e-01, β₋₄=-8.91e-02, β₊₀=-7.62e-02, β₊₂=+9.10e-02

5. DATA RELIABILITY (statistical, not a trade-count cutoff)
   Tier: Adequate
   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)
   calendar(full RTH grid): n_active=130  n_obs=621  n_days=33  K=8  params=50  df=571  median_SE=2.90e-05  sig(FDR)=0
   event: n_active=27  n_obs=48  n_days=9  K=8  params=27  df=21  median_SE=3.62e-04  sig(FDR)=0

6. COARSE-FREQUENCY ROBUSTNESS (re-run calendar at 30min / 60min)
    30min: n_obs=219 df=172 K=8  sig=0 (Kalshi-leads 0 / ETF-leads 0) -> No-sig
    60min: n_obs=138 df=94 K=6  sig=0 (Kalshi-leads 0 / ETF-leads 0) -> No-sig

7. VERDICT
   Calendar leans Kalshi-leads but Event leans ETF-leads -- NOT robust across time-axis; no clean lead.

8. FIGURE CAVEATS — figures are still drawn, but know their problems
   - Adequate info: figures and regression are mutually readable; note that flat Kalshi segments still mean 'no trade', not 'no change'.
   - Mixed coefficient signs across lags -- relationship not monotone.
   - Kalshi updates only on trades (flat line = no trade, NOT 'no change'); ETF mid refreshes continuously.

------------------------------------------------------------------------------------------------
Conventions: ET | 09:30-16:00 (forward windows capped to 16:00) | ETF in log return | median causal bars | full RTH grid | day-grouped lags (no overnight) | ADL self-control | significance = BH-FDR corrected.
Figures for this pair follow on the next page.