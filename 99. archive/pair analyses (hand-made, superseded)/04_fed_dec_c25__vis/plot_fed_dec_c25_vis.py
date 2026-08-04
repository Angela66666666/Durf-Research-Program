"""
Visualize the lead-lag relationship between:
  - Kalshi contract: "Will the Federal Reserve Cut rates by 25bps at their December 2024 meeting?"
    (ticker: KXFEDDECISION-24DEC-C25)
  - ETF: VIS (Vanguard Industrials)

This is the LARGEST sample pair in the dataset:
  5,374 Kalshi trades over 50 days, 1,887 obs after lag construction

Cross-validation classification: B_both_etf_leads
  - Profile: ETF leads at horizon 270s (4.5 min), p=0.006
  - Event_unified: 1 etf_leads sig coef, 0 kalshi_leads sig coef

We test whether the strongest "ETF-leads" candidate visually confirms.

Three figures (same as Pair #01 - no election-night special):
  1. Full-window overview (2024-10-30 → 2024-12-19)
  2. Three event-day zooms during US market hours
  3. Tick-level zooms at second resolution
"""

import duckdb
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

HERE       = Path(__file__).parent
LEADLAG    = HERE.parent.parent
KALSHI     = LEADLAG / "kalshi_hf_cache.parquet"
ETF_HF     = LEADLAG / "etf_hf" / "VIS_hf.parquet"
PLOT_DIR   = HERE / "plots"
PLOT_DIR.mkdir(exist_ok=True)

TICKER         = "KXFEDDECISION-24DEC-C25"
CONTRACT_TITLE = ("Will the Federal Reserve Cut rates by 25bps "
                  "at their December 2024 meeting?")
ETF            = "VIS"
ETF_NAME       = "Vanguard Industrials ETF"
DATE_START     = "2024-10-30"
DATE_END       = "2024-12-19"

con = duckdb.connect()

kalshi = con.execute(f"""
    SELECT (created_time AT TIME ZONE 'UTC')::TIMESTAMP AS ts_utc, yes_price
    FROM read_parquet('{KALSHI}')
    WHERE ticker = '{TICKER}'
      AND created_time >= TIMESTAMPTZ '{DATE_START} 00:00:00+00'
      AND created_time <= TIMESTAMPTZ '{DATE_END} 23:59:59+00'
    ORDER BY 1
""").df()
kalshi["ts_utc"] = pd.to_datetime(kalshi["ts_utc"])
kalshi["prob"]   = kalshi["yes_price"] / 100.0
print(f"Loaded {len(kalshi)} Kalshi trades")

etf = con.execute(f"""
    SELECT timestamp_utc AS ts_utc, mid
    FROM read_parquet('{ETF_HF}')
    WHERE timestamp_utc >= TIMESTAMP '{DATE_START} 00:00:00'
      AND timestamp_utc <= TIMESTAMP '{DATE_END} 23:59:59'
    ORDER BY 1
""").df()
etf["ts_utc"] = pd.to_datetime(etf["ts_utc"])
print(f"Loaded {len(etf):,} VIS ticks")

etf_1m = etf.set_index("ts_utc")["mid"].resample("1min").last().dropna().reset_index()

color_kalshi = "#D32F2F"
color_etf    = "#1565C0"

# ────────────────────────────────────────────────────────────────────────────────
# FIGURE 1 — Full-window overview
# ────────────────────────────────────────────────────────────────────────────────
fig, ax1 = plt.subplots(figsize=(14, 6))

ax1.set_xlabel("Date (UTC)", fontsize=11)
ax1.set_ylabel("Kalshi probability  P(Fed cuts 25bps in Dec 2024) (%)",
               color=color_kalshi, fontsize=11)
ax1.plot(kalshi["ts_utc"], kalshi["prob"] * 100,
         color=color_kalshi, linewidth=0.6, alpha=0.85)
ax1.tick_params(axis="y", labelcolor=color_kalshi)
ax1.set_ylim(0, 105)
ax1.grid(axis="y", linestyle=":", alpha=0.4)

ax2 = ax1.twinx()
ax2.set_ylabel("VIS mid price (USD)", color=color_etf, fontsize=11)
ax2.plot(etf_1m["ts_utc"], etf_1m["mid"],
         color=color_etf, linewidth=0.9, alpha=0.85)
ax2.tick_params(axis="y", labelcolor=color_etf)

# Annotate key dates
for date_str, label in [
    ("2024-11-05", "Election Day"),
    ("2024-11-07 19:00", "Nov FOMC\n(cut 25bp)"),
    ("2024-11-13 13:30", "Oct CPI"),
    ("2024-12-06 13:30", "Nov Jobs"),
    ("2024-12-11 13:30", "Nov CPI"),
    ("2024-12-18 19:00", "Dec FOMC\n(cut 25bp)"),
]:
    t = pd.Timestamp(date_str)
    ax1.axvline(t, color="black", linestyle="--", linewidth=0.7, alpha=0.5)
    ax1.text(t, 102, "  " + label, fontsize=8, va="top", ha="left")

ax1.set_title(
    f'Kalshi contract: "{CONTRACT_TITLE}"\n'
    f'vs {ETF} ({ETF_NAME}) — full window {DATE_START} → {DATE_END} '
    f'(LARGEST sample: {len(kalshi):,} Kalshi trades)',
    fontsize=11
)
ax1.xaxis.set_major_locator(mdates.DayLocator(interval=5))
ax1.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))

fig.tight_layout()
out1 = PLOT_DIR / "fed_dec_c25_vis_overview.png"
fig.savefig(out1, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Saved → {out1}")

# ────────────────────────────────────────────────────────────────────────────────
# FIGURE 2 — Three intraday event zooms during US market hours
# ────────────────────────────────────────────────────────────────────────────────
events = [
    {
        "title": "Nov 7, 2024 — November FOMC decision day (Fed cut 25bp at 14:00 ET)",
        "t0":    "2024-11-07 16:00",
        "t1":    "2024-11-07 20:30",
        "marks": [
            ("2024-11-07 19:00", "FOMC decision\n(14:00 ET)"),
            ("2024-11-07 19:30", "Powell press conf\n(14:30 ET)"),
        ],
        "story": ("Multiple ±20-35pp Kalshi jumps as the market digests the November cut and "
                  "Powell's outlook for December."),
    },
    {
        "title": "Nov 13, 2024 — October CPI release (8:30 ET)",
        "t0":    "2024-11-13 13:00",
        "t1":    "2024-11-13 17:00",
        "marks": [
            ("2024-11-13 13:30", "CPI release\n(8:30 ET)"),
            ("2024-11-13 14:30", "US equity open\n(9:30 ET)"),
        ],
        "story": ("Sharp 56 → 15 → 62 Kalshi swing in 5 minutes around 14:00-14:05 UTC. "
                  "Likely anomalous/thin-book episode — examine if VIS responds."),
    },
    {
        "title": "Dec 11, 2024 — November CPI release + Dec FOMC anticipation",
        "t0":    "2024-12-11 13:00",
        "t1":    "2024-12-11 21:00",
        "marks": [
            ("2024-12-11 13:30", "CPI release\n(8:30 ET)"),
            ("2024-12-11 14:30", "US equity open\n(9:30 ET)"),
        ],
        "story": ("November CPI lands in line with expectations. Kalshi swings 50-96 — large "
                  "intraday volatility a week before Dec FOMC."),
    },
]

n = len(events)
fig, axes = plt.subplots(n, 1, figsize=(13, 4.3 * n))

for ax_idx, ev in enumerate(events):
    t0 = pd.Timestamp(ev["t0"])
    t1 = pd.Timestamp(ev["t1"])

    k_win = kalshi[(kalshi["ts_utc"] >= t0) & (kalshi["ts_utc"] <= t1)].copy()
    e_win = etf[(etf["ts_utc"] >= t0) & (etf["ts_utc"] <= t1)].copy()
    e_win_10s = (e_win.set_index("ts_utc")["mid"]
                       .resample("10s").last().dropna().reset_index())

    ax = axes[ax_idx] if n > 1 else axes
    ax2 = ax.twinx()

    ax.plot(k_win["ts_utc"], k_win["prob"] * 100,
            color=color_kalshi, marker="o", markersize=3, linewidth=0.9,
            alpha=0.85)
    ax.set_ylabel("Kalshi  P(Dec cut) (%)", color=color_kalshi, fontsize=10)
    ax.tick_params(axis="y", labelcolor=color_kalshi)
    ax.grid(axis="y", linestyle=":", alpha=0.4)

    ax2.plot(e_win_10s["ts_utc"], e_win_10s["mid"],
             color=color_etf, linewidth=1.0, alpha=0.85)
    ax2.set_ylabel("VIS mid price (USD)", color=color_etf, fontsize=10)
    ax2.tick_params(axis="y", labelcolor=color_etf)

    for mark_t_str, mark_label in ev["marks"]:
        mark_t = pd.Timestamp(mark_t_str)
        if t0 <= mark_t <= t1:
            ax.axvline(mark_t, color="black", linestyle="--", linewidth=1, alpha=0.6)
            ax.text(mark_t, ax.get_ylim()[1] * 0.97, "  " + mark_label,
                    fontsize=8, va="top", ha="left", color="black")

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
out2 = PLOT_DIR / "fed_dec_c25_vis_event_zooms.png"
fig.savefig(out2, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Saved → {out2}")

# ────────────────────────────────────────────────────────────────────────────────
# FIGURE 3 — TICK-LEVEL zooms
# ────────────────────────────────────────────────────────────────────────────────
tick_events = [
    {
        "title":  "Nov 13 13:55-14:15 UTC — The 56→15→62 wild swing (Oct CPI digestion)",
        "t0":     "2024-11-13 13:55:00",
        "t1":     "2024-11-13 14:15:00",
        "marks":  [
            ("2024-11-13 13:30", "CPI release (8:30 ET)"),
            ("2024-11-13 14:30", "US equity open (9:30 ET)"),
        ],
        "narr":   ("20 min ultra-zoom. Watch VIS tick-by-tick during the Kalshi 56→15 crash."),
    },
    {
        "title":  "Nov 7 18:55-19:30 UTC — Around the FOMC announcement (19:00 UTC = 14:00 ET)",
        "t0":     "2024-11-07 18:55:00",
        "t1":     "2024-11-07 19:30:00",
        "marks":  [
            ("2024-11-07 19:00", "FOMC decision"),
            ("2024-11-07 19:30", "Powell press conf"),
        ],
        "narr":   ("Critical 35-min window: Fed cuts 25bp at 19:00. Kalshi jumps +24pp at 19:02. Does VIS lead or follow?"),
    },
    {
        "title":  "Nov 8 15:45-16:00 UTC — Post-election positioning Kalshi double swing",
        "t0":     "2024-11-08 15:45:00",
        "t1":     "2024-11-08 16:00:00",
        "marks":  [],
        "narr":   ("Both -22 and +20 jumps at 15:50:45 same second. Anomalous burst pattern."),
    },
]

n_tick = len(tick_events)
fig, axes = plt.subplots(n_tick, 1, figsize=(13, 4.5 * n_tick))

for ax_idx, ev in enumerate(tick_events):
    t0 = pd.Timestamp(ev["t0"])
    t1 = pd.Timestamp(ev["t1"])

    k_win = kalshi[(kalshi["ts_utc"] >= t0) & (kalshi["ts_utc"] <= t1)].copy()
    e_win = etf[(etf["ts_utc"] >= t0) & (etf["ts_utc"] <= t1)].copy()

    ax = axes[ax_idx] if n_tick > 1 else axes
    ax2 = ax.twinx()

    ax.plot(k_win["ts_utc"], k_win["prob"] * 100,
            color=color_kalshi, marker="o", markersize=5, linewidth=1.0,
            alpha=0.95)
    # Annotate every Kalshi price (sparingly for dense zones)
    for _, row in k_win.iterrows():
        ax.annotate(f"{int(row['yes_price'])}¢",
                    xy=(row["ts_utc"], row["prob"] * 100),
                    xytext=(4, 6), textcoords="offset points",
                    fontsize=6.5, color=color_kalshi, alpha=0.85)
    ax.set_ylabel("Kalshi  P(Dec cut) (%)", color=color_kalshi, fontsize=10)
    ax.tick_params(axis="y", labelcolor=color_kalshi)
    ax.grid(axis="y", linestyle=":", alpha=0.4)

    ax2.plot(e_win["ts_utc"], e_win["mid"],
             color=color_etf, linewidth=0.7, alpha=0.85)
    ax2.set_ylabel("VIS mid price (USD)", color=color_etf, fontsize=10)
    ax2.tick_params(axis="y", labelcolor=color_etf)

    for mark_t_str, mark_label in ev["marks"]:
        mark_t = pd.Timestamp(mark_t_str)
        if t0 <= mark_t <= t1:
            ax.axvline(mark_t, color="black", linestyle="--", linewidth=1, alpha=0.6)
            ax.text(mark_t, ax.get_ylim()[1] * 0.97, "  " + mark_label,
                    fontsize=8, va="top", ha="left", color="black")

    ax.set_title(f"{ev['title']}\n{ev['narr']}\n"
                 f"({len(k_win)} Kalshi trades, {len(e_win):,} VIS ticks)",
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
out3 = PLOT_DIR / "fed_dec_c25_vis_tick_zooms.png"
fig.savefig(out3, dpi=160, bbox_inches="tight")
plt.close(fig)
print(f"Saved → {out3}")

print("\nDone.")
