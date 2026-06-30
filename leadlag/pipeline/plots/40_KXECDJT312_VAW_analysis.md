PAIR ANALYSIS    —    Rank 13 / 48
================================================================================================
KXECDJT312   x   VAW
Contract : "Will Trump win 312-226 - swing state sweep?"
Sector relevance : Election outcome (all sectors)
Window : 2024-11-04 to 2024-12-12     Kalshi trades : 204     primary bar : 10min     daily-screen R^2 : 0.31

>>> RELIABILITY:  Low-info   <<<   (see section 5; unreliable pairs still get figures, but read their problems in section 8)

DEFINITIONS
   xₜ₋ₖ = Kalshi yes-probability change, k bars before t   (1 bar = 10min)
   yₜ   = ETF log return over bar t
   calendar = full market-hours grid: x=0 in bars with no Kalshi trade (not dropped).
   k>0 => Kalshi leads ETF ;  k<0 => ETF leads Kalshi ;  k=0 => contemporaneous

1. CALENDAR-TIME REGRESSION (clock-time lags, full RTH grid)
   Full model:  yₜ = α + Σ(k=-5..5) βₖ·xₜ₋ₖ + φ₁·yₜ₋₁ + Σ(d=1..9) γ_d·Day_d
      where  ADL ETF self-lags p=1 (BIC-chosen): φ₁·yₜ₋₁;  day-FE: 9 day dummies over 10 trading days (first day = baseline).
      controls counted (so you can see the total at a glance):  11 lead/lag x-terms + 1 ETF self-lag(s) + 9 day-FE dummies + 1 intercept = 22 RHS regressors  (model n_params=22).
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₋₅·xₜ₊₅ + β₋₄·xₜ₊₄ + β₋₂·xₜ₊₂ + β₊₅·xₜ₋₅
   where:
      β₋₅ = +9.268e-05   (t/z=+2.64, p=8.2e-03, p_fdr=6.9e-02) *   [ETF leads]
      β₋₄ = +7.277e-05   (t/z=+2.35, p=1.9e-02, p_fdr=6.9e-02) *   [ETF leads]
      β₋₂ = -6.824e-05   (t/z=-2.42, p=1.5e-02, p_fdr=6.9e-02) *   [ETF leads]
      β₊₅ = -7.215e-05   (t/z=-1.54, p=1.2e-01, p_fdr=3.4e-01)    [Kalshi leads]
   Lean by count of significant lags: ETF-leads  (k>0:1, k<0:3).

2. EVENT-TIME REGRESSION (event-count lags)
   Full model:  yₜ = α + Σ(k=-5..5) βₖ·xₜ₋ₖ + Σ(d=1..2) γ_d·Day_d
      where  ADL ETF self-lags p=0 (BIC chose none -> no ETF self-lag term);  day-FE: 2 day dummies over 3 trading days (first day = baseline).
      controls counted (so you can see the total at a glance):  11 lead/lag x-terms + 0 ETF self-lag(s) + 2 day-FE dummies + 1 intercept = 14 RHS regressors  (model n_params=14).
   -> 11 coefficients tested, NONE significant at raw p<0.15.

3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)
      k |       calendar b (FDR) |          event b (FDR)
   ------------------------------------------------------
     -5 |          +9.27e-05 *   |          +1.89e-05    
     -4 |          +7.28e-05 *   |          -5.90e-05    
     -3 |          -4.87e-05     |          +4.41e-05    
     -2 |          -6.82e-05 *   |          -5.87e-04    
     -1 |          +1.39e-05     |          -5.76e-04    
     +0 |          +6.88e-07     |          -7.10e-04    
     +1 |          -3.35e-05     |          -1.08e-03    
     +2 |          +2.45e-06     |          -6.97e-04    
     +3 |          +7.16e-06     |          -1.30e-03    
     +4 |          -3.53e-05     |          -1.61e-03    
     +5 |          -7.21e-05     |          -4.77e-04    
   (stars = BH-FDR corrected:  *** p_fdr<.01  ** <.05  * <.10)

4. DIRECTIONAL TEST (probit, ETF up/down)
   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k
   calendar: β₋₄=-1.65e-01*, β₋₁=+1.43e-01, β₊₄=-2.78e-01
   event: β₋₅=+5.47e-02, β₋₄=-3.16e-01*, β₋₁=+2.99e-01*, β₊₄=-3.95e-01*

5. DATA RELIABILITY (statistical, not a trade-count cutoff)
   Tier: Low-info
   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)
   calendar(full RTH grid): n_active=38  n_obs=169  n_days=10  K=5  params=22  df=147  median_SE=3.50e-05  sig(FDR)=0
   event: n_active=20  n_obs=26  n_days=3  K=5  params=14  df=12  median_SE=1.67e-03  sig(FDR)=0

6. COARSE-FREQUENCY ROBUSTNESS (re-run calendar at 30min / 60min)
    30min: n_obs=34 df=17 K=5  sig=1 (Kalshi-leads 0 / ETF-leads 1) -> ETF-leads
    60min: n_obs=20 df=5 K=4  sig=5 (Kalshi-leads 1 / ETF-leads 4) -> ETF-leads

7. VERDICT
   Only one time-axis significant (ETF-leads) -- weak / single-mode evidence.

8. FIGURE CAVEATS — figures are still drawn, but know their problems
   - Low info (15<= active bars <40): direction is indicative but imprecise; do not over-interpret any single coefficient.
   - Mixed coefficient signs across lags -- relationship not monotone.
   - Kalshi updates only on trades (flat line = no trade, NOT 'no change'); ETF mid refreshes continuously.

9. REAL-WORLD CONTEXT (WebSearch-verified; see URLs)
   - 2024 US presidential election held Tue Nov 5, 2024; ballots counted overnight Nov 5-6.
   - AP called the race for Trump ~5:34-5:37 AM ET on Wed Nov 6, 2024 (Wisconsin pushed him past 270) -- this is PRE-MARKET, so the regular-hours equity reaction shows up at the Nov 6 open.
   - Final electoral result: Trump 312, Harris 226.
   - Sources: en.wikipedia.org/wiki/2024_United_States_presidential_election ; spectrumlocalnews.com/us/snplus/news/2024/11/06/trump-wins-ap-projection-2024-election

------------------------------------------------------------------------------------------------
Conventions: ET | 09:30-16:00 (forward windows capped to 16:00) | ETF in log return | median causal bars | full RTH grid | day-grouped lags (no overnight) | ADL self-control | significance = BH-FDR corrected.
Figures for this pair follow on the next page.