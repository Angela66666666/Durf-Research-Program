PAIR ANALYSIS    —    Rank 6 / 48
================================================================================================
FEDDECISION-24SEP-C25   x   VDC
Contract : "Will the Federal Reserve Cut rates by 25bps at their September 2024 meeting?"
Sector relevance : VFH_VNQ_VPU (Rate-sensitive: Financials / Real Estate / Utilities)
Window : 2024-09-04 to 2024-09-18     Kalshi trades : 1125     primary bar : 2min     daily-screen R^2 : 0.63

>>> RELIABILITY:  Adequate   <<<   (see section 5; unreliable pairs still get figures, but read their problems in section 8)

DEFINITIONS
   xₜ₋ₖ = Kalshi yes-probability change, k bars before t   (1 bar = 2min)
   yₜ   = ETF log return over bar t
   calendar = full market-hours grid: x=0 in bars with no Kalshi trade (not dropped).
   k>0 => Kalshi leads ETF ;  k<0 => ETF leads Kalshi ;  k=0 => contemporaneous

1. CALENDAR-TIME REGRESSION (clock-time lags, full RTH grid)
   Full model:  yₜ = α + Σ(k=-8..8) βₖ·xₜ₋ₖ + φ₁·yₜ₋₁ + Σ(d=1..10) γ_d·Day_d
      where  ADL ETF self-lags p=1 (BIC-chosen): φ₁·yₜ₋₁;  day-FE: 10 day dummies over 11 trading days (first day = baseline).
      controls counted (so you can see the total at a glance):  17 lead/lag x-terms + 1 ETF self-lag(s) + 10 day-FE dummies + 1 intercept = 29 RHS regressors  (model n_params=29).
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₋₆·xₜ₊₆ + β₊₃·xₜ₋₃
   where:
      β₋₆ = -1.465e-05   (t/z=-1.87, p=6.2e-02, p_fdr=7.0e-01)    [ETF leads]
      β₊₃ = +2.104e-05   (t/z=+1.48, p=1.4e-01, p_fdr=7.0e-01)    [Kalshi leads]
   Lean by count of significant lags: balanced/no clear side  (k>0:1, k<0:1).

2. EVENT-TIME REGRESSION (event-count lags)
   Full model:  yₜ = α + Σ(k=-8..8) βₖ·xₜ₋ₖ + Σ(d=1..7) γ_d·Day_d
      where  ADL ETF self-lags p=0 (BIC chose none -> no ETF self-lag term);  day-FE: 7 day dummies over 8 trading days (first day = baseline).
      controls counted (so you can see the total at a glance):  17 lead/lag x-terms + 0 ETF self-lag(s) + 7 day-FE dummies + 1 intercept = 25 RHS regressors  (model n_params=25).
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₋₂·xₜ₊₂ + β₊₃·xₜ₋₃
   where:
      β₋₂ = +1.097e-04   (t/z=+2.09, p=3.7e-02, p_fdr=6.2e-01)    [ETF leads]
      β₊₃ = -2.256e-05   (t/z=-1.58, p=1.1e-01, p_fdr=6.6e-01)    [Kalshi leads]
   Lean by count of significant lags: balanced/no clear side  (k>0:1, k<0:1).

3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)
      k |       calendar b (FDR) |          event b (FDR)
   ------------------------------------------------------
     -8 |          -5.85e-06     |          +4.38e-05    
     -7 |          -6.45e-06     |          -1.29e-05    
     -6 |          -1.46e-05     |          +3.37e-05    
     -5 |          +1.19e-05     |          -2.67e-05    
     -4 |          +8.79e-07     |          +3.32e-05    
     -3 |          +1.34e-05     |          +7.96e-05    
     -2 |          -1.77e-06     |          +1.10e-04    
     -1 |          -8.27e-06     |          -5.75e-05    
     +0 |          -6.06e-06     |          -1.80e-05    
     +1 |          +6.48e-06     |          +9.45e-06    
     +2 |          -1.21e-05     |          -1.36e-05    
     +3 |          +2.10e-05     |          -2.26e-05    
     +4 |          -9.76e-06     |          +8.05e-06    
     +5 |          -1.50e-05     |          +3.83e-05    
     +6 |          +6.50e-06     |          +9.82e-06    
     +7 |          +1.28e-05     |          -1.98e-05    
     +8 |          -1.81e-06     |          +7.38e-06    
   (stars = BH-FDR corrected:  *** p_fdr<.01  ** <.05  * <.10)

4. DIRECTIONAL TEST (probit, ETF up/down)
   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k
   calendar: β₋₇=-9.96e-02*, β₋₅=-6.33e-02, β₊₅=+2.26e-01**
   event: β₋₇=-8.94e-02**, β₋₅=-7.57e-02***, β₋₁=-9.50e-02, β₊₂=-5.83e-02, β₊₃=-7.78e-02, β₊₅=+1.92e-01*, β₊₈=-7.20e-02

5. DATA RELIABILITY (statistical, not a trade-count cutoff)
   Tier: Adequate
   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)
   calendar(full RTH grid): n_active=282  n_obs=1906  n_days=11  K=8  params=29  df=1877  median_SE=1.01e-05  sig(FDR)=0
   event: n_active=207  n_obs=322  n_days=8  K=8  params=25  df=297  median_SE=3.09e-05  sig(FDR)=0

6. COARSE-FREQUENCY ROBUSTNESS (re-run calendar at 30min / 60min)
    30min: n_obs=93 df=69 K=6  sig=0 (Kalshi-leads 0 / ETF-leads 0) -> No-sig
    60min: n_obs=50 df=29 K=5  sig=0 (Kalshi-leads 0 / ETF-leads 0) -> No-sig

7. VERDICT
   Both time-axes balanced -- no clean directional lead.

8. FIGURE CAVEATS — figures are still drawn, but know their problems
   - Adequate info: figures and regression are mutually readable; note that flat Kalshi segments still mean 'no trade', not 'no change'.
   - Mixed coefficient signs across lags -- relationship not monotone.
   - Kalshi updates only on trades (flat line = no trade, NOT 'no change'); ETF mid refreshes continuously.

9. REAL-WORLD CONTEXT (WebSearch-verified; see URLs)
   - Sept 2024 FOMC decided Wed Sep 18, 2024 (statement 2:00 PM ET, Powell press conf 2:30 PM ET).
   - Outcome: 50bps cut to 4.75-5.00% -- a surprise vs the 25bps many expected (first cut in 4+ years).
   - This contract asked specifically about a 25bps cut; the 50bps outcome resolved it NO.
   - Sources: federalreserve.gov/monetarypolicy/files/fomcminutes20240918.pdf ; jpmorgan.com/insights/outlook/economic-outlook/fed-meeting-september-2024

------------------------------------------------------------------------------------------------
Conventions: ET | 09:30-16:00 (forward windows capped to 16:00) | ETF in log return | median causal bars | full RTH grid | day-grouped lags (no overnight) | ADL self-control | significance = BH-FDR corrected.
Figures for this pair follow on the next page.