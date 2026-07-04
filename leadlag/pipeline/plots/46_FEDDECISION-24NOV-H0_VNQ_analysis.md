PAIR ANALYSIS    —    Rank 7 / 48
================================================================================================
FEDDECISION-24NOV-H0   x   VNQ
Contract : "Will the Federal Reserve Hike rates by 0bps at their November 2024 meeting?"
Sector relevance : VFH_VNQ_VPU (Rate-sensitive: Financials / Real Estate / Utilities)
Window : 2024-09-18 to 2024-11-07     Kalshi trades : 452     primary bar : 10min     daily-screen R^2 : 0.17

>>> RELIABILITY:  Adequate   <<<   (see section 5; unreliable pairs still get figures, but read their problems in section 8)

DEFINITIONS
   xₜ₋ₖ = Kalshi yes-probability change, k bars before t   (1 bar = 10min)
   yₜ   = ETF log return over bar t
   calendar = full market-hours grid: x=0 in bars with no Kalshi trade (not dropped).
   k>0 => Kalshi leads ETF ;  k<0 => ETF leads Kalshi ;  k=0 => contemporaneous

1. CALENDAR-TIME REGRESSION (clock-time lags, full RTH grid)
   Full model:  yₜ = α + Σ(k=-6..6) βₖ·xₜ₋ₖ + φ₁·yₜ₋₁ + Σ(d=1..35) γ_d·Day_d
      where  ADL ETF self-lags p=1 (BIC-chosen): φ₁·yₜ₋₁;  day-FE: 35 day dummies over 36 trading days (first day = baseline).
      controls counted (so you can see the total at a glance):  13 lead/lag x-terms + 1 ETF self-lag(s) + 35 day-FE dummies + 1 intercept = 50 RHS regressors  (model n_params=50).
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₋₁·xₜ₊₁ + β₊₄·xₜ₋₄ + β₊₅·xₜ₋₅
   where:
      β₋₁ = -1.035e-04   (t/z=-2.23, p=2.5e-02, p_fdr=3.3e-01)    [ETF leads]
      β₊₄ = +3.620e-05   (t/z=+1.88, p=5.9e-02, p_fdr=3.8e-01)    [Kalshi leads]
      β₊₅ = +3.914e-05   (t/z=+1.71, p=8.8e-02, p_fdr=3.8e-01)    [Kalshi leads]
   Lean by count of significant lags: Kalshi-leads  (k>0:2, k<0:1).

2. EVENT-TIME REGRESSION (event-count lags)
   Full model:  yₜ = α + Σ(k) βₖ·xₜ₋ₖ + (ADL self-lags) + (day fixed effects)
   -> no regression result (insufficient data).

3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)
      k |       calendar b (FDR) |          event b (FDR)
   ------------------------------------------------------
     -6 |          -2.42e-05     |                     --
     -5 |          -7.56e-06     |                     --
     -4 |          -4.94e-06     |                     --
     -3 |          +2.40e-06     |                     --
     -2 |          +5.00e-05     |                     --
     -1 |          -1.04e-04     |                     --
     +0 |          -1.10e-05     |                     --
     +1 |          +5.39e-06     |                     --
     +2 |          +8.11e-06     |                     --
     +3 |          +2.10e-05     |                     --
     +4 |          +3.62e-05     |                     --
     +5 |          +3.91e-05     |                     --
     +6 |          +2.75e-06     |                     --
   (stars = BH-FDR corrected:  *** p_fdr<.01  ** <.05  * <.10)

4. DIRECTIONAL TEST (probit, ETF up/down)
   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k
   calendar: β₋₆=+1.68e-01
   event: β₋₆=+2.76e-01, β₋₃=-1.38e-01, β₊₃=+1.21e-01

5. DATA RELIABILITY (statistical, not a trade-count cutoff)
   Tier: Adequate
   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)
   calendar(full RTH grid): n_active=74  n_obs=685  n_days=36  K=6  params=50  df=635  median_SE=2.89e-05  sig(FDR)=0
   event: not estimable (insufficient data)

6. COARSE-FREQUENCY ROBUSTNESS (re-run calendar at 30min / 60min)
    30min: n_obs=121 df=76 K=6  sig=3 (Kalshi-leads 2 / ETF-leads 1) -> Kalshi-leads
    60min: n_obs=87 df=45 K=5  sig=1 (Kalshi-leads 0 / ETF-leads 1) -> ETF-leads

7. VERDICT
   Only one time-axis significant (Kalshi-leads) -- weak / single-mode evidence.

8. FIGURE CAVEATS — figures are still drawn, but know their problems
   - Adequate info: figures and regression are mutually readable; note that flat Kalshi segments still mean 'no trade', not 'no change'.
   - Mixed coefficient signs across lags -- relationship not monotone.
   - Kalshi updates only on trades (flat line = no trade, NOT 'no change'); ETF mid refreshes continuously.

------------------------------------------------------------------------------------------------
Conventions: ET | 09:30-16:00 (forward windows capped to 16:00) | ETF in log return | median causal bars | full RTH grid | day-grouped lags (no overnight) | ADL self-control | significance = BH-FDR corrected.
Figures for this pair follow on the next page.