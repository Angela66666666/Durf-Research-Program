MERGE super-signal:  APPROVAL_strength

Members pooled (sign-aligned Δprob, never concatenated price levels):
  +  538APPROVEMAX-24OCT31-T43, 538APPROVEMAX-24SEP30-T43, KX538APPROVEMAX-24NOV30-T41
  -  KX538APPROVEMIN-24NOV30-T37   (reverse contracts: Δprob flipped so +Δ = same direction)
Relevant-ETF union (8): VAW, VCR, VFH, VGT, VHT, VIS, VNQ, VOX

Pooling engine: per-member lag/ADL shift, member fixed effects, day-clustered SE;
ADL self-lag order chosen per pooled regression by BIC (column n_ylags).
Direction counts below use RAW p (same graded-threshold convention as the single-pair report).

== CALENDAR (primary bar) ==
ETF      K  ADL   n_obs   Kalshi-leads(k>0) / ETF-leads(k<0)
VAW      3    1    7058   p<0.05: K8/E0  p<0.10: K8/E1  p<0.15: K8/E2
VCR      3    1    7058   p<0.05: K0/E0  p<0.10: K2/E0  p<0.15: K2/E0
VFH      3    1    7059   p<0.05: K0/E2  p<0.10: K0/E2  p<0.15: K0/E2
VGT      3    1    7345   p<0.05: K5/E2  p<0.10: K5/E2  p<0.15: K7/E2
VHT      3    1    7188   p<0.05: K1/E1  p<0.10: K1/E1  p<0.15: K1/E1
VIS      3    1    7058   p<0.05: K2/E1  p<0.10: K2/E1  p<0.15: K4/E1
VNQ      3    1    7342   p<0.05: K1/E4  p<0.10: K2/E6  p<0.15: K2/E6
VOX      3    1    7091   p<0.05: K2/E1  p<0.10: K3/E1  p<0.15: K4/E2

== EVENT (active-event subsequence) ==
ETF      K  ADL   n_obs   Kalshi-leads(k>0) / ETF-leads(k<0)
VAW      -    -        -   (no result)
VCR      -    -        -   (no result)
VFH      -    -        -   (no result)
VGT      -    -        -   (no result)
VHT      -    -        -   (no result)
VIS      -    -        -   (no result)
VNQ      -    -        -   (no result)
VOX      -    -        -   (no result)

== PROBIT (direction test Pr(ETF up)) ==
ETF      K  ADL   n_obs   Kalshi-leads(k>0) / ETF-leads(k<0)
VAW      -    -        -   (no result)
VCR      -    -        -   (no result)
VFH      -    -        -   (no result)
VGT      -    -        -   (no result)
VHT      -    -        -   (no result)
VIS      -    -        -   (no result)
VNQ      -    -        -   (no result)
VOX      -    -        -   (no result)

== Conclusion (calendar+event pooled across the group's ETFs) ==
  p<0.05: Kalshi-leads (K19/E11) | p<0.10: Kalshi-leads (K23/E14) | p<0.15: Kalshi-leads (K28/E16)
  Read alongside the single-pair tally; pooling buys df but the lead is in the sign, not magnitude.