PAIR ANALYSIS    —    Rank 1 / 48
================================================================================================
KXECDJT281   x   VOX
Contract : "Will Trump win 281-257 - AZ, GA, NC, PA?"
Sector relevance : Election outcome (all sectors)
Window : 2024-11-04 to 2024-11-25     Kalshi trades : 294     primary bar : 5min     daily-screen R^2 : 0.33

>>> RELIABILITY:  Adequate   <<<   (see section 5; unreliable pairs still get figures, but read their problems in section 8)

DEFINITIONS
   xₜ₋ₖ = Kalshi yes-probability change, k bars before t   (1 bar = 5min)
   yₜ   = ETF log return over bar t
   calendar = full market-hours grid: x=0 in bars with no Kalshi trade (not dropped).
   k>0 => Kalshi leads ETF ;  k<0 => ETF leads Kalshi ;  k=0 => contemporaneous

1. CALENDAR-TIME REGRESSION (clock-time lags, full RTH grid)
   Full model: yₜ = α + Σₖ βₖ·xₜ₋ₖ + Σᵢ φᵢ·yₜ₋ᵢ (ADL self-control) + day-FE
   Significant terms (BH-FDR) expanded:  yₜ = α + β₋₃·xₜ₊₃ + β₋₂·xₜ₊₂ + β₊₃·xₜ₋₃
   where:
      β₋₃ = +3.884e-05   (t/z=+4.51, p=6.4e-06, p_fdr=7.1e-05) ***   [ETF leads]
      β₋₂ = +6.175e-05   (t/z=+3.91, p=9.2e-05, p_fdr=5.0e-04) ***   [ETF leads]
      β₊₃ = +4.123e-05   (t/z=+3.42, p=6.4e-04, p_fdr=2.3e-03) ***   [Kalshi leads]
   Lean by count of significant lags: ETF-leads  (k>0:1, k<0:2).

2. EVENT-TIME REGRESSION (event-count lags)
   Full model: yₜ = α + Σₖ βₖ·xₜ₋ₖ + Σᵢ φᵢ·yₜ₋ᵢ (ADL self-control) + day-FE
   Significant terms (BH-FDR) expanded:  yₜ = α + β₋₅·xₜ₊₅ + β₋₁·xₜ₊₁ + β₊₄·xₜ₋₄ + β₊₅·xₜ₋₅
   where:
      β₋₅ = -5.688e-05   (t/z=-3.15, p=1.7e-03, p_fdr=7.2e-03) ***   [ETF leads]
      β₋₁ = +3.281e-05   (t/z=+3.42, p=6.2e-04, p_fdr=4.0e-03) ***   [ETF leads]
      β₊₄ = +9.501e-05   (t/z=+2.52, p=1.2e-02, p_fdr=3.8e-02) **   [Kalshi leads]
      β₊₅ = +1.075e-04   (t/z=+5.05, p=4.4e-07, p_fdr=5.7e-06) ***   [Kalshi leads]
   Lean by count of significant lags: balanced/no clear side  (k>0:2, k<0:2).

3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)
      k |       calendar b (FDR) |          event b (FDR)
   ------------------------------------------------------
     -6 |                     -- |          +5.23e-05 *  
     -5 |          +1.97e-05     |          -5.69e-05 ***
     -4 |          +8.75e-06     |          -4.41e-05    
     -3 |          +3.88e-05 *** |          -8.21e-05    
     -2 |          +6.18e-05 *** |          +5.78e-06    
     -1 |          +1.63e-05     |          +3.28e-05 ***
     +0 |          +2.86e-05     |          -1.62e-05    
     +1 |          -1.99e-06     |          +1.76e-05    
     +2 |          +2.81e-05     |          +3.40e-05    
     +3 |          +4.12e-05 *** |          +3.45e-05    
     +4 |          -5.87e-07     |          +9.50e-05 ** 
     +5 |          -3.26e-05     |          +1.08e-04 ***
     +6 |                     -- |          +1.03e-04    
   (stars = BH-FDR corrected:  *** p_fdr<.01  ** <.05  * <.10)

4. DIRECTIONAL TEST (probit, ETF up/down)
   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k
   calendar: β₋₁=+2.82e-01***
   event: β₋₆=+1.36e-01***, β₋₅=-1.16e-01***, β₋₄=+1.19e-01**, β₊₁=+1.05e-01**, β₊₃=-1.26e-01**, β₊₆=+1.37e-01**

5. DATA RELIABILITY (statistical, not a trade-count cutoff)
   Tier: Adequate
   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)
   calendar(full RTH grid): n_active=51  n_obs=385  n_days=8  K=5  params=24  df=361  median_SE=1.34e-05  sig(FDR)=3
   event: n_active=65  n_obs=106  n_days=2  K=6  params=20  df=86  median_SE=3.76e-05  sig(FDR)=4

6. COARSE-FREQUENCY ROBUSTNESS (re-run calendar at 30min / 60min)
    30min: n_obs=31 df=15 K=5  sig=5 (Kalshi-leads 2 / ETF-leads 3) -> ETF-leads
    60min: n_obs=18 df=4 K=4  sig=2 (Kalshi-leads 2 / ETF-leads 0) -> Kalshi-leads

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