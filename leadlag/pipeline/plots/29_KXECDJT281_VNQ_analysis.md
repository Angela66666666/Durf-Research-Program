PAIR ANALYSIS    —    Rank 2 / 48
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
   Full model: yₜ = α + Σₖ βₖ·xₜ₋ₖ + Σᵢ φᵢ·yₜ₋ᵢ (ADL self-control) + day-FE
   Significant terms (BH-FDR) expanded:  yₜ = α + β₋₃·xₜ₊₃ + β₋₂·xₜ₊₂ + β₊₁·xₜ₋₁
   where:
      β₋₃ = -3.902e-05   (t/z=-3.20, p=1.4e-03, p_fdr=5.0e-03) ***   [ETF leads]
      β₋₂ = +9.541e-05   (t/z=+7.47, p=7.8e-14, p_fdr=8.6e-13) ***   [ETF leads]
      β₊₁ = +7.377e-05   (t/z=+3.79, p=1.5e-04, p_fdr=8.4e-04) ***   [Kalshi leads]
   Lean by count of significant lags: ETF-leads  (k>0:1, k<0:2).

2. EVENT-TIME REGRESSION (event-count lags)
   Full model: yₜ = α + Σₖ βₖ·xₜ₋ₖ + Σᵢ φᵢ·yₜ₋ᵢ (ADL self-control) + day-FE
   Significant terms (BH-FDR) expanded:  yₜ = α + β₋₃·xₜ₊₃ + β₊₂·xₜ₋₂ + β₊₄·xₜ₋₄
   where:
      β₋₃ = -1.241e-04   (t/z=-3.37, p=7.5e-04, p_fdr=4.1e-03) ***   [ETF leads]
      β₊₂ = +4.193e-04   (t/z=+2.84, p=4.5e-03, p_fdr=1.6e-02) **   [Kalshi leads]
      β₊₄ = +9.013e-05   (t/z=+10.19, p=2.2e-24, p_fdr=2.4e-23) ***   [Kalshi leads]
   Lean by count of significant lags: Kalshi-leads  (k>0:2, k<0:1).

3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)
      k |       calendar b (FDR) |          event b (FDR)
   ------------------------------------------------------
     -5 |          -4.44e-06     |          -6.16e-05    
     -4 |          -2.02e-05     |          -1.07e-04 *  
     -3 |          -3.90e-05 *** |          -1.24e-04 ***
     -2 |          +9.54e-05 *** |          -2.38e-04    
     -1 |          +1.22e-04     |          +1.28e-04    
     +0 |          -1.59e-05     |          +5.09e-05    
     +1 |          +7.38e-05 *** |          +2.56e-04    
     +2 |          +7.73e-06     |          +4.19e-04 ** 
     +3 |          +1.99e-05     |          +2.54e-04    
     +4 |          -1.52e-06     |          +9.01e-05 ***
     +5 |          +1.19e-05     |          +7.32e-05    
   (stars = BH-FDR corrected:  *** p_fdr<.01  ** <.05  * <.10)

4. DIRECTIONAL TEST (probit, ETF up/down)
   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k
   calendar: 13 lags tested, none significant after BH-FDR.
   event: 13 lags tested, none significant after BH-FDR.
   -> no significant directional predictability either mode (BH-FDR).

5. DATA RELIABILITY (statistical, not a trade-count cutoff)
   Tier: Adequate
   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)
   calendar(full RTH grid): n_active=51  n_obs=385  n_days=8  K=5  params=24  df=361  median_SE=2.18e-05  sig(FDR)=3
   event: n_active=35  n_obs=58  n_days=2  K=5  params=18  df=40  median_SE=1.31e-04  sig(FDR)=3

6. COARSE-FREQUENCY ROBUSTNESS (re-run calendar at 30min / 60min)
    30min: n_obs=31 df=15 K=5  sig=4 (Kalshi-leads 3 / ETF-leads 1) -> Kalshi-leads
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