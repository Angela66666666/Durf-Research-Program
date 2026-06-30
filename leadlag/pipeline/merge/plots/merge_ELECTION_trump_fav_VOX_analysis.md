MERGE pseudo-pair:  ELECTION_trump_fav  ×  VOX

'Contract' = combined super-signal (members' sign-aligned Δprob, pooled — NOT a price level):
  +  KXECDJT281, KXECDJT306, KXECDJT312, KXECDJT316
  -  KXECKH276, KXECKH287   (reverse contracts: Δprob flipped)

Pooled regression vs this ETF (per-member FE, day-clustered SE, ADL self-lags by BIC).
Direction counts use RAW p (graded thresholds), k>0 Kalshi-leads / k<0 ETF-leads.

== CALENDAR (primary bar) ==
  K=6  ADL self-lags=1  n_obs=631
  p<0.05: Kalshi-leads 1 / ETF-leads 3   p<0.10: Kalshi-leads 1 / ETF-leads 4   p<0.15: Kalshi-leads 1 / ETF-leads 5

== EVENT (active-event) ==
  K=8  ADL self-lags=0  n_obs=62
  p<0.05: Kalshi-leads 1 / ETF-leads 1   p<0.10: Kalshi-leads 3 / ETF-leads 2   p<0.15: Kalshi-leads 3 / ETF-leads 2

== PROBIT (Pr(ETF up)) ==
  K=8  ADL self-lags=-  n_obs=94
  p<0.05: Kalshi-leads 8 / ETF-leads 9   p<0.10: Kalshi-leads 8 / ETF-leads 9   p<0.15: Kalshi-leads 10 / ETF-leads 10

== Conclusion (calendar+event) ==
  p<0.05: ETF-leads (K2/E4) | p<0.10: ETF-leads (K4/E6) | p<0.15: ETF-leads (K4/E7)