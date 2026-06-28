PAIR ANALYSIS    —    Rank 1 / 48
================================================================================================
KXECKH276   x   VOX
Contract : "Will Harris win 276-262 - PA, NV, MI, WI?"
Sector relevance : Election outcome (all sectors)
Window : 2024-11-04 to 2024-11-26     Kalshi trades : 37     primary bar : 10min     daily-screen R^2 : 0.59

>>> RELIABILITY:  Very-low-info   <<<   (see section 5; unreliable pairs still get figures, but read their problems in section 8)

DEFINITIONS
   xₜ₋ₖ = Kalshi yes-probability change, k bars before t   (1 bar = 10min)
   yₜ   = ETF log return over bar t
   calendar = full market-hours grid: x=0 in bars with no Kalshi trade (not dropped).
   k>0 => Kalshi leads ETF ;  k<0 => ETF leads Kalshi ;  k=0 => contemporaneous

1. CALENDAR-TIME REGRESSION (clock-time lags, full RTH grid)
   Full model: yₜ = α + Σₖ βₖ·xₜ₋ₖ + Σᵢ φᵢ·yₜ₋ᵢ (ADL self-control) + day-FE
   Significant terms (BH-FDR) expanded:  yₜ = α + β₋₃·xₜ₊₃ + β₋₂·xₜ₊₂ + β₋₁·xₜ₊₁ + β₊₁·xₜ₋₁ + β₊₂·xₜ₋₂ + β₊₃·xₜ₋₃
   where:
      β₋₃ = +1.182e-04   (t/z=+3.53, p=4.2e-04, p_fdr=7.4e-04) ***   [ETF leads]
      β₋₂ = -8.380e-05   (t/z=-3.57, p=3.5e-04, p_fdr=7.4e-04) ***   [ETF leads]
      β₋₁ = +7.363e-05   (t/z=+9.51, p=1.9e-21, p_fdr=6.5e-21) ***   [ETF leads]
      β₊₁ = +1.104e-04   (t/z=+2.14, p=3.3e-02, p_fdr=3.8e-02) **   [Kalshi leads]
      β₊₂ = -7.553e-05   (t/z=-2.89, p=3.9e-03, p_fdr=5.4e-03) ***   [Kalshi leads]
      β₊₃ = +1.907e-04   (t/z=+10.94, p=7.2e-28, p_fdr=5.1e-27) ***   [Kalshi leads]
   Lean by count of significant lags: balanced/no clear side  (k>0:3, k<0:3).

2. EVENT-TIME REGRESSION (event-count lags)
   Full model: yₜ = α + Σₖ βₖ·xₜ₋ₖ + Σᵢ φᵢ·yₜ₋ᵢ (ADL self-control) + day-FE
   -> no regression result (insufficient data).

3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)
      k |       calendar b (FDR) |          event b (FDR)
   ------------------------------------------------------
     -3 |          +1.18e-04 *** |                     --
     -2 |          -8.38e-05 *** |                     --
     -1 |          +7.36e-05 *** |                     --
     +0 |          -3.90e-05     |                     --
     +1 |          +1.10e-04 **  |                     --
     +2 |          -7.55e-05 *** |                     --
     +3 |          +1.91e-04 *** |                     --
   (stars = BH-FDR corrected:  *** p_fdr<.01  ** <.05  * <.10)

4. DIRECTIONAL TEST (probit, ETF up/down)
   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k
   calendar: n/a
   event: n/a
   -> no significant directional predictability either mode (BH-FDR).

5. DATA RELIABILITY (statistical, not a trade-count cutoff)
   Tier: Very-low-info
   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)
   calendar(full RTH grid): n_active=7  n_obs=53  n_days=3  K=3  params=15  df=38  median_SE=2.62e-05  sig(FDR)=6
   event: not estimable (insufficient data)
   => Very low info: even 'significant' coefficients are untrustworthy (huge SE, possibly spurious significance).

6. COARSE-FREQUENCY ROBUSTNESS (re-run calendar at 30min / 60min)
    30min: not estimable (n_obs=11 < minimum) -- coarser bars have even fewer observations
    60min: not estimable (n_obs=6 < minimum) -- coarser bars have even fewer observations

7. VERDICT
   Only one time-axis significant (balanced) -- weak / single-mode evidence.
   (Note: this pair lacks the data to support reliable inference; the verdict above is descriptive only -- do not put it in the conclusions.)

8. FIGURE CAVEATS — figures are still drawn, but know their problems
   - Very low info (only 7 bars with an actual Kalshi move, < 15): even 'significant' coefficients are untrustworthy (huge SE, possibly spurious significance).
   - Most of the chart is flat no-trade lines; only a handful of bars carry real variation, so the lead calls in leadglance/segments are not robust.
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