PAIR ANALYSIS    —    Rank 3 / 48
================================================================================================
KXECDJT281   x   VGT
Contract : "Will Trump win 281-257 - AZ, GA, NC, PA?"
Sector relevance : Election outcome (all sectors)
Window : 2024-11-04 to 2024-11-25     Kalshi trades : 294     primary bar : 5min     daily-screen R^2 : 0.32

>>> RELIABILITY:  Adequate   <<<   (see section 5; unreliable pairs still get figures, but read their problems in section 8)

DEFINITIONS
   xₜ₋ₖ = Kalshi yes-probability change, k bars before t   (1 bar = 5min)
   yₜ   = ETF log return over bar t
   calendar = full market-hours grid: x=0 in bars with no Kalshi trade (not dropped).
   k>0 => Kalshi leads ETF ;  k<0 => ETF leads Kalshi ;  k=0 => contemporaneous

1. CALENDAR-TIME REGRESSION (clock-time lags, full RTH grid)
   Full model: yₜ = α + Σₖ βₖ·xₜ₋ₖ + Σᵢ φᵢ·yₜ₋ᵢ (ADL self-control) + day-FE
   Significant terms (BH-FDR) expanded:  yₜ = α + β₋₁·xₜ₊₁
   where:
      β₋₁ = -3.611e-05   (t/z=-3.45, p=5.5e-04, p_fdr=6.1e-03) ***   [ETF leads]
   Lean by count of significant lags: ETF-leads  (k>0:0, k<0:1).

2. EVENT-TIME REGRESSION (event-count lags)
   Full model: yₜ = α + Σₖ βₖ·xₜ₋ₖ + Σᵢ φᵢ·yₜ₋ᵢ (ADL self-control) + day-FE
   Significant terms (BH-FDR) expanded:  yₜ = α + β₋₅·xₜ₊₅ + β₊₀·xₜ + β₊₁·xₜ₋₁ + β₊₂·xₜ₋₂
   where:
      β₋₅ = -1.191e-04   (t/z=-10.66, p=1.6e-26, p_fdr=1.8e-25) ***   [ETF leads]
      β₊₀ = -2.469e-04   (t/z=-5.65, p=1.7e-08, p_fdr=9.1e-08) ***   [contemporaneous]
      β₊₁ = -1.278e-04   (t/z=-5.26, p=1.4e-07, p_fdr=5.2e-07) ***   [Kalshi leads]
      β₊₂ = +4.278e-05   (t/z=+3.11, p=1.9e-03, p_fdr=5.2e-03) ***   [Kalshi leads]
   Lean by count of significant lags: Kalshi-leads  (k>0:2, k<0:1).

3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)
      k |       calendar b (FDR) |          event b (FDR)
   ------------------------------------------------------
     -5 |          -2.05e-05     |          -1.19e-04 ***
     -4 |          +2.37e-05     |          +1.50e-05    
     -3 |          -2.27e-06     |          -8.70e-06    
     -2 |          +2.83e-05     |          -3.68e-05    
     -1 |          -3.61e-05 *** |          -1.00e-04    
     +0 |          -2.22e-05     |          -2.47e-04 ***
     +1 |          -2.18e-05     |          -1.28e-04 ***
     +2 |          +5.85e-06     |          +4.28e-05 ***
     +3 |          -2.47e-05     |          +5.23e-05    
     +4 |          -7.65e-06     |          +5.71e-05    
     +5 |          -5.06e-05     |          +1.52e-04    
   (stars = BH-FDR corrected:  *** p_fdr<.01  ** <.05  * <.10)

4. DIRECTIONAL TEST (probit, ETF up/down)
   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k
   calendar: 13 lags tested, none significant after BH-FDR.
   event: 13 lags tested, none significant after BH-FDR.
   -> no significant directional predictability either mode (BH-FDR).

5. DATA RELIABILITY (statistical, not a trade-count cutoff)
   Tier: Adequate
   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)
   calendar(full RTH grid): n_active=51  n_obs=385  n_days=8  K=5  params=24  df=361  median_SE=2.50e-05  sig(FDR)=1
   event: n_active=35  n_obs=58  n_days=2  K=5  params=18  df=40  median_SE=4.37e-05  sig(FDR)=4

6. COARSE-FREQUENCY ROBUSTNESS (re-run calendar at 30min / 60min)
    30min: n_obs=31 df=15 K=5  sig=6 (Kalshi-leads 3 / ETF-leads 2) -> Kalshi-leads
    60min: n_obs=18 df=4 K=4  sig=1 (Kalshi-leads 0 / ETF-leads 1) -> ETF-leads

7. VERDICT
   Calendar leans ETF-leads but Event leans Kalshi-leads -- NOT robust across time-axis; no clean lead.

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