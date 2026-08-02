MERGE pooled signal:  APPROVAL_strength

Members pooled (sign-aligned Δprob, never concatenated price levels):
  +  538APPROVEMAX-24OCT31-T43, 538APPROVEMAX-24SEP30-T43, KX538APPROVEMAX-24NOV30-T41
  -  KX538APPROVEMIN-24NOV30-T37   (reverse contracts: Δprob flipped so +Δ = same direction)
Relevant-ETF union (8): VAW, VCR, VFH, VGT, VHT, VIS, VNQ, VOX

Pooling engine: per-member lag/ADL shift, member fixed effects, day-clustered SE;
ADL self-lag order chosen per pooled regression by BIC (column n_ylags).
Direction counts below use RAW p (same graded-threshold convention as the single-pair report).

== CALENDAR (primary bar) ==
ETF      K  ADL   n_obs   Kalshi-leads(k>0) / ETF-leads(k<0)
VAW      4    1     450   p<0.05: K1/E1  p<0.10: K1/E1  p<0.15: K1/E1
VCR      4    1     450   p<0.05: K1/E1  p<0.10: K1/E1  p<0.15: K1/E1
VFH      4    1     450   p<0.05: K0/E1  p<0.10: K0/E1  p<0.15: K0/E1
VGT      4    1     464   p<0.05: K1/E1  p<0.10: K1/E2  p<0.15: K1/E2
VHT      4    1     456   p<0.05: K0/E1  p<0.10: K0/E1  p<0.15: K2/E1
VIS      4    0     450   p<0.05: K1/E1  p<0.10: K1/E1  p<0.15: K1/E1
VNQ      4    0     464   p<0.05: K0/E0  p<0.10: K0/E1  p<0.15: K0/E1
VOX      4    1     452   p<0.05: K2/E0  p<0.10: K2/E0  p<0.15: K2/E1

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
  p<0.05: Kalshi-leads (K29/E25) | p<0.10: Kalshi-leads (K36/E31) | p<0.15: Kalshi-leads (K48/E35)
  Read alongside the single-pair tally; pooling buys df but the lead is in the sign, not magnitude.