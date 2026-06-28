PAIR ANALYSIS    —    Rank 17 / 48
================================================================================================
FEDDECISION-24SEP-C25   x   VPU
Contract : "Will the Federal Reserve Cut rates by 25bps at their September 2024 meeting?"
Sector relevance : VFH_VNQ_VPU (Rate-sensitive: Financials / Real Estate / Utilities)
Window : 2024-09-04 to 2024-09-18     Kalshi trades : 1110     primary bar : 2min     daily-screen R^2 : 0.42

>>> RELIABILITY:  Adequate   <<<   (see section 5; unreliable pairs still get figures, but read their problems in section 8)

DEFINITIONS
   xₜ₋ₖ = Kalshi yes-probability change, k bars before t   (1 bar = 2min)
   yₜ   = ETF log return over bar t
   calendar = full market-hours grid: x=0 in bars with no Kalshi trade (not dropped).
   k>0 => Kalshi leads ETF ;  k<0 => ETF leads Kalshi ;  k=0 => contemporaneous

1. CALENDAR-TIME REGRESSION (clock-time lags, full RTH grid)
   Full model: yₜ = α + Σₖ βₖ·xₜ₋ₖ + Σᵢ φᵢ·yₜ₋ᵢ (ADL self-control) + day-FE
   -> 17 coefficients tested, NONE significant after BH-FDR (p_fdr<0.05).

2. EVENT-TIME REGRESSION (event-count lags)
   Full model: yₜ = α + Σₖ βₖ·xₜ₋ₖ + Σᵢ φᵢ·yₜ₋ᵢ (ADL self-control) + day-FE
   -> 17 coefficients tested, NONE significant after BH-FDR (p_fdr<0.05).

3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)
      k |       calendar b (FDR) |          event b (FDR)
   ------------------------------------------------------
     -8 |          +5.97e-06     |          +3.37e-05    
     -7 |          -2.13e-05     |          -2.59e-05    
     -6 |          -4.55e-06     |          +5.49e-05    
     -5 |          +1.24e-05     |          -1.37e-05    
     -4 |          +1.72e-05     |          +5.18e-05    
     -3 |          +1.34e-05     |          +1.36e-04    
     -2 |          -3.23e-06     |          +1.14e-04    
     -1 |          -1.73e-05     |          -1.13e-05    
     +0 |          +1.18e-06     |          -1.33e-05    
     +1 |          -3.22e-06     |          -5.21e-05    
     +2 |          -5.70e-06     |          -2.52e-06    
     +3 |          +3.66e-05     |          -2.04e-06    
     +4 |          -2.44e-05     |          -3.46e-06    
     +5 |          -1.55e-05     |          -5.24e-06    
     +6 |          +1.82e-05 *   |          +2.77e-05    
     +7 |          +1.08e-05     |          -2.41e-05    
     +8 |          +4.74e-06     |          +1.01e-06    
   (stars = BH-FDR corrected:  *** p_fdr<.01  ** <.05  * <.10)

4. DIRECTIONAL TEST (probit, ETF up/down)
   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k
   calendar: β₋₃=+7.38e-02***
   event: β₋₈=-6.96e-02**

5. DATA RELIABILITY (statistical, not a trade-count cutoff)
   Tier: Adequate
   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)
   calendar(full RTH grid): n_active=270  n_obs=1829  n_days=11  K=8  params=33  df=1796  median_SE=1.18e-05  sig(FDR)=0
   event: n_active=205  n_obs=316  n_days=8  K=8  params=30  df=286  median_SE=3.64e-05  sig(FDR)=0

6. COARSE-FREQUENCY ROBUSTNESS (re-run calendar at 30min / 60min)
    30min: n_obs=90 df=66 K=6  sig=1 (Kalshi-leads 1 / ETF-leads 0) -> Kalshi-leads
    60min: n_obs=47 df=26 K=5  sig=0 (Kalshi-leads 0 / ETF-leads 0) -> No-sig

7. VERDICT
   No lead-lag detected -- too sparse / no significant structure.

8. FIGURE CAVEATS — figures are still drawn, but know their problems
   - Adequate info: figures and regression are mutually readable; note that flat Kalshi segments still mean 'no trade', not 'no change'.
   - Kalshi updates only on trades (flat line = no trade, NOT 'no change'); ETF mid refreshes continuously.

9. REAL-WORLD CONTEXT (WebSearch-verified; see URLs)
   - Sept 2024 FOMC decided Wed Sep 18, 2024 (statement 2:00 PM ET, Powell press conf 2:30 PM ET).
   - Outcome: 50bps cut to 4.75-5.00% -- a surprise vs the 25bps many expected (first cut in 4+ years).
   - This contract asked specifically about a 25bps cut; the 50bps outcome resolved it NO.
   - Sources: federalreserve.gov/monetarypolicy/files/fomcminutes20240918.pdf ; jpmorgan.com/insights/outlook/economic-outlook/fed-meeting-september-2024

------------------------------------------------------------------------------------------------
Conventions: ET | 09:30-16:00 (forward windows capped to 16:00) | ETF in log return | median causal bars | full RTH grid | day-grouped lags (no overnight) | ADL self-control | significance = BH-FDR corrected.
Figures for this pair follow on the next page.