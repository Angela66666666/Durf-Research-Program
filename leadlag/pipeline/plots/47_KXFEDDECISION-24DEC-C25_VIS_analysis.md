PAIR ANALYSIS    —    Rank 1 / 48
================================================================================================
KXFEDDECISION-24DEC-C25   x   VIS
Contract : "Will the Federal Reserve Cut rates by 25bps at their December 2024 meeting?"
Sector relevance : VFH_VNQ_VPU (Rate-sensitive: Financials / Real Estate / Utilities)
Window : 2024-10-31 to 2024-12-18     Kalshi trades : 2308     primary bar : 5min     daily-screen R^2 : 0.15

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
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₋₁₀·xₜ₊₁₀ + β₋₉·xₜ₊₉ + β₋₇·xₜ₊₇ + β₋₅·xₜ₊₅ + β₋₁·xₜ₊₁ + β₊₁·xₜ₋₁ + β₊₉·xₜ₋₉
   where:
      β₋₁₀ = +3.089e-05   (t/z=+3.12, p=1.8e-03, p_fdr=3.7e-02) **   [ETF leads]
      β₋₉ = +2.488e-05   (t/z=+2.27, p=2.3e-02, p_fdr=9.8e-02) *   [ETF leads]
      β₋₇ = +3.570e-05   (t/z=+2.78, p=5.5e-03, p_fdr=3.8e-02) **   [ETF leads]
      β₋₅ = +2.434e-05   (t/z=+2.68, p=7.4e-03, p_fdr=3.9e-02) **   [ETF leads]
      β₋₁ = -2.509e-05   (t/z=-2.02, p=4.3e-02, p_fdr=1.5e-01)    [ETF leads]
      β₊₁ = +2.149e-05   (t/z=+2.85, p=4.4e-03, p_fdr=3.8e-02) **   [Kalshi leads]
      β₊₉ = -1.533e-05   (t/z=-1.53, p=1.3e-01, p_fdr=3.8e-01)    [Kalshi leads]
   Lean by count of significant lags: ETF-leads  (k>0:2, k<0:5).

2. EVENT-TIME REGRESSION (event-count lags)
   Full model:  yₜ = α + Σ(k=-10..10) βₖ·xₜ₋ₖ + Σ(d=1..18) γ_d·Day_d
      where  ADL ETF self-lags p=0 (BIC chose none -> no ETF self-lag term);  day-FE: 18 day dummies over 19 trading days (first day = baseline).
      controls counted (so you can see the total at a glance):  21 lead/lag x-terms + 0 ETF self-lag(s) + 18 day-FE dummies + 1 intercept = 40 RHS regressors  (model n_params=40).
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₋₁₀·xₜ₊₁₀ + β₋₉·xₜ₊₉ + β₋₆·xₜ₊₆ + β₋₃·xₜ₊₃ + β₋₁·xₜ₊₁ + β₊₅·xₜ₋₅ + β₊₇·xₜ₋₇
   where:
      β₋₁₀ = -9.809e-05   (t/z=-1.48, p=1.4e-01, p_fdr=4.2e-01)    [ETF leads]
      β₋₉ = -7.580e-05   (t/z=-1.83, p=6.8e-02, p_fdr=4.2e-01)    [ETF leads]
      β₋₆ = +1.247e-04   (t/z=+1.70, p=8.9e-02, p_fdr=4.2e-01)    [ETF leads]
      β₋₃ = -2.267e-04   (t/z=-1.62, p=1.0e-01, p_fdr=4.2e-01)    [ETF leads]
      β₋₁ = -1.050e-04   (t/z=-1.74, p=8.2e-02, p_fdr=4.2e-01)    [ETF leads]
      β₊₅ = -1.163e-04   (t/z=-3.12, p=1.8e-03, p_fdr=3.8e-02) **   [Kalshi leads]
      β₊₇ = +6.567e-05   (t/z=+1.51, p=1.3e-01, p_fdr=4.2e-01)    [Kalshi leads]
   Lean by count of significant lags: ETF-leads  (k>0:2, k<0:5).

3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)
      k |       calendar b (FDR) |          event b (FDR)
   ------------------------------------------------------
    -10 |          +3.09e-05 **  |          -9.81e-05    
     -9 |          +2.49e-05 *   |          -7.58e-05    
     -8 |          -8.91e-06     |          -8.81e-05    
     -7 |          +3.57e-05 **  |          +1.10e-04    
     -6 |          +4.89e-06     |          +1.25e-04    
     -5 |          +2.43e-05 **  |          +9.28e-08    
     -4 |          +1.57e-05     |          -8.55e-05    
     -3 |          +1.46e-05     |          -2.27e-04    
     -2 |          -7.53e-06     |          -7.10e-05    
     -1 |          -2.51e-05     |          -1.05e-04    
     +0 |          -1.13e-08     |          -1.60e-06    
     +1 |          +2.15e-05 **  |          +9.09e-05    
     +2 |          +6.32e-06     |          +8.54e-05    
     +3 |          +9.31e-07     |          +1.05e-04    
     +4 |          +3.77e-06     |          -7.36e-06    
     +5 |          -3.08e-06     |          -1.16e-04 ** 
     +6 |          +1.30e-06     |          -5.56e-05    
     +7 |          -3.96e-06     |          +6.57e-05    
     +8 |          +6.20e-07     |          -1.92e-06    
     +9 |          -1.53e-05     |          +1.30e-05    
    +10 |          -7.06e-06     |          +9.79e-06    
   (stars = BH-FDR corrected:  *** p_fdr<.01  ** <.05  * <.10)

4. DIRECTIONAL TEST (probit, ETF up/down)
   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k
   calendar: β₋₇=-8.06e-02, β₊₄=+5.76e-02, β₊₈=-5.54e-02, β₊₁₀=-5.04e-02
   event: β₋₈=-9.36e-02*, β₋₃=+6.89e-02, β₋₂=-5.58e-02, β₊₇=+1.00e-01*, β₊₈=-6.27e-02, β₊₁₀=-6.01e-02

5. DATA RELIABILITY (statistical, not a trade-count cutoff)
   Tier: Adequate
   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)
   calendar(full RTH grid): n_active=344  n_obs=1807  n_days=33  K=10  params=55  df=1752  median_SE=1.00e-05  sig(FDR)=4
   event: n_active=148  n_obs=253  n_days=19  K=10  params=40  df=213  median_SE=8.12e-05  sig(FDR)=1

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