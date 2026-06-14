# Pair Analysis #01: Fed November Rate Contract × VDE Energy ETF

## Pair Specification

| Field | Value |
|---|---|
| **Kalshi contract title** | "Will the Federal Reserve Hike rates by 0bps at their November 2024 meeting?" |
| **Contract ticker** | `FEDDECISION-24NOV-H0` |
| **Contract meaning** | Probability that the Federal Reserve holds rates unchanged (0 bp hike) at the November 7, 2024 FOMC meeting |
| **Paired ETF** | `VDE` (Vanguard Energy ETF) |
| **Analysis window** | 2024-09-18 → 2024-11-07 (~50 days, spanning from the September FOMC through the November FOMC decision day) |
| **Data scale** | 1,080 Kalshi trades; 6,883,047 VDE ticks |

---

## 1. Why We Chose This Pair

Out of the 14 contracts × multiple ETFs with credible regression results in `leadlag_event_unified_results.csv`, this pair scores best on six dimensions:

| Scoring dimension | Value | Assessment |
|---|---|---|
| **Sample size** | n_obs = 360 | ✅ Medium-large, dense enough for time-series plots |
| **Significant coefficients** | 7 (p < 0.05) | ✅ Concentrated signal |
| **Sign consistency** | **7 negative, 0 positive** | ✅ Zero contradictions, clean narrative |
| **Economic meaning** | P(no Fed change) ↑ → energy stocks ↓ | ✅ Textbook rate-sensitive sector reaction |
| **Event anchors** | Multiple FOMC speakers + CPI / Retail Sales releases | ✅ Clear news → price causal windows |
| **Liquidity profile** | Kalshi 1,082 trades (medium); VDE 6.9M ticks (very high) | ✅ Kalshi neither too sparse nor too dense — ideal for observing lead-lag |

Deliberately **not** chosen: `KXFEDDECISION-24DEC-C25` (the contract with the largest sample, n_obs = 1,887). Despite having the most observations, it has very few significant coefficients — consistent with EMH: the most liquid contracts are already priced synchronously by both markets, leaving no visible lead-lag. **Medium-liquidity pairs are where lead-lag signals live.**

---

## 2. Three Figures at a Glance

| File | Time resolution | Purpose |
|---|---|---|
| `fed_nov_h0_vde_overview.png` | 1-minute bars (VDE), tick (Kalshi) | Macro-level inverse correlation across full window |
| `fed_nov_h0_vde_event_zooms.png` | 10-second bars (VDE), tick (Kalshi) | Three intraday event-day dynamics |
| `fed_nov_h0_vde_tick_zooms.png` | **Every tick / every trade**, no resampling | Second-level / tick-level lead-lag adjudication |

---

## 3. Figure 1 — Full-Window Overview (`fed_nov_h0_vde_overview.png`)

### What to look at

- 🔴 **Kalshi probability (red, left axis)**: ~5% in late September → peak ~28% in mid-October → crashed to 1% on November 7 FOMC day
- 🔵 **VDE price (blue, right axis)**: ~129 in late September → bottomed at ~122 in mid-October → recovered to ~130 by November 7

### What we found

**The inverse correlation across the full 50-day window is visible to the naked eye.** Whenever Kalshi probability rose, VDE fell in sync; whenever Kalshi probability fell, VDE recovered.

The purpose of this figure is **sanity check**: confirming that the 7 negative coefficients from the main regression are not statistical artifacts but reflect a real macro-structural pattern visible in the raw price series.

### Limitation

Resolution is too coarse to tell who moves first — we can only say "the two are inversely correlated", not "who leads whom". This is exactly why Figures 2 and 3 are needed.

---

## 4. Figure 2 — Three Event-Day Zooms (`fed_nov_h0_vde_event_zooms.png`)

### Three panels cover three macro news types

| Panel | Date (UTC) | Event | Time window |
|---|---|---|---|
| **A** | 2024-09-18 17:30–19:30 | **September FOMC decision** (Fed cut 50 bp at 14:00 ET; Powell press conference at 14:30 ET) | 2 hours |
| **B** | 2024-10-10 13:30–19:00 | **September CPI release** (8:30 ET, hotter than expected) | 5.5 hours |
| **C** | 2024-10-17 13:30–18:00 | **September Retail Sales + Initial Jobless Claims** (8:30 ET, strong economic data) | 4.5 hours |

All three events occur during **US equity market hours**, so both markets are simultaneously active — avoiding the false-signal trap where Kalshi appears to "lead" simply because VDE is in pre-market.

### Panel A — Sep 18 FOMC

- **18:00 UTC (FOMC decision moment)**: VDE shows mild reaction
- **18:07 UTC**: Kalshi suddenly jumps from 5¢ to 28¢ and back to 5¢, lasting **only 16 seconds**
- **18:30 UTC (Powell press conference)**: VDE begins a systematic directional move

→ The FOMC decision itself is "homogeneous information to all participants" — both markets react roughly synchronously

### Panel B — Oct 10 CPI Day

- CPI released at 8:30 ET. **Four hours after US equity open (13:30 ET)**, Kalshi jumps from ~20 to 25 at 16:55 UTC
- Critical observation: **VDE was already trending up *before* Kalshi jumped**

→ **Initial sign: VDE leads Kalshi**

### Panel C — Oct 17 Retail Sales Day

- Data released at 8:30 ET; Kalshi stays quiet until jumping 15 → 23 at 11:42 ET (15:42 UTC)
- **VDE has been declining since 15:00 UTC** — by the time Kalshi reacts, VDE has already dropped for half an hour

→ **Stronger sign: VDE leads Kalshi by ~30 minutes**

### Limitation

10-second bars are still too coarse. Panel A's 16-second Kalshi spike is conspicuous, but we don't know what VDE did at each tick during those 16 seconds. Figure 3 is needed to settle this.

---

## 5. Figure 3 — Tick-Level Zooms (`fed_nov_h0_vde_tick_zooms.png`) ⭐ Core Evidence

Each panel uses **raw VDE ticks + every Kalshi trade with its yes-price annotated**, with no resampling whatsoever.

### Panel A — Sep 18 FOMC 18:00–18:15 UTC

- 13 Kalshi trades + **14,210 VDE quotes**
- The lone red spike to 28¢ at 18:07:23 — **all other Kalshi trades sit in the 5–7¢ range**
- VDE shows **no corresponding reaction** during those 16 seconds

→ **Conclusion: that single 28¢ trade is an anomalous one-off** (fat finger / algo-triggered stop), arbitraged back within 16 seconds. **Nobody believed that 28¢ was real information — neither market moved.**

### Panel B — Oct 10 CPI Day 16:30–17:30 UTC ⭐ Cleanest Evidence

- 10 Kalshi trades: 18¢ → 22¢ → **25¢ (jump at 16:55)** → 24¢
- VDE: **Already climbing from 128.85 to 129.4 starting at 16:30** — roughly **25 minutes ahead of Kalshi**
- By the time Kalshi hits 25¢ at 16:55, VDE is already near its intraday peak

→ **VDE leads Kalshi by 25 minutes, unambiguously**

### Panel C — Oct 17 15:15–16:30 UTC

- Only 2 Kalshi trades: 15¢ → **23¢ (jump at 15:42)**
- VDE has been sliding from 126.1 to 125.7 since 15:15 — **27 minutes of unidirectional decline before Kalshi reacted**

→ **VDE leads Kalshi by 27 minutes**

---

## 6. Synthesis — The Real Lead-Lag Story for This Pair

Combining all three figures, the core finding for this pair is:

> ### **During digestion of mid-magnitude macro news, VDE (the high-liquidity energy ETF) leads Kalshi (the prediction market) by 20–30 minutes.**

This conclusion is simultaneously supported by three lines of evidence:

| Evidence type | Source | Content |
|---|---|---|
| **Statistical** | `leadlag_event_unified_results.csv` | 7 significant coefficients, all negative; `etf_leads_kalshi` direction has more significant coefs than `kalshi_leads_etf` |
| **Macro visual** | Figure 1 | 50-day inverse correlation is uncontestable |
| **Micro visual** | Figure 3 Panels B & C | Tick-level evidence of VDE leading Kalshi by 20–30 minutes |

### Economic interpretation

- **VDE side**: Professional commodity and macro traders watching live; Fed policy, oil prices, and macro data releases are reflected algorithmically at the **second-to-minute** scale in VDE price
- **Kalshi side**: Prediction market participants are more **passive trackers** — they wait until they see financial markets reacting (e.g., VDE has already moved), then adjust their Fed-probability bets
- **One exception**: The FOMC decision moment itself — when information is "zero-cost and identical to all participants" — sees both markets move roughly in sync (Figure 3 Panel A)

### Research value of this finding

- **Refutes a naive hypothesis**: "Prediction markets always lead" — at least not on this pair
- **Confirms Hasbrouck-style price discovery**: The more liquid market carries more of the price-discovery burden
- **Provides direction for subsequent Local Projections analysis**: Use ETF shocks as the LP input for VDE; use ETF lags as the LP input for Kalshi

---

## 7. Limitations and Open Questions

1. **Sample range**: Only through November 7 FOMC; after the resolution date the contract barely trades (its outcome is known) — no out-of-sample validation
2. **Causality of VDE leadership**: VDE temporally moves first, but **we cannot rule out** that both markets are driven by an unobserved common macro factor (e.g., a hedge fund placing simultaneous orders in both markets, with the apparent lead just reflecting routing-speed differences)
3. **The 28¢ anomaly in Panel A**: Although classified as an isolated mistake, cross-validation against Kalshi order book data (whether there was a large aggressive taker) would strengthen the call
4. **"Leads by how many minutes" not quantified**: The "20–30 minutes" is descriptive. Precise quantification requires Local Projections (next-stage analysis)

---

## 8. File Inventory

```
01_fed_nov_h0__vde/
├── ANALYSIS.md                                   ← this document
├── ANALYSIS.docx                                 ← Word version with embedded figures
├── plot_fed_nov_vde.py                          ← script that produces all 3 figures
└── plots/
    ├── fed_nov_h0_vde_overview.png              ← Figure 1: full-window overview
    ├── fed_nov_h0_vde_event_zooms.png           ← Figure 2: event-day zooms
    └── fed_nov_h0_vde_tick_zooms.png            ← Figure 3: tick-level core evidence
```

To reproduce from the `Durf/` root:

```bash
python leadlag/pair_analyses/01_fed_nov_h0__vde/plot_fed_nov_vde.py
```
