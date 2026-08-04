PAIR ANALYSIS    —    Rank 4 / 48
================================================================================================
FEDDECISION-24SEP-C25   x   VOX
Contract : "Will the Federal Reserve Cut rates by 25bps at their September 2024 meeting?"
Sector relevance : VFH_VNQ_VPU (Rate-sensitive: Financials / Real Estate / Utilities)
Window : 2024-09-04 to 2024-09-18     Kalshi trades : 1125     primary bar : 2min     daily-screen R^2 : 0.43

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
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₋₂·xₜ₊₂ + β₊₃·xₜ₋₃ + β₊₄·xₜ₋₄ + β₊₅·xₜ₋₅ + β₊₆·xₜ₋₆
   where:
      β₋₂ = -8.760e-06   (t/z=-1.72, p=8.5e-02, p_fdr=2.9e-01)    [ETF leads]
      β₊₃ = +3.271e-05   (t/z=+1.79, p=7.4e-02, p_fdr=2.9e-01)    [Kalshi leads]
      β₊₄ = -3.972e-05   (t/z=-3.54, p=4.0e-04, p_fdr=6.8e-03) ***   [Kalshi leads]
      β₊₅ = -6.317e-05   (t/z=-2.49, p=1.3e-02, p_fdr=1.1e-01)    [Kalshi leads]
      β₊₆ = +2.263e-05   (t/z=+1.96, p=5.0e-02, p_fdr=2.8e-01)    [Kalshi leads]
   Lean by count of significant lags: Kalshi-leads  (k>0:4, k<0:1).

2. EVENT-TIME REGRESSION (event-count lags)
   Full model:  yₜ = α + Σ(k=-8..8) βₖ·xₜ₋ₖ + Σ(d=1..7) γ_d·Day_d
      where  ADL ETF self-lags p=0 (BIC chose none -> no ETF self-lag term);  day-FE: 7 day dummies over 8 trading days (first day = baseline).
      controls counted (so you can see the total at a glance):  17 lead/lag x-terms + 0 ETF self-lag(s) + 7 day-FE dummies + 1 intercept = 25 RHS regressors  (model n_params=25).
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₋₂·xₜ₊₂ + β₊₃·xₜ₋₃
   where:
      β₋₂ = +1.231e-04   (t/z=+1.76, p=7.8e-02, p_fdr=6.7e-01)    [ETF leads]
      β₊₃ = -3.671e-05   (t/z=-2.01, p=4.5e-02, p_fdr=6.7e-01)    [Kalshi leads]
   Lean by count of significant lags: balanced/no clear side  (k>0:1, k<0:1).

3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)
      k |       calendar b (FDR) |          event b (FDR)
   ------------------------------------------------------
     -8 |          -7.08e-06     |          +2.11e-05    
     -7 |          -2.16e-05     |          -3.19e-06    
     -6 |          +7.34e-06     |          +2.33e-05    
     -5 |          +2.00e-05     |          -1.84e-05    
     -4 |          +6.29e-06     |          +6.43e-05    
     -3 |          +1.37e-05     |          +1.19e-04    
     -2 |          -8.76e-06     |          +1.23e-04    
     -1 |          -1.17e-05     |          -5.66e-05    
     +0 |          +5.14e-07     |          -3.90e-05    
     +1 |          +3.15e-06     |          +3.87e-05    
     +2 |          -1.40e-05     |          -8.83e-06    
     +3 |          +3.27e-05     |          -3.67e-05    
     +4 |          -3.97e-05 *** |          -1.22e-05    
     +5 |          -6.32e-05     |          +4.22e-06    
     +6 |          +2.26e-05     |          -1.76e-05    
     +7 |          +7.28e-06     |          -1.73e-05    
     +8 |          +2.34e-06     |          +8.76e-06    
   (stars = BH-FDR corrected:  *** p_fdr<.01  ** <.05  * <.10)

4. DIRECTIONAL TEST (probit, ETF up/down)
   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k
   calendar: β₋₆=+9.99e-02, β₋₃=-1.01e-01, β₋₁=-8.18e-02, β₊₂=-8.94e-02
   event: β₋₁=-8.58e-02, β₊₂=-9.42e-02, β₊₇=-1.56e-01

5. DATA RELIABILITY (statistical, not a trade-count cutoff)
   Tier: Adequate
   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)
   calendar(full RTH grid): n_active=282  n_obs=1906  n_days=11  K=8  params=29  df=1877  median_SE=1.58e-05  sig(FDR)=1
   event: n_active=207  n_obs=322  n_days=8  K=8  params=25  df=297  median_SE=4.67e-05  sig(FDR)=0

6. COARSE-FREQUENCY ROBUSTNESS (re-run calendar at 30min / 60min)
    30min: n_obs=93 df=69 K=6  sig=0 (Kalshi-leads 0 / ETF-leads 0) -> No-sig
    60min: n_obs=50 df=29 K=5  sig=2 (Kalshi-leads 1 / ETF-leads 1) -> Balanced/mixed

7. VERDICT
   Calendar leans Kalshi-leads but Event leans balanced -- NOT robust across time-axis; no clean lead.

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