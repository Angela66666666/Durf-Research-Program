PAIR ANALYSIS    —    Rank 8 / 48
================================================================================================
FEDDECISION-24NOV-H0   x   VDE
Contract : "Will the Federal Reserve Hike rates by 0bps at their November 2024 meeting?"
Sector relevance : VFH_VNQ_VPU (Rate-sensitive: Financials / Real Estate / Utilities)
Window : 2024-09-18 to 2024-11-07     Kalshi trades : 401     primary bar : 10min     daily-screen R^2 : 0.19

>>> RELIABILITY:  Adequate   <<<   (see section 5; unreliable pairs still get figures, but read their problems in section 8)

DEFINITIONS
   xₜ₋ₖ = Kalshi yes-probability change, k bars before t   (1 bar = 10min)
   yₜ   = ETF log return over bar t
   calendar = full market-hours grid: x=0 in bars with no Kalshi trade (not dropped).
   k>0 => Kalshi leads ETF ;  k<0 => ETF leads Kalshi ;  k=0 => contemporaneous

1. CALENDAR-TIME REGRESSION (clock-time lags, full RTH grid)
   Full model:  yₜ = α + Σ(k=-6..6) βₖ·xₜ₋ₖ + φ₁·yₜ₋₁ + Σ(d=1..30) γ_d·Day_d
      where  ADL ETF self-lags p=1 (BIC-chosen): φ₁·yₜ₋₁;  day-FE: 30 day dummies over 31 trading days (first day = baseline).
      controls counted (so you can see the total at a glance):  13 lead/lag x-terms + 1 ETF self-lag(s) + 30 day-FE dummies + 1 intercept = 45 RHS regressors  (model n_params=45).
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₋₅·xₜ₊₅ + β₊₁·xₜ₋₁
   where:
      β₋₅ = +6.779e-05   (t/z=+1.93, p=5.4e-02, p_fdr=6.6e-01)    [ETF leads]
      β₊₁ = -7.736e-05   (t/z=-1.64, p=1.0e-01, p_fdr=6.6e-01)    [Kalshi leads]
   Lean by count of significant lags: balanced/no clear side  (k>0:1, k<0:1).

2. EVENT-TIME REGRESSION (event-count lags)
   Full model:  yₜ = α + Σ(k) βₖ·xₜ₋ₖ + (ADL self-lags) + (day fixed effects)
   -> no regression result (insufficient data).

3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)
      k |       calendar b (FDR) |          event b (FDR)
   ------------------------------------------------------
     -6 |          +9.01e-05     |                     --
     -5 |          +6.78e-05     |                     --
     -4 |          +8.00e-06     |                     --
     -3 |          +3.79e-05     |                     --
     -2 |          -2.55e-05     |                     --
     -1 |          +1.07e-05     |                     --
     +0 |          +2.26e-05     |                     --
     +1 |          -7.74e-05     |                     --
     +2 |          +3.80e-05     |                     --
     +3 |          -1.59e-05     |                     --
     +4 |          +5.41e-05     |                     --
     +5 |          -3.60e-05     |                     --
     +6 |          -1.10e-05     |                     --
   (stars = BH-FDR corrected:  *** p_fdr<.01  ** <.05  * <.10)

4. DIRECTIONAL TEST (probit, ETF up/down)
   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k
   calendar: β₋₆=-2.08e-01*, β₋₁=-2.31e-01*, β₊₁=-1.46e-01
   event: β₋₆=-1.73e-01, β₊₆=+1.57e-01

5. DATA RELIABILITY (statistical, not a trade-count cutoff)
   Tier: Adequate
   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)
   calendar(full RTH grid): n_active=55  n_obs=488  n_days=31  K=6  params=45  df=443  median_SE=4.73e-05  sig(FDR)=0
   event: not estimable (insufficient data)

6. COARSE-FREQUENCY ROBUSTNESS (re-run calendar at 30min / 60min)
    30min: n_obs=99 df=57 K=6  sig=0 (Kalshi-leads 0 / ETF-leads 0) -> No-sig
    60min: n_obs=67 df=32 K=5  sig=0 (Kalshi-leads 0 / ETF-leads 0) -> No-sig

7. VERDICT
   Only one time-axis significant (balanced) -- weak / single-mode evidence.

8. FIGURE CAVEATS — figures are still drawn, but know their problems
   - Adequate info: figures and regression are mutually readable; note that flat Kalshi segments still mean 'no trade', not 'no change'.
   - Mixed coefficient signs across lags -- relationship not monotone.
   - Kalshi updates only on trades (flat line = no trade, NOT 'no change'); ETF mid refreshes continuously.

------------------------------------------------------------------------------------------------
Conventions: ET | 09:30-16:00 (forward windows capped to 16:00) | ETF in log return | median causal bars | full RTH grid | day-grouped lags (no overnight) | ADL self-control | significance = BH-FDR corrected.
Figures for this pair follow on the next page.