MERGE super-signal:  ELECTION_trump_fav

Members pooled (sign-aligned Δprob, never concatenated price levels):
  +  KXECDJT281, KXECDJT306, KXECDJT312, KXECDJT316
  -  KXECKH276, KXECKH287   (reverse contracts: Δprob flipped so +Δ = same direction)
Relevant-ETF union (9): VAW, VCR, VDC, VDE, VFH, VGT, VIS, VNQ, VOX

Pooling engine: per-member lag/ADL shift, member fixed effects, day-clustered SE;
ADL self-lag order chosen per pooled regression by BIC (column n_ylags).
Direction counts below use RAW p (same graded-threshold convention as the single-pair report).

== CALENDAR (primary bar) ==
ETF      K  ADL   n_obs   Kalshi-leads(k>0) / ETF-leads(k<0)
VAW      6    1     909   p<0.05: K1/E1  p<0.10: K1/E2  p<0.15: K3/E2
VCR      6    3     909   p<0.05: K1/E2  p<0.10: K1/E2  p<0.15: K1/E3
VDC      6    2     909   p<0.05: K2/E4  p<0.10: K3/E4  p<0.15: K3/E5
VDE      6    1     909   p<0.05: K4/E3  p<0.10: K5/E3  p<0.15: K5/E3
VFH      6    1     909   p<0.05: K1/E1  p<0.10: K2/E1  p<0.15: K2/E1
VGT      6    4     909   p<0.05: K1/E2  p<0.10: K2/E2  p<0.15: K2/E2
VIS      6    6     909   p<0.05: K2/E2  p<0.10: K3/E2  p<0.15: K3/E3
VNQ      6    2     909   p<0.05: K3/E3  p<0.10: K4/E3  p<0.15: K4/E3
VOX      6    2     909   p<0.05: K1/E4  p<0.10: K1/E4  p<0.15: K1/E4

== EVENT (active-event subsequence) ==
ETF      K  ADL   n_obs   Kalshi-leads(k>0) / ETF-leads(k<0)
VAW      8    0      65   p<0.05: K2/E1  p<0.10: K2/E1  p<0.15: K3/E3
VCR      8    0      65   p<0.05: K4/E5  p<0.10: K5/E5  p<0.15: K5/E5
VDC      8    2      65   p<0.05: K0/E2  p<0.10: K1/E3  p<0.15: K1/E3
VDE      8    0      65   p<0.05: K4/E4  p<0.10: K4/E4  p<0.15: K6/E4
VFH      8    0      65   p<0.05: K5/E4  p<0.10: K5/E5  p<0.15: K6/E6
VGT      8    0      65   p<0.05: K4/E2  p<0.10: K4/E2  p<0.15: K4/E3
VIS      8    0      65   p<0.05: K7/E1  p<0.10: K7/E1  p<0.15: K7/E2
VNQ      8    0      65   p<0.05: K3/E2  p<0.10: K3/E2  p<0.15: K3/E4
VOX      8    0      65   p<0.05: K3/E2  p<0.10: K3/E2  p<0.15: K3/E2

== PROBIT (direction test Pr(ETF up)) ==
ETF      K  ADL   n_obs   Kalshi-leads(k>0) / ETF-leads(k<0)
VAW      8    -     105   p<0.05: K6/E7  p<0.10: K6/E9  p<0.15: K7/E9
VCR      8    -     105   p<0.05: K7/E7  p<0.10: K8/E8  p<0.15: K9/E8
VDC      8    -     101   p<0.05: K7/E8  p<0.10: K8/E8  p<0.15: K9/E8
VDE      8    -     104   p<0.05: K5/E5  p<0.10: K5/E8  p<0.15: K7/E8
VFH      8    -      98   p<0.05: K6/E4  p<0.10: K7/E5  p<0.15: K7/E5
VGT      8    -     106   p<0.05: K6/E5  p<0.10: K8/E8  p<0.15: K10/E8
VIS      8    -     105   p<0.05: K6/E3  p<0.10: K7/E5  p<0.15: K8/E6
VNQ      8    -     102   p<0.05: K3/E7  p<0.10: K7/E8  p<0.15: K9/E9
VOX      8    -     102   p<0.05: K8/E7  p<0.10: K8/E9  p<0.15: K9/E9

== Conclusion (calendar+event pooled across the group's ETFs) ==
  p<0.05: Kalshi-leads (K201/E187) | p<0.10: Kalshi-leads (K224/E207) | p<0.15: Kalshi-leads (K245/E225)
  Read alongside the single-pair tally; pooling buys df but the lead is in the sign, not magnitude.