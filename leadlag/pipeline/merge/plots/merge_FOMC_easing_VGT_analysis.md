MERGE pseudo-pair:  FOMC_easing  ×  VGT

'Contract' = combined super-signal (members' sign-aligned Δprob, pooled — NOT a price level):
  +  FEDDECISION-24SEP-C25, RATECUT-24SEP18, KXFEDDECISION-24DEC-C25
  -  FEDDECISION-24NOV-H0, KXFEDDECISION-24DEC-H0   (reverse contracts: Δprob flipped)

Pooled regression vs this ETF (per-member FE, day-clustered SE, ADL self-lags by BIC).
Direction counts use RAW p (graded thresholds), k>0 Kalshi-leads / k<0 ETF-leads.

== CALENDAR (primary bar) ==
  K=10  ADL self-lags=2  n_obs=1517
  p<0.05: Kalshi-leads 1 / ETF-leads 1   p<0.10: Kalshi-leads 1 / ETF-leads 1   p<0.15: Kalshi-leads 2 / ETF-leads 2

== EVENT (active-event) ==
  K=10  ADL self-lags=1  n_obs=547
  p<0.05: Kalshi-leads 0 / ETF-leads 1   p<0.10: Kalshi-leads 1 / ETF-leads 1   p<0.15: Kalshi-leads 2 / ETF-leads 1

== PROBIT (Pr(ETF up)) ==
  K=10  ADL self-lags=-  n_obs=530
  p<0.05: Kalshi-leads 2 / ETF-leads 2   p<0.10: Kalshi-leads 4 / ETF-leads 3   p<0.15: Kalshi-leads 4 / ETF-leads 3

== Conclusion (calendar+event) ==
  p<0.05: ETF-leads (K1/E2) | p<0.10: balanced/none (K2/E2) | p<0.15: Kalshi-leads (K4/E3)