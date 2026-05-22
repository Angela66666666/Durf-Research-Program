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

### Step 4: Install Homebrew (Mac only, required for the next step)

Homebrew is a package manager for Mac that installs command-line tools.

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

After installation, add Homebrew to your PATH:
```bash
echo >> /Users/your-username/.zprofile
echo 'eval "$(/opt/homebrew/bin/brew shellenv zsh)"' >> /Users/your-username/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv zsh)"
```

Replace `your-username` with your actual Mac username.

### Step 5: Download the complete dataset

```bash
make setup
```

This will:
1. Automatically install `aria2c` (a fast download tool) if not already installed
2. Download the complete dataset (`data.tar.zst`, ~36GB) from Cloudflare R2 Storage
3. Automatically extract it to `data/`

This takes approximately **2-3 hours** depending on your internet speed. Do not close the terminal or let your computer sleep during the download.

Data will be saved to:
```
data/kalshi/markets/    # contract metadata
data/kalshi/trades/     # trade records
```

Files are in **Parquet format** (read with pandas or duckdb — cannot be opened directly in Excel).

**Note:** `make index` was tested but does not download historical contracts in chronological order, making it unreliable for retrieving 2024 election data. Use `make setup` instead.

---

## Quick Reference

| Command | What it does |
|---|---|
| `cd path/` | Navigate into a folder |
| `ls` | List contents of current folder |
| `pwd` | Show current folder path |
| `uv sync` | Install project dependencies |
| `make setup` | Download complete dataset (~36GB) |
| `uv run script.py` | Run a Python script |
| `Control + C` | Stop the currently running program |
| `rm -rf folder/` | Delete a folder and all its contents |

---

## Key Notes

1. `make setup` requires **~36GB of free disk space** and takes 2-3 hours
2. Do **not** close the terminal or sleep your computer during download
3. Parquet files require **pandas or duckdb** to read — not directly openable in Excel
4. `yes_price` is in **cents (0–100)**, not decimals
5. Kalshi's public API only serves **currently active contracts** — historical data must come from the downloaded dataset
