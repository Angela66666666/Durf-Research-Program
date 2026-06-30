MERGE super-signal:  GAS_above

Members pooled (sign-aligned Δprob, never concatenated price levels):
  +  AAAGASM-24OCT31-US-3.15, AAAGASM-24OCT31-US-3.20, AAAGASM-24SEP30-US-3.15, KXAAAGASM-24NOV30-US-3.30
  -  (none)
Relevant-ETF union (11): VAW, VCR, VDC, VDE, VFH, VGT, VHT, VIS, VNQ, VOX, VPU

Pooling engine: per-member lag/ADL shift, member fixed effects, day-clustered SE;
ADL self-lag order chosen per pooled regression by BIC (column n_ylags).
Direction counts below use RAW p (same graded-threshold convention as the single-pair report).

== CALENDAR (primary bar) ==
ETF      K  ADL   n_obs   Kalshi-leads(k>0) / ETF-leads(k<0)
VAW      4    1     334   p<0.05: K1/E0  p<0.10: K1/E0  p<0.15: K2/E1
VCR      4    3     334   p<0.05: K2/E1  p<0.10: K4/E1  p<0.15: K4/E1
VDC      4    2     334   p<0.05: K3/E2  p<0.10: K4/E2  p<0.15: K4/E2
VDE      4    1     334   p<0.05: K1/E0  p<0.10: K1/E0  p<0.15: K1/E0
VFH      4    1     334   p<0.05: K0/E1  p<0.10: K1/E1  p<0.15: K1/E1
VGT      4    1     334   p<0.05: K3/E3  p<0.10: K4/E3  p<0.15: K4/E3
VHT      4    1     334   p<0.05: K4/E1  p<0.10: K4/E1  p<0.15: K4/E1
VIS      4    1     334   p<0.05: K2/E2  p<0.10: K2/E3  p<0.15: K2/E3
VNQ      4    0     334   p<0.05: K1/E1  p<0.10: K1/E1  p<0.15: K1/E1
VOX      4    1     334   p<0.05: K2/E2  p<0.10: K3/E3  p<0.15: K4/E3
VPU      4    1     334   p<0.05: K2/E2  p<0.10: K3/E2  p<0.15: K3/E2

== EVENT (active-event subsequence) ==
ETF      K  ADL   n_obs   Kalshi-leads(k>0) / ETF-leads(k<0)
VAW      -    -        -   (no result)
VCR      -    -        -   (no result)
VDC      -    -        -   (no result)
VDE      -    -        -   (no result)
VFH      -    -        -   (no result)
VGT      -    -        -   (no result)
VHT      -    -        -   (no result)
VIS      -    -        -   (no result)
VNQ      -    -        -   (no result)
VOX      -    -        -   (no result)
VPU      -    -        -   (no result)

== PROBIT (direction test Pr(ETF up)) ==
ETF      K  ADL   n_obs   Kalshi-leads(k>0) / ETF-leads(k<0)
VAW      -    -        -   (no result)
VCR      -    -        -   (no result)
VDC      -    -        -   (no result)
VDE      -    -        -   (no result)
VFH      -    -        -   (no result)
VGT      -    -        -   (no result)
VHT      -    -        -   (no result)
VIS      -    -        -   (no result)
VNQ      -    -        -   (no result)
VOX      -    -        -   (no result)
VPU      -    -        -   (no result)

== Conclusion (calendar+event pooled across the group's ETFs) ==
  p<0.05: Kalshi-leads (K75/E69) | p<0.10: Kalshi-leads (K92/E78) | p<0.15: Kalshi-leads (K102/E89)
  Read alongside the single-pair tally; pooling buys df but the lead is in the sign, not magnitude.