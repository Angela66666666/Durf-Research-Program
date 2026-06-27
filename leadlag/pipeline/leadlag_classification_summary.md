# Lead/Lag classification summary

Scope: all 48 pairs (Kalshi contract x ETF). Lean rule: across calendar+event, count
significant (p<0.05) lags with k>0 (Kalshi leads) vs k<0 (ETF leads); the net majority sets the lean.
Reliability rule: tiered by residual df (= effective obs - #parameters), NOT a trade-count cutoff.

## Overall

- Kalshi-leads: 4   |   ETF-leads: 7   |   Balanced/mixed: 8   |   No-sig-lead: 29

## By contract type

```
lean           Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
contract_type                                                             
Election                  3          6               7            2     18
GasPrice                  0          0               0           11     11
Rates(FOMC)               1          1               1            8     11
Approval                  0          0               0            8      8
```

## By event kind (sharp one-shot vs continuous)

```
lean             Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
event_kind                                                                  
Sharp(one-shot)             4          7               8           10     29
Continuous                  0          0               0           19     19
```

## By ETF sector

```
lean          Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
sector                                                                   
Comm                     1          1               1            3      6
Info-Tech                0          2               1            3      6
Cons.Disc                1          1               0            3      5
Financials               0          1               1            3      5
Industrials              1          0               1            3      5
Real-Estate              0          0               1            4      5
Cons.Staples             0          1               1            2      4
Energy                   1          0               0            3      4
Materials                0          0               2            2      4
Health                   0          0               0            2      2
Utilities                0          1               0            1      2
```

## By statistical reliability (df-based)

```
lean             Kalshi-leads  ETF-leads  Balanced/mixed  No-sig-lead  Total
reliability                                                                 
Cannot-estimate             0          0               0           23     23
Adequate                    1          4               2            5     12
Very-low-info               3          3               4            1     11
Low-info                    0          0               2            0      2
```

## Conclusion

- **Pairs without data expose themselves**: 23 **cannot be estimated** (params >= obs) and 11 have **very low df** (huge SE, 'significant' is untrustworthy) -- high-frequency lead-lag is only meaningful on the 12 pairs with adequate df.
- **Even the reliable group is not one-sided**: of 12 adequate-df pairs, Kalshi-leads 1 and ETF-leads 4 -- no side dominates.
- **By type**: election / FOMC (one-shot event) contracts contribute almost all of the estimable, significant structure; gas-price / approval (continuous) contracts mostly fall in 'cannot estimate'.
- **Conclusion**: directional lead is **NOT concentrated in any single clean category**; the strongest signal comes from adequate-df one-shot-event contracts (election, FOMC), but within them Kalshi-leads and ETF-leads coexist -- supporting the main finding of 'no clean single-direction lead'.

> Note: auto-generated from the tables above; edit this file then merge into the report. Figure: plots/classification_summary.png.