PAIR ANALYSIS    —    Rank 2 / 48
================================================================================================
KXFEDDECISION-24DEC-C25   x   VFH
Contract : "Will the Federal Reserve Cut rates by 25bps at their December 2024 meeting?"
Sector relevance : VFH_VNQ_VPU (Rate-sensitive: Financials / Real Estate / Utilities)
Window : 2024-10-31 to 2024-12-18     Kalshi trades : 2308     primary bar : 5min     daily-screen R^2 : 0.27

>>> RELIABILITY:  Adequate   <<<   (see section 5; unreliable pairs still get figures, but read their problems in section 8)

DEFINITIONS
   xₜ₋ₖ = Kalshi yes-probability change, k bars before t   (1 bar = 5min)
   yₜ   = ETF log return over bar t
   calendar = full market-hours grid: x=0 in bars with no Kalshi trade (not dropped).
   k>0 => Kalshi leads ETF ;  k<0 => ETF leads Kalshi ;  k=0 => contemporaneous

1. CALENDAR-TIME REGRESSION (clock-time lags, full RTH grid)
   Full model:  yₜ = α + Σ(k=-10..10) βₖ·xₜ₋ₖ + φ₁·yₜ₋₁ + Σ(d=1..32) γ_d·Day_d
      where  ADL ETF self-lags p=1 (BIC-chosen): φ₁·yₜ₋₁;  day-FE: 32 day dummies over 33 trading days (first day = baseline).
      controls counted (so you can see the total at a glance):  21 lead/lag x-terms + 1 ETF self-lag(s) + 32 day-FE dummies + 1 intercept = 55 RHS regressors  (model n_params=55).
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₋₇·xₜ₊₇ + β₋₂·xₜ₊₂ + β₋₁·xₜ₊₁ + β₊₁·xₜ₋₁
   where:
      β₋₇ = +3.363e-05   (t/z=+2.33, p=2.0e-02, p_fdr=4.2e-01)    [ETF leads]
      β₋₂ = -2.566e-05   (t/z=-1.90, p=5.8e-02, p_fdr=5.5e-01)    [ETF leads]
      β₋₁ = -1.555e-05   (t/z=-1.69, p=9.1e-02, p_fdr=5.5e-01)    [ETF leads]
      β₊₁ = +2.374e-05   (t/z=+1.63, p=1.0e-01, p_fdr=5.5e-01)    [Kalshi leads]
   Lean by count of significant lags: ETF-leads  (k>0:1, k<0:3).

2. EVENT-TIME REGRESSION (event-count lags)
   Full model:  yₜ = α + Σ(k=-10..10) βₖ·xₜ₋ₖ + Σ(d=1..18) γ_d·Day_d
      where  ADL ETF self-lags p=0 (BIC chose none -> no ETF self-lag term);  day-FE: 18 day dummies over 19 trading days (first day = baseline).
      controls counted (so you can see the total at a glance):  21 lead/lag x-terms + 0 ETF self-lag(s) + 18 day-FE dummies + 1 intercept = 40 RHS regressors  (model n_params=40).
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₋₇·xₜ₊₇ + β₋₆·xₜ₊₆ + β₋₁·xₜ₊₁ + β₊₁·xₜ₋₁ + β₊₅·xₜ₋₅
   where:
      β₋₇ = +1.758e-04   (t/z=+1.46, p=1.4e-01, p_fdr=6.1e-01)    [ETF leads]
      β₋₆ = +1.388e-04   (t/z=+1.62, p=1.0e-01, p_fdr=6.1e-01)    [ETF leads]
      β₋₁ = -1.134e-04   (t/z=-1.46, p=1.4e-01, p_fdr=6.1e-01)    [ETF leads]
      β₊₁ = +1.979e-04   (t/z=+3.04, p=2.3e-03, p_fdr=4.9e-02) **   [Kalshi leads]
      β₊₅ = -5.949e-05   (t/z=-1.78, p=7.5e-02, p_fdr=6.1e-01)    [Kalshi leads]
   Lean by count of significant lags: ETF-leads  (k>0:2, k<0:3).

3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)
      k |       calendar b (FDR) |          event b (FDR)
   ------------------------------------------------------
    -10 |          +1.51e-06     |          +4.65e-05    
     -9 |          +1.52e-06     |          +1.10e-05    
     -8 |          -1.06e-05     |          -3.74e-05    
     -7 |          +3.36e-05     |          +1.76e-04    
     -6 |          +1.18e-06     |          +1.39e-04    
     -5 |          +1.26e-05     |          +9.93e-05    
     -4 |          -3.28e-06     |          +2.76e-05    
     -3 |          +1.20e-05     |          -8.45e-05    
     -2 |          -2.57e-05     |          -5.92e-05    
     -1 |          -1.56e-05     |          -1.13e-04    
     +0 |          +9.74e-06     |          +6.98e-05    
     +1 |          +2.37e-05     |          +1.98e-04 ** 
     +2 |          -1.23e-05     |          +7.52e-05    
     +3 |          -2.94e-06     |          +9.16e-05    
     +4 |          -1.44e-06     |          +1.71e-06    
     +5 |          +7.93e-06     |          -5.95e-05    
     +6 |          -6.51e-06     |          -6.02e-06    
     +7 |          -1.22e-05     |          +4.19e-05    
     +8 |          -8.37e-09     |          -6.23e-05    
     +9 |          -1.89e-06     |          -3.91e-06    
    +10 |          -1.21e-05     |          +1.92e-05    
   (stars = BH-FDR corrected:  *** p_fdr<.01  ** <.05  * <.10)

4. DIRECTIONAL TEST (probit, ETF up/down)
   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k
   calendar: β₋₆=+7.34e-02**, β₊₄=+8.58e-02, β₊₅=-1.08e-01**, β₊₆=+5.86e-02**
   event: β₋₅=-1.08e-01*, β₋₃=+1.43e-01***, β₋₂=-1.05e-01*, β₊₀=+6.82e-02, β₊₂=-1.24e-01*, β₊₃=+1.13e-01, β₊₅=-1.02e-01***, β₊₆=-4.01e-02*, β₊₇=+7.45e-02***

5. DATA RELIABILITY (statistical, not a trade-count cutoff)
   Tier: Adequate
   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)
   calendar(full RTH grid): n_active=344  n_obs=1807  n_days=33  K=10  params=55  df=1752  median_SE=1.31e-05  sig(FDR)=0
   event: n_active=148  n_obs=253  n_days=19  K=10  params=40  df=213  median_SE=8.36e-05  sig(FDR)=1

6. COARSE-FREQUENCY ROBUSTNESS (re-run calendar at 30min / 60min)
    30min: n_obs=293 df=245 K=8  sig=0 (Kalshi-leads 0 / ETF-leads 0) -> No-sig
    60min: n_obs=164 df=120 K=6  sig=0 (Kalshi-leads 0 / ETF-leads 0) -> No-sig

7. VERDICT
   Both time-axes lean ETF-leads (relatively robust; see strongest single term).

8. FIGURE CAVEATS — figures are still drawn, but know their problems
   - Adequate info: figures and regression are mutually readable; note that flat Kalshi segments still mean 'no trade', not 'no change'.
   - Mixed coefficient signs across lags -- relationship not monotone.
   - Kalshi updates only on trades (flat line = no trade, NOT 'no change'); ETF mid refreshes continuously.

------------------------------------------------------------------------------------------------
Conventions: ET | 09:30-16:00 (forward windows capped to 16:00) | ETF in log return | median causal bars | full RTH grid | day-grouped lags (no overnight) | ADL self-control | significance = BH-FDR corrected.
Figures for this pair follow on the next page.