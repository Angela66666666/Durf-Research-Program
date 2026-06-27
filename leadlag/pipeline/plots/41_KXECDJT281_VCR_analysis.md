PAIR ANALYSIS    —    Rank 16 / 48
================================================================================================
KXECDJT281   x   VCR
Contract : "Will Trump win 281-257 - AZ, GA, NC, PA?"
Sector relevance : Election outcome (all sectors)
Window : 2024-11-04 to 2024-11-25     Kalshi trades : 294     primary bar : 5min     daily-screen R^2 : 0.28

>>> RELIABILITY:  Adequate   <<<   (see section 5; unreliable pairs still get figures, but read their problems in section 8)

DEFINITIONS
   xₜ₋ₖ = Kalshi yes-probability change, k bars before t   (1 bar = 5min)
   yₜ   = ETF log return over bar t
   calendar = full market-hours grid: x=0 in bars with no Kalshi trade (not dropped).
   k>0 => Kalshi leads ETF ;  k<0 => ETF leads Kalshi ;  k=0 => contemporaneous

1. CALENDAR-TIME REGRESSION (clock-time lags, full RTH grid)
   Full model: yₜ = α + Σₖ βₖ·xₜ₋ₖ + Σᵢ φᵢ·yₜ₋ᵢ (ADL self-control) + day-FE
   -> 11 coefficients tested, NONE significant after BH-FDR (p_fdr<0.05).

2. EVENT-TIME REGRESSION (event-count lags)
   Full model: yₜ = α + Σₖ βₖ·xₜ₋ₖ + Σᵢ φᵢ·yₜ₋ᵢ (ADL self-control) + day-FE
   Significant terms (BH-FDR) expanded:  yₜ = α + β₋₆·xₜ₊₆ + β₋₁·xₜ₊₁
   where:
      β₋₆ = +3.278e-05   (t/z=+2.68, p=7.5e-03, p_fdr=4.9e-02) **   [ETF leads]
      β₋₁ = +4.530e-05   (t/z=+2.79, p=5.3e-03, p_fdr=4.9e-02) **   [ETF leads]
   Lean by count of significant lags: ETF-leads  (k>0:0, k<0:2).

3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)
      k |       calendar b (FDR) |          event b (FDR)
   ------------------------------------------------------
     -6 |                     -- |          +3.28e-05 ** 
     -5 |          -1.45e-05     |          -2.65e-05    
     -4 |          +1.04e-05     |          -1.18e-05    
     -3 |          +3.66e-05     |          -4.00e-05    
     -2 |          +2.84e-05     |          +3.92e-05    
     -1 |          +6.96e-06     |          +4.53e-05 ** 
     +0 |          -1.02e-05     |          -8.21e-06    
     +1 |          -9.95e-06     |          +2.17e-05    
     +2 |          -5.99e-06     |          -6.96e-05    
     +3 |          +1.58e-05     |          +7.90e-06    
     +4 |          +2.78e-05     |          +5.20e-05    
     +5 |          -2.40e-06     |          +4.38e-05    
     +6 |                     -- |          +7.83e-05    
   (stars = BH-FDR corrected:  *** p_fdr<.01  ** <.05  * <.10)

4. DIRECTIONAL TEST (probit, ETF up/down)
   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k
   calendar: 13 lags tested, none significant after BH-FDR.
   event: β₋₂=+1.90e-01***, β₊₆=+1.44e-01***

5. DATA RELIABILITY (statistical, not a trade-count cutoff)
   Tier: Adequate
   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)
   calendar(full RTH grid): n_active=51  n_obs=385  n_days=8  K=5  params=24  df=361  median_SE=2.74e-05  sig(FDR)=0
   event: n_active=65  n_obs=106  n_days=2  K=6  params=20  df=86  median_SE=4.99e-05  sig(FDR)=2

6. COARSE-FREQUENCY ROBUSTNESS (re-run calendar at 30min / 60min)
    30min: n_obs=31 df=15 K=5  sig=7 (Kalshi-leads 4 / ETF-leads 2) -> Kalshi-leads
    60min: n_obs=18 df=4 K=4  sig=0 (Kalshi-leads 0 / ETF-leads 0) -> No-sig

7. VERDICT
   Only one time-axis significant (ETF-leads) -- weak / single-mode evidence.

8. FIGURE CAVEATS — figures are still drawn, but know their problems
   - Adequate info: figures and regression are mutually readable; note that flat Kalshi segments still mean 'no trade', not 'no change'.
   - Kalshi updates only on trades (flat line = no trade, NOT 'no change'); ETF mid refreshes continuously.

9. REAL-WORLD CONTEXT (WebSearch-verified; see URLs)
   - 2024 US presidential election held Tue Nov 5, 2024; ballots counted overnight Nov 5-6.
   - AP called the race for Trump ~5:34-5:37 AM ET on Wed Nov 6, 2024 (Wisconsin pushed him past 270) -- this is PRE-MARKET, so the regular-hours equity reaction shows up at the Nov 6 open.
   - Final electoral result: Trump 312, Harris 226.
   - Sources: en.wikipedia.org/wiki/2024_United_States_presidential_election ; spectrumlocalnews.com/us/snplus/news/2024/11/06/trump-wins-ap-projection-2024-election

------------------------------------------------------------------------------------------------
Conventions: ET | 09:30-16:00 (forward windows capped to 16:00) | ETF in log return | median causal bars | full RTH grid | day-grouped lags (no overnight) | ADL self-control | significance = BH-FDR corrected.
Figures for this pair follow on the next page.