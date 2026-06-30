PAIR ANALYSIS    —    Rank 1 / 48
================================================================================================
KXFEDDECISION-24DEC-C25   x   VFH
Contract : "Will the Federal Reserve Cut rates by 25bps at their December 2024 meeting?"
Sector relevance : VFH_VNQ_VPU (Rate-sensitive: Financials / Real Estate / Utilities)
Window : 2024-10-31 to 2024-12-18     Kalshi trades : 2260     primary bar : 5min     daily-screen R^2 : 0.27

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
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₋₇·xₜ₊₇ + β₋₂·xₜ₊₂ + β₋₁·xₜ₊₁ + β₊₁·xₜ₋₁ + β₊₆·xₜ₋₆ + β₊₇·xₜ₋₇
   where:
      β₋₇ = +3.514e-05   (t/z=+2.30, p=2.2e-02, p_fdr=2.7e-01)    [ETF leads]
      β₋₂ = -2.330e-05   (t/z=-1.53, p=1.3e-01, p_fdr=3.5e-01)    [ETF leads]
      β₋₁ = -1.778e-05   (t/z=-1.58, p=1.1e-01, p_fdr=3.5e-01)    [ETF leads]
      β₊₁ = +2.472e-05   (t/z=+1.93, p=5.4e-02, p_fdr=2.7e-01)    [Kalshi leads]
      β₊₆ = -1.298e-05   (t/z=-1.86, p=6.3e-02, p_fdr=2.7e-01)    [Kalshi leads]
      β₊₇ = -1.992e-05   (t/z=-1.87, p=6.1e-02, p_fdr=2.7e-01)    [Kalshi leads]
   Lean by count of significant lags: balanced/no clear side  (k>0:3, k<0:3).

2. EVENT-TIME REGRESSION (event-count lags)
   Full model:  yₜ = α + Σ(k=-8..8) βₖ·xₜ₋ₖ + Σ(d=1..22) γ_d·Day_d
      where  ADL ETF self-lags p=0 (BIC chose none -> no ETF self-lag term);  day-FE: 22 day dummies over 23 trading days (first day = baseline).
      controls counted (so you can see the total at a glance):  17 lead/lag x-terms + 0 ETF self-lag(s) + 22 day-FE dummies + 1 intercept = 40 RHS regressors  (model n_params=40).
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₊₁·xₜ₋₁ + β₊₅·xₜ₋₅ + β₊₈·xₜ₋₈
   where:
      β₊₁ = +1.366e-04   (t/z=+2.40, p=1.7e-02, p_fdr=2.8e-01)    [Kalshi leads]
      β₊₅ = -6.918e-05   (t/z=-1.55, p=1.2e-01, p_fdr=6.4e-01)    [Kalshi leads]
      β₊₈ = -6.115e-05   (t/z=-1.44, p=1.5e-01, p_fdr=6.4e-01)    [Kalshi leads]
   Lean by count of significant lags: Kalshi-leads  (k>0:3, k<0:0).

3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)
      k |       calendar b (FDR) |          event b (FDR)
   ------------------------------------------------------
     -8 |          +9.23e-06     |          -4.60e-05    
     -7 |          +3.51e-05     |          +8.86e-05    
     -6 |          +8.93e-06     |          +8.79e-05    
     -5 |          +1.40e-05     |          +6.95e-05    
     -4 |          -7.29e-06     |          +2.92e-05    
     -3 |          +1.45e-05     |          -8.39e-05    
     -2 |          -2.33e-05     |          -9.29e-05    
     -1 |          -1.78e-05     |          -1.02e-04    
     +0 |          +9.44e-06     |          +7.26e-05    
     +1 |          +2.47e-05     |          +1.37e-04    
     +2 |          -3.08e-06     |          +6.27e-07    
     +3 |          +9.36e-08     |          +3.92e-05    
     +4 |          +3.79e-06     |          -2.86e-05    
     +5 |          +5.27e-06     |          -6.92e-05    
     +6 |          -1.30e-05     |          -3.46e-05    
     +7 |          -1.99e-05     |          +2.38e-05    
     +8 |          -1.35e-06     |          -6.12e-05    
   (stars = BH-FDR corrected:  *** p_fdr<.01  ** <.05  * <.10)

4. DIRECTIONAL TEST (probit, ETF up/down)
   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k
   calendar: β₋₁₀=+1.08e-01, β₊₀=+4.17e-02
   event: β₋₁₀=+6.88e-02, β₋₆=+8.12e-02, β₋₄=-7.18e-02, β₋₃=+9.38e-02, β₋₂=-8.53e-02, β₊₅=-1.21e-01***

5. DATA RELIABILITY (statistical, not a trade-count cutoff)
   Tier: Adequate
   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)
   calendar(full RTH grid): n_active=362  n_obs=1879  n_days=33  K=8  params=51  df=1828  median_SE=1.19e-05  sig(FDR)=0
   event: n_active=195  n_obs=326  n_days=23  K=8  params=40  df=286  median_SE=7.86e-05  sig(FDR)=0

6. COARSE-FREQUENCY ROBUSTNESS (re-run calendar at 30min / 60min)
    30min: n_obs=288 df=240 K=8  sig=0 (Kalshi-leads 0 / ETF-leads 0) -> No-sig
    60min: n_obs=159 df=115 K=6  sig=0 (Kalshi-leads 0 / ETF-leads 0) -> No-sig

7. VERDICT
   Calendar leans balanced but Event leans Kalshi-leads -- NOT robust across time-axis; no clean lead.

8. FIGURE CAVEATS — figures are still drawn, but know their problems
   - Adequate info: figures and regression are mutually readable; note that flat Kalshi segments still mean 'no trade', not 'no change'.
   - Mixed coefficient signs across lags -- relationship not monotone.
   - Kalshi updates only on trades (flat line = no trade, NOT 'no change'); ETF mid refreshes continuously.

------------------------------------------------------------------------------------------------
Conventions: ET | 09:30-16:00 (forward windows capped to 16:00) | ETF in log return | median causal bars | full RTH grid | day-grouped lags (no overnight) | ADL self-control | significance = BH-FDR corrected.
Figures for this pair follow on the next page.