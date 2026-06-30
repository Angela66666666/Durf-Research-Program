PAIR ANALYSIS    —    Rank 9 / 48
================================================================================================
KXECDJT281   x   VNQ
Contract : "Will Trump win 281-257 - AZ, GA, NC, PA?"
Sector relevance : Election outcome (all sectors)
Window : 2024-11-04 to 2024-11-25     Kalshi trades : 294     primary bar : 5min     daily-screen R^2 : 0.43

>>> RELIABILITY:  Adequate   <<<   (see section 5; unreliable pairs still get figures, but read their problems in section 8)

DEFINITIONS
   xₜ₋ₖ = Kalshi yes-probability change, k bars before t   (1 bar = 5min)
   yₜ   = ETF log return over bar t
   calendar = full market-hours grid: x=0 in bars with no Kalshi trade (not dropped).
   k>0 => Kalshi leads ETF ;  k<0 => ETF leads Kalshi ;  k=0 => contemporaneous

1. CALENDAR-TIME REGRESSION (clock-time lags, full RTH grid)
   Full model:  yₜ = α + Σ(k=-5..5) βₖ·xₜ₋ₖ + φ₁·yₜ₋₁ + φ₂·yₜ₋₂ + Σ(d=1..7) γ_d·Day_d
      where  ADL ETF self-lags p=2 (BIC-chosen): φ₁·yₜ₋₁ + φ₂·yₜ₋₂;  day-FE: 7 day dummies over 8 trading days (first day = baseline).
      controls counted (so you can see the total at a glance):  11 lead/lag x-terms + 2 ETF self-lag(s) + 7 day-FE dummies + 1 intercept = 21 RHS regressors  (model n_params=21).
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₋₃·xₜ₊₃ + β₋₂·xₜ₊₂ + β₋₁·xₜ₊₁ + β₊₁·xₜ₋₁
   where:
      β₋₃ = -3.383e-05   (t/z=-2.81, p=5.0e-03, p_fdr=1.8e-02) **   [ETF leads]
      β₋₂ = +9.779e-05   (t/z=+7.03, p=2.0e-12, p_fdr=2.2e-11) ***   [ETF leads]
      β₋₁ = +1.274e-04   (t/z=+2.24, p=2.5e-02, p_fdr=7.0e-02) *   [ETF leads]
      β₊₁ = +8.129e-05   (t/z=+4.65, p=3.4e-06, p_fdr=1.8e-05) ***   [Kalshi leads]
   Lean by count of significant lags: ETF-leads  (k>0:1, k<0:3).

2. EVENT-TIME REGRESSION (event-count lags)
   Full model:  yₜ = α + Σ(k=-5..5) βₖ·xₜ₋ₖ + Σ(d=1..1) γ_d·Day_d
      where  ADL ETF self-lags p=0 (BIC chose none -> no ETF self-lag term);  day-FE: 1 day dummies over 2 trading days (first day = baseline).
      controls counted (so you can see the total at a glance):  11 lead/lag x-terms + 0 ETF self-lag(s) + 1 day-FE dummies + 1 intercept = 13 RHS regressors  (model n_params=13).
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₋₄·xₜ₊₄ + β₋₃·xₜ₊₃ + β₊₂·xₜ₋₂ + β₊₄·xₜ₋₄
   where:
      β₋₄ = -1.091e-04   (t/z=-1.85, p=6.5e-02, p_fdr=2.1e-01)    [ETF leads]
      β₋₃ = -1.160e-04   (t/z=-3.15, p=1.6e-03, p_fdr=1.8e-02) **   [ETF leads]
      β₊₂ = +3.729e-04   (t/z=+1.77, p=7.7e-02, p_fdr=2.1e-01)    [Kalshi leads]
      β₊₄ = +7.545e-05   (t/z=+2.14, p=3.3e-02, p_fdr=1.8e-01)    [Kalshi leads]
   Lean by count of significant lags: balanced/no clear side  (k>0:2, k<0:2).

3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)
      k |       calendar b (FDR) |          event b (FDR)
   ------------------------------------------------------
     -5 |          +1.35e-06     |          -7.73e-05    
     -4 |          -1.75e-05     |          -1.09e-04    
     -3 |          -3.38e-05 **  |          -1.16e-04 ** 
     -2 |          +9.78e-05 *** |          -2.13e-04    
     -1 |          +1.27e-04 *   |          +1.68e-04    
     +0 |          -1.88e-05     |          +3.70e-05    
     +1 |          +8.13e-05 *** |          +2.38e-04    
     +2 |          +1.86e-05     |          +3.73e-04    
     +3 |          +2.86e-05     |          +1.99e-04    
     +4 |          +8.12e-06     |          +7.55e-05    
     +5 |          +1.45e-05     |          +8.95e-05    
   (stars = BH-FDR corrected:  *** p_fdr<.01  ** <.05  * <.10)

4. DIRECTIONAL TEST (probit, ETF up/down)
   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k
   calendar: β₋₆=-2.19e-01, β₋₅=+1.71e-01, β₋₃=+7.80e-02, β₋₂=+1.76e-01, β₊₀=-3.76e-01, β₊₂=-1.89e-01, β₊₅=-1.59e-01
   event: β₋₃=+1.59e-01, β₋₁=+8.44e-02, β₊₀=-8.95e-02, β₊₆=-5.64e-02

5. DATA RELIABILITY (statistical, not a trade-count cutoff)
   Tier: Adequate
   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)
   calendar(full RTH grid): n_active=51  n_obs=385  n_days=8  K=5  params=21  df=364  median_SE=2.28e-05  sig(FDR)=3
   event: n_active=35  n_obs=58  n_days=2  K=5  params=13  df=45  median_SE=1.62e-04  sig(FDR)=1

6. COARSE-FREQUENCY ROBUSTNESS (re-run calendar at 30min / 60min)
    30min: n_obs=31 df=15 K=5  sig=4 (Kalshi-leads 3 / ETF-leads 1) -> Kalshi-leads
    60min: n_obs=18 df=4 K=4  sig=1 (Kalshi-leads 0 / ETF-leads 1) -> ETF-leads

7. VERDICT
   Calendar leans ETF-leads but Event leans balanced -- NOT robust across time-axis; no clean lead.

8. FIGURE CAVEATS — figures are still drawn, but know their problems
   - Adequate info: figures and regression are mutually readable; note that flat Kalshi segments still mean 'no trade', not 'no change'.
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