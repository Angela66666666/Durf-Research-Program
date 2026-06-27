PAIR ANALYSIS    —    Rank 24 / 48
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
   Full model: yₜ = α + Σₖ βₖ·xₜ₋ₖ + Σᵢ φᵢ·yₜ₋ᵢ (ADL self-control) + day-FE
   -> 13 coefficients tested, NONE significant after BH-FDR (p_fdr<0.05).

2. EVENT-TIME REGRESSION (event-count lags)
   Full model: yₜ = α + Σₖ βₖ·xₜ₋ₖ + Σᵢ φᵢ·yₜ₋ᵢ (ADL self-control) + day-FE
   -> no regression result (insufficient data).

3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)
      k |       calendar b (FDR) |          event b (FDR)
   ------------------------------------------------------
     -6 |          +9.02e-05     |                     --
     -5 |          +7.71e-05     |                     --
     -4 |          +1.68e-05     |                     --
     -3 |          +4.79e-05     |                     --
     -2 |          -1.31e-05     |                     --
     -1 |          +1.77e-05     |                     --
     +0 |          +3.10e-05     |                     --
     +1 |          -6.86e-05     |                     --
     +2 |          +3.79e-05     |                     --
     +3 |          -1.37e-05     |                     --
     +4 |          +5.51e-05     |                     --
     +5 |          -3.75e-05     |                     --
     +6 |          -1.07e-05     |                     --
   (stars = BH-FDR corrected:  *** p_fdr<.01  ** <.05  * <.10)

4. DIRECTIONAL TEST (probit, ETF up/down)
   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k
   calendar: 13 lags tested, none significant after BH-FDR.
   event: 17 lags tested, none significant after BH-FDR.
   -> no significant directional predictability either mode (BH-FDR).

5. DATA RELIABILITY (statistical, not a trade-count cutoff)
   Tier: Adequate
   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)
   calendar(full RTH grid): n_active=55  n_obs=488  n_days=31  K=6  params=49  df=439  median_SE=4.54e-05  sig(FDR)=0
   event: not estimable (insufficient data)

6. COARSE-FREQUENCY ROBUSTNESS (re-run calendar at 30min / 60min)
    30min: n_obs=99 df=57 K=6  sig=0 (Kalshi-leads 0 / ETF-leads 0) -> No-sig
    60min: n_obs=67 df=32 K=5  sig=0 (Kalshi-leads 0 / ETF-leads 0) -> No-sig

7. VERDICT
   No lead-lag detected -- too sparse / no significant structure.

8. FIGURE CAVEATS — figures are still drawn, but know their problems
   - Adequate info: figures and regression are mutually readable; note that flat Kalshi segments still mean 'no trade', not 'no change'.
   - Kalshi updates only on trades (flat line = no trade, NOT 'no change'); ETF mid refreshes continuously.

------------------------------------------------------------------------------------------------
Conventions: ET | 09:30-16:00 (forward windows capped to 16:00) | ETF in log return | median causal bars | full RTH grid | day-grouped lags (no overnight) | ADL self-control | significance = BH-FDR corrected.
Figures for this pair follow on the next page.