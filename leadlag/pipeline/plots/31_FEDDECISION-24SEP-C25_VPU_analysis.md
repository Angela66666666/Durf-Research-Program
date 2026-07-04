PAIR ANALYSIS    —    Rank 5 / 48
================================================================================================
FEDDECISION-24SEP-C25   x   VPU
Contract : "Will the Federal Reserve Cut rates by 25bps at their September 2024 meeting?"
Sector relevance : VFH_VNQ_VPU (Rate-sensitive: Financials / Real Estate / Utilities)
Window : 2024-09-04 to 2024-09-18     Kalshi trades : 1125     primary bar : 2min     daily-screen R^2 : 0.42

>>> RELIABILITY:  Adequate   <<<   (see section 5; unreliable pairs still get figures, but read their problems in section 8)

DEFINITIONS
   xₜ₋ₖ = Kalshi yes-probability change, k bars before t   (1 bar = 2min)
   yₜ   = ETF log return over bar t
   calendar = full market-hours grid: x=0 in bars with no Kalshi trade (not dropped).
   k>0 => Kalshi leads ETF ;  k<0 => ETF leads Kalshi ;  k=0 => contemporaneous

1. CALENDAR-TIME REGRESSION (clock-time lags, full RTH grid)
   Full model:  yₜ = α + Σ(k=-8..8) βₖ·xₜ₋ₖ + φ₁·yₜ₋₁ + φ₂·yₜ₋₂ + φ₃·yₜ₋₃ + φ₄·yₜ₋₄ + φ₅·yₜ₋₅ + φ₆·yₜ₋₆ + Σ(d=1..10) γ_d·Day_d
      where  ADL ETF self-lags p=6 (BIC-chosen): φ₁·yₜ₋₁ + φ₂·yₜ₋₂ + φ₃·yₜ₋₃ + φ₄·yₜ₋₄ + φ₅·yₜ₋₅ + φ₆·yₜ₋₆;  day-FE: 10 day dummies over 11 trading days (first day = baseline).
      controls counted (so you can see the total at a glance):  17 lead/lag x-terms + 6 ETF self-lag(s) + 10 day-FE dummies + 1 intercept = 34 RHS regressors  (model n_params=34).
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₋₄·xₜ₊₄ + β₊₃·xₜ₋₃ + β₊₄·xₜ₋₄ + β₊₆·xₜ₋₆
   where:
      β₋₄ = +2.026e-05   (t/z=+1.65, p=9.9e-02, p_fdr=4.3e-01)    [ETF leads]
      β₊₃ = +3.630e-05   (t/z=+1.77, p=7.7e-02, p_fdr=4.3e-01)    [Kalshi leads]
      β₊₄ = -2.709e-05   (t/z=-1.81, p=7.0e-02, p_fdr=4.3e-01)    [Kalshi leads]
      β₊₆ = +1.291e-05   (t/z=+1.64, p=1.0e-01, p_fdr=4.3e-01)    [Kalshi leads]
   Lean by count of significant lags: Kalshi-leads  (k>0:3, k<0:1).

2. EVENT-TIME REGRESSION (event-count lags)
   Full model:  yₜ = α + Σ(k=-8..8) βₖ·xₜ₋ₖ + Σ(d=1..7) γ_d·Day_d
      where  ADL ETF self-lags p=0 (BIC chose none -> no ETF self-lag term);  day-FE: 7 day dummies over 8 trading days (first day = baseline).
      controls counted (so you can see the total at a glance):  17 lead/lag x-terms + 0 ETF self-lag(s) + 7 day-FE dummies + 1 intercept = 25 RHS regressors  (model n_params=25).
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₋₃·xₜ₊₃ + β₋₂·xₜ₊₂
   where:
      β₋₃ = +1.271e-04   (t/z=+2.10, p=3.5e-02, p_fdr=6.0e-01)    [ETF leads]
      β₋₂ = +9.975e-05   (t/z=+1.78, p=7.6e-02, p_fdr=6.4e-01)    [ETF leads]
   Lean by count of significant lags: ETF-leads  (k>0:0, k<0:2).

3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)
      k |       calendar b (FDR) |          event b (FDR)
   ------------------------------------------------------
     -8 |          +8.15e-06     |          +3.50e-05    
     -7 |          -1.31e-05     |          -3.62e-05    
     -6 |          -5.56e-06     |          +4.73e-05    
     -5 |          +1.78e-05     |          -2.10e-05    
     -4 |          +2.03e-05     |          +3.48e-05    
     -3 |          +1.60e-05     |          +1.27e-04    
     -2 |          -3.74e-07     |          +9.98e-05    
     -1 |          -1.80e-05     |          -4.63e-05    
     +0 |          -1.59e-06     |          -3.17e-05    
     +1 |          -3.87e-06     |          -3.99e-05    
     +2 |          -7.87e-06     |          -6.94e-06    
     +3 |          +3.63e-05     |          +3.06e-06    
     +4 |          -2.71e-05     |          -7.22e-06    
     +5 |          -1.90e-05     |          -7.04e-06    
     +6 |          +1.29e-05     |          +2.40e-05    
     +7 |          +7.90e-06     |          -2.11e-05    
     +8 |          +1.33e-06     |          -3.67e-06    
   (stars = BH-FDR corrected:  *** p_fdr<.01  ** <.05  * <.10)

4. DIRECTIONAL TEST (probit, ETF up/down)
   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k
   calendar: β₋₈=-6.84e-02, β₋₅=+8.77e-02, β₋₃=+1.13e-01**, β₋₁=-1.10e-01, β₊₁=-6.61e-02, β₊₃=+1.29e-01, β₊₆=+1.22e-01, β₊₈=-8.50e-02
   event: β₋₈=-4.73e-02, β₋₆=+4.22e-02, β₋₅=+8.17e-02, β₋₁=-1.84e-01*, β₊₁=-9.01e-02, β₊₄=+4.63e-02, β₊₅=-1.20e-01*

5. DATA RELIABILITY (statistical, not a trade-count cutoff)
   Tier: Adequate
   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)
   calendar(full RTH grid): n_active=282  n_obs=1906  n_days=11  K=8  params=34  df=1872  median_SE=1.34e-05  sig(FDR)=0
   event: n_active=207  n_obs=322  n_days=8  K=8  params=25  df=297  median_SE=3.71e-05  sig(FDR)=0

6. COARSE-FREQUENCY ROBUSTNESS (re-run calendar at 30min / 60min)
    30min: n_obs=93 df=69 K=6  sig=1 (Kalshi-leads 1 / ETF-leads 0) -> Kalshi-leads
    60min: n_obs=50 df=29 K=5  sig=0 (Kalshi-leads 0 / ETF-leads 0) -> No-sig

7. VERDICT
   Calendar leans Kalshi-leads but Event leans ETF-leads -- NOT robust across time-axis; no clean lead.

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