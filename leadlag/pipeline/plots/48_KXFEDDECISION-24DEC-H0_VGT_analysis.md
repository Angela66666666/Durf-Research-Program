PAIR ANALYSIS    —    Rank 14 / 48
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
   Full model: yₜ = α + Σₖ βₖ·xₜ₋ₖ + Σᵢ φᵢ·yₜ₋ᵢ (ADL self-control) + day-FE
   -> 17 coefficients tested, NONE significant after BH-FDR (p_fdr<0.05).

2. EVENT-TIME REGRESSION (event-count lags)
   Full model: yₜ = α + Σₖ βₖ·xₜ₋ₖ + Σᵢ φᵢ·yₜ₋ᵢ (ADL self-control) + day-FE
   Significant terms (BH-FDR) expanded:  yₜ = α + β₋₇·xₜ₊₇ + β₊₃·xₜ₋₃
   where:
      β₋₇ = -1.588e-04   (t/z=-3.97, p=7.1e-05, p_fdr=1.5e-03) ***   [ETF leads]
      β₊₃ = -1.073e-04   (t/z=-3.32, p=8.9e-04, p_fdr=9.4e-03) ***   [Kalshi leads]
   Lean by count of significant lags: balanced/no clear side  (k>0:1, k<0:1).

3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)
      k |       calendar b (FDR) |          event b (FDR)
   ------------------------------------------------------
    -10 |                     -- |          -2.69e-06    
     -9 |                     -- |          -8.69e-05    
     -8 |          +2.56e-05     |          -4.58e-05    
     -7 |          +1.45e-05     |          -1.59e-04 ***
     -6 |          +2.65e-05     |          -8.40e-05    
     -5 |          +2.69e-05     |          -6.79e-05    
     -4 |          +1.51e-05     |          -1.21e-05    
     -3 |          -4.70e-06     |          -1.19e-05    
     -2 |          +5.27e-06     |          +1.66e-05    
     -1 |          -1.46e-05     |          -6.02e-05    
     +0 |          +2.15e-05     |          -5.24e-05    
     +1 |          +2.56e-05     |          -5.59e-05    
     +2 |          +3.52e-05     |          -1.12e-05    
     +3 |          -3.22e-05     |          -1.07e-04 ***
     +4 |          +2.96e-05     |          -3.14e-05    
     +5 |          +3.76e-05     |          +2.43e-05    
     +6 |          -4.68e-06     |          -4.96e-05    
     +7 |          +1.43e-05     |          +3.65e-05    
     +8 |          +3.78e-05     |          +6.13e-05    
     +9 |                     -- |          -1.32e-05    
    +10 |                     -- |          -9.09e-06    
   (stars = BH-FDR corrected:  *** p_fdr<.01  ** <.05  * <.10)

4. DIRECTIONAL TEST (probit, ETF up/down)
   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k
   calendar: 17 lags tested, none significant after BH-FDR.
   event: β₊₃=-1.11e-01***

5. DATA RELIABILITY (statistical, not a trade-count cutoff)
   Tier: Adequate
   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)
   calendar(full RTH grid): n_active=126  n_obs=586  n_days=31  K=8  params=53  df=533  median_SE=3.26e-05  sig(FDR)=0
   event: n_active=108  n_obs=205  n_days=11  K=10  params=37  df=168  median_SE=4.58e-05  sig(FDR)=2

6. COARSE-FREQUENCY ROBUSTNESS (re-run calendar at 30min / 60min)
    30min: n_obs=210 df=164 K=8  sig=0 (Kalshi-leads 0 / ETF-leads 0) -> No-sig
    60min: n_obs=131 df=88 K=6  sig=1 (Kalshi-leads 1 / ETF-leads 0) -> Kalshi-leads

7. VERDICT
   Only one time-axis significant (balanced) -- weak / single-mode evidence.

8. FIGURE CAVEATS — figures are still drawn, but know their problems
   - Adequate info: figures and regression are mutually readable; note that flat Kalshi segments still mean 'no trade', not 'no change'.
   - Kalshi updates only on trades (flat line = no trade, NOT 'no change'); ETF mid refreshes continuously.

------------------------------------------------------------------------------------------------
Conventions: ET | 09:30-16:00 (forward windows capped to 16:00) | ETF in log return | median causal bars | full RTH grid | day-grouped lags (no overnight) | ADL self-control | significance = BH-FDR corrected.
Figures for this pair follow on the next page.