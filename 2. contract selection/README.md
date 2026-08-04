# 2. Contract Selection

## Goal of this folder

Starting from the full Kalshi historical dataset (in `1. data/kalshi/`), find the
subset of prediction-market contracts that are usable for this study — i.e.
contracts whose outcome is plausibly linked to a Vanguard sector ETF and that
have enough trading activity to carry a price signal.

The output of this folder is a single list — **`selected_contracts.csv`, the 295
contracts the study runs on**. Turning that list into a daily price panel and
screening it happens in the next folder (`3. daily screen`).

The pipeline is two steps:

1. **Screen** the raw market metadata by keyword, date, and volume → 358 candidates.
2. **Curate** those 358 by hand down to the 295 contracts actually used.

Both scripts locate the project root automatically by walking up until they find
`1. data/`, so they run from any working directory.

---

## Step 1 — Keyword screen (358 candidates)

**Script:** `find_election_contracts.py`
**Reads:** `1. data/kalshi/kalshi/markets/*.parquet` (contract metadata)
**Writes:** `election_contracts.csv` (in this folder)

A contract is kept only if it (a) matches at least one sector-relevant keyword,
(b) closes between 2024-09-01 and 2024-12-31, and (c) has volume > 1,000. The
core of the screen is a single DuckDB query:

```python
conditions = " OR ".join(f"title ILIKE '%{kw}%'" for kw in all_keywords)
df = con.execute(f"""
    SELECT ticker, title, status, close_time, volume
    FROM '{markets_dir}/*.parquet'
    WHERE ({conditions})
      AND close_time >= '2024-09-01' AND close_time <= '2024-12-31'
      AND volume > 1000
    ORDER BY volume DESC NULLS LAST
""").df()
```

Keywords are grouped by the sector they speak to (the full list lives in the
`SECTOR_KEYWORDS` dict in the script):

| Target ETF(s)                       | Example keywords                                        |
|-------------------------------------|---------------------------------------------------------|
| VFH / VNQ / VPU (rate-sensitive)    | federal reserve, rate cut, rate hike, fed, bps          |
| VDE (energy)                        | oil, gas, energy, drill, pipeline, opec, lng            |
| VHT (health care)                   | health, pharma, drug, medicare, medicaid, aca, fda      |
| VIS / VAW (industrials / materials) | tariff, trade, infrastructure, defense, steel, china    |
| VGT (information technology)        | antitrust, tech regulation, ai regulation, tiktok       |
| All sectors (election outcome)      | president, trump, harris, election, electoral           |

Each surviving contract is tagged with the sector group(s) it matched
(`sector_relevance` column). **Output: `election_contracts.csv` — 358 contracts.**

---

## Step 2 — Manual curation (358 → 295)

The keyword screen in Step 1 is deliberately loose, so it also catches
**keyword false positives**: contracts that contain a screen word ("trump",
"president", "election", "fed", "china", ...) but whose *outcome* has no credible
link to a U.S. sector ETF. These were removed by hand, leaving the **295
contracts** in `selected_contracts.csv` (same columns as the screen output). This
file is the contract universe the rest of the study runs on.

There is no script for this step — it is a human judgment call — so the rule
below is not a hard filter in code; it is the criterion the curation applied,
and the 63 removed contracts all fit it. Concretely, the removed contracts are:

| Type of removed contract | Count | Examples |
|---|---|---|
| Personnel / cabinet-appointment markets | 30 | "Will Trump's Press Secretary be …", Secretary of Defense, UN / Mexico ambassador |
| Non-U.S. or non-market questions | 14 | Ghana / Ireland / Canada / Mexico elections, "Will more university presidents leave?" |
| Process / trivia markets | 7 | "Number of Trump–Biden debates?", "…go on the Joe Rogan Experience" |
| Other edge cases | 12 | near-zero-probability Fed **hike** contracts (the 2024 cycle was cutting, not hiking), demographic sub-splits ("win white women"), a Biden-pardon market |

Two things are worth stating because they show the cut was about **relevance, not
liquidity**:

- The removed contracts were, if anything, **higher-volume** than the ones kept
  (median volume ~18k vs ~5k). The single largest removed market was a
  649k-volume "number of debates" trivia contract. So this is not a volume
  filter — the `volume > 1000` liquidity screen already happened in Step 1.
- Every removed contract is `status = finalized` and carries a sector tag, i.e.
  it passed every *mechanical* Step-1 test; what it lacked was a plausible
  economic channel from its resolution to a sector ETF.

In short: **Step 1 keeps anything a keyword touches; Step 2 keeps only the
contracts whose resolution could actually move a U.S. sector ETF** (the 2024
election outcome and its policy-relevant sub-markets, Federal Reserve rate
decisions, and energy / health / financials / tech policy contracts).

---

## Next step (in `3. daily screen`)

This folder stops at the **295-contract list**. The next folder reads
`selected_contracts.csv`, aggregates the trade-level data into a daily price
panel (`extract_contract_trades.py` → `contract_daily_prices.csv`), and screens
each contract against the sector ETFs. See `3. daily screen/README.md`.

---

## File reference

| File | Role | Reads | Writes |
|---|---|---|---|
| `find_election_contracts.py` | Step 1 — keyword screen | `1. data/kalshi/kalshi/markets/*.parquet` | `election_contracts.csv` |
| `election_contracts.csv` | 358 screened candidates | — | — |
| `selected_contracts.csv` | 295 hand-curated contracts (the study universe, handed to `3. daily screen`) | — | — |

---

## Raw data (Step 0, done once)

The ~36 GB Kalshi dataset was downloaded once from Cloudflare R2 into
`1. data/kalshi/kalshi/` (`markets/` = contract metadata, `trades/` = every
trade), in Parquet format. Reproduction, for reference only:

```bash
git clone https://github.com/Jon-Becker/prediction-market-analysis
cd prediction-market-analysis
uv sync
make setup      # downloads data.tar.zst (~36 GB) and extracts to data/
```

Notes: `make index` does not return contracts in chronological order and was not
used. Kalshi's public API only serves currently-active contracts, so all
historical data comes from this one-time bulk download.
