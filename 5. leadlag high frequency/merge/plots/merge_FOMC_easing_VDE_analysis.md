MERGE pseudo-pair:  FOMC_easing  ×  VDE

'Contract' = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level):
  +  FEDDECISION-24SEP-C25, RATECUT-24SEP18, KXFEDDECISION-24DEC-C25
  -  FEDDECISION-24NOV-H0, KXFEDDECISION-24DEC-H0   (reverse contracts: Δprob flipped)

Pooled regression vs this ETF (per-member FE, day-clustered SE, ADL self-lags by BIC).
Direction counts use RAW p (graded thresholds), k>0 Kalshi-leads / k<0 ETF-leads.

== CALENDAR (primary bar) ==
  K=10  ADL self-lags=0  n_obs=1790
  p<0.05: Kalshi-leads 3 / ETF-leads 1   p<0.10: Kalshi-leads 3 / ETF-leads 2   p<0.15: Kalshi-leads 5 / ETF-leads 3

== EVENT (active-event) ==
  K=10  ADL self-lags=0  n_obs=566
  p<0.05: Kalshi-leads 0 / ETF-leads 2   p<0.10: Kalshi-leads 0 / ETF-leads 3   p<0.15: Kalshi-leads 0 / ETF-leads 3

== PROBIT (Pr(ETF up)) ==
  K=10  ADL self-lags=-  n_obs=539
  p<0.05: Kalshi-leads 0 / ETF-leads 3   p<0.10: Kalshi-leads 1 / ETF-leads 5   p<0.15: Kalshi-leads 3 / ETF-leads 8

== Conclusion (calendar+event) ==
  p<0.05: balanced/none (K3/E3) | p<0.10: ETF-leads (K3/E5) | p<0.15: ETF-leads (K5/E6)