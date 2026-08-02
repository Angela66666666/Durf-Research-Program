"""
Visualize the lead-lag relationship between:
  - Kalshi contract: "Will the Federal Reserve Hike rates by 0bps at their November 2024 meeting?"
    (ticker: FEDDECISION-24NOV-H0)
  - ETF: VDE (Vanguard Energy)

Two figures:
  1. Full-window overview (2024-09-18 → 2024-11-07): Kalshi probability vs VDE price overlay
  2. Zoomed-in event-day views: focus on days with large Kalshi probability jumps
     showing intraday minute-level dynamics of both series
"""

import duckdb
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

HERE       = Path(__file__).parent                 # leadlag/pair_analyses/01_fed_nov_h0__vde/
LEADLAG    = HERE.parent.parent                    # leadlag/
KALSHI     = LEADLAG / "kalshi_hf_cache.parquet"
ETF_HF     = LEADLAG / "etf_hf" / "VDE_hf.parquet"
PLOT_DIR   = HERE / "plots"
PLOT_DIR.mkdir(exist_ok=True)

TICKER         = "FEDDECISION-24NOV-H0"
CONTRACT_TITLE = ("Will the Federal Reserve Hike rates by 0bps "
                  "at their November 2024 meeting?")
ETF            = "VDE"
ETF_NAME       = "Vanguard Energy ETF"
DATE_START     = "2024-09-18"
DATE_END       = "2024-11-07"

con = duckdb.connect()

# ── Load Kalshi trades ─────────────────────────────────────────────────────────
kalshi = con.execute(f"""
    SELECT (created_time AT TIME ZONE 'UTC')::TIMESTAMP AS ts_utc,
           yes_price
    FROM read_parquet('{KALSHI}')
    WHERE ticker = '{TICKER}'
      AND created_time >= TIMESTAMPTZ '{DATE_START} 00:00:00+00'
      AND created_time <= TIMESTAMPTZ '{DATE_END} 23:59:59+00'
    ORDER BY 1
""").df()
kalshi["ts_utc"] = pd.to_datetime(kalshi["ts_utc"])
kalshi["prob"]   = kalshi["yes_price"] / 100.0
print(f"Loaded {len(kalshi)} Kalshi trades")

# ── Load VDE HF mid prices ─────────────────────────────────────────────────────
etf = con.execute(f"""
    SELECT timestamp_utc AS ts_utc, mid
    FROM read_parquet('{ETF_HF}')
    WHERE timestamp_utc >= TIMESTAMP '{DATE_START} 00:00:00'
      AND timestamp_utc <= TIMESTAMP '{DATE_END} 23:59:59'
    ORDER BY 1
""").df()
etf["ts_utc"] = pd.to_datetime(etf["ts_utc"])
print(f"Loaded {len(etf):,} VDE ticks")

# Resample VDE to 1-minute bars for plot performance
etf_1m = etf.set_index("ts_utc")["mid"].resample("1min").last().dropna().reset_index()
print(f"VDE resampled to {len(etf_1m):,} 1-min bars")

# ────────────────────────────────────────────────────────────────────────────────
# FIGURE 1 — Full window overview
# ────────────────────────────────────────────────────────────────────────────────
fig, ax1 = plt.subplots(figsize=(14, 6))

color_kalshi = "#D32F2F"
color_etf    = "#1565C0"

# Left axis: Kalshi probability
ax1.set_xlabel("Date (UTC)", fontsize=11)
ax1.set_ylabel("Kalshi probability  P(Fed holds rates at Nov 2024 meeting)",
               color=color_kalshi, fontsize=11)
ax1.plot(kalshi["ts_utc"], kalshi["prob"] * 100,
         color=color_kalshi, linewidth=1.0, alpha=0.9,
         label="Kalshi probability")
ax1.tick_params(axis="y", labelcolor=color_kalshi)
ax1.set_ylim(0, 32)
ax1.grid(axis="y", linestyle=":", alpha=0.4)

# Right axis: VDE price
ax2 = ax1.twinx()
ax2.set_ylabel("VDE price (USD)", color=color_etf, fontsize=11)
ax2.plot(etf_1m["ts_utc"], etf_1m["mid"],
         color=color_etf, linewidth=1.0, alpha=0.85,
         label="VDE price")
ax2.tick_params(axis="y", labelcolor=color_etf)

# Annotate FOMC meeting date
fomc_date = pd.Timestamp("2024-11-07 19:00:00")
ax1.axvline(fomc_date, color="black", linestyle="--", linewidth=1, alpha=0.6)
ax1.text(fomc_date, 30, "  FOMC\n  Nov 7", fontsize=9, ha="left", va="top")

# Title and date format
ax1.set_title(
    f'Kalshi contract: "{CONTRACT_TITLE}"\n'
    f'vs {ETF} ({ETF_NAME}) — full window {DATE_START} → {DATE_END} '
    f'(~1.1k Kalshi trades, 1-min VDE bars)',
    fontsize=11
)
ax1.xaxis.set_major_locator(mdates.DayLocator(interval=7))
ax1.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=0)

fig.tight_layout()
out1 = PLOT_DIR / "fed_nov_h0_vde_overview.png"
fig.savefig(out1, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Saved → {out1}")

# ────────────────────────────────────────────────────────────────────────────────
# FIGURE 2 — Event-driven zooms during US MARKET HOURS only
# Both Kalshi and VDE are simultaneously active, so lead-lag is meaningful
# ────────────────────────────────────────────────────────────────────────────────
# Each event: (date, window_start_hr_utc, window_end_hr_utc, news, who_moves_first_hint)
events = [
    {
        "day":   "2024-09-18",
        "t0":    "2024-09-18 17:30",
        "t1":    "2024-09-18 19:30",
        "title": "Sep 18, 2024 — September FOMC decision (Fed cut 50bps at 14:00 ET)",
        "marks": [
            ("2024-09-18 18:00", "FOMC decision\n(14:00 ET)"),
            ("2024-09-18 18:30", "Powell press conf\n(14:30 ET)"),
        ],
        "story": ("Largest Kalshi swing in entire sample: 5 → 28 → 5 within 16 sec at 14:07 ET, "
                  "right after the 50bps cut surprised the market."),
    },
    {
        "day":   "2024-10-10",
        "t0":    "2024-10-10 13:30",
        "t1":    "2024-10-10 19:00",
        "title": "Oct 10, 2024 — September CPI release (hotter than expected, 8:30 ET)",
        "marks": [
            ("2024-10-10 12:30", "CPI release\n(8:30 ET)"),
            ("2024-10-10 13:30", "US equity open\n(9:30 ET)"),
        ],
        "story": ("Hot CPI lowered odds of further aggressive cuts → P(no Nov change) climbed "
                  "20 → 25 in the afternoon as the market digested the print."),
    },
    {
        "day":   "2024-10-17",
        "t0":    "2024-10-17 13:30",
        "t1":    "2024-10-17 18:00",
        "title": "Oct 17, 2024 — Sep Retail Sales & jobless claims release (8:30 ET)",
        "marks": [
            ("2024-10-17 12:30", "Retail sales\n(8:30 ET)"),
            ("2024-10-17 13:30", "US equity open\n(9:30 ET)"),
        ],
        "story": ("Strong retail sales + low jobless claims → Kalshi P(no change) "
                  "jumped 15 → 23 around 11:42 ET as Fed-speak digestion continued."),
    },
]

n = len(events)
fig, axes = plt.subplots(n, 1, figsize=(13, 4.3 * n))

for ax_idx, ev in enumerate(events):
    t0 = pd.Timestamp(ev["t0"])
    t1 = pd.Timestamp(ev["t1"])

    k_win = kalshi[(kalshi["ts_utc"] >= t0) & (kalshi["ts_utc"] <= t1)].copy()
    e_win = etf[(etf["ts_utc"] >= t0) & (etf["ts_utc"] <= t1)].copy()
    # 10-second bars for VDE (smooth but high-res)
    e_win_10s = (e_win.set_index("ts_utc")["mid"]
                       .resample("10s").last().dropna().reset_index())

    ax = axes[ax_idx] if n > 1 else axes
    ax2 = ax.twinx()

    # Kalshi: every trade is a marker, joined by line
    ax.plot(k_win["ts_utc"], k_win["prob"] * 100,
            color=color_kalshi, marker="o", markersize=5, linewidth=1.4,
            alpha=0.95, label="Kalshi probability")
    ax.set_ylabel("Kalshi  P(no Nov rate change)  (%)",
                  color=color_kalshi, fontsize=10)
    ax.tick_params(axis="y", labelcolor=color_kalshi)
    ax.grid(axis="y", linestyle=":", alpha=0.4)

    # VDE
    ax2.plot(e_win_10s["ts_utc"], e_win_10s["mid"],
             color=color_etf, linewidth=1.1, alpha=0.85, label="VDE mid price")
    ax2.set_ylabel("VDE mid price (USD)", color=color_etf, fontsize=10)
    ax2.tick_params(axis="y", labelcolor=color_etf)

    # Annotate event markers
    for mark_t_str, mark_label in ev["marks"]:
        mark_t = pd.Timestamp(mark_t_str)
        if t0 <= mark_t <= t1:
            ax.axvline(mark_t, color="black", linestyle="--", linewidth=1, alpha=0.6)
            ax.text(mark_t, ax.get_ylim()[1] * 0.98, "  " + mark_label,
                    fontsize=8, va="top", ha="left", color="black")

    # Title: event + brief narrative
    ax.set_title(f'{ev["title"]}\n{ev["story"]}',
                 fontsize=10.5, loc="left")

    ax.xaxis.set_major_locator(mdates.MinuteLocator(byminute=[0, 30]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.set_xlim(t0, t1)

axes[-1].set_xlabel("Time (UTC)", fontsize=10)
fig.suptitle(
    f'Intraday lead-lag during US market hours\n'
    f'Contract: "{CONTRACT_TITLE}"  ×  {ETF} ({ETF_NAME})',
    fontsize=12, fontweight="bold", y=1.00
)
fig.tight_layout()
out2 = PLOT_DIR / "fed_nov_h0_vde_event_zooms.png"
fig.savefig(out2, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Saved → {out2}")

# ────────────────────────────────────────────────────────────────────────────────
# FIGURE 3 — TICK-LEVEL zooms (every VDE quote, every Kalshi trade, no resampling)
# ────────────────────────────────────────────────────────────────────────────────
tick_events = [
    {
        "title":  "Sep 18 FOMC — the 16-second Kalshi spike (5 → 28 → 5)",
        "t0":     "2024-09-18 18:00:00",
        "t1":     "2024-09-18 18:15:00",
        "marks":  [("2024-09-18 18:00:00", "FOMC decision (14:00 ET)")],
        "narr":   ("Two Kalshi trades at 18:07:23 (28¢) and 18:07:39 (5¢) — 16 sec apart. "
                   "Compare VDE tick-by-tick in that interval."),
    },
    {
        "title":  "Oct 10 CPI day — Kalshi jump 20 → 25 at 12:55 ET",
        "t0":     "2024-10-10 16:30:00",
        "t1":     "2024-10-10 17:30:00",
        "marks":  [],
        "narr":   ("Does VDE start moving up *before* the Kalshi jump at 16:55 UTC?"),
    },
    {
        "title":  "Oct 17 — Kalshi jump 15 → 23 at 11:42 ET",
        "t0":     "2024-10-17 15:15:00",
        "t1":     "2024-10-17 16:30:00",
        "marks":  [],
        "narr":   ("Does VDE start declining *before* the Kalshi jump at 15:42 UTC?"),
    },
]

n_tick = len(tick_events)
fig, axes = plt.subplots(n_tick, 1, figsize=(13, 4.5 * n_tick))

for ax_idx, ev in enumerate(tick_events):
    t0 = pd.Timestamp(ev["t0"])
    t1 = pd.Timestamp(ev["t1"])

    k_win = kalshi[(kalshi["ts_utc"] >= t0) & (kalshi["ts_utc"] <= t1)].copy()
    # Raw VDE ticks — NO resampling
    e_win = etf[(etf["ts_utc"] >= t0) & (etf["ts_utc"] <= t1)].copy()

    ax  = axes[ax_idx] if n_tick > 1 else axes
    ax2 = ax.twinx()

    # Kalshi: every trade with its price annotated
    ax.plot(k_win["ts_utc"], k_win["prob"] * 100,
            color=color_kalshi, marker="o", markersize=8, linewidth=1.3,
            alpha=0.95, label="Kalshi trade")
    # Annotate each Kalshi trade with its yes_price
    for _, row in k_win.iterrows():
        ax.annotate(f"{int(row['yes_price'])}¢",
                    xy=(row["ts_utc"], row["prob"] * 100),
                    xytext=(4, 6), textcoords="offset points",
                    fontsize=7, color=color_kalshi, alpha=0.9)
    ax.set_ylabel("Kalshi  P(no Nov change)  (%)",
                  color=color_kalshi, fontsize=10)
    ax.tick_params(axis="y", labelcolor=color_kalshi)
    ax.grid(axis="y", linestyle=":", alpha=0.4)

    # VDE: every single tick, no resampling
    ax2.plot(e_win["ts_utc"], e_win["mid"],
             color=color_etf, linewidth=0.7, alpha=0.85,
             label=f"VDE every tick ({len(e_win):,})")
    ax2.set_ylabel("VDE mid price (USD)", color=color_etf, fontsize=10)
    ax2.tick_params(axis="y", labelcolor=color_etf)

    # Event markers (FOMC decision, etc.)
    for mark_t_str, mark_label in ev["marks"]:
        mark_t = pd.Timestamp(mark_t_str)
        if t0 <= mark_t <= t1:
            ax.axvline(mark_t, color="black", linestyle="--", linewidth=1, alpha=0.6)
            ax.text(mark_t, ax.get_ylim()[1] * 0.97, "  " + mark_label,
                    fontsize=8, va="top", ha="left", color="black")

    ax.set_title(f"{ev['title']}\n{ev['narr']}\n"
                 f"({len(k_win)} Kalshi trades, {len(e_win):,} VDE ticks)",
                 fontsize=10.5, loc="left")
    ax.xaxis.set_major_locator(mdates.MinuteLocator(byminute=range(0, 60, 5)))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    ax.set_xlim(t0, t1)
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=0, fontsize=8)

axes[-1].set_xlabel("Time (UTC)", fontsize=10)
fig.suptitle(
    f'TICK-LEVEL zoom (no resampling)\n'
    f'Contract: "{CONTRACT_TITLE}"  ×  {ETF} ({ETF_NAME})',
    fontsize=12, fontweight="bold", y=1.00
)
fig.tight_layout()
out3 = PLOT_DIR / "fed_nov_h0_vde_tick_zooms.png"
fig.savefig(out3, dpi=160, bbox_inches="tight")
plt.close(fig)
print(f"Saved → {out3}")

print("\nDone.")
