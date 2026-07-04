MERGE super-signal:  FOMC_easing

Members pooled (sign-aligned Δprob, never concatenated price levels):
  +  FEDDECISION-24SEP-C25, RATECUT-24SEP18, KXFEDDECISION-24DEC-C25
  -  FEDDECISION-24NOV-H0, KXFEDDECISION-24DEC-H0   (reverse contracts: Δprob flipped so +Δ = same direction)
Relevant-ETF union (9): VCR, VDC, VDE, VFH, VGT, VIS, VNQ, VOX, VPU

Pooling engine: per-member lag/ADL shift, member fixed effects, day-clustered SE;
ADL self-lag order chosen per pooled regression by BIC (column n_ylags).
Direction counts below use RAW p (same graded-threshold convention as the single-pair report).

== CALENDAR (primary bar) ==
ETF      K  ADL   n_obs   Kalshi-leads(k>0) / ETF-leads(k<0)
VCR     10    1    1790   p<0.05: K1/E0  p<0.10: K3/E2  p<0.15: K3/E2
VDC     10    1    1790   p<0.05: K2/E2  p<0.10: K3/E2  p<0.15: K3/E2
VDE     10    0    1790   p<0.05: K3/E1  p<0.10: K3/E2  p<0.15: K5/E3
VFH     10    1    1790   p<0.05: K1/E1  p<0.10: K2/E1  p<0.15: K2/E1
VGT     10    1    1794   p<0.05: K1/E1  p<0.10: K4/E1  p<0.15: K4/E2
VIS     10    0    1790   p<0.05: K2/E2  p<0.10: K2/E2  p<0.15: K4/E2
VNQ     10    0    1794   p<0.05: K3/E1  p<0.10: K4/E2  p<0.15: K7/E2
VOX     10    1    1790   p<0.05: K2/E0  p<0.10: K3/E0  p<0.15: K4/E1
VPU     10    1    1790   p<0.05: K2/E5  p<0.10: K4/E6  p<0.15: K4/E6

== EVENT (active-event subsequence) ==
ETF      K  ADL   n_obs   Kalshi-leads(k>0) / ETF-leads(k<0)
VCR     10    1     566   p<0.05: K0/E1  p<0.10: K0/E1  p<0.15: K0/E2
VDC     10    1     566   p<0.05: K1/E1  p<0.10: K2/E1  p<0.15: K4/E1
VDE     10    0     566   p<0.05: K0/E2  p<0.10: K0/E3  p<0.15: K0/E3
VFH     10    1     566   p<0.05: K1/E0  p<0.10: K1/E0  p<0.15: K1/E1
VGT     10    1     566   p<0.05: K1/E1  p<0.10: K2/E1  p<0.15: K2/E1
VIS     10    1     566   p<0.05: K0/E0  p<0.10: K1/E1  p<0.15: K2/E2
VNQ     10    1     566   p<0.05: K1/E0  p<0.10: K2/E1  p<0.15: K2/E1
VOX     10    1     566   p<0.05: K2/E1  p<0.10: K4/E2  p<0.15: K4/E2
VPU     10    0     566   p<0.05: K0/E1  p<0.10: K3/E2  p<0.15: K3/E3

== PROBIT (direction test Pr(ETF up)) ==
ETF      K  ADL   n_obs   Kalshi-leads(k>0) / ETF-leads(k<0)
VCR     10    -     550   p<0.05: K3/E0  p<0.10: K3/E1  p<0.15: K6/E2
VDC     10    -     546   p<0.05: K1/E2  p<0.10: K2/E2  p<0.15: K3/E2
VDE     10    -     539   p<0.05: K0/E3  p<0.10: K1/E5  p<0.15: K3/E8
VFH     10    -     527   p<0.05: K5/E2  p<0.10: K6/E4  p<0.15: K7/E5
VGT     10    -     553   p<0.05: K1/E2  p<0.10: K3/E3  p<0.15: K5/E4
VIS     10    -     544   p<0.05: K1/E1  p<0.10: K4/E4  p<0.15: K5/E5
VNQ     10    -     529   p<0.05: K4/E2  p<0.10: K6/E3  p<0.15: K6/E4
VOX     10    -     532   p<0.05: K1/E0  p<0.10: K2/E1  p<0.15: K3/E1
VPU     10    -     541   p<0.05: K5/E2  p<0.10: K6/E2  p<0.15: K6/E3

== Conclusion (calendar+event pooled across the group's ETFs) ==
  p<0.05: ETF-leads (K54/E55) | p<0.10: Kalshi-leads (K95/E88) | p<0.15: Kalshi-leads (K123/E112)
  Read alongside the single-pair tally; pooling buys df but the lead is in the sign, not magnitude.