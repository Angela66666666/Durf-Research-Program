PAIR ANALYSIS    —    Rank 14 / 48
================================================================================================
KXECDJT306   x   VDC
Contract : "Will Trump win 306-232 - AZ, GA, MI, PA, WI, NC?"
Sector relevance : Election outcome (all sectors)
Window : 2024-11-04 to 2024-12-16     Kalshi trades : 123     primary bar : 10min     daily-screen R^2 : 0.32

>>> RELIABILITY:  Low-info   <<<   (see section 5; unreliable pairs still get figures, but read their problems in section 8)

DEFINITIONS
   xₜ₋ₖ = Kalshi yes-probability change, k bars before t   (1 bar = 10min)
   yₜ   = ETF log return over bar t
   calendar = full market-hours grid: x=0 in bars with no Kalshi trade (not dropped).
   k>0 => Kalshi leads ETF ;  k<0 => ETF leads Kalshi ;  k=0 => contemporaneous

1. CALENDAR-TIME REGRESSION (clock-time lags, full RTH grid)
   Full model:  yₜ = α + Σ(k=-4..4) βₖ·xₜ₋ₖ + φ₁·yₜ₋₁ + φ₂·yₜ₋₂ + φ₃·yₜ₋₃ + Σ(d=1..12) γ_d·Day_d
      where  ADL ETF self-lags p=3 (BIC-chosen): φ₁·yₜ₋₁ + φ₂·yₜ₋₂ + φ₃·yₜ₋₃;  day-FE: 12 day dummies over 13 trading days (first day = baseline).
      controls counted (so you can see the total at a glance):  9 lead/lag x-terms + 3 ETF self-lag(s) + 12 day-FE dummies + 1 intercept = 25 RHS regressors  (model n_params=25).
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₋₄·xₜ₊₄ + β₋₃·xₜ₊₃ + β₋₂·xₜ₊₂ + β₊₀·xₜ + β₊₁·xₜ₋₁ + β₊₂·xₜ₋₂ + β₊₃·xₜ₋₃ + β₊₄·xₜ₋₄
   where:
      β₋₄ = -3.617e-05   (t/z=-6.49, p=8.5e-11, p_fdr=3.8e-10) ***   [ETF leads]
      β₋₃ = -2.254e-05   (t/z=-2.57, p=1.0e-02, p_fdr=1.3e-02) **   [ETF leads]
      β₋₂ = +4.835e-05   (t/z=+9.23, p=2.6e-20, p_fdr=2.4e-19) ***   [ETF leads]
      β₊₀ = -5.342e-05   (t/z=-5.24, p=1.6e-07, p_fdr=4.8e-07) ***   [contemporaneous]
      β₊₁ = +3.960e-05   (t/z=+3.27, p=1.1e-03, p_fdr=1.9e-03) ***   [Kalshi leads]
      β₊₂ = +1.648e-05   (t/z=+2.91, p=3.6e-03, p_fdr=5.5e-03) ***   [Kalshi leads]
      β₊₃ = +4.123e-05   (t/z=+3.74, p=1.8e-04, p_fdr=4.1e-04) ***   [Kalshi leads]
      β₊₄ = -4.758e-05   (t/z=-1.59, p=1.1e-01, p_fdr=1.3e-01)    [Kalshi leads]
   Lean by count of significant lags: Kalshi-leads  (k>0:4, k<0:3).

2. EVENT-TIME REGRESSION (event-count lags)
   Full model:  yₜ = α + Σ(k=-4..4) βₖ·xₜ₋ₖ + φ₁·yₜ₋₁ + φ₂·yₜ₋₂ + φ₃·yₜ₋₃ + Σ(d=1..1) γ_d·Day_d
      where  ADL ETF self-lags p=3 (BIC-chosen): φ₁·yₜ₋₁ + φ₂·yₜ₋₂ + φ₃·yₜ₋₃;  day-FE: 1 day dummies over 2 trading days (first day = baseline).
      controls counted (so you can see the total at a glance):  9 lead/lag x-terms + 3 ETF self-lag(s) + 1 day-FE dummies + 1 intercept = 14 RHS regressors  (model n_params=14).
   -> 9 coefficients tested, NONE significant at raw p<0.15.

3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)
      k |       calendar b (FDR) |          event b (FDR)
   ------------------------------------------------------
     -4 |          -3.62e-05 *** |          -1.64e-04    
     -3 |          -2.25e-05 **  |          -3.96e-04    
     -2 |          +4.84e-05 *** |          -3.35e-04    
     -1 |          +4.56e-06     |          -3.50e-04    
     +0 |          -5.34e-05 *** |          -4.26e-04    
     +1 |          +3.96e-05 *** |          -4.83e-04    
     +2 |          +1.65e-05 *** |          +1.21e-04    
     +3 |          +4.12e-05 *** |          -7.22e-04    
     +4 |          -4.76e-05     |          +7.84e-06    
   (stars = BH-FDR corrected:  *** p_fdr<.01  ** <.05  * <.10)

4. DIRECTIONAL TEST (probit, ETF up/down)
   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k
   calendar: β₋₃=-9.65e-01***, β₋₂=+2.07e-01*, β₋₁=+2.07e-01***
   event: β₋₃=-1.18e+00***, β₋₂=+2.17e-01*, β₋₁=+1.86e-01***, β₊₀=-1.64e-01***, β₊₃=-3.28e-01***

5. DATA RELIABILITY (statistical, not a trade-count cutoff)
   Tier: Low-info
   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)
   calendar(full RTH grid): n_active=21  n_obs=265  n_days=13  K=4  params=25  df=240  median_SE=1.02e-05  sig(FDR)=7
   event: n_active=12  n_obs=13  n_days=2  K=4  params=14  df=-1  median_SE=nan  sig(FDR)=0

6. COARSE-FREQUENCY ROBUSTNESS (re-run calendar at 30min / 60min)
    30min: n_obs=15 df=3 K=4  sig=6 (Kalshi-leads 3 / ETF-leads 2) -> Kalshi-leads
    60min: not estimable (n_obs=14 < minimum) -- coarser bars have even fewer observations

7. VERDICT
   Only one time-axis significant (Kalshi-leads) -- weak / single-mode evidence.

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