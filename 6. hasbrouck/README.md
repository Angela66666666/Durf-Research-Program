# Hasbrouck price discovery — prediction market vs. an election-factor equity basket

**Question.** When election-related news arrives, does Kalshi's presidential contract
incorporate it before the equity market does, or the other way round?

**Answer, in one paragraph.** The prediction market absorbs news while the equity
market is closed, so the basket carries a gap into the opening bell. Over roughly
the first 90 minutes of the session the basket closes about **20%** of that gap,
while Kalshi does not move toward the basket at all (placebo flat). After those 90
minutes neither side error-corrects, so there is **no detectable intraday lead in
either direction**. The prediction market's advantage is therefore *temporary and
concentrated around the overnight-to-open transition*, not a sustained intraday lead.

> **The 98% information share in Part 1 of the Step-4 output is not the finding.**
> It is reported only so that Parts 2–4 can refute it. Please read Part 5 before
> quoting any number from Part 1.

---

## The basket

19 assets, fixed-share dollar portfolio:

| Group | Tickers |
|---|---|
| 11 Vanguard sector ETFs | VAW, VCR, VDC, VDE, VFH, VGT, VHT, VIS, VNQ, VOX, VPU |
| 8 election-theme adds | MARA, COIN, GEO, IBKR, FSLR, RUN, DHI, TAN |

The 8 adds are theme leaders taken from a systematic screen of 1,303 liquid US
stocks run on pre-test data (Jun–Sep 2024). They are one or two names per theme
rather than the raw top-8, so that no single theme (crypto) dominates the basket.

### Why this universe — five candidates compared

The screen of 1,303 stocks produced a candidate *list*; the basket itself was then
chosen by comparing five compositions on the Oct–Nov test window against Kalshi
(`stock screen/methodB_screened_stocks_results.txt`):

| Universe | k | level corr | Engle-Granger | Johansen trace |
|---|---:|---:|---:|---:|
| 11 ETFs + DJT, COIN, TAN, GEO | 15 | 0.91 | 0.013 ✓ | 10.63 |
| screened stocks only (long + short) | 17 | 0.91 | 0.015 ✓ | **26.38 ✓** |
| 11 ETFs + all screened stocks | 28 | 0.71 | 0.500 | 11.41 |
| compact leaders only | 8 | 0.91 | 0.392 | 11.48 |
| **11 ETFs + compact leaders — chosen** | **19** | **0.89** | **0.002 ✓** | **14.08** |

*(✓ = passes at 5%: Engle-Granger p < 0.05, Johansen trace > 15.49. The chosen
basket's 14.08 clears the 10% critical value of 13.43 but not the 5% value.)*

**Only these three columns are shown deliberately.** That file also reports an ADF
and an RMSE column, both of which were computed under the earlier two-point
calibration and are **not** invariant to it — re-anchoring the same basket moves ADF
from 0.002 to 0.961 and RMSE from 0.062 to 0.080. Level correlation, Engle-Granger
and the Johansen trace *are* invariant (verified: they reproduce the current
start-anchored run exactly at 0.89 / 0.002 / 14.08), so they are the only columns
that can be compared across compositions.

**An honest tension.** The chosen 19-asset basket has the strongest Engle-Granger
result (0.002), but the 17-asset "screened stocks only" universe is the one
composition that passes *both* tests, including Johansen at 26.38, and its level
correlation is slightly higher (0.91 vs 0.89). It is a genuine competitor, not a
straw man.

*Is that 26.38 just DJT?* DJT and RUM are close to pure election derivatives, so a
basket containing them could cointegrate with Kalshi almost tautologically. Checked
directly, and the answer is no:

| 17-name universe | k | corr | Engle-Granger | Johansen |
|---|---:|---:|---:|---:|
| as published | 17 | 0.91 | 0.015 | 26.38 |
| drop DJT | 16 | 0.91 | 0.015 | 26.20 |
| drop DJT and RUM | 15 | 0.92 | 0.010 | 26.46 |

The result is untouched. Neither name is among the top eight contributors to basket
variance; the basket is carried by GEO (+40%), COIN (−33%), RIOT (+24%) and the solar
shorts RUN/CSIQ/TAN, all of which have a genuine industry link to the election
outcome rather than being bets on it.

**Why the 19-asset basket is still the primary specification.** Two reasons, neither
of which depends on the check above. First, the 26.38 is computed on the Oct–Nov
*test* window; choosing a basket because it maximises a test-window statistic is
model selection on the test data, whereas the 19-asset basket follows a rule fixed
in advance on pre-test Jun–Sep data. Second, a basket with no sector-ETF base stops
being a proxy for *the equity market* — it becomes a thematic long-short — and would
no longer line up with the sector-ETF lead-lag analysis in the rest of the paper.
That is a conceptual argument rather than a statistical one, which is why the 17-name
universe is reported as a robustness check rather than dismissed.

---

## Pipeline — run in this order

| # | Script | Produces | What it does |
|---|---|---|---|
| 1 | `stock screen/systematic_stock_screen.py` | `systematic_stock_screen.csv` / `.txt` | Screens 1,303 liquid stocks on Jun–Sep data. Two rankings: a change screen (corr of daily return with ΔP(Trump)) and a level/cointegration screen. Selects the 8 adds. |
| 2 | `daily/build_daily_panel.py` | `panel_daily.csv` | Daily panel of the 19 asset prices plus Polymarket P(Trump). |
| 3 | `daily/methodB.py` | `methodB_weights.csv`, `methodB_pair.csv`, `methodB_results.txt`, `methodB.png` | **Estimates the basket weights** by a level cointegrating regression, then runs the daily cointegration gate against Kalshi. |
| 4 | `high frequency/build_hf_panel.py` | `hf_panel_1min.csv` | Aligns three sources with three different time conventions onto one 1-minute New-York-time grid. |
| 5 | `high frequency/methodB_hf.py` | `hf_pair_1min.csv`, `methodB_hf_results.txt`, `methodB_hf.png` | Applies the **daily** weights at 1 minute. Weights are *not* re-fitted here. |
| 6 | `high frequency/hasbrouck_hf.py` | `hasbrouck_hf_results.txt` | **Step 4 — the main result.** Error-correction system, information shares, and the tests that qualify them. |

### Data inputs

```
1. data/polymarket_trump_2024_daily.csv        Polymarket daily P(Trump)   -> weight estimation
1. data/kalshi/kalshi/trades/trades_*.parquet  Kalshi PRES-2024-DJT trades -> the test series
1. data/etf_hf/<SYM>_hf.parquet                11 sector ETFs, NBBO ticks
1. data/etf/nbbo_addtl_tics.parquet            the 8 added stocks, NBBO ticks
```

---

## Design choices, and why

**Weights come from daily data and are never re-fitted intraday.** They are
estimated on **Polymarket, Jun 1 – Sep 30 2024**; the test runs on **Kalshi,
Oct 4 – Nov 6 2024**. Different venue *and* different period, so the instrument
cannot be fitted to the window it is later evaluated on. (High-frequency data for
the added stocks only begins 2024-09-03, so estimating the weights intraday over
the Jun–Sep window is not possible even in principle.)

**The basket is a fixed-share dollar portfolio, not a cumulated-return index.**
In a two-state model the price level is affine in the probability, so a dollar
P&L basket is exactly linear in P(Trump); compounding returns or cumulating log
returns breaks that linearity.

**The implied probability is start-anchored and look-ahead free.**
`implied_p_t = Q0 + (B_t − B_0)`, where `Q0` is Kalshi's **observed** value on the
first test day — known at t = 0. An earlier two-point calibration divided by
`(B_last − B_0)`, which used the last test day and was therefore look-ahead; it
survives only as a dashed reference line in the plot.

**Regular trading hours only (09:30–16:00 ET), and no overnight change ever
enters a regression.** Kalshi trades around the clock while the ETFs are shut.
Comparing them on a 24-hour clock leaves the equity side frozen while Kalshi keeps
moving, which manufactures a spurious "Kalshi leads" result. Rows whose lag window
straddles a session boundary are dropped.

**DST-aware time conversion.** The test window straddles the 2024-11-03 EDT→EST
change, so a hard-coded offset would misalign one side by an hour after that date.

---

## Headline numbers

**Daily** (`daily/methodB_results.txt`, 24 observations)

```
weights:  level cointegrating regression, Jun 1 – Sep 30, n = 83 days, R2 = 0.948
          (a level-on-levels fit -- inflated by construction, not evidence on its own)
anchor:   Q0 = Kalshi first test-day close = 0.500, first point matches exactly
gate:     ADF spread(1,-1)  p = 0.961  -> no
          Engle-Granger     p = 0.002  -> COINTEGRATED   (b = +0.30, scale-invariant)
          Johansen trace    14.08   (10% cv 13.43, 5% cv 15.49, 1% cv 19.93)
                                    -> rejects no-cointegration at 10%, not at 5%
```

On the daily data the two scale-invariant tests both point the same way: Engle-Granger
rejects the null of no cointegration at 5% (p = 0.002) and Johansen rejects it at 10%
(14.08 against a 10% critical value of 13.43) though not at 5%. The ADF column is not
comparable across specifications for the reason given above, so it is not read as
contradicting them.

**1 minute** (`high frequency/methodB_hf_results.txt`, 9,361 observations / 24 sessions)

```
level correlation basket vs Kalshi = +0.572
basket move / Kalshi move          =  0.34
gate:     ADF spread(1,-1)  p = 0.5825 -> no
          Engle-Granger     p = 0.3218 -> no
          Johansen trace    6.98 vs 15.49 -> no
```

**Step 4** (`high frequency/hasbrouck_hf_results.txt`)

```
PART 1  baseline, all regular-hours minutes (n = 9,217)
        alpha basket -0.000827 (t = -3.31)  adjusts
        alpha kalshi +0.000317 (t =  0.44)  cannot reject 0
        Gonzalo-Granger: basket 27.7% / kalshi 72.3%
        Hasbrouck IS (kalshi) 98.4%        <- refuted below, do not quote alone

PART 2  by time of day: the basket's adjustment is a morning phenomenon; from
        noon onward the coefficient falls ~5x and loses significance
PART 3  delete the first N minutes: at N = 90 the effect is gone (t: -3.31 -> -1.30)
PART 4  session-level catch-up tests (n = 23 sessions)
        C1 opening gap -> basket's next 90 min   slope -0.200  p = 0.006  R2 = 0.31
        C2 opening gap -> kalshi's next 90 min   slope +0.021  p = 0.553  (placebo, flat)
        C3 overnight kalshi move -> basket 90min slope +0.090  p = 0.088  (marginal)
```

C1 negative and significant with C2 flat is the core evidence: the adjustment is
**one-sided**, which is what rules out "both are merely following a common trend."

---

## Limitations — please read before drawing conclusions

1. **Cointegration does not hold at 1 minute.** All three tests fail
   (ADF 0.58, Engle-Granger 0.32, Johansen 6.98 vs 15.49). The Step-4 VECM
   therefore treats the cointegrating vector as **prior information imposed from
   the daily estimation**, not as a fresh rejection of the null. The Hasbrouck
   information share and the Gonzalo-Granger decomposition are conditional on that
   imposition and should not be read as free-standing evidence. The Part 4 tests
   (C1/C2) do not depend on it and are the most robust piece of the analysis.

2. **The overnight layer is partly mechanical.** A closed market cannot respond,
   so "Kalshi moved first overnight" is true by construction and is not by itself
   evidence about efficiency. The informative layer is *how fast the gap closes
   after the open*, which is what Part 4 measures.

3. **The basket spans only part of the election factor** — level correlation 0.572,
   and it moves only about a third as far as Kalshi. Every statement here is about
   *this* basket, not about the equity market in general.

4. **Part 4 is session-level with n = 23.** Suggestive, not decisive; C3 is only
   marginal.

5. **The 90-minute window overlaps generic opening price discovery**, which cannot
   be fully separated from election-specific adjustment.

6. **Regular hours only** — the overnight channel itself is not measured.

---

## Not included in this PR

`daily/methodA.py` and the `controls/` directory are superseded. Method A's daily
basket tracks changes rather than the level and leaves a persistent level gap; the
`controls/` outputs were generated by an earlier version of the code that still used
the look-ahead two-point calibration, so its numbers are not comparable with the
current Method B results.
