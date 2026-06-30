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
VAW      6    1     631   p<0.05: K1/E1  p<0.10: K1/E1  p<0.15: K2/E1
VCR      6    3     631   p<0.05: K0/E2  p<0.10: K0/E3  p<0.15: K0/E4
VDC      6    1     631   p<0.05: K2/E4  p<0.10: K2/E4  p<0.15: K3/E4
VDE      6    1     631   p<0.05: K4/E3  p<0.10: K4/E3  p<0.15: K4/E3
VFH      6    1     631   p<0.05: K0/E0  p<0.10: K1/E1  p<0.15: K1/E2
VGT      6    4     631   p<0.05: K2/E1  p<0.10: K2/E1  p<0.15: K2/E1
VIS      6    6     631   p<0.05: K3/E2  p<0.10: K3/E2  p<0.15: K4/E2
VNQ      6    3     631   p<0.05: K4/E3  p<0.10: K4/E3  p<0.15: K4/E3
VOX      6    1     631   p<0.05: K1/E3  p<0.10: K1/E4  p<0.15: K1/E5

== EVENT (active-event subsequence) ==
ETF      K  ADL   n_obs   Kalshi-leads(k>0) / ETF-leads(k<0)
VAW      8    0      62   p<0.05: K1/E1  p<0.10: K3/E3  p<0.15: K3/E4
VCR      8    0      62   p<0.05: K3/E5  p<0.10: K4/E5  p<0.15: K6/E5
VDC      8    1      62   p<0.05: K3/E2  p<0.10: K4/E2  p<0.15: K4/E3
VDE      8    0      62   p<0.05: K5/E6  p<0.10: K6/E6  p<0.15: K6/E6
VFH      8    1      62   p<0.05: K4/E4  p<0.10: K5/E5  p<0.15: K6/E5
VGT      8    0      62   p<0.05: K3/E3  p<0.10: K4/E4  p<0.15: K4/E4
VIS      8    2      62   p<0.05: K7/E1  p<0.10: K7/E1  p<0.15: K7/E1
VNQ      8    0      62   p<0.05: K3/E3  p<0.10: K3/E3  p<0.15: K3/E3
VOX      8    0      62   p<0.05: K1/E1  p<0.10: K3/E2  p<0.15: K3/E2

== PROBIT (direction test Pr(ETF up)) ==
ETF      K  ADL   n_obs   Kalshi-leads(k>0) / ETF-leads(k<0)
VAW      8    -      97   p<0.05: K7/E7  p<0.10: K7/E8  p<0.15: K7/E8
VCR      8    -      97   p<0.05: K7/E8  p<0.10: K7/E8  p<0.15: K8/E8
VDC      8    -      95   p<0.05: K7/E7  p<0.10: K10/E8  p<0.15: K12/E8
VDE      8    -      96   p<0.05: K5/E6  p<0.10: K6/E8  p<0.15: K6/E9
VFH      8    -      91   p<0.05: K4/E3  p<0.10: K8/E5  p<0.15: K9/E6
VGT      8    -      98   p<0.05: K7/E6  p<0.10: K9/E9  p<0.15: K9/E10
VIS      8    -      97   p<0.05: K7/E4  p<0.10: K7/E7  p<0.15: K8/E7
VNQ      8    -      95   p<0.05: K3/E7  p<0.10: K7/E9  p<0.15: K8/E9
VOX      8    -      94   p<0.05: K8/E9  p<0.10: K8/E9  p<0.15: K10/E10

== Conclusion (calendar+event pooled across the group's ETFs) ==
  p<0.05: Kalshi-leads (K189/E187) | p<0.10: Kalshi-leads (K214/E210) | p<0.15: Kalshi-leads (K234/E229)
  Read alongside the single-pair tally; pooling buys df but the lead is in the sign, not magnitude.