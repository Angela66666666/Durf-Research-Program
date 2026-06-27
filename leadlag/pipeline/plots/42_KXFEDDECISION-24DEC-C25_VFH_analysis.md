PAIR ANALYSIS    —    Rank 22 / 48
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
   Full model: yₜ = α + Σₖ βₖ·xₜ₋ₖ + Σᵢ φᵢ·yₜ₋ᵢ (ADL self-control) + day-FE
   -> 17 coefficients tested, NONE significant after BH-FDR (p_fdr<0.05).

2. EVENT-TIME REGRESSION (event-count lags)
   Full model: yₜ = α + Σₖ βₖ·xₜ₋ₖ + Σᵢ φᵢ·yₜ₋ᵢ (ADL self-control) + day-FE
   -> 21 coefficients tested, NONE significant after BH-FDR (p_fdr<0.05).

3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)
      k |       calendar b (FDR) |          event b (FDR)
   ------------------------------------------------------
    -10 |                     -- |          +2.07e-05    
     -9 |                     -- |          +4.83e-05    
     -8 |          +9.54e-06     |          +4.56e-05    
     -7 |          +3.52e-05     |          +8.45e-06    
     -6 |          +9.16e-06     |          +2.27e-05    
     -5 |          +1.42e-05     |          -9.26e-06    
     -4 |          -6.13e-06     |          -9.29e-06    
     -3 |          +1.59e-05     |          -9.32e-06    
     -2 |          -2.17e-05     |          +5.35e-06    
     -1 |          -1.68e-05     |          +2.67e-05    
     +0 |          +1.14e-05     |          +2.78e-05    
     +1 |          +2.51e-05     |          +2.40e-05    
     +2 |          -4.16e-06     |          +3.56e-05    
     +3 |          -2.21e-07     |          +4.22e-05    
     +4 |          +5.25e-06     |          +4.34e-05    
     +5 |          +7.40e-06     |          -1.42e-05    
     +6 |          -1.11e-05     |          -1.24e-05    
     +7 |          -1.91e-05     |          -7.64e-06    
     +8 |          -7.19e-07     |          -1.49e-06    
     +9 |                     -- |          +1.58e-05    
    +10 |                     -- |          +1.31e-05    
   (stars = BH-FDR corrected:  *** p_fdr<.01  ** <.05  * <.10)

4. DIRECTIONAL TEST (probit, ETF up/down)
   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k
   calendar: 21 lags tested, none significant after BH-FDR.
   event: 21 lags tested, none significant after BH-FDR.
   -> no significant directional predictability either mode (BH-FDR).

5. DATA RELIABILITY (statistical, not a trade-count cutoff)
   Tier: Adequate
   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)
   calendar(full RTH grid): n_active=362  n_obs=1879  n_days=33  K=8  params=55  df=1824  median_SE=1.14e-05  sig(FDR)=0
   event: n_active=323  n_obs=597  n_days=23  K=10  params=49  df=548  median_SE=2.78e-05  sig(FDR)=0

6. COARSE-FREQUENCY ROBUSTNESS (re-run calendar at 30min / 60min)
    30min: n_obs=288 df=240 K=8  sig=0 (Kalshi-leads 0 / ETF-leads 0) -> No-sig
    60min: n_obs=159 df=115 K=6  sig=0 (Kalshi-leads 0 / ETF-leads 0) -> No-sig

7. VERDICT
   No lead-lag detected -- too sparse / no significant structure.

8. FIGURE CAVEATS — figures are still drawn, but know their problems
   - Adequate info: figures and regression are mutually readable; note that flat Kalshi segments still mean 'no trade', not 'no change'.
   - Kalshi updates only on trades (flat line = no trade, NOT 'no change'); ETF mid refreshes continuously.

------------------------------------------------------------------------------------------------
Conventions: ET | 09:30-16:00 (forward windows capped to 16:00) | ETF in log return | median causal bars | full RTH grid | day-grouped lags (no overnight) | ADL self-control | significance = BH-FDR corrected.
Figures for this pair follow on the next page.