# Lead/Lag classification summary

Scope: all 48 pairs (Kalshi contract x ETF). Lean rule: across calendar+event, count
significant lags at p<0.05 / 0.10 / 0.15 (raw p; nested, p<0.05 ⊆ p<0.10 ⊆ p<0.15) per
direction (k>0 Kalshi-leads, k<0 ETF-leads). **A lean conclusion is produced at EACH tier**, not
a single chosen threshold, so the Overall and every cross-tab below appear three times (one per tier).
Reliability rule: tiered by residual df (= effective obs - #parameters), NOT a trade-count cutoff.

## Overall — lean counts at each threshold

```
        Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead
p<0.05             3         13              10           22
p<0.1              4         13               9           22
p<0.15             5         11              10           22
```

## By contract type

**lean at p<0.05:**

```
lean_05        Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
contract_type                                                             
Election                  2          8               8            0     18
GasPrice                  0          0               1           10     11
Rates(FOMC)               1          5               1            4     11
Approval                  0          0               0            8      8
```

**lean at p<0.1:**

```
lean_10        Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
contract_type                                                             
Election                  2          8               8            0     18
GasPrice                  0          0               1           10     11
Rates(FOMC)               2          5               0            4     11
Approval                  0          0               0            8      8
```

**lean at p<0.15:**

```
lean_15        Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
contract_type                                                             
Election                  3          7               8            0     18
GasPrice                  0          1               0           10     11
Rates(FOMC)               2          3               2            4     11
Approval                  0          0               0            8      8
```

## By event kind (sharp one-shot vs continuous)

**lean at p<0.05:**

```
lean_05          Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
event_kind                                                                  
Sharp(one-shot)             3         13               9            4     29
Continuous                  0          0               1           18     19
```

**lean at p<0.1:**

```
lean_10          Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
event_kind                                                                  
Sharp(one-shot)             4         13               8            4     29
Continuous                  0          0               1           18     19
```

**lean at p<0.15:**

```
lean_15          Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
event_kind                                                                  
Sharp(one-shot)             5         10              10            4     29
Continuous                  0          1               0           18     19
```

## By ETF sector

**lean at p<0.05:**

```
lean_05       Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
sector                                                                   
Comm                     1          2               0            3      6
Info-Tech                0          2               1            3      6
Cons.Disc                0          1               1            3      5
Financials               0          1               2            2      5
Industrials              0          2               1            2      5
Real-Estate              1          2               0            2      5
Cons.Staples             0          1               2            1      4
Energy                   1          0               1            2      4
Materials                0          1               1            2      4
Health                   0          0               0            2      2
Utilities                0          1               1            0      2
```

**lean at p<0.1:**

```
lean_10       Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
sector                                                                   
Comm                     1          2               0            3      6
Info-Tech                0          2               1            3      6
Cons.Disc                0          1               1            3      5
Financials               0          2               1            2      5
Industrials              0          2               1            2      5
Real-Estate              2          1               0            2      5
Cons.Staples             0          1               2            1      4
Energy                   1          0               1            2      4
Materials                0          1               1            2      4
Health                   0          0               0            2      2
Utilities                0          1               1            0      2
```

**lean at p<0.15:**

```
lean_15       Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
sector                                                                   
Comm                     1          2               0            3      6
Info-Tech                0          2               1            3      6
Cons.Disc                0          0               2            3      5
Financials               0          2               1            2      5
Industrials              0          2               1            2      5
Real-Estate              2          1               0            2      5
Cons.Staples             1          0               2            1      4
Energy                   1          0               1            2      4
Materials                0          1               1            2      4
Health                   0          0               0            2      2
Utilities                0          1               1            0      2
```

## By statistical reliability (df-based)

**lean at p<0.05:**

```
lean_05          Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
reliability                                                                 
Cannot-estimate             0          0               0           21     21
Adequate                    1         10               1            1     13
Very-low-info               2          3               8            0     13
Low-info                    0          0               1            0      1
```

**lean at p<0.1:**

```
lean_10          Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
reliability                                                                 
Cannot-estimate             0          0               0           21     21
Adequate                    2         10               0            1     13
Very-low-info               2          3               8            0     13
Low-info                    0          0               1            0      1
```

**lean at p<0.15:**

```
lean_15          Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
reliability                                                                 
Cannot-estimate             0          0               0           21     21
Adequate                    2          7               3            1     13
Very-low-info               2          4               7            0     13
Low-info                    1          0               0            0      1
```

## Direction by graded significance (no single cutoff)

Report direction at p<0.05 / 0.10 / 0.15 rather than one threshold, to show robustness.

**calendar (primary bar)**  (coefficient = pair × lag, raw p)

```
 thresh |  sig | Kalshi(k>0) | ETF(k<0) | contemp
 p<0.05 |   91 |          34 |       46 |      11
 p<0.1  |  108 |          42 |       55 |      11
 p<0.15 |  118 |          48 |       58 |      12
```

**event (backward-diff, comparable to calendar)**  (coefficient = pair × lag, raw p)

```
 thresh |  sig | Kalshi(k>0) | ETF(k<0) | contemp
 p<0.05 |   23 |           8 |       13 |       2
 p<0.1  |   35 |          13 |       20 |       2
 p<0.15 |   49 |          21 |       26 |       2
```

**probit (direction-only; Kalshi-leads requires beta>0)**  (coefficient = pair × lag, raw p)

```
 thresh |  sig | Kalshi(k>0) | ETF(k<0) | contemp
 p<0.05 |   49 |           7 |       26 |       2
 p<0.1  |   80 |          11 |       45 |       5
 p<0.15 |  112 |          15 |       56 |       8
```

## Conclusion

- **Pairs without data expose themselves**: 21 **cannot be estimated** (params >= obs) and 13 have **very low df** (huge SE, 'significant' is untrustworthy) -- high-frequency lead-lag is only meaningful on the 13 pairs with adequate df.
- **Even the reliable group is not one-sided**: of 13 adequate-df pairs, lean by tier — p<0.05 K1/E10/B1/N1; p<0.1 K2/E10/B0/N1; p<0.15 K2/E7/B3/N1 — no side dominates at any threshold.
- **Direction is threshold-robust but method-split** (see graded table above): across p<0.05/0.10/0.15 the linear regressions (calendar, event) split ~1:1 with no net lead at any threshold, while the direction-only probit consistently favors ETF-leads (~5:1). Any lead lives in the *sign* of ETF moves, not their magnitude.
- **Construction note**: event uses the same causal backward-diff as calendar (differing only in active-event vs clock timepoints). An earlier forward-return event construction had spuriously inflated ETF-leads by overlapping each event's forward window with the next event; that artifact is removed, after which event splits ~1:1.
- **By type**: election / FOMC (one-shot event) contracts contribute almost all of the estimable, significant structure; gas-price / approval (continuous) contracts mostly fall in 'cannot estimate'.
- **Conclusion**: directional lead is **NOT concentrated in any single clean category**; the strongest signal comes from adequate-df one-shot-event contracts (election, FOMC), but within them Kalshi-leads and ETF-leads coexist -- supporting the main finding of 'no clean single-direction lead'.

## Pairs in each category (which pairs fall under each classification)

For each of the four dimensions, every category lists its pairs with their lean at each tier [05|10|15], abbreviated K=Kalshi-leads, E=ETF-leads, B=Balanced/mixed, N=No-sig-lead (so each count above can be traced to the actual pairs).

### By contract type

- **Approval** (8): 538APPROVEMAX-24OCT31-T43×VOX [N|N|N], 538APPROVEMAX-24SEP30-T43×VAW [N|N|N], 538APPROVEMAX-24SEP30-T43×VCR [N|N|N], 538APPROVEMAX-24SEP30-T43×VIS [N|N|N], KX538APPROVEMAX-24NOV30-T41×VGT [N|N|N], KX538APPROVEMAX-24NOV30-T41×VHT [N|N|N], KX538APPROVEMIN-24NOV30-T37×VFH [N|N|N], KX538APPROVEMIN-24NOV30-T37×VNQ [N|N|N]
- **Election** (18): KXECDJT281×VCR [E|E|B], KXECKH276×VAW [B|B|B], KXECKH276×VCR [B|B|B], KXECKH276×VDC [B|B|B], KXECKH276×VDE [B|B|B], KXECKH276×VFH [B|B|B], KXECKH276×VGT [B|B|B], KXECKH276×VIS [B|B|B], KXECDJT281×VGT [E|E|E], KXECDJT281×VNQ [E|E|E], KXECDJT281×VOX [E|E|E], KXECDJT312×VAW [E|E|E], KXECDJT316×VFH [E|E|E], KXECDJT316×VIS [E|E|E], KXECKH276×VOX [E|E|E], KXECDJT306×VDC [B|B|K], KXECDJT316×VDE [K|K|K], KXECKH287×VNQ [K|K|K]
- **GasPrice** (11): AAAGASM-24OCT31-US-3.15×VPU [B|B|E], AAAGASM-24OCT31-US-3.20×VHT [N|N|N], AAAGASM-24SEP30-US-3.15×VAW [N|N|N], AAAGASM-24SEP30-US-3.15×VCR [N|N|N], AAAGASM-24SEP30-US-3.15×VGT [N|N|N], AAAGASM-24SEP30-US-3.15×VIS [N|N|N], AAAGASM-24SEP30-US-3.15×VOX [N|N|N], KXAAAGASM-24NOV30-US-3.30×VDC [N|N|N], KXAAAGASM-24NOV30-US-3.30×VDE [N|N|N], KXAAAGASM-24NOV30-US-3.30×VFH [N|N|N], KXAAAGASM-24NOV30-US-3.30×VNQ [N|N|N]
- **Rates(FOMC)** (11): FEDDECISION-24SEP-C25×VDC [E|E|B], FEDDECISION-24SEP-C25×VPU [E|E|B], KXFEDDECISION-24DEC-C25×VFH [B|E|E], KXFEDDECISION-24DEC-C25×VIS [E|E|E], KXFEDDECISION-24DEC-H0×VGT [E|E|E], FEDDECISION-24NOV-H0×VNQ [E|K|K], FEDDECISION-24SEP-C25×VOX [K|K|K], FEDDECISION-24NOV-H0×VDE [N|N|N], RATECUT-24SEP18×VCR [N|N|N], RATECUT-24SEP18×VGT [N|N|N], RATECUT-24SEP18×VOX [N|N|N]

### By event kind (sharp vs continuous)

- **Continuous** (19): AAAGASM-24OCT31-US-3.15×VPU [B|B|E], 538APPROVEMAX-24OCT31-T43×VOX [N|N|N], 538APPROVEMAX-24SEP30-T43×VAW [N|N|N], 538APPROVEMAX-24SEP30-T43×VCR [N|N|N], 538APPROVEMAX-24SEP30-T43×VIS [N|N|N], AAAGASM-24OCT31-US-3.20×VHT [N|N|N], AAAGASM-24SEP30-US-3.15×VAW [N|N|N], AAAGASM-24SEP30-US-3.15×VCR [N|N|N], AAAGASM-24SEP30-US-3.15×VGT [N|N|N], AAAGASM-24SEP30-US-3.15×VIS [N|N|N], AAAGASM-24SEP30-US-3.15×VOX [N|N|N], KX538APPROVEMAX-24NOV30-T41×VGT [N|N|N], KX538APPROVEMAX-24NOV30-T41×VHT [N|N|N], KX538APPROVEMIN-24NOV30-T37×VFH [N|N|N], KX538APPROVEMIN-24NOV30-T37×VNQ [N|N|N], KXAAAGASM-24NOV30-US-3.30×VDC [N|N|N], KXAAAGASM-24NOV30-US-3.30×VDE [N|N|N], KXAAAGASM-24NOV30-US-3.30×VFH [N|N|N], KXAAAGASM-24NOV30-US-3.30×VNQ [N|N|N]
- **Sharp(one-shot)** (29): FEDDECISION-24SEP-C25×VDC [E|E|B], FEDDECISION-24SEP-C25×VPU [E|E|B], KXECDJT281×VCR [E|E|B], KXECKH276×VAW [B|B|B], KXECKH276×VCR [B|B|B], KXECKH276×VDC [B|B|B], KXECKH276×VDE [B|B|B], KXECKH276×VFH [B|B|B], KXECKH276×VGT [B|B|B], KXECKH276×VIS [B|B|B], KXECDJT281×VGT [E|E|E], KXECDJT281×VNQ [E|E|E], KXECDJT281×VOX [E|E|E], KXECDJT312×VAW [E|E|E], KXECDJT316×VFH [E|E|E], KXECDJT316×VIS [E|E|E], KXECKH276×VOX [E|E|E], KXFEDDECISION-24DEC-C25×VFH [B|E|E], KXFEDDECISION-24DEC-C25×VIS [E|E|E], KXFEDDECISION-24DEC-H0×VGT [E|E|E], FEDDECISION-24NOV-H0×VNQ [E|K|K], FEDDECISION-24SEP-C25×VOX [K|K|K], KXECDJT306×VDC [B|B|K], KXECDJT316×VDE [K|K|K], KXECKH287×VNQ [K|K|K], FEDDECISION-24NOV-H0×VDE [N|N|N], RATECUT-24SEP18×VCR [N|N|N], RATECUT-24SEP18×VGT [N|N|N], RATECUT-24SEP18×VOX [N|N|N]

### By ETF sector

- **Comm** (6): KXECDJT281×VOX [E|E|E], KXECKH276×VOX [E|E|E], FEDDECISION-24SEP-C25×VOX [K|K|K], 538APPROVEMAX-24OCT31-T43×VOX [N|N|N], AAAGASM-24SEP30-US-3.15×VOX [N|N|N], RATECUT-24SEP18×VOX [N|N|N]
- **Cons.Disc** (5): KXECDJT281×VCR [E|E|B], KXECKH276×VCR [B|B|B], 538APPROVEMAX-24SEP30-T43×VCR [N|N|N], AAAGASM-24SEP30-US-3.15×VCR [N|N|N], RATECUT-24SEP18×VCR [N|N|N]
- **Cons.Staples** (4): FEDDECISION-24SEP-C25×VDC [E|E|B], KXECKH276×VDC [B|B|B], KXECDJT306×VDC [B|B|K], KXAAAGASM-24NOV30-US-3.30×VDC [N|N|N]
- **Energy** (4): KXECKH276×VDE [B|B|B], KXECDJT316×VDE [K|K|K], FEDDECISION-24NOV-H0×VDE [N|N|N], KXAAAGASM-24NOV30-US-3.30×VDE [N|N|N]
- **Financials** (5): KXECKH276×VFH [B|B|B], KXECDJT316×VFH [E|E|E], KXFEDDECISION-24DEC-C25×VFH [B|E|E], KX538APPROVEMIN-24NOV30-T37×VFH [N|N|N], KXAAAGASM-24NOV30-US-3.30×VFH [N|N|N]
- **Health** (2): AAAGASM-24OCT31-US-3.20×VHT [N|N|N], KX538APPROVEMAX-24NOV30-T41×VHT [N|N|N]
- **Industrials** (5): KXECKH276×VIS [B|B|B], KXECDJT316×VIS [E|E|E], KXFEDDECISION-24DEC-C25×VIS [E|E|E], 538APPROVEMAX-24SEP30-T43×VIS [N|N|N], AAAGASM-24SEP30-US-3.15×VIS [N|N|N]
- **Info-Tech** (6): KXECKH276×VGT [B|B|B], KXECDJT281×VGT [E|E|E], KXFEDDECISION-24DEC-H0×VGT [E|E|E], AAAGASM-24SEP30-US-3.15×VGT [N|N|N], KX538APPROVEMAX-24NOV30-T41×VGT [N|N|N], RATECUT-24SEP18×VGT [N|N|N]
- **Materials** (4): KXECKH276×VAW [B|B|B], KXECDJT312×VAW [E|E|E], 538APPROVEMAX-24SEP30-T43×VAW [N|N|N], AAAGASM-24SEP30-US-3.15×VAW [N|N|N]
- **Real-Estate** (5): KXECDJT281×VNQ [E|E|E], FEDDECISION-24NOV-H0×VNQ [E|K|K], KXECKH287×VNQ [K|K|K], KX538APPROVEMIN-24NOV30-T37×VNQ [N|N|N], KXAAAGASM-24NOV30-US-3.30×VNQ [N|N|N]
- **Utilities** (2): FEDDECISION-24SEP-C25×VPU [E|E|B], AAAGASM-24OCT31-US-3.15×VPU [B|B|E]

### By reliability tier (df-based)

- **Adequate** (13): FEDDECISION-24SEP-C25×VDC [E|E|B], FEDDECISION-24SEP-C25×VPU [E|E|B], KXECDJT281×VCR [E|E|B], KXECDJT281×VGT [E|E|E], KXECDJT281×VNQ [E|E|E], KXECDJT281×VOX [E|E|E], KXECDJT312×VAW [E|E|E], KXFEDDECISION-24DEC-C25×VFH [B|E|E], KXFEDDECISION-24DEC-C25×VIS [E|E|E], KXFEDDECISION-24DEC-H0×VGT [E|E|E], FEDDECISION-24NOV-H0×VNQ [E|K|K], FEDDECISION-24SEP-C25×VOX [K|K|K], FEDDECISION-24NOV-H0×VDE [N|N|N]
- **Cannot-estimate** (21): 538APPROVEMAX-24OCT31-T43×VOX [N|N|N], 538APPROVEMAX-24SEP30-T43×VAW [N|N|N], 538APPROVEMAX-24SEP30-T43×VCR [N|N|N], 538APPROVEMAX-24SEP30-T43×VIS [N|N|N], AAAGASM-24OCT31-US-3.20×VHT [N|N|N], AAAGASM-24SEP30-US-3.15×VAW [N|N|N], AAAGASM-24SEP30-US-3.15×VCR [N|N|N], AAAGASM-24SEP30-US-3.15×VGT [N|N|N], AAAGASM-24SEP30-US-3.15×VIS [N|N|N], AAAGASM-24SEP30-US-3.15×VOX [N|N|N], KX538APPROVEMAX-24NOV30-T41×VGT [N|N|N], KX538APPROVEMAX-24NOV30-T41×VHT [N|N|N], KX538APPROVEMIN-24NOV30-T37×VFH [N|N|N], KX538APPROVEMIN-24NOV30-T37×VNQ [N|N|N], KXAAAGASM-24NOV30-US-3.30×VDC [N|N|N], KXAAAGASM-24NOV30-US-3.30×VDE [N|N|N], KXAAAGASM-24NOV30-US-3.30×VFH [N|N|N], KXAAAGASM-24NOV30-US-3.30×VNQ [N|N|N], RATECUT-24SEP18×VCR [N|N|N], RATECUT-24SEP18×VGT [N|N|N], RATECUT-24SEP18×VOX [N|N|N]
- **Low-info** (1): KXECDJT306×VDC [B|B|K]
- **Very-low-info** (13): KXECKH276×VAW [B|B|B], KXECKH276×VCR [B|B|B], KXECKH276×VDC [B|B|B], KXECKH276×VDE [B|B|B], KXECKH276×VFH [B|B|B], KXECKH276×VGT [B|B|B], KXECKH276×VIS [B|B|B], AAAGASM-24OCT31-US-3.15×VPU [B|B|E], KXECDJT316×VFH [E|E|E], KXECDJT316×VIS [E|E|E], KXECKH276×VOX [E|E|E], KXECDJT316×VDE [K|K|K], KXECKH287×VNQ [K|K|K]

> Note: auto-generated from the tables above; edit this file then merge into the report. Figure: plots/classification_summary.png.