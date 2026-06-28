# Lead/Lag classification summary

Scope: all 48 pairs (Kalshi contract x ETF). Lean rule: across calendar+event, count
significant (p<0.05) lags with k>0 (Kalshi leads) vs k<0 (ETF leads); the net majority sets the lean.
Reliability rule: tiered by residual df (= effective obs - #parameters), NOT a trade-count cutoff.

## Overall

- Kalshi-leads: 4   |   ETF-leads: 4   |   Balanced/mixed: 8   |   No-sig-lead: 32

## By contract type

```
lean           Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
contract_type                                                             
Election                  3          4               8            3     18
GasPrice                  0          0               0           11     11
Rates(FOMC)               1          0               0           10     11
Approval                  0          0               0            8      8
```

## By event kind (sharp one-shot vs continuous)

```
lean             Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
event_kind                                                                  
Sharp(one-shot)             4          4               8           13     29
Continuous                  0          0               0           19     19
```

## By ETF sector

```
lean          Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
sector                                                                   
Comm                     1          1               1            3      6
Info-Tech                0          1               1            4      6
Cons.Disc                2          0               0            3      5
Financials               0          1               1            3      5
Industrials              0          0               2            3      5
Real-Estate              0          0               1            4      5
Cons.Staples             0          1               1            2      4
Energy                   1          0               0            3      4
Materials                0          0               1            3      4
Health                   0          0               0            2      2
Utilities                0          0               0            2      2
```

## By statistical reliability (df-based)

```
lean             Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
reliability                                                                 
Cannot-estimate             0          0               0           23     23
Adequate                    2          1               2            7     12
Very-low-info               2          3               5            1     11
Low-info                    0          0               1            1      2
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
- **Even the reliable group is not one-sided**: of 12 adequate-df pairs, Kalshi-leads 2 and ETF-leads 1 -- no side dominates.
- **Direction is threshold-robust but method-split** (see graded table above): across p<0.05/0.10/0.15 the linear regressions (calendar, event) split ~1:1 with no net lead at any threshold, while the direction-only probit consistently favors ETF-leads (~5:1). Any lead lives in the *sign* of ETF moves, not their magnitude.
- **Construction note**: event uses the same causal backward-diff as calendar (differing only in active-event vs clock timepoints). An earlier forward-return event construction had spuriously inflated ETF-leads by overlapping each event's forward window with the next event; that artifact is removed, after which event splits ~1:1.
- **By type**: election / FOMC (one-shot event) contracts contribute almost all of the estimable, significant structure; gas-price / approval (continuous) contracts mostly fall in 'cannot estimate'.
- **Conclusion**: directional lead is **NOT concentrated in any single clean category**; the strongest signal comes from adequate-df one-shot-event contracts (election, FOMC), but within them Kalshi-leads and ETF-leads coexist -- supporting the main finding of 'no clean single-direction lead'.

> Note: auto-generated from the tables above; edit this file then merge into the report. Figure: plots/classification_summary.png.