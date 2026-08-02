# Pair Analysis #02: Trump 281-257 Contract × VCR Consumer Discretionary ETF

## Pair Specification

| Field | Value |
|---|---|
| **Kalshi contract title** | "Will Trump win 281-257 - AZ, GA, NC, PA?" |
| **Contract ticker** | `KXECDJT281` |
| **Contract meaning** | Probability that Trump wins the 2024 U.S. presidential election by the specific Electoral College count 281-257 (winning AZ, GA, NC, PA) |
| **Paired ETF** | `VCR` (Vanguard Consumer Discretionary ETF) |
| **Analysis window** | 2024-11-04 → 2024-11-15 (~12 days, spanning the election eve, Election Day, the result-night swing, and the post-election Trump-trade rally) |
| **Data scale** | 907 Kalshi trades; 770,422 VCR ticks |

---

## 1. Why We Chose This Pair (And What We Were Looking For)

This pair was chosen specifically as a **methodological complement** to Pair #01 (Fed × VDE):

| Dimension | Pair #01 (Fed × VDE) | Pair #02 (Election × VCR) |
|---|---|---|
| Information source | Central bank speakers, macro data | **Real-time state-by-state vote counting** |
| Signal type | Slow-moving "expectation updates" | **Discrete "fact revelations"** |
| Who theoretically has informational edge | Professional macro traders | **Kalshi bettors** (closer to AP vote tallies) |

### Initial Hypothesis (which the data partially overturns)

We hypothesized that **for election information specifically, Kalshi might lead VCR**, since prediction-market participants watch raw vote counts in real time, while equity traders react to broader market narratives. This would create a clean 2×2:

|  | Fed-policy news | Election news |
|---|---|---|
| **Pair #01** | VDE leads Kalshi ✓ |  |
| **Pair #02** |  | Kalshi leads VCR ??? |

The actual finding turned out to be more nuanced — see Section 6.

### Pair-level scoring criteria

| Dimension | Value | Assessment |
|---|---|---|
| Sample size | n_obs = 285 | ✅ Adequate |
| Significant coefficients | 14 (p < 0.05) | ✅ **Most in the entire dataset** |
| Sign consistency | **14 positive, 0 negative** | ✅ Cleanest sign pattern in dataset |
| Economic meaning | Trump win prob ↑ → consumer discretionary ↑ | ✅ Classic "Trump trade" |
| Event anchors | Election Day + result night + post-election week | ✅ Unique dramatic event window |
| Liquidity profile | Kalshi 907 trades; VCR 770k ticks | ✅ Both markets active during overlap hours |

---

## 2. Five Figures at a Glance (Figure 5 added in correction pass)

| File | Time resolution | Purpose |
|---|---|---|
| `ecdjt281_vcr_overview.png` | 1-minute bars (VCR), tick (Kalshi) | Macro-level co-movement across full window |
| `ecdjt281_vcr_event_zooms.png` | 10-second bars (VCR), tick (Kalshi) | Three intraday event-day dynamics |
| `ecdjt281_vcr_tick_zooms.png` | **Every tick / every trade**, no resampling | Second-level lead-lag adjudication |
| `ecdjt281_vcr_election_night.png` | 1-min bars (VCR), tick (Kalshi) | **Special:** election-night structural pattern (VCR closed) |
| **`ecdjt281_vcr_multiday_compression.png`** | **Hourly resample** | **⭐ Multi-day Type B compression (Kalshi peak leads VCR adjustment by ~6 days)** |

Pair #02 has **one more figure than Pair #01** because the election-night overnight pattern is a unique structural feature that requires its own treatment. Figure 5 was added in a correction pass to capture multi-day Type B compression.

---

## 3. Figure 1 — Full-Window Overview (`ecdjt281_vcr_overview.png`)

### What to look at

- 🔴 **Kalshi probability (red, left axis)**: ~12% on 11/4 → election-night swing peaks at **98%** (11/6 03:00 UTC) → declines to single digits as the actual Trump victory took a different specific state path
- 🔵 **VCR price (blue, right axis)**: ~340 on 11/4 → **gap up to ~353** at 11/6 14:30 UTC open → steady step-wise climb to ~370 over the following week

### What we found

**The election-night Kalshi swing is the single most dramatic price action in the entire dataset.** Probability vaults from ~22% to 98% over a few hours, then crashes back as the specific 281-257 outcome looks less likely (Trump's actual winning path was wider).

VCR's behavior is structurally different from Kalshi:
- VCR is **closed** during the dramatic overnight Kalshi swing
- VCR opens 11/6 with a large gap-up (+1%) that integrates the overnight result
- VCR continues climbing for ~6 more trading days as the "Trump trade" narrative widens (tax cuts, deregulation expectations)

### Limitation

Resolution too coarse to assess intraday lead-lag.

---

## 4. Figure 2 — Three Event-Day Zooms (`ecdjt281_vcr_event_zooms.png`)

### Three panels cover three election-week phases

| Panel | Date (UTC) | Phase | Time window |
|---|---|---|---|
| **A** | 2024-11-05 15:00–21:00 | Election Day afternoon (pre-poll-close) | 6 hours |
| **B** | 2024-11-06 14:30–17:30 | Morning after election (VCR gap-open + catch-up) | 3 hours |
| **C** | 2024-11-06 18:00–21:00 | Afternoon dramatic Kalshi swings | 3 hours |

### Panel A — Election Day Afternoon (Nov 5)

- Kalshi cluster-jumps ±8–10pp through the afternoon as exit-poll rumors circulate
- VCR drifts up modestly from 341 to 344

→ **Both markets move in the same direction together — no clean lead-lag here**

### Panel B — Morning After Election (Nov 6)

- VCR **gaps up from ~350 to ~353 at open** absorbing overnight result
- Kalshi has already declined from its 98¢ overnight peak (now ~17%) as the 281-257 specific outcome looks less likely
- Through the morning, Kalshi continues declining (17 → 5)

→ **VCR price stays positive; Kalshi declines on path-specificity. Different dynamics — not a simple lead-lag.**

### Panel C — Afternoon Dramatic Swings (Nov 6)

- **18:34 UTC**: Kalshi spikes 4→25→4 in 34 seconds — single anomalous trade pattern
- **18:57 UTC**: Another spike to 24
- **20:50 UTC**: ±14 swing near close
- VCR climbs steadily from 353 to 355 throughout, unaffected by Kalshi spikes

→ **The Kalshi spikes are anomalous trades, not real information** — VCR ignores them. Underlying VCR trend (up) reflects digestion of the broader Trump-trade narrative.

---

## 5. Figure 3 — Tick-Level Zooms (`ecdjt281_vcr_tick_zooms.png`)

### Panel A — Nov 6 18:30–19:15 UTC: The 4→25→4 spike

- 10 Kalshi trades + 5,026 VCR ticks
- 18:34 UTC: Kalshi jumps to 25¢ then back to 4¢ in seconds
- **VCR shows no corresponding reaction** to the 25¢ print
- After the spike, VCR drifts gently upward, but in a way that began *before* the 25¢ trade

→ **Same diagnosis as Pair #01 Sep 18 FOMC anomaly**: the 25¢ is an isolated mistaken trade (fat finger or algo error), arbitraged back instantly. **Neither market believed it was real information.**

### Panel B — Nov 6 20:30–21:00 UTC: Late-day swing near close

- 7 Kalshi trades + 4,590 VCR ticks
- Kalshi swings 4 → 19 → 4 — again the same anomalous spike pattern at 20:50
- VCR climbs from 354.4 to 355 — driven by underlying trend, not the Kalshi spike

→ **Same pattern: isolated Kalshi spike, no VCR response.**

### Panel C — Nov 5 16:30–17:00 UTC: Election Day cluster jumps

- **21 Kalshi trades + 3,423 VCR ticks** — Kalshi is genuinely active here (not just spikes)
- Kalshi cluster jumps 8 → 18 → 12 → 21 over 30 minutes
- VCR rises modestly from 342.0 to 342.5 in parallel
- **Both markets move up together — Kalshi visually leads by a few seconds on some trades, VCR leads on others — no consistent direction**

→ **This is the most honest tick-level evidence:** when both markets digest the same information stream (election day exit-poll chatter), they move roughly **synchronously**, with no consistent lead-lag detectable at the tick level.

---

## 6. Figure 4 — Election Night Special (`ecdjt281_vcr_election_night.png`) ⭐ Core Finding

This is the figure that reveals the actual structural story of this pair.

### What it shows

- **Time axis**: Nov 5 19:00 UTC → Nov 6 21:00 UTC (~26 hours, covering pre-close, overnight, and full Nov 6)
- **Grey shaded region**: VCR market closed (21:00 UTC Nov 5 → 14:30 UTC Nov 6 — about 17.5 hours)
- 🔴 Kalshi probability and 🔵 VCR price overlaid

### Three key moments

1. **23:00 UTC Nov 5**: Eastern-state polls close. Kalshi starts running (the contract becomes informationally active).
2. **03:00 UTC Nov 6 (22:00 ET Nov 5)**: Kalshi peaks at **98¢** as key states (PA, GA, NC) start being called for Trump. **VCR has been closed for 6 hours.**
3. **14:30 UTC Nov 6 (9:30 ET)**: VCR opens with a large gap-up (+~1%), **integrating 17.5 hours of overnight Kalshi-priced information in a single jump**.

### The structural finding

> ### **During election night, Kalshi monopolizes price discovery for ~17.5 hours while VCR is closed. When VCR finally opens, it gaps to reflect the overnight Kalshi consensus.**

This is **not** "Kalshi leads VCR at tick level". It's a different, more interesting structural property:

| Market state | Price discovery site |
|---|---|
| Both markets open (intraday) | Roughly synchronous (Figure 3 Panel C, Figure 2 Panel A) |
| Equity market closed (overnight) | **Kalshi alone** — by structural necessity |
| First moment after equity reopens | VCR gap-up absorbs the entire overnight Kalshi consensus |

### Why this matters

- **Prediction markets have a unique structural role**: filling the price-discovery gap when traditional markets are closed
- **This is most valuable for events that resolve overnight or on weekends** — exactly the case for U.S. presidential elections
- **It is not a tick-level lead-lag in the standard sense** — Hasbrouck-style information shares can't be computed during the overnight closure (only one market has prices to share)

---

## 6b. Figure 5 — Multi-day Type B Compression ⭐ Added in correction pass

After identifying Type A (spike) vs Type B (compressed real adjustment) Kalshi moves, we re-examined Pair #02 at multi-day scale and found a clean (though noisier than Pair #03) Type B compression.

### What it shows

- 🔴 **Red shaded band (narrow, ~1 night)**: Kalshi-281 surges from ~22% to 98% peak overnight (11/5 19:00 → 11/6 06:00 UTC). After 11/6 morning Kalshi-281 *falls* because the specific 281-257 path didn't happen (Trump actually won 312-226).
- 🔵 **Blue shaded band (wide, ~5 days)**: VCR price climbs from ~340 to ~370 over 5 trading days (11/6 14:30 → 11/12 21:00 UTC).
- **Black double-arrow**: ~6-day lead from Kalshi-281 peak to VCR completion.

### Important nuance — noisier signal than Pair #03

Unlike Pair #03 where Kalshi 312 was the actual outcome (so probability went up and stayed at 99%), Pair #02's Kalshi 281 contract is for a SPECIFIC outcome that didn't happen. So:

- **Kalshi-281's overnight peak at 98%** = market thinking "281-257 is the most likely Trump-win path"
- **Kalshi-281's subsequent decline** = market updating that the actual path was different
- **VCR's monotonic rise** = broader "Trump won → consumer up" trade

So the **underlying signal both markets respond to is "Trump won"**. Kalshi-281 reflects this via a noisy peak; VCR reflects it via a smooth rise. **The COMPRESSION is still present** — Kalshi's full information about "Trump winning" was visible at the overnight peak; VCR took 5 more days to fully price in the consumer-rally implications.

### Why VCR takes 5 days (3 mechanisms, same as Pair #03)

1. **Closure asymmetry**: VCR closed ~17.5 hours during election night; Kalshi was open and priced in result immediately
2. **Signal complexity asymmetry**: Kalshi tracks one probability; VCR must integrate "Trump → tax cuts → consumer confidence → discretionary spending"
3. **Order book thickness**: VCR's deep book requires many trades to drift

### Important caveat

The 6-day lead is **structural** (closure + slow integration), **not informational**. Kalshi traders are not "smarter" than VCR traders — they just had less to figure out (one number vs full economic chain) and more time when alone.

---

## 7. Synthesis — The Real Lead-Lag Story for This Pair

Combining all four figures, the core findings are:

### Finding 1 — Intraday synchronization (counter to initial hypothesis)

When both markets are simultaneously open, **Kalshi and VCR move roughly synchronously**, with no consistent tick-level lead-lag detectable for election information. This is **different** from Pair #01 where VDE clearly led Kalshi by 20–30 minutes.

The regression direction breakdown (etf_leads_kalshi: 8, kalshi_leads_etf: 5, contemp: 1) is consistent with this — neither direction dominates strongly.

### Finding 2 — Anomalous Kalshi trades are universal

The pattern of isolated 25¢ / 24¢ / 19¢ spikes that revert within seconds and elicit zero ETF response is **identical to** the 28¢ spike at the Sep 18 FOMC in Pair #01. This appears to be a **structural Kalshi market microstructure phenomenon** (fat fingers, algo errors), not contract-specific.

### Finding 3 — Election night is a unique structural regime ⭐ Most Important

**Kalshi monopolizes price discovery for the ~17.5 hours when U.S. equity markets are closed during election night.** When VCR opens on Nov 6, it gaps up to absorb the entire overnight Kalshi consensus. This is not a lead-lag in the standard sense — it's prediction markets serving as the only available price discovery venue during a closure window.

### Finding 4 — Multi-day Kalshi leadership ⭐ Added in correction pass

At multi-day scale, **Kalshi-281's overnight peak leads VCR's full adjustment by ~6 days**. This is a clean (though noisier than Pair #03) Type B compression. See Section 6b.

The lead is **structural** (closure asymmetry + slow VCR integration), **not informational** (Kalshi traders aren't smarter).

### Comparison table (Pair #01 vs Pair #02, with multi-day scale added)

|  | Pair #01: Fed × VDE | Pair #02: Election × VCR |
|---|---|---|
| Statistical signature | 7 neg coefs, etf_leads dominant | 14 pos coefs, etf_leads slightly favored |
| **Tick-level verdict** | **VDE leads Kalshi by 20–30 min** | **Roughly synchronous** |
| **Multi-day verdict** | No multi-day compression | **Kalshi leads VCR by ~6 days** |
| Anomalous spike pattern | Sep 18 28¢ event | Nov 6 25¢, 24¢, 19¢ events (recurring) |
| Unique structural pattern | None | **Overnight monopoly during election night** |
| Sign of co-movement | Negative (rate hold → energy down) | Positive (Trump win → consumer up) |

### Revised 2×2 framework for the eventual paper (with timescale dimension)

| | Markets simultaneously active (tick scale) | One market closed / multi-day scale |
|---|---|---|
| **Macro/policy info (Pair #01)** | ETF leads Kalshi 20–30 min | No multi-day compression — both adjust similarly |
| **Event-revelation info (Pair #02)** | Synchronous | **Kalshi leads VCR by ~6 days** (closure + slow integration) |

---

## 8. Limitations and Open Questions

1. **Anomalous trades**: The pattern of one-off 25¢/24¢ spikes that revert within seconds appears across pairs. To strengthen the claim that these are "not information", cross-validation against Kalshi order book data (whether there was a large aggressive taker, or whether it was a single tiny order) would help.
2. **Overnight Kalshi → VCR open gap quantification**: The Nov 6 14:30 UTC gap-up of ~1% reflects the integration of overnight Kalshi. We have not quantified the magnitude: how many bps of VCR gap-up per percentage point of overnight Kalshi swing? This is a candidate for a structural regression.
3. **Sample is one election**: Findings on overnight price discovery may not generalize beyond the 2024 election. Comparison with other contracts that resolve overnight (Fed surprise overnight statements?) is limited.
4. **Direction of intraday synchronization**: Visually we say "roughly synchronous" but a more rigorous test would compute lead-lag correlation functions at sub-second resolution.

---

## 9. File Inventory

```
02_ecdjt281__vcr/
├── ANALYSIS.md                                   ← this document
├── ANALYSIS.docx                                 ← Word version with embedded figures
├── plot_ecdjt281_vcr.py                          ← script producing all 5 figures
└── plots/
    ├── ecdjt281_vcr_overview.png                 ← Figure 1: full-window overview
    ├── ecdjt281_vcr_event_zooms.png              ← Figure 2: event-day zooms
    ├── ecdjt281_vcr_tick_zooms.png               ← Figure 3: tick-level zooms
    ├── ecdjt281_vcr_election_night.png           ← Figure 4: election-night special
    └── ecdjt281_vcr_multiday_compression.png     ← Figure 5: multi-day Type B compression (added in correction pass)
```

Reproduce from the `Durf/` root:

```bash
python leadlag/pair_analyses/02_ecdjt281__vcr/plot_ecdjt281_vcr.py
```
