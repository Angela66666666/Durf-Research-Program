# 01 - Kalshi Data Download Guide

## Research Context

This project investigates the **lead-lag relationship** between Kalshi prediction market contracts and sector ETFs, using the 2024 U.S. Presidential Election as the key event.

### Data We Need
- **Kalshi data**: Daily price changes for election-related contracts, September 1 – November 5, 2024
- **ETF data**: Daily returns for Vanguard Sector ETFs over the same period

---

## Environment Setup

### Requirements
- Mac or Windows
- Python 3.9+
- Internet connection

### Step 1: Install uv (Python package manager)

**Mac:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

**Verify installation:**
```bash
uv --version
# Should show something like: uv 0.11.15
```

---

## Download the Project

### Step 2: Clone the GitHub repository

```bash
git clone https://github.com/Jon-Becker/prediction-market-analysis
cd prediction-market-analysis
```

### Step 3: Install dependencies

```bash
uv sync
```

This reads `pyproject.toml` and installs all required libraries (pandas, duckdb, etc.) into an isolated virtual environment at `.venv/`.

You should see:
```
Installed 84 packages in 151ms
```

---

## Download Kalshi Data

### Step 4: Run the data collection tool

```bash
make index
```

This opens an interactive menu:
```
> Kalshi Markets: Backfills Kalshi markets data to parquet files
  Kalshi Trades: Backfills Kalshi trades data to parquet files
  ...
```

### Step 5: Download Markets data (contract metadata)

Use the **arrow keys** to select `Kalshi Markets`, then press **Enter**.

**Markets vs Trades — what's the difference?**

| | Kalshi Markets | Kalshi Trades |
|---|---|---|
| Each row is | One contract's basic info | One individual trade |
| Contains | ticker, title, close time, result | timestamp, price, volume |
| File size | Small (a few hundred MB) | Large |
| Purpose | Find the correct ticker for the election contract | Calculate daily price changes Δp |

**Important:** The indexer downloads from newest to oldest. The 2024 election contracts appear after approximately 350,000 records have been downloaded. When the counter reaches ~350,000, press `Control + C` to pause and check whether 2024 data has appeared.

Data is saved to:
```
data/kalshi/markets/
```

Files are in **Parquet format** (read with pandas or duckdb — cannot be opened directly in Excel).

---

## Quick Reference

| Command | What it does |
|---|---|
| `cd path/` | Navigate into a folder |
| `ls` | List contents of current folder |
| `pwd` | Show current folder path |
| `uv sync` | Install project dependencies |
| `make index` | Launch data collection menu |
| `uv run script.py` | Run a Python script |
| `Control + C` | Stop the currently running program |
| `rm -rf folder/` | Delete a folder and all its contents |

---

## Key Notes

1. The indexer downloads **from newest to oldest** — 2024 data takes time to appear
2. Pressing `Control + C` **does not corrupt data** — progress is saved automatically
3. Parquet files require **pandas or duckdb** to read — not directly openable in Excel
4. `yes_price` is in **cents (0–100)**, not decimals
5. Kalshi's public API only serves **currently active contracts** — historical data must come from local Parquet files
