PAIR ANALYSIS    —    Rank 41 / 48
================================================================================================
538APPROVEMAX-24SEP30-T43   x   VCR
Contract : "Will the President's approval rating ever get above 43% by Sep 30, 2024?"
Sector relevance : Election outcome (all sectors)
Window : 2024-09-04 to 2024-09-30     Kalshi trades : 17     primary bar : n/a     daily-screen R^2 : 0.27

>>> RELIABILITY:  Cannot-estimate   <<<   (see section 5; unreliable pairs still get figures, but read their problems in section 8)

DEFINITIONS
   xₜ₋ₖ = Kalshi yes-probability change, k bars before t   (1 bar = n/a)
   yₜ   = ETF log return over bar t
   calendar = full market-hours grid: x=0 in bars with no Kalshi trade (not dropped).
   k>0 => Kalshi leads ETF ;  k<0 => ETF leads Kalshi ;  k=0 => contemporaneous

1. CALENDAR-TIME REGRESSION (clock-time lags, full RTH grid)
   Full model:  yₜ = α + Σ(k) βₖ·xₜ₋ₖ + (ADL self-lags) + (day fixed effects)
   -> no regression result (insufficient data).

2. EVENT-TIME REGRESSION (event-count lags)
   Full model:  yₜ = α + Σ(k) βₖ·xₜ₋ₖ + (ADL self-lags) + (day fixed effects)
   -> no regression result (insufficient data).

3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)
   (no coefficients in either mode)

4. DIRECTIONAL TEST (probit, ETF up/down)
   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k
   calendar: n/a
   event: n/a
   -> no significant directional predictability either mode (raw p<0.15).

5. DATA RELIABILITY (statistical, not a trade-count cutoff)
   Tier: Cannot-estimate
   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)
   calendar(full RTH grid): not estimable (insufficient data)
   event: not estimable (insufficient data)
   => Neither axis is estimable: this pair has descriptive figures only, no reliable regression result.

6. COARSE-FREQUENCY ROBUSTNESS (re-run calendar at 30min / 60min)
    30min: not estimable (n_obs=1 < minimum) -- coarser bars have even fewer observations
    60min: not estimable (n_obs=1 < minimum) -- coarser bars have even fewer observations

7. VERDICT
   No lead-lag detected -- too sparse / no significant structure.
   (Note: this pair lacks the data to support reliable inference; the verdict above is descriptive only -- do not put it in the conclusions.)

8. FIGURE CAVEATS — figures are still drawn, but know their problems
   - Regression cannot be estimated: the lag-coefficient plot (B) shows 'no regression result'; only the time-series / zoom plots are descriptive.
   - Long flat Kalshi segments = NO TRADE in that span (not 'probability unchanged'); do not read lead direction from them.
   - Too few active bars: the red/blue lead shading in zoom2/segments and the K#/E# pairing in leadglance are illustrative only, with no statistical meaning.
   - Kalshi updates only on trades (flat line = no trade, NOT 'no change'); ETF mid refreshes continuously.

------------------------------------------------------------------------------------------------
Conventions: ET | 09:30-16:00 (forward windows capped to 16:00) | ETF in log return | median causal bars | full RTH grid | day-grouped lags (no overnight) | ADL self-control | significance = BH-FDR corrected.
Figures for this pair follow on the next page.