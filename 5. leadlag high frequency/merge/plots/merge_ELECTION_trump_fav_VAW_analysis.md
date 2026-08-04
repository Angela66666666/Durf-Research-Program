MERGE pseudo-pair:  ELECTION_trump_fav  ×  VAW

'Contract' = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level):
  +  KXECDJT281, KXECDJT306, KXECDJT312, KXECDJT316
  -  KXECKH276, KXECKH287   (reverse contracts: Δprob flipped)

Pooled regression vs this ETF (per-member FE, day-clustered SE, ADL self-lags by BIC).
Direction counts use RAW p (graded thresholds), k>0 Kalshi-leads / k<0 ETF-leads.

== CALENDAR (primary bar) ==
  K=6  ADL self-lags=1  n_obs=909
  p<0.05: Kalshi-leads 1 / ETF-leads 1   p<0.10: Kalshi-leads 1 / ETF-leads 2   p<0.15: Kalshi-leads 3 / ETF-leads 2

== EVENT (active-event) ==
  K=8  ADL self-lags=0  n_obs=65
  p<0.05: Kalshi-leads 2 / ETF-leads 1   p<0.10: Kalshi-leads 2 / ETF-leads 1   p<0.15: Kalshi-leads 3 / ETF-leads 3

== PROBIT (Pr(ETF up)) ==
  K=8  ADL self-lags=-  n_obs=105
  p<0.05: Kalshi-leads 6 / ETF-leads 7   p<0.10: Kalshi-leads 6 / ETF-leads 9   p<0.15: Kalshi-leads 7 / ETF-leads 9

== Conclusion (calendar+event) ==
  p<0.05: Kalshi-leads (K3/E2) | p<0.10: balanced/none (K3/E3) | p<0.15: Kalshi-leads (K6/E5)