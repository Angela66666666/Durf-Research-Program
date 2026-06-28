# Lead/Lag classification summary

Scope: all 48 pairs (Kalshi contract x ETF). Lean rule: across calendar+event, count
significant lags at p<0.05 / 0.10 / 0.15 (raw p; nested, p<0.05 ⊆ p<0.10 ⊆ p<0.15) per
direction (k>0 Kalshi-leads, k<0 ETF-leads). **A lean conclusion is produced at EACH tier**, not
a single chosen threshold, so the Overall and every cross-tab below appear three times (one per tier).
Reliability rule: tiered by residual df (= effective obs - #parameters), NOT a trade-count cutoff.

## Overall — lean counts at each threshold

```
        Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead
p<0.05             5          8              10           25
p<0.1              7          8               9           24
p<0.15             6          7              11           24
```

## By contract type

**lean at p<0.05:**

```
lean_05        Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
contract_type                                                             
Election                  3          5               8            2     18
GasPrice                  0          0               0           11     11
Rates(FOMC)               2          3               2            4     11
Approval                  0          0               0            8      8
```

**lean at p<0.1:**

```
lean_10        Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
contract_type                                                             
Election                  4          4               8            2     18
GasPrice                  0          0               0           11     11
Rates(FOMC)               3          4               1            3     11
Approval                  0          0               0            8      8
```

**lean at p<0.15:**

```
lean_15        Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
contract_type                                                             
Election                  3          5               8            2     18
GasPrice                  0          0               0           11     11
Rates(FOMC)               3          2               3            3     11
Approval                  0          0               0            8      8
```

## By event kind (sharp one-shot vs continuous)

**lean at p<0.05:**

```
lean_05          Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
event_kind                                                                  
Sharp(one-shot)             5          8              10            6     29
Continuous                  0          0               0           19     19
```

**lean at p<0.1:**

```
lean_10          Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
event_kind                                                                  
Sharp(one-shot)             7          8               9            5     29
Continuous                  0          0               0           19     19
```

**lean at p<0.15:**

```
lean_15          Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
event_kind                                                                  
Sharp(one-shot)             6          7              11            5     29
Continuous                  0          0               0           19     19
```

## By ETF sector

**lean at p<0.05:**

```
lean_05       Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
sector                                                                   
Comm                     1          1               1            3      6
Info-Tech                0          1               2            3      6
Cons.Disc                2          0               0            3      5
Financials               0          0               3            2      5
Industrials              0          1               2            2      5
Real-Estate              0          1               0            4      5
Cons.Staples             0          2               1            1      4
Energy                   1          1               0            2      4
Materials                0          1               1            2      4
Health                   0          0               0            2      2
Utilities                1          0               0            1      2
```

**lean at p<0.1:**

```
lean_10       Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
sector                                                                   
Comm                     1          1               1            3      6
Info-Tech                1          1               1            3      6
Cons.Disc                2          0               0            3      5
Financials               1          0               2            2      5
Industrials              0          2               1            2      5
Real-Estate              0          1               1            3      5
Cons.Staples             0          1               2            1      4
Energy                   1          1               0            2      4
Materials                0          1               1            2      4
Health                   0          0               0            2      2
Utilities                1          0               0            1      2
```

**lean at p<0.15:**

```
lean_15       Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
sector                                                                   
Comm                     1          1               1            3      6
Info-Tech                1          1               1            3      6
Cons.Disc                1          0               1            3      5
Financials               1          1               1            2      5
Industrials              0          2               1            2      5
Real-Estate              0          1               1            3      5
Cons.Staples             0          0               3            1      4
Energy                   1          0               1            2      4
Materials                0          1               1            2      4
Health                   0          0               0            2      2
Utilities                1          0               0            1      2
```

## By statistical reliability (df-based)

**lean at p<0.05:**

```
lean_05          Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
reliability                                                                 
Cannot-estimate             0          0               0           23     23
Adequate                    3          5               3            1     12
Very-low-info               2          2               6            1     11
Low-info                    0          1               1            0      2
```

**lean at p<0.1:**

```
lean_10          Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
reliability                                                                 
Cannot-estimate             0          0               0           23     23
Adequate                    5          6               1            0     12
Very-low-info               2          1               7            1     11
Low-info                    0          1               1            0      2
```

**lean at p<0.15:**

```
lean_15          Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
reliability                                                                 
Cannot-estimate             0          0               0           23     23
Adequate                    4          4               4            0     12
Very-low-info               2          2               6            1     11
Low-info                    0          1               1            0      2
```

## Direction by graded significance (no single cutoff)

Report direction at p<0.05 / 0.10 / 0.15 rather than one threshold, to show robustness.

**calendar (primary bar)**  (coefficient = pair × lag, raw p)

```
 thresh |  sig | Kalshi(k>0) | ETF(k<0) | contemp
 p<0.05 |   53 |          25 |       26 |       2
 p<0.1  |   67 |          34 |       31 |       2
 p<0.15 |   81 |          39 |       38 |       4
```

**event (backward-diff, comparable to calendar)**  (coefficient = pair × lag, raw p)

```
 thresh |  sig | Kalshi(k>0) | ETF(k<0) | contemp
 p<0.05 |   14 |           7 |        6 |       1
 p<0.1  |   21 |          10 |       10 |       1
 p<0.15 |   30 |          14 |       14 |       2
```

**probit (direction-only; Kalshi-leads requires beta>0)**  (coefficient = pair × lag, raw p)

```
 thresh |  sig | Kalshi(k>0) | ETF(k<0) | contemp
 p<0.05 |   39 |           4 |       22 |       3
 p<0.1  |   65 |           6 |       37 |       5
 p<0.15 |   88 |          11 |       49 |       6
```

## Conclusion

- **Pairs without data expose themselves**: 23 **cannot be estimated** (params >= obs) and 11 have **very low df** (huge SE, 'significant' is untrustworthy) -- high-frequency lead-lag is only meaningful on the 12 pairs with adequate df.
- **Even the reliable group is not one-sided**: of 12 adequate-df pairs, lean by tier — p<0.05 K3/E5/B3/N1; p<0.1 K5/E6/B1/N0; p<0.15 K4/E4/B4/N0 — no side dominates at any threshold.
- **Direction is threshold-robust but method-split** (see graded table above): across p<0.05/0.10/0.15 the linear regressions (calendar, event) split ~1:1 with no net lead at any threshold, while the direction-only probit consistently favors ETF-leads (~5:1). Any lead lives in the *sign* of ETF moves, not their magnitude.
- **Construction note**: event uses the same causal backward-diff as calendar (differing only in active-event vs clock timepoints). An earlier forward-return event construction had spuriously inflated ETF-leads by overlapping each event's forward window with the next event; that artifact is removed, after which event splits ~1:1.
- **By type**: election / FOMC (one-shot event) contracts contribute almost all of the estimable, significant structure; gas-price / approval (continuous) contracts mostly fall in 'cannot estimate'.
- **Conclusion**: directional lead is **NOT concentrated in any single clean category**; the strongest signal comes from adequate-df one-shot-event contracts (election, FOMC), but within them Kalshi-leads and ETF-leads coexist -- supporting the main finding of 'no clean single-direction lead'.

## Pairs in each category (which pairs fall under each classification)

For each of the four dimensions, every category lists its pairs with their lean at each tier [05|10|15], abbreviated K=Kalshi-leads, E=ETF-leads, B=Balanced/mixed, N=No-sig-lead (so each count above can be traced to the actual pairs).

### By contract type

- **Approval** (8): 538APPROVEMAX-24OCT31-T43×VOX [N|N|N], 538APPROVEMAX-24SEP30-T43×VAW [N|N|N], 538APPROVEMAX-24SEP30-T43×VCR [N|N|N], 538APPROVEMAX-24SEP30-T43×VIS [N|N|N], KX538APPROVEMAX-24NOV30-T41×VGT [N|N|N], KX538APPROVEMAX-24NOV30-T41×VHT [N|N|N], KX538APPROVEMIN-24NOV30-T37×VFH [N|N|N], KX538APPROVEMIN-24NOV30-T37×VNQ [N|N|N]
- **Election** (18): KXECDJT281×VCR [K|K|B], KXECDJT306×VDC [B|B|B], KXECKH276×VAW [B|B|B], KXECKH276×VDC [E|B|B], KXECKH276×VFH [B|B|B], KXECKH276×VGT [B|B|B], KXECKH276×VIS [B|B|B], KXECKH276×VOX [B|B|B], KXECDJT281×VNQ [E|E|E], KXECDJT281×VOX [E|E|E], KXECDJT312×VAW [E|E|E], KXECDJT316×VFH [B|B|E], KXECDJT316×VIS [E|E|E], KXECDJT281×VGT [B|K|K], KXECKH276×VCR [K|K|K], KXECKH276×VDE [K|K|K], KXECDJT316×VDE [N|N|N], KXECKH287×VNQ [N|N|N]
- **GasPrice** (11): AAAGASM-24OCT31-US-3.15×VPU [N|N|N], AAAGASM-24OCT31-US-3.20×VHT [N|N|N], AAAGASM-24SEP30-US-3.15×VAW [N|N|N], AAAGASM-24SEP30-US-3.15×VCR [N|N|N], AAAGASM-24SEP30-US-3.15×VGT [N|N|N], AAAGASM-24SEP30-US-3.15×VIS [N|N|N], AAAGASM-24SEP30-US-3.15×VOX [N|N|N], KXAAAGASM-24NOV30-US-3.30×VDC [N|N|N], KXAAAGASM-24NOV30-US-3.30×VDE [N|N|N], KXAAAGASM-24NOV30-US-3.30×VFH [N|N|N], KXAAAGASM-24NOV30-US-3.30×VNQ [N|N|N]
- **Rates(FOMC)** (11): FEDDECISION-24NOV-H0×VDE [E|E|B], FEDDECISION-24NOV-H0×VNQ [N|B|B], FEDDECISION-24SEP-C25×VDC [E|E|B], KXFEDDECISION-24DEC-C25×VIS [B|E|E], KXFEDDECISION-24DEC-H0×VGT [E|E|E], FEDDECISION-24SEP-C25×VOX [K|K|K], FEDDECISION-24SEP-C25×VPU [K|K|K], KXFEDDECISION-24DEC-C25×VFH [B|K|K], RATECUT-24SEP18×VCR [N|N|N], RATECUT-24SEP18×VGT [N|N|N], RATECUT-24SEP18×VOX [N|N|N]

### By event kind (sharp vs continuous)

- **Continuous** (19): 538APPROVEMAX-24OCT31-T43×VOX [N|N|N], 538APPROVEMAX-24SEP30-T43×VAW [N|N|N], 538APPROVEMAX-24SEP30-T43×VCR [N|N|N], 538APPROVEMAX-24SEP30-T43×VIS [N|N|N], AAAGASM-24OCT31-US-3.15×VPU [N|N|N], AAAGASM-24OCT31-US-3.20×VHT [N|N|N], AAAGASM-24SEP30-US-3.15×VAW [N|N|N], AAAGASM-24SEP30-US-3.15×VCR [N|N|N], AAAGASM-24SEP30-US-3.15×VGT [N|N|N], AAAGASM-24SEP30-US-3.15×VIS [N|N|N], AAAGASM-24SEP30-US-3.15×VOX [N|N|N], KX538APPROVEMAX-24NOV30-T41×VGT [N|N|N], KX538APPROVEMAX-24NOV30-T41×VHT [N|N|N], KX538APPROVEMIN-24NOV30-T37×VFH [N|N|N], KX538APPROVEMIN-24NOV30-T37×VNQ [N|N|N], KXAAAGASM-24NOV30-US-3.30×VDC [N|N|N], KXAAAGASM-24NOV30-US-3.30×VDE [N|N|N], KXAAAGASM-24NOV30-US-3.30×VFH [N|N|N], KXAAAGASM-24NOV30-US-3.30×VNQ [N|N|N]
- **Sharp(one-shot)** (29): FEDDECISION-24NOV-H0×VDE [E|E|B], FEDDECISION-24NOV-H0×VNQ [N|B|B], FEDDECISION-24SEP-C25×VDC [E|E|B], KXECDJT281×VCR [K|K|B], KXECDJT306×VDC [B|B|B], KXECKH276×VAW [B|B|B], KXECKH276×VDC [E|B|B], KXECKH276×VFH [B|B|B], KXECKH276×VGT [B|B|B], KXECKH276×VIS [B|B|B], KXECKH276×VOX [B|B|B], KXECDJT281×VNQ [E|E|E], KXECDJT281×VOX [E|E|E], KXECDJT312×VAW [E|E|E], KXECDJT316×VFH [B|B|E], KXECDJT316×VIS [E|E|E], KXFEDDECISION-24DEC-C25×VIS [B|E|E], KXFEDDECISION-24DEC-H0×VGT [E|E|E], FEDDECISION-24SEP-C25×VOX [K|K|K], FEDDECISION-24SEP-C25×VPU [K|K|K], KXECDJT281×VGT [B|K|K], KXECKH276×VCR [K|K|K], KXECKH276×VDE [K|K|K], KXFEDDECISION-24DEC-C25×VFH [B|K|K], KXECDJT316×VDE [N|N|N], KXECKH287×VNQ [N|N|N], RATECUT-24SEP18×VCR [N|N|N], RATECUT-24SEP18×VGT [N|N|N], RATECUT-24SEP18×VOX [N|N|N]

### By ETF sector

- **Comm** (6): KXECKH276×VOX [B|B|B], KXECDJT281×VOX [E|E|E], FEDDECISION-24SEP-C25×VOX [K|K|K], 538APPROVEMAX-24OCT31-T43×VOX [N|N|N], AAAGASM-24SEP30-US-3.15×VOX [N|N|N], RATECUT-24SEP18×VOX [N|N|N]
- **Cons.Disc** (5): KXECDJT281×VCR [K|K|B], KXECKH276×VCR [K|K|K], 538APPROVEMAX-24SEP30-T43×VCR [N|N|N], AAAGASM-24SEP30-US-3.15×VCR [N|N|N], RATECUT-24SEP18×VCR [N|N|N]
- **Cons.Staples** (4): FEDDECISION-24SEP-C25×VDC [E|E|B], KXECDJT306×VDC [B|B|B], KXECKH276×VDC [E|B|B], KXAAAGASM-24NOV30-US-3.30×VDC [N|N|N]
- **Energy** (4): FEDDECISION-24NOV-H0×VDE [E|E|B], KXECKH276×VDE [K|K|K], KXAAAGASM-24NOV30-US-3.30×VDE [N|N|N], KXECDJT316×VDE [N|N|N]
- **Financials** (5): KXECKH276×VFH [B|B|B], KXECDJT316×VFH [B|B|E], KXFEDDECISION-24DEC-C25×VFH [B|K|K], KX538APPROVEMIN-24NOV30-T37×VFH [N|N|N], KXAAAGASM-24NOV30-US-3.30×VFH [N|N|N]
- **Health** (2): AAAGASM-24OCT31-US-3.20×VHT [N|N|N], KX538APPROVEMAX-24NOV30-T41×VHT [N|N|N]
- **Industrials** (5): KXECKH276×VIS [B|B|B], KXECDJT316×VIS [E|E|E], KXFEDDECISION-24DEC-C25×VIS [B|E|E], 538APPROVEMAX-24SEP30-T43×VIS [N|N|N], AAAGASM-24SEP30-US-3.15×VIS [N|N|N]
- **Info-Tech** (6): KXECKH276×VGT [B|B|B], KXFEDDECISION-24DEC-H0×VGT [E|E|E], KXECDJT281×VGT [B|K|K], AAAGASM-24SEP30-US-3.15×VGT [N|N|N], KX538APPROVEMAX-24NOV30-T41×VGT [N|N|N], RATECUT-24SEP18×VGT [N|N|N]
- **Materials** (4): KXECKH276×VAW [B|B|B], KXECDJT312×VAW [E|E|E], 538APPROVEMAX-24SEP30-T43×VAW [N|N|N], AAAGASM-24SEP30-US-3.15×VAW [N|N|N]
- **Real-Estate** (5): FEDDECISION-24NOV-H0×VNQ [N|B|B], KXECDJT281×VNQ [E|E|E], KX538APPROVEMIN-24NOV30-T37×VNQ [N|N|N], KXAAAGASM-24NOV30-US-3.30×VNQ [N|N|N], KXECKH287×VNQ [N|N|N]
- **Utilities** (2): FEDDECISION-24SEP-C25×VPU [K|K|K], AAAGASM-24OCT31-US-3.15×VPU [N|N|N]

### By reliability tier (df-based)

- **Adequate** (12): FEDDECISION-24NOV-H0×VDE [E|E|B], FEDDECISION-24NOV-H0×VNQ [N|B|B], FEDDECISION-24SEP-C25×VDC [E|E|B], KXECDJT281×VCR [K|K|B], KXECDJT281×VNQ [E|E|E], KXECDJT281×VOX [E|E|E], KXFEDDECISION-24DEC-C25×VIS [B|E|E], KXFEDDECISION-24DEC-H0×VGT [E|E|E], FEDDECISION-24SEP-C25×VOX [K|K|K], FEDDECISION-24SEP-C25×VPU [K|K|K], KXECDJT281×VGT [B|K|K], KXFEDDECISION-24DEC-C25×VFH [B|K|K]
- **Cannot-estimate** (23): 538APPROVEMAX-24OCT31-T43×VOX [N|N|N], 538APPROVEMAX-24SEP30-T43×VAW [N|N|N], 538APPROVEMAX-24SEP30-T43×VCR [N|N|N], 538APPROVEMAX-24SEP30-T43×VIS [N|N|N], AAAGASM-24OCT31-US-3.15×VPU [N|N|N], AAAGASM-24OCT31-US-3.20×VHT [N|N|N], AAAGASM-24SEP30-US-3.15×VAW [N|N|N], AAAGASM-24SEP30-US-3.15×VCR [N|N|N], AAAGASM-24SEP30-US-3.15×VGT [N|N|N], AAAGASM-24SEP30-US-3.15×VIS [N|N|N], AAAGASM-24SEP30-US-3.15×VOX [N|N|N], KX538APPROVEMAX-24NOV30-T41×VGT [N|N|N], KX538APPROVEMAX-24NOV30-T41×VHT [N|N|N], KX538APPROVEMIN-24NOV30-T37×VFH [N|N|N], KX538APPROVEMIN-24NOV30-T37×VNQ [N|N|N], KXAAAGASM-24NOV30-US-3.30×VDC [N|N|N], KXAAAGASM-24NOV30-US-3.30×VDE [N|N|N], KXAAAGASM-24NOV30-US-3.30×VFH [N|N|N], KXAAAGASM-24NOV30-US-3.30×VNQ [N|N|N], KXECKH287×VNQ [N|N|N], RATECUT-24SEP18×VCR [N|N|N], RATECUT-24SEP18×VGT [N|N|N], RATECUT-24SEP18×VOX [N|N|N]
- **Low-info** (2): KXECDJT306×VDC [B|B|B], KXECDJT312×VAW [E|E|E]
- **Very-low-info** (11): KXECKH276×VAW [B|B|B], KXECKH276×VDC [E|B|B], KXECKH276×VFH [B|B|B], KXECKH276×VGT [B|B|B], KXECKH276×VIS [B|B|B], KXECKH276×VOX [B|B|B], KXECDJT316×VFH [B|B|E], KXECDJT316×VIS [E|E|E], KXECKH276×VCR [K|K|K], KXECKH276×VDE [K|K|K], KXECDJT316×VDE [N|N|N]

> Note: auto-generated from the tables above; edit this file then merge into the report. Figure: plots/classification_summary.png.