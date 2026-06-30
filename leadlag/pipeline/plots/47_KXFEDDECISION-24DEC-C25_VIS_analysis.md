PAIR ANALYSIS    —    Rank 2 / 48
================================================================================================
KXFEDDECISION-24DEC-C25   x   VIS
Contract : "Will the Federal Reserve Cut rates by 25bps at their December 2024 meeting?"
Sector relevance : VFH_VNQ_VPU (Rate-sensitive: Financials / Real Estate / Utilities)
Window : 2024-10-31 to 2024-12-18     Kalshi trades : 2260     primary bar : 5min     daily-screen R^2 : 0.15

>>> RELIABILITY:  Adequate   <<<   (see section 5; unreliable pairs still get figures, but read their problems in section 8)

DEFINITIONS
   xₜ₋ₖ = Kalshi yes-probability change, k bars before t   (1 bar = 5min)
   yₜ   = ETF log return over bar t
   calendar = full market-hours grid: x=0 in bars with no Kalshi trade (not dropped).
   k>0 => Kalshi leads ETF ;  k<0 => ETF leads Kalshi ;  k=0 => contemporaneous

1. CALENDAR-TIME REGRESSION (clock-time lags, full RTH grid)
   Full model:  yₜ = α + Σ(k=-8..8) βₖ·xₜ₋ₖ + φ₁·yₜ₋₁ + Σ(d=1..32) γ_d·Day_d
      where  ADL ETF self-lags p=1 (BIC-chosen): φ₁·yₜ₋₁;  day-FE: 32 day dummies over 33 trading days (first day = baseline).
      controls counted (so you can see the total at a glance):  17 lead/lag x-terms + 1 ETF self-lag(s) + 32 day-FE dummies + 1 intercept = 51 RHS regressors  (model n_params=51).
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₋₇·xₜ₊₇ + β₋₃·xₜ₊₃ + β₋₁·xₜ₊₁ + β₊₁·xₜ₋₁ + β₊₂·xₜ₋₂
   where:
      β₋₇ = +2.207e-05   (t/z=+1.63, p=1.0e-01, p_fdr=3.5e-01)    [ETF leads]
      β₋₃ = +1.797e-05   (t/z=+1.83, p=6.7e-02, p_fdr=3.5e-01)    [ETF leads]
      β₋₁ = -2.409e-05   (t/z=-2.43, p=1.5e-02, p_fdr=1.3e-01)    [ETF leads]
      β₊₁ = +1.333e-05   (t/z=+2.53, p=1.2e-02, p_fdr=1.3e-01)    [Kalshi leads]
      β₊₂ = +1.490e-05   (t/z=+1.68, p=9.3e-02, p_fdr=3.5e-01)    [Kalshi leads]
   Lean by count of significant lags: ETF-leads  (k>0:2, k<0:3).

2. EVENT-TIME REGRESSION (event-count lags)
   Full model:  yₜ = α + Σ(k=-8..8) βₖ·xₜ₋ₖ + Σ(d=1..22) γ_d·Day_d
      where  ADL ETF self-lags p=0 (BIC chose none -> no ETF self-lag term);  day-FE: 22 day dummies over 23 trading days (first day = baseline).
      controls counted (so you can see the total at a glance):  17 lead/lag x-terms + 0 ETF self-lag(s) + 22 day-FE dummies + 1 intercept = 40 RHS regressors  (model n_params=40).
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₊₇·xₜ₋₇
   where:
      β₊₇ = +4.455e-05   (t/z=+1.49, p=1.4e-01, p_fdr=7.3e-01)    [Kalshi leads]
   Lean by count of significant lags: Kalshi-leads  (k>0:1, k<0:0).

3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)
      k |       calendar b (FDR) |          event b (FDR)
   ------------------------------------------------------
     -8 |          -8.18e-06     |          -6.13e-05    
     -7 |          +2.21e-05     |          +1.64e-05    
     -6 |          +2.25e-06     |          +8.20e-05    
     -5 |          +1.40e-05     |          -2.91e-05    
     -4 |          +7.63e-06     |          -4.89e-05    
     -3 |          +1.80e-05     |          -1.20e-04    
     -2 |          -1.74e-06     |          -5.42e-05    
     -1 |          -2.41e-05     |          -4.99e-05    
     +0 |          +2.69e-06     |          +5.74e-05    
     +1 |          +1.33e-05     |          +5.70e-05    
     +2 |          +1.49e-05     |          +9.85e-06    
     +3 |          -1.63e-06     |          -1.41e-06    
     +4 |          +1.14e-06     |          -6.38e-05    
     +5 |          -6.16e-06     |          -4.68e-05    
     +6 |          -2.55e-07     |          -1.36e-05    
     +7 |          -5.19e-06     |          +4.45e-05    
     +8 |          +7.75e-06     |          -2.71e-05    
   (stars = BH-FDR corrected:  *** p_fdr<.01  ** <.05  * <.10)

4. DIRECTIONAL TEST (probit, ETF up/down)
   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k
   calendar: β₊₆=+5.90e-02
   event: β₋₉=+4.36e-02, β₊₂=-6.57e-02, β₊₇=+6.54e-02, β₊₁₀=+6.84e-02

5. DATA RELIABILITY (statistical, not a trade-count cutoff)
   Tier: Adequate
   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)
   calendar(full RTH grid): n_active=362  n_obs=1879  n_days=33  K=8  params=51  df=1828  median_SE=9.30e-06  sig(FDR)=0
   event: n_active=195  n_obs=326  n_days=23  K=8  params=40  df=286  median_SE=6.69e-05  sig(FDR)=0

6. COARSE-FREQUENCY ROBUSTNESS (re-run calendar at 30min / 60min)
    30min: n_obs=288 df=240 K=8  sig=0 (Kalshi-leads 0 / ETF-leads 0) -> No-sig
    60min: n_obs=159 df=115 K=6  sig=1 (Kalshi-leads 1 / ETF-leads 0) -> Kalshi-leads

7. VERDICT
   Calendar leans ETF-leads but Event leans Kalshi-leads -- NOT robust across time-axis; no clean lead.

8. FIGURE CAVEATS — figures are still drawn, but know their problems
   - Adequate info: figures and regression are mutually readable; note that flat Kalshi segments still mean 'no trade', not 'no change'.
   - Mixed coefficient signs across lags -- relationship not monotone.
   - Kalshi updates only on trades (flat line = no trade, NOT 'no change'); ETF mid refreshes continuously.

------------------------------------------------------------------------------------------------
Conventions: ET | 09:30-16:00 (forward windows capped to 16:00) | ETF in log return | median causal bars | full RTH grid | day-grouped lags (no overnight) | ADL self-control | significance = BH-FDR corrected.
Figures for this pair follow on the next page.