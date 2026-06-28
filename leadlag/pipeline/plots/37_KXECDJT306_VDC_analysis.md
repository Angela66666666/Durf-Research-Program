PAIR ANALYSIS    —    Rank 7 / 48
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
   Full model: yₜ = α + Σₖ βₖ·xₜ₋ₖ + Σᵢ φᵢ·yₜ₋ᵢ (ADL self-control) + day-FE
   Significant terms (BH-FDR) expanded:  yₜ = α + β₋₄·xₜ₊₄ + β₊₀·xₜ + β₊₂·xₜ₋₂
   where:
      β₋₄ = -6.257e-05   (t/z=-6.31, p=2.8e-10, p_fdr=2.5e-09) ***   [ETF leads]
      β₊₀ = -7.328e-05   (t/z=-2.89, p=3.9e-03, p_fdr=1.2e-02) **   [contemporaneous]
      β₊₂ = -2.744e-05   (t/z=-2.91, p=3.6e-03, p_fdr=1.2e-02) **   [Kalshi leads]
   Lean by count of significant lags: balanced/no clear side  (k>0:1, k<0:1).

2. EVENT-TIME REGRESSION (event-count lags)
   Full model: yₜ = α + Σₖ βₖ·xₜ₋ₖ + Σᵢ φᵢ·yₜ₋ᵢ (ADL self-control) + day-FE
   -> no regression result (insufficient data).

3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)
      k |       calendar b (FDR) |          event b (FDR)
   ------------------------------------------------------
     -4 |          -6.26e-05 *** |                     --
     -3 |          -3.25e-05     |                     --
     -2 |          +2.33e-05 *   |                     --
     -1 |          -1.78e-05     |                     --
     +0 |          -7.33e-05 **  |                     --
     +1 |          -2.25e-05     |                     --
     +2 |          -2.74e-05 **  |                     --
     +3 |          +4.28e-05     |                     --
     +4 |          -1.13e-04 *   |                     --
   (stars = BH-FDR corrected:  *** p_fdr<.01  ** <.05  * <.10)

4. DIRECTIONAL TEST (probit, ETF up/down)
   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k
   calendar: β₋₁=+5.70e-01***
   event: β₋₁=+5.10e-01***, β₊₀=-1.74e-01***

5. DATA RELIABILITY (statistical, not a trade-count cutoff)
   Tier: Low-info
   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)
   calendar(full RTH grid): n_active=20  n_obs=205  n_days=11  K=4  params=25  df=180  median_SE=2.54e-05  sig(FDR)=3
   event: not estimable (insufficient data)

6. COARSE-FREQUENCY ROBUSTNESS (re-run calendar at 30min / 60min)
    30min: n_obs=13 df=1 K=4  sig=2 (Kalshi-leads 0 / ETF-leads 2) -> ETF-leads
    60min: not estimable (n_obs=13 < minimum) -- coarser bars have even fewer observations

7. VERDICT
   Only one time-axis significant (balanced) -- weak / single-mode evidence.

8. FIGURE CAVEATS — figures are still drawn, but know their problems
   - Low info (15<= active bars <40): direction is indicative but imprecise; do not over-interpret any single coefficient.
   - Kalshi updates only on trades (flat line = no trade, NOT 'no change'); ETF mid refreshes continuously.

9. REAL-WORLD CONTEXT (WebSearch-verified; see URLs)
   - 2024 US presidential election held Tue Nov 5, 2024; ballots counted overnight Nov 5-6.
   - AP called the race for Trump ~5:34-5:37 AM ET on Wed Nov 6, 2024 (Wisconsin pushed him past 270) -- this is PRE-MARKET, so the regular-hours equity reaction shows up at the Nov 6 open.
   - Final electoral result: Trump 312, Harris 226.
   - Sources: en.wikipedia.org/wiki/2024_United_States_presidential_election ; spectrumlocalnews.com/us/snplus/news/2024/11/06/trump-wins-ap-projection-2024-election

------------------------------------------------------------------------------------------------
Conventions: ET | 09:30-16:00 (forward windows capped to 16:00) | ETF in log return | median causal bars | full RTH grid | day-grouped lags (no overnight) | ADL self-control | significance = BH-FDR corrected.
Figures for this pair follow on the next page.