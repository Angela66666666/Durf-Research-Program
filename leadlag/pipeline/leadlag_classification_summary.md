# Lead/Lag classification summary

Scope: all 48 pairs (Kalshi contract x ETF). Lean rule: across calendar+event, count
significant lags at p<0.05 / 0.10 / 0.15 (raw p; nested, p<0.05 ⊆ p<0.10 ⊆ p<0.15) per
direction (k>0 Kalshi-leads, k<0 ETF-leads). **A lean conclusion is produced at EACH tier**, not
a single chosen threshold, so the Overall and every cross-tab below appear three times (one per tier).
Reliability rule: tiered by residual df (= effective obs - #parameters), NOT a trade-count cutoff.

## Overall — lean counts at each threshold

```
        Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead
p<0.05             6          8               8           26
p<0.1              6         10               8           24
p<0.15             6          8              10           24
```

## By contract type

**lean at p<0.05:**

```
lean_05        Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
contract_type                                                             
Election                  5          6               5            2     18
GasPrice                  0          0               0           11     11
Rates(FOMC)               1          2               3            5     11
Approval                  0          0               0            8      8
```

**lean at p<0.1:**

```
lean_10        Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
contract_type                                                             
Election                  3          7               6            2     18
GasPrice                  0          0               0           11     11
Rates(FOMC)               3          3               2            3     11
Approval                  0          0               0            8      8
```

**lean at p<0.15:**

```
lean_15        Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
contract_type                                                             
Election                  3          7               6            2     18
GasPrice                  0          0               0           11     11
Rates(FOMC)               3          1               4            3     11
Approval                  0          0               0            8      8
```

## By event kind (sharp one-shot vs continuous)

**lean at p<0.05:**

```
lean_05          Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
event_kind                                                                  
Sharp(one-shot)             6          8               8            7     29
Continuous                  0          0               0           19     19
```

**lean at p<0.1:**

```
lean_10          Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
event_kind                                                                  
Sharp(one-shot)             6         10               8            5     29
Continuous                  0          0               0           19     19
```

**lean at p<0.15:**

```
lean_15          Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
event_kind                                                                  
Sharp(one-shot)             6          8              10            5     29
Continuous                  0          0               0           19     19
```

## By ETF sector

**lean at p<0.05:**

```
lean_05       Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
sector                                                                   
Comm                     1          1               1            3      6
Info-Tech                0          1               2            3      6
Cons.Disc                1          1               0            3      5
Financials               0          1               2            2      5
Industrials              2          0               1            2      5
Real-Estate              0          1               0            4      5
Cons.Staples             1          1               1            1      4
Energy                   1          0               0            3      4
Materials                0          2               0            2      4
Health                   0          0               0            2      2
Utilities                0          0               1            1      2
```

**lean at p<0.1:**

```
lean_10       Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
sector                                                                   
Comm                     1          2               0            3      6
Info-Tech                0          1               2            3      6
Cons.Disc                0          1               1            3      5
Financials               1          1               1            2      5
Industrials              1          0               2            2      5
Real-Estate              0          1               1            3      5
Cons.Staples             1          1               1            1      4
Energy                   1          1               0            2      4
Materials                0          2               0            2      4
Health                   0          0               0            2      2
Utilities                1          0               0            1      2
```

**lean at p<0.15:**

```
lean_15       Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
sector                                                                   
Comm                     1          2               0            3      6
Info-Tech                0          1               2            3      6
Cons.Disc                0          1               1            3      5
Financials               1          1               1            2      5
Industrials              1          0               2            2      5
Real-Estate              0          1               1            3      5
Cons.Staples             1          0               2            1      4
Energy                   1          0               1            2      4
Materials                0          2               0            2      4
Health                   0          0               0            2      2
Utilities                1          0               0            1      2
```

## By statistical reliability (df-based)

**lean at p<0.05:**

```
lean_05          Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
reliability                                                                 
Cannot-estimate             0          0               0           23     23
Adequate                    1          4               5            2     12
Very-low-info               4          3               3            1     11
Low-info                    1          1               0            0      2
```

**lean at p<0.1:**

```
lean_10          Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
reliability                                                                 
Cannot-estimate             0          0               0           23     23
Adequate                    3          6               3            0     12
Very-low-info               2          3               5            1     11
Low-info                    1          1               0            0      2
```

**lean at p<0.15:**

```
lean_15          Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
reliability                                                                 
Cannot-estimate             0          0               0           23     23
Adequate                    3          4               5            0     12
Very-low-info               2          3               5            1     11
Low-info                    1          1               0            0      2
```

## Direction by graded significance (no single cutoff)

Report direction at p<0.05 / 0.10 / 0.15 rather than one threshold, to show robustness.

**calendar (primary bar)**  (coefficient = pair × lag, raw p)

```
 thresh |  sig | Kalshi(k>0) | ETF(k<0) | contemp
 p<0.05 |   73 |          34 |       35 |       4
 p<0.1  |   89 |          42 |       41 |       6
 p<0.15 |   98 |          46 |       46 |       6
```

**event (backward-diff, comparable to calendar)**  (coefficient = pair × lag, raw p)

```
 thresh |  sig | Kalshi(k>0) | ETF(k<0) | contemp
 p<0.05 |   19 |           5 |       12 |       2
 p<0.1  |   28 |           9 |       17 |       2
 p<0.15 |   34 |          14 |       18 |       2
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
- **Even the reliable group is not one-sided**: of 12 adequate-df pairs, lean by tier — p<0.05 K1/E4/B5/N2; p<0.1 K3/E6/B3/N0; p<0.15 K3/E4/B5/N0 — no side dominates at any threshold.
- **Direction is threshold-robust but method-split** (see graded table above): across p<0.05/0.10/0.15 the linear regressions (calendar, event) split ~1:1 with no net lead at any threshold, while the direction-only probit consistently favors ETF-leads (~5:1). Any lead lives in the *sign* of ETF moves, not their magnitude.
- **Construction note**: event uses the same causal backward-diff as calendar (differing only in active-event vs clock timepoints). An earlier forward-return event construction had spuriously inflated ETF-leads by overlapping each event's forward window with the next event; that artifact is removed, after which event splits ~1:1.
- **By type**: election / FOMC (one-shot event) contracts contribute almost all of the estimable, significant structure; gas-price / approval (continuous) contracts mostly fall in 'cannot estimate'.
- **Conclusion**: directional lead is **NOT concentrated in any single clean category**; the strongest signal comes from adequate-df one-shot-event contracts (election, FOMC), but within them Kalshi-leads and ETF-leads coexist -- supporting the main finding of 'no clean single-direction lead'.

## Pairs in each category (which pairs fall under each classification)

For each of the four dimensions, every category lists its pairs with their lean at each tier [05|10|15], abbreviated K=Kalshi-leads, E=ETF-leads, B=Balanced/mixed, N=No-sig-lead (so each count above can be traced to the actual pairs).

### By contract type

- **Approval** (8): 538APPROVEMAX-24OCT31-T43×VOX [N|N|N], 538APPROVEMAX-24SEP30-T43×VAW [N|N|N], 538APPROVEMAX-24SEP30-T43×VCR [N|N|N], 538APPROVEMAX-24SEP30-T43×VIS [N|N|N], KX538APPROVEMAX-24NOV30-T41×VGT [N|N|N], KX538APPROVEMAX-24NOV30-T41×VHT [N|N|N], KX538APPROVEMIN-24NOV30-T37×VFH [N|N|N], KX538APPROVEMIN-24NOV30-T37×VNQ [N|N|N]
- **Election** (18): KXECDJT281×VGT [B|B|B], KXECDJT316×VIS [K|B|B], KXECKH276×VCR [K|B|B], KXECKH276×VDC [B|B|B], KXECKH276×VFH [B|B|B], KXECKH276×VGT [B|B|B], KXECDJT281×VCR [E|E|E], KXECDJT281×VNQ [E|E|E], KXECDJT281×VOX [B|E|E], KXECDJT312×VAW [E|E|E], KXECDJT316×VFH [E|E|E], KXECKH276×VAW [E|E|E], KXECKH276×VOX [E|E|E], KXECDJT306×VDC [K|K|K], KXECKH276×VDE [K|K|K], KXECKH276×VIS [K|K|K], KXECDJT316×VDE [N|N|N], KXECKH287×VNQ [N|N|N]
- **GasPrice** (11): AAAGASM-24OCT31-US-3.15×VPU [N|N|N], AAAGASM-24OCT31-US-3.20×VHT [N|N|N], AAAGASM-24SEP30-US-3.15×VAW [N|N|N], AAAGASM-24SEP30-US-3.15×VCR [N|N|N], AAAGASM-24SEP30-US-3.15×VGT [N|N|N], AAAGASM-24SEP30-US-3.15×VIS [N|N|N], AAAGASM-24SEP30-US-3.15×VOX [N|N|N], KXAAAGASM-24NOV30-US-3.30×VDC [N|N|N], KXAAAGASM-24NOV30-US-3.30×VDE [N|N|N], KXAAAGASM-24NOV30-US-3.30×VFH [N|N|N], KXAAAGASM-24NOV30-US-3.30×VNQ [N|N|N]
- **Rates(FOMC)** (11): FEDDECISION-24NOV-H0×VDE [N|E|B], FEDDECISION-24NOV-H0×VNQ [N|B|B], FEDDECISION-24SEP-C25×VDC [E|E|B], KXFEDDECISION-24DEC-C25×VIS [B|B|B], KXFEDDECISION-24DEC-H0×VGT [E|E|E], FEDDECISION-24SEP-C25×VOX [K|K|K], FEDDECISION-24SEP-C25×VPU [B|K|K], KXFEDDECISION-24DEC-C25×VFH [B|K|K], RATECUT-24SEP18×VCR [N|N|N], RATECUT-24SEP18×VGT [N|N|N], RATECUT-24SEP18×VOX [N|N|N]

### By event kind (sharp vs continuous)

- **Continuous** (19): 538APPROVEMAX-24OCT31-T43×VOX [N|N|N], 538APPROVEMAX-24SEP30-T43×VAW [N|N|N], 538APPROVEMAX-24SEP30-T43×VCR [N|N|N], 538APPROVEMAX-24SEP30-T43×VIS [N|N|N], AAAGASM-24OCT31-US-3.15×VPU [N|N|N], AAAGASM-24OCT31-US-3.20×VHT [N|N|N], AAAGASM-24SEP30-US-3.15×VAW [N|N|N], AAAGASM-24SEP30-US-3.15×VCR [N|N|N], AAAGASM-24SEP30-US-3.15×VGT [N|N|N], AAAGASM-24SEP30-US-3.15×VIS [N|N|N], AAAGASM-24SEP30-US-3.15×VOX [N|N|N], KX538APPROVEMAX-24NOV30-T41×VGT [N|N|N], KX538APPROVEMAX-24NOV30-T41×VHT [N|N|N], KX538APPROVEMIN-24NOV30-T37×VFH [N|N|N], KX538APPROVEMIN-24NOV30-T37×VNQ [N|N|N], KXAAAGASM-24NOV30-US-3.30×VDC [N|N|N], KXAAAGASM-24NOV30-US-3.30×VDE [N|N|N], KXAAAGASM-24NOV30-US-3.30×VFH [N|N|N], KXAAAGASM-24NOV30-US-3.30×VNQ [N|N|N]
- **Sharp(one-shot)** (29): FEDDECISION-24NOV-H0×VDE [N|E|B], FEDDECISION-24NOV-H0×VNQ [N|B|B], FEDDECISION-24SEP-C25×VDC [E|E|B], KXECDJT281×VGT [B|B|B], KXECDJT316×VIS [K|B|B], KXECKH276×VCR [K|B|B], KXECKH276×VDC [B|B|B], KXECKH276×VFH [B|B|B], KXECKH276×VGT [B|B|B], KXFEDDECISION-24DEC-C25×VIS [B|B|B], KXECDJT281×VCR [E|E|E], KXECDJT281×VNQ [E|E|E], KXECDJT281×VOX [B|E|E], KXECDJT312×VAW [E|E|E], KXECDJT316×VFH [E|E|E], KXECKH276×VAW [E|E|E], KXECKH276×VOX [E|E|E], KXFEDDECISION-24DEC-H0×VGT [E|E|E], FEDDECISION-24SEP-C25×VOX [K|K|K], FEDDECISION-24SEP-C25×VPU [B|K|K], KXECDJT306×VDC [K|K|K], KXECKH276×VDE [K|K|K], KXECKH276×VIS [K|K|K], KXFEDDECISION-24DEC-C25×VFH [B|K|K], KXECDJT316×VDE [N|N|N], KXECKH287×VNQ [N|N|N], RATECUT-24SEP18×VCR [N|N|N], RATECUT-24SEP18×VGT [N|N|N], RATECUT-24SEP18×VOX [N|N|N]

### By ETF sector

- **Comm** (6): KXECDJT281×VOX [B|E|E], KXECKH276×VOX [E|E|E], FEDDECISION-24SEP-C25×VOX [K|K|K], 538APPROVEMAX-24OCT31-T43×VOX [N|N|N], AAAGASM-24SEP30-US-3.15×VOX [N|N|N], RATECUT-24SEP18×VOX [N|N|N]
- **Cons.Disc** (5): KXECKH276×VCR [K|B|B], KXECDJT281×VCR [E|E|E], 538APPROVEMAX-24SEP30-T43×VCR [N|N|N], AAAGASM-24SEP30-US-3.15×VCR [N|N|N], RATECUT-24SEP18×VCR [N|N|N]
- **Cons.Staples** (4): FEDDECISION-24SEP-C25×VDC [E|E|B], KXECKH276×VDC [B|B|B], KXECDJT306×VDC [K|K|K], KXAAAGASM-24NOV30-US-3.30×VDC [N|N|N]
- **Energy** (4): FEDDECISION-24NOV-H0×VDE [N|E|B], KXECKH276×VDE [K|K|K], KXAAAGASM-24NOV30-US-3.30×VDE [N|N|N], KXECDJT316×VDE [N|N|N]
- **Financials** (5): KXECKH276×VFH [B|B|B], KXECDJT316×VFH [E|E|E], KXFEDDECISION-24DEC-C25×VFH [B|K|K], KX538APPROVEMIN-24NOV30-T37×VFH [N|N|N], KXAAAGASM-24NOV30-US-3.30×VFH [N|N|N]
- **Health** (2): AAAGASM-24OCT31-US-3.20×VHT [N|N|N], KX538APPROVEMAX-24NOV30-T41×VHT [N|N|N]
- **Industrials** (5): KXECDJT316×VIS [K|B|B], KXFEDDECISION-24DEC-C25×VIS [B|B|B], KXECKH276×VIS [K|K|K], 538APPROVEMAX-24SEP30-T43×VIS [N|N|N], AAAGASM-24SEP30-US-3.15×VIS [N|N|N]
- **Info-Tech** (6): KXECDJT281×VGT [B|B|B], KXECKH276×VGT [B|B|B], KXFEDDECISION-24DEC-H0×VGT [E|E|E], AAAGASM-24SEP30-US-3.15×VGT [N|N|N], KX538APPROVEMAX-24NOV30-T41×VGT [N|N|N], RATECUT-24SEP18×VGT [N|N|N]
- **Materials** (4): KXECDJT312×VAW [E|E|E], KXECKH276×VAW [E|E|E], 538APPROVEMAX-24SEP30-T43×VAW [N|N|N], AAAGASM-24SEP30-US-3.15×VAW [N|N|N]
- **Real-Estate** (5): FEDDECISION-24NOV-H0×VNQ [N|B|B], KXECDJT281×VNQ [E|E|E], KX538APPROVEMIN-24NOV30-T37×VNQ [N|N|N], KXAAAGASM-24NOV30-US-3.30×VNQ [N|N|N], KXECKH287×VNQ [N|N|N]
- **Utilities** (2): FEDDECISION-24SEP-C25×VPU [B|K|K], AAAGASM-24OCT31-US-3.15×VPU [N|N|N]

### By reliability tier (df-based)

- **Adequate** (12): FEDDECISION-24NOV-H0×VDE [N|E|B], FEDDECISION-24NOV-H0×VNQ [N|B|B], FEDDECISION-24SEP-C25×VDC [E|E|B], KXECDJT281×VGT [B|B|B], KXFEDDECISION-24DEC-C25×VIS [B|B|B], KXECDJT281×VCR [E|E|E], KXECDJT281×VNQ [E|E|E], KXECDJT281×VOX [B|E|E], KXFEDDECISION-24DEC-H0×VGT [E|E|E], FEDDECISION-24SEP-C25×VOX [K|K|K], FEDDECISION-24SEP-C25×VPU [B|K|K], KXFEDDECISION-24DEC-C25×VFH [B|K|K]
- **Cannot-estimate** (23): 538APPROVEMAX-24OCT31-T43×VOX [N|N|N], 538APPROVEMAX-24SEP30-T43×VAW [N|N|N], 538APPROVEMAX-24SEP30-T43×VCR [N|N|N], 538APPROVEMAX-24SEP30-T43×VIS [N|N|N], AAAGASM-24OCT31-US-3.15×VPU [N|N|N], AAAGASM-24OCT31-US-3.20×VHT [N|N|N], AAAGASM-24SEP30-US-3.15×VAW [N|N|N], AAAGASM-24SEP30-US-3.15×VCR [N|N|N], AAAGASM-24SEP30-US-3.15×VGT [N|N|N], AAAGASM-24SEP30-US-3.15×VIS [N|N|N], AAAGASM-24SEP30-US-3.15×VOX [N|N|N], KX538APPROVEMAX-24NOV30-T41×VGT [N|N|N], KX538APPROVEMAX-24NOV30-T41×VHT [N|N|N], KX538APPROVEMIN-24NOV30-T37×VFH [N|N|N], KX538APPROVEMIN-24NOV30-T37×VNQ [N|N|N], KXAAAGASM-24NOV30-US-3.30×VDC [N|N|N], KXAAAGASM-24NOV30-US-3.30×VDE [N|N|N], KXAAAGASM-24NOV30-US-3.30×VFH [N|N|N], KXAAAGASM-24NOV30-US-3.30×VNQ [N|N|N], KXECKH287×VNQ [N|N|N], RATECUT-24SEP18×VCR [N|N|N], RATECUT-24SEP18×VGT [N|N|N], RATECUT-24SEP18×VOX [N|N|N]
- **Low-info** (2): KXECDJT312×VAW [E|E|E], KXECDJT306×VDC [K|K|K]
- **Very-low-info** (11): KXECDJT316×VIS [K|B|B], KXECKH276×VCR [K|B|B], KXECKH276×VDC [B|B|B], KXECKH276×VFH [B|B|B], KXECKH276×VGT [B|B|B], KXECDJT316×VFH [E|E|E], KXECKH276×VAW [E|E|E], KXECKH276×VOX [E|E|E], KXECKH276×VDE [K|K|K], KXECKH276×VIS [K|K|K], KXECDJT316×VDE [N|N|N]

> Note: auto-generated from the tables above; edit this file then merge into the report. Figure: plots/classification_summary.png.