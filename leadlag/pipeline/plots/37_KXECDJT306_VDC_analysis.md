PAIR ANALYSIS    —    Rank 14 / 48
================================================================================================
KXECDJT306   x   VDC
Contract : "Will Trump win 306-232 - AZ, GA, MI, PA, WI, NC?"
Sector relevance : Election outcome (all sectors)
Window : 2024-11-04 to 2024-12-16     Kalshi trades : 108     primary bar : 10min     daily-screen R^2 : 0.32

>>> RELIABILITY:  Low-info   <<<   (see section 5; unreliable pairs still get figures, but read their problems in section 8)

DEFINITIONS
   xₜ₋ₖ = Kalshi yes-probability change, k bars before t   (1 bar = 10min)
   yₜ   = ETF log return over bar t
   calendar = full market-hours grid: x=0 in bars with no Kalshi trade (not dropped).
   k>0 => Kalshi leads ETF ;  k<0 => ETF leads Kalshi ;  k=0 => contemporaneous

1. CALENDAR-TIME REGRESSION (clock-time lags, full RTH grid)
   Full model:  yₜ = α + Σ(k=-4..4) βₖ·xₜ₋ₖ + φ₁·yₜ₋₁ + Σ(d=1..10) γ_d·Day_d
      where  ADL ETF self-lags p=1 (BIC-chosen): φ₁·yₜ₋₁;  day-FE: 10 day dummies over 11 trading days (first day = baseline).
      controls counted (so you can see the total at a glance):  9 lead/lag x-terms + 1 ETF self-lag(s) + 10 day-FE dummies + 1 intercept = 21 RHS regressors  (model n_params=21).
   Significant terms (raw p<0.15) expanded:  yₜ = α + β₋₄·xₜ₊₄ + β₋₂·xₜ₊₂ + β₊₀·xₜ + β₊₂·xₜ₋₂ + β₊₃·xₜ₋₃ + β₊₄·xₜ₋₄
   where:
      β₋₄ = -5.111e-05   (t/z=-6.71, p=2.0e-11, p_fdr=6.0e-11) ***   [ETF leads]
      β₋₂ = +4.614e-05   (t/z=+27.40, p=2.4e-165, p_fdr=2.2e-164) ***   [ETF leads]
      β₊₀ = -5.134e-05   (t/z=-2.74, p=6.2e-03, p_fdr=1.4e-02) **   [contemporaneous]
      β₊₂ = -2.431e-05   (t/z=-8.51, p=1.8e-17, p_fdr=8.1e-17) ***   [Kalshi leads]
      β₊₃ = +6.257e-05   (t/z=+2.53, p=1.1e-02, p_fdr=2.0e-02) **   [Kalshi leads]
      β₊₄ = -7.315e-05   (t/z=-2.32, p=2.0e-02, p_fdr=3.1e-02) **   [Kalshi leads]
   Lean by count of significant lags: Kalshi-leads  (k>0:3, k<0:2).

2. EVENT-TIME REGRESSION (event-count lags)
   Full model:  yₜ = α + Σ(k) βₖ·xₜ₋ₖ + (ADL self-lags) + (day fixed effects)
   -> no regression result (insufficient data).

3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)
      k |       calendar b (FDR) |          event b (FDR)
   ------------------------------------------------------
     -4 |          -5.11e-05 *** |                     --
     -3 |          -1.73e-05     |                     --
     -2 |          +4.61e-05 *** |                     --
     -1 |          -8.62e-06     |                     --
     +0 |          -5.13e-05 **  |                     --
     +1 |          -4.77e-07     |                     --
     +2 |          -2.43e-05 *** |                     --
     +3 |          +6.26e-05 **  |                     --
     +4 |          -7.32e-05 **  |                     --
   (stars = BH-FDR corrected:  *** p_fdr<.01  ** <.05  * <.10)

4. DIRECTIONAL TEST (probit, ETF up/down)
   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k
   calendar: β₋₁=+5.70e-01***
   event: β₋₁=+5.10e-01***, β₊₀=-1.74e-01***, β₊₃=-1.84e-01

5. DATA RELIABILITY (statistical, not a trade-count cutoff)
   Tier: Low-info
   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)
   calendar(full RTH grid): n_active=20  n_obs=216  n_days=11  K=4  params=21  df=195  median_SE=1.88e-05  sig(FDR)=6
   event: not estimable (insufficient data)

6. COARSE-FREQUENCY ROBUSTNESS (re-run calendar at 30min / 60min)
    30min: n_obs=13 df=1 K=4  sig=2 (Kalshi-leads 0 / ETF-leads 2) -> ETF-leads
    60min: not estimable (n_obs=13 < minimum) -- coarser bars have even fewer observations

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