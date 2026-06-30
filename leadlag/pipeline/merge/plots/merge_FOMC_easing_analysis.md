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
VCR     10    1    1513   p<0.05: K0/E0  p<0.10: K1/E1  p<0.15: K1/E2
VDC     10    1    1513   p<0.05: K2/E2  p<0.10: K3/E3  p<0.15: K4/E4
VDE     10    0    1513   p<0.05: K2/E2  p<0.10: K3/E2  p<0.15: K4/E3
VFH     10    1    1513   p<0.05: K1/E1  p<0.10: K1/E1  p<0.15: K1/E1
VGT     10    2    1517   p<0.05: K1/E1  p<0.10: K1/E1  p<0.15: K2/E2
VIS     10    0    1513   p<0.05: K1/E2  p<0.10: K1/E2  p<0.15: K2/E2
VNQ     10    1    1517   p<0.05: K3/E1  p<0.10: K3/E1  p<0.15: K3/E2
VOX     10    1    1513   p<0.05: K2/E0  p<0.10: K2/E1  p<0.15: K3/E1
VPU     10    1    1513   p<0.05: K1/E3  p<0.10: K2/E3  p<0.15: K2/E4

== EVENT (active-event subsequence) ==
ETF      K  ADL   n_obs   Kalshi-leads(k>0) / ETF-leads(k<0)
VCR     10    1     547   p<0.05: K0/E1  p<0.10: K0/E1  p<0.15: K0/E1
VDC     10    1     547   p<0.05: K1/E0  p<0.10: K2/E1  p<0.15: K3/E1
VDE     10    0     547   p<0.05: K0/E1  p<0.10: K0/E1  p<0.15: K2/E4
VFH     10    1     547   p<0.05: K0/E0  p<0.10: K1/E0  p<0.15: K1/E0
VGT     10    1     547   p<0.05: K0/E1  p<0.10: K1/E1  p<0.15: K2/E1
VIS     10    1     547   p<0.05: K0/E0  p<0.10: K0/E1  p<0.15: K1/E1
VNQ     10    1     547   p<0.05: K1/E1  p<0.10: K2/E1  p<0.15: K2/E1
VOX     10    1     547   p<0.05: K1/E1  p<0.10: K3/E1  p<0.15: K3/E3
VPU     10    0     547   p<0.05: K0/E1  p<0.10: K1/E2  p<0.15: K3/E3

== PROBIT (direction test Pr(ETF up)) ==
ETF      K  ADL   n_obs   Kalshi-leads(k>0) / ETF-leads(k<0)
VCR     10    -     528   p<0.05: K3/E0  p<0.10: K4/E2  p<0.15: K5/E3
VDC     10    -     524   p<0.05: K1/E2  p<0.10: K3/E2  p<0.15: K3/E3
VDE     10    -     518   p<0.05: K0/E2  p<0.10: K3/E4  p<0.15: K4/E5
VFH     10    -     504   p<0.05: K4/E2  p<0.10: K6/E2  p<0.15: K8/E4
VGT     10    -     530   p<0.05: K2/E2  p<0.10: K4/E3  p<0.15: K4/E3
VIS     10    -     522   p<0.05: K1/E3  p<0.10: K3/E5  p<0.15: K5/E6
VNQ     10    -     507   p<0.05: K5/E3  p<0.10: K6/E4  p<0.15: K7/E5
VOX     10    -     511   p<0.05: K0/E0  p<0.10: K3/E1  p<0.15: K3/E3
VPU     10    -     519   p<0.05: K4/E2  p<0.10: K5/E3  p<0.15: K5/E5

== Conclusion (calendar+event pooled across the group's ETFs) ==
  p<0.05: ETF-leads (K54/E55) | p<0.10: Kalshi-leads (K85/E80) | p<0.15: ETF-leads (K105/E114)
  Read alongside the single-pair tally; pooling buys df but the lead is in the sign, not magnitude.