PAIR ANALYSIS    —    Rank 15 / 48
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
   Full model: yₜ = α + Σₖ βₖ·xₜ₋ₖ + Σᵢ φᵢ·yₜ₋ᵢ (ADL self-control) + day-FE
   -> 11 coefficients tested, NONE significant after BH-FDR (p_fdr<0.05).

2. EVENT-TIME REGRESSION (event-count lags)
   Full model: yₜ = α + Σₖ βₖ·xₜ₋ₖ + Σᵢ φᵢ·yₜ₋ᵢ (ADL self-control) + day-FE
   Significant terms (BH-FDR) expanded:  yₜ = α + β₋₆·xₜ₊₆ + β₊₆·xₜ₋₆
   where:
      β₋₆ = +2.361e-04   (t/z=+3.11, p=1.9e-03, p_fdr=1.2e-02) **   [ETF leads]
      β₊₆ = +8.944e-05   (t/z=+3.64, p=2.7e-04, p_fdr=3.5e-03) ***   [Kalshi leads]
   Lean by count of significant lags: balanced/no clear side  (k>0:1, k<0:1).

3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)
      k |       calendar b (FDR) |          event b (FDR)
   ------------------------------------------------------
     -6 |                     -- |          +2.36e-04 ** 
     -5 |          +9.52e-05     |          +2.47e-04    
     -4 |          +6.64e-05     |          +1.11e-04    
     -3 |          -4.02e-05     |          +1.59e-04    
     -2 |          -5.69e-05     |          +1.93e-04    
     -1 |          +5.29e-06     |          +1.30e-04    
     +0 |          -7.77e-06     |          +1.35e-04    
     +1 |          -3.08e-05     |          +3.42e-05    
     +2 |          +3.85e-06     |          -6.37e-05    
     +3 |          +1.85e-06     |          +3.07e-05    
     +4 |          -3.73e-05     |          -3.79e-05    
     +5 |          -6.94e-05     |          +5.55e-05    
     +6 |                     -- |          +8.94e-05 ***
   (stars = BH-FDR corrected:  *** p_fdr<.01  ** <.05  * <.10)

4. DIRECTIONAL TEST (probit, ETF up/down)
   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k
   calendar: 11 lags tested, none significant after BH-FDR.
   event: β₊₁=+1.39e-01***, β₊₂=-1.20e-01***, β₊₅=-1.92e-01***, β₊₆=+1.39e-01***

5. DATA RELIABILITY (statistical, not a trade-count cutoff)
   Tier: Low-info
   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)
   calendar(full RTH grid): n_active=38  n_obs=169  n_days=10  K=5  params=26  df=143  median_SE=4.46e-05  sig(FDR)=0
   event: n_active=34  n_obs=50  n_days=4  K=6  params=22  df=28  median_SE=7.58e-05  sig(FDR)=2

6. COARSE-FREQUENCY ROBUSTNESS (re-run calendar at 30min / 60min)
    30min: n_obs=34 df=17 K=5  sig=1 (Kalshi-leads 0 / ETF-leads 1) -> ETF-leads
    60min: n_obs=20 df=5 K=4  sig=5 (Kalshi-leads 1 / ETF-leads 4) -> ETF-leads

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