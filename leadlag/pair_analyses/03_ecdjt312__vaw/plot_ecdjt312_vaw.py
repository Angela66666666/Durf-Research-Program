"""
Visualize the lead-lag relationship between:
  - Kalshi contract: "Will Trump win 312-226 - swing state sweep?"
    (ticker: KXECDJT312)
  - ETF: VAW (Vanguard Materials)

This contract resolved YES (Trump won 312-226). Probability went from
~13% pre-election to 99% by Nov 8 and stayed there.

Regression says this pair is the strongest "Kalshi leads ETF" candidate
in the dataset (8 kalshi_leads vs 4 etf_leads significant coefficients).
We test that visually.

Four figures:
  1. Full-window overview (2024-11-01 → 2024-11-15)
  2. Three intraday event zooms during US market hours
  3. Tick-level zooms at second resolution
  4. Election-night special.
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
ETF_HF     = LEADLAG / "etf_hf" / "VAW_hf.parquet"
PLOT_DIR   = HERE / "plots"
PLOT_DIR.mkdir(exist_ok=True)

TICKER         = "KXECDJT312"
CONTRACT_TITLE = "Will Trump win 312-226 - swing state sweep?"
ETF            = "VAW"
ETF_NAME       = "Vanguard Materials ETF"
DATE_START     = "2024-11-01"
DATE_END       = "2024-11-15"

con = duckdb.connect()

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

etf = con.execute(f"""
    SELECT timestamp_utc AS ts_utc, mid
    FROM read_parquet('{ETF_HF}')
    WHERE timestamp_utc >= TIMESTAMP '{DATE_START} 00:00:00'
      AND timestamp_utc <= TIMESTAMP '{DATE_END} 23:59:59'
    ORDER BY 1
""").df()
etf["ts_utc"] = pd.to_datetime(etf["ts_utc"])
print(f"Loaded {len(etf):,} VAW ticks")

etf_1m = etf.set_index("ts_utc")["mid"].resample("1min").last().dropna().reset_index()

color_kalshi = "#D32F2F"
color_etf    = "#1565C0"

# ────────────────────────────────────────────────────────────────────────────────
# FIGURE 1 — Full-window overview
# ────────────────────────────────────────────────────────────────────────────────
fig, ax1 = plt.subplots(figsize=(14, 6))

ax1.set_xlabel("Date (UTC)", fontsize=11)
ax1.set_ylabel("Kalshi probability  P(Trump 312-226 sweep) (%)",
               color=color_kalshi, fontsize=11)
ax1.plot(kalshi["ts_utc"], kalshi["prob"] * 100,
         color=color_kalshi, linewidth=0.9, alpha=0.9)
ax1.tick_params(axis="y", labelcolor=color_kalshi)
ax1.set_ylim(0, 105)
ax1.grid(axis="y", linestyle=":", alpha=0.4)

ax2 = ax1.twinx()
ax2.set_ylabel("VAW mid price (USD)", color=color_etf, fontsize=11)
ax2.plot(etf_1m["ts_utc"], etf_1m["mid"],
         color=color_etf, linewidth=1.0, alpha=0.85)
ax2.tick_params(axis="y", labelcolor=color_etf)

election_day = pd.Timestamp("2024-11-05 23:00:00")
ax1.axvline(election_day, color="black", linestyle="--", linewidth=1, alpha=0.6)
ax1.text(election_day, 100, "  Election Day\n  (polls close 23:00 UTC)",
         fontsize=9, va="top", ha="left")

ax1.set_title(
    f'Kalshi contract: "{CONTRACT_TITLE}"\n'
    f'vs {ETF} ({ETF_NAME}) — full window {DATE_START} → {DATE_END}',
    fontsize=11
)
ax1.xaxis.set_major_locator(mdates.DayLocator(interval=1))
ax1.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))

fig.tight_layout()
out1 = PLOT_DIR / "ecdjt312_vaw_overview.png"
fig.savefig(out1, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Saved → {out1}")

# ────────────────────────────────────────────────────────────────────────────────
# FIGURE 2 — Three intraday event zooms during US market hours
# ────────────────────────────────────────────────────────────────────────────────
events = [
    {
        "title": "Nov 1, 2024 — Friday pre-election: mysterious mid-afternoon swing (98 → 30 → 55 → 98)",
        "t0":    "2024-11-01 16:00",
        "t1":    "2024-11-01 19:30",
        "marks": [
            ("2024-11-01 14:30", "US equity open"),
        ],
        "story": ("KXECDJT312 swings violently — likely contract launch / illiquid early "
                  "trading on low-volume Friday. Examine whether VAW reacts."),
    },
    {
        "title": "Nov 6, 2024 — Post-election morning: Kalshi finalizes the 312-226 path (14:30–16:00 UTC)",
        "t0":    "2024-11-06 14:30",
        "t1":    "2024-11-06 16:00",
        "marks": [
            ("2024-11-06 14:30", "US equity open — VAW gap"),
        ],
        "story": ("VAW opens with a gap absorbing overnight result. Kalshi oscillates 52→93→55→99 "
                  "as final swing states (e.g. WI, NV) are called. Both markets simultaneously active "
                  "during a regime of extreme prediction-market uncertainty."),
    },
    {
        "title": "Nov 6, 2024 — Afternoon swings: large back-and-forth (96↔67) at 17:30–18:45 UTC",
        "t0":    "2024-11-06 17:00",
        "t1":    "2024-11-06 19:00",
        "marks": [],
        "story": ("Late-day re-oscillations as the specific 312-226 path gets re-evaluated. "
                  "Big Kalshi jumps ±20-30 pp. VAW continues a steady directional move."),
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

    ax  = axes[ax_idx] if n > 1 else axes
    ax2 = ax.twinx()

    ax.plot(k_win["ts_utc"], k_win["prob"] * 100,
            color=color_kalshi, marker="o", markersize=4, linewidth=1.2,
            alpha=0.9)
    ax.set_ylabel("Kalshi  P(312-226) (%)", color=color_kalshi, fontsize=10)
    ax.tick_params(axis="y", labelcolor=color_kalshi)
    ax.grid(axis="y", linestyle=":", alpha=0.4)

    ax2.plot(e_win_10s["ts_utc"], e_win_10s["mid"],
             color=color_etf, linewidth=1.0, alpha=0.85)
    ax2.set_ylabel("VAW mid price (USD)", color=color_etf, fontsize=10)
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
out2 = PLOT_DIR / "ecdjt312_vaw_event_zooms.png"
fig.savefig(out2, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Saved → {out2}")

# ────────────────────────────────────────────────────────────────────────────────
# FIGURE 3 — TICK-LEVEL zooms
# ────────────────────────────────────────────────────────────────────────────────
tick_events = [
    {
        "title":  "Nov 6 14:15-14:55 UTC — Morning extreme oscillation: 52 → 93 → 55 → 99 in 40 min",
        "t0":     "2024-11-06 14:15:00",
        "t1":     "2024-11-06 14:55:00",
        "marks":  [
            ("2024-11-06 14:30", "VAW equity open"),
        ],
        "narr":   ("Kalshi swings violently as remaining swing states are called. "
                   "Did VAW track or stay independent?"),
    },
    {
        "title":  "Nov 6 18:20-18:45 UTC — Afternoon 96 → 67 → 96 swing",
        "t0":     "2024-11-06 18:20:00",
        "t1":     "2024-11-06 18:45:00",
        "marks":  [],
        "narr":   ("Kalshi oscillates ~30 pp. Tick-by-tick VAW response."),
    },
    {
        "title":  "Nov 6 17:30-17:40 UTC — Rapid ±23 pp oscillation",
        "t0":     "2024-11-06 17:30:00",
        "t1":     "2024-11-06 17:40:00",
        "marks":  [],
        "narr":   ("10-min ultra-tight zoom on a sharp Kalshi flip."),
    },
]

n_tick = len(tick_events)
fig, axes = plt.subplots(n_tick, 1, figsize=(13, 4.5 * n_tick))

for ax_idx, ev in enumerate(tick_events):
    t0 = pd.Timestamp(ev["t0"])
    t1 = pd.Timestamp(ev["t1"])

    k_win = kalshi[(kalshi["ts_utc"] >= t0) & (kalshi["ts_utc"] <= t1)].copy()
    e_win = etf[(etf["ts_utc"] >= t0) & (etf["ts_utc"] <= t1)].copy()

    ax  = axes[ax_idx] if n_tick > 1 else axes
    ax2 = ax.twinx()

    ax.plot(k_win["ts_utc"], k_win["prob"] * 100,
            color=color_kalshi, marker="o", markersize=6, linewidth=1.2,
            alpha=0.95)
    for _, row in k_win.iterrows():
        ax.annotate(f"{int(row['yes_price'])}¢",
                    xy=(row["ts_utc"], row["prob"] * 100),
                    xytext=(4, 6), textcoords="offset points",
                    fontsize=6.5, color=color_kalshi, alpha=0.9)
    ax.set_ylabel("Kalshi  P(312-226) (%)", color=color_kalshi, fontsize=10)
    ax.tick_params(axis="y", labelcolor=color_kalshi)
    ax.grid(axis="y", linestyle=":", alpha=0.4)

    ax2.plot(e_win["ts_utc"], e_win["mid"],
             color=color_etf, linewidth=0.7, alpha=0.85)
    ax2.set_ylabel("VAW mid price (USD)", color=color_etf, fontsize=10)
    ax2.tick_params(axis="y", labelcolor=color_etf)

    for mark_t_str, mark_label in ev["marks"]:
        mark_t = pd.Timestamp(mark_t_str)
        if t0 <= mark_t <= t1:
            ax.axvline(mark_t, color="black", linestyle="--", linewidth=1, alpha=0.6)
            ax.text(mark_t, ax.get_ylim()[1] * 0.97, "  " + mark_label,
                    fontsize=8, va="top", ha="left", color="black")

    ax.set_title(f"{ev['title']}\n{ev['narr']}\n"
                 f"({len(k_win)} Kalshi trades, {len(e_win):,} VAW ticks)",
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
out3 = PLOT_DIR / "ecdjt312_vaw_tick_zooms.png"
fig.savefig(out3, dpi=160, bbox_inches="tight")
plt.close(fig)
print(f"Saved → {out3}")

# ────────────────────────────────────────────────────────────────────────────────
# FIGURE 4 — Election-night special
# ────────────────────────────────────────────────────────────────────────────────
t0 = pd.Timestamp("2024-11-05 19:00:00")
t1 = pd.Timestamp("2024-11-06 21:00:00")
k_night = kalshi[(kalshi["ts_utc"] >= t0) & (kalshi["ts_utc"] <= t1)].copy()
e_night = etf[(etf["ts_utc"] >= t0) & (etf["ts_utc"] <= t1)].copy()
e_night_1m = (e_night.set_index("ts_utc")["mid"]
                       .resample("1min").last().dropna().reset_index())

fig, ax = plt.subplots(figsize=(15, 7))
ax2 = ax.twinx()

ax.plot(k_night["ts_utc"], k_night["prob"] * 100,
        color=color_kalshi, marker="o", markersize=2.5, linewidth=0.8,
        alpha=0.9)
ax.set_ylabel("Kalshi  P(312-226) (%)", color=color_kalshi, fontsize=11)
ax.tick_params(axis="y", labelcolor=color_kalshi)
ax.set_ylim(-2, 102)
ax.grid(axis="y", linestyle=":", alpha=0.4)

ax2.plot(e_night_1m["ts_utc"], e_night_1m["mid"],
         color=color_etf, linewidth=1.4, alpha=0.85)
ax2.set_ylabel("VAW mid price (USD)", color=color_etf, fontsize=11)
ax2.tick_params(axis="y", labelcolor=color_etf)

nov5_close = pd.Timestamp("2024-11-05 21:00:00")
nov6_open  = pd.Timestamp("2024-11-06 14:30:00")
ax.axvspan(nov5_close, nov6_open, color="grey", alpha=0.12)
ax.text(nov5_close + (nov6_open - nov5_close) / 2, 95,
        "VAW market CLOSED\n(Kalshi runs alone)",
        ha="center", va="top", fontsize=11, color="#555", fontweight="bold")

markers = [
    ("2024-11-05 23:00", "Polls close (East)\n18:00 ET"),
    ("2024-11-06 02:30", "PA called for Trump\n21:30 ET"),
    ("2024-11-06 10:35", "Race called for Trump\n05:35 ET (AP)"),
    ("2024-11-06 14:30", "VAW open\nGAP to integrate"),
]
for mt_str, lbl in markers:
    mt = pd.Timestamp(mt_str)
    ax.axvline(mt, color="black", linestyle="--", linewidth=1, alpha=0.7)
    ax.text(mt, 65, "  " + lbl, fontsize=9, va="center", ha="left")

ax.set_title(
    f'Election-night SPECIAL: {TICKER} surges overnight as actual outcome (312-226) resolves\n'
    f'Contract: "{CONTRACT_TITLE}"  ×  {ETF} ({ETF_NAME})',
    fontsize=12, fontweight="bold"
)
ax.xaxis.set_major_locator(mdates.HourLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d %H:%M"))
ax.set_xlim(t0, t1)
ax.set_xlabel("Time (UTC) — grey shaded = VAW market closed", fontsize=10)

fig.tight_layout()
out4 = PLOT_DIR / "ecdjt312_vaw_election_night.png"
fig.savefig(out4, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Saved → {out4}")

# ────────────────────────────────────────────────────────────────────────────────
# FIGURE 5 — Multi-day Type B compression
# Kalshi compresses adjustment to 1 night; VAW spreads over ~10 days
# ────────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 7))
ax2 = ax.twinx()

# Hourly resample for smoother daily view
k_hr = (kalshi.set_index("ts_utc")["prob"]
              .resample("1h").mean().dropna().reset_index())
e_hr = (etf.set_index("ts_utc")["mid"]
            .resample("1h").last().dropna().reset_index())

ax.plot(k_hr["ts_utc"], k_hr["prob"] * 100,
        color=color_kalshi, linewidth=1.8, alpha=0.95,
        label="Kalshi (hourly avg)")
ax.set_ylabel("Kalshi  P(Trump 312-226 sweep) (%)",
              color=color_kalshi, fontsize=11)
ax.tick_params(axis="y", labelcolor=color_kalshi)
ax.set_ylim(0, 105)
ax.grid(axis="y", linestyle=":", alpha=0.3)

ax2.plot(e_hr["ts_utc"], e_hr["mid"],
         color=color_etf, linewidth=1.8, alpha=0.85,
         label="VAW (hourly close)")
ax2.set_ylabel("VAW mid price (USD)", color=color_etf, fontsize=11)
ax2.tick_params(axis="y", labelcolor=color_etf)

# Shade Kalshi's compressed adjustment window: 11/5 19:00 → 11/6 14:00 UTC
k_window_start = pd.Timestamp("2024-11-05 19:00")
k_window_end   = pd.Timestamp("2024-11-06 14:00")
ax.axvspan(k_window_start, k_window_end, color=color_kalshi, alpha=0.18,
           label="_nolegend_")
ax.text(k_window_start + (k_window_end - k_window_start)/2, 50,
        "Kalshi adjustment\n~1 night",
        ha="center", va="center", fontsize=10, color="#900",
        fontweight="bold")

# Shade VAW's slow spread adjustment window: 11/6 14:30 → 11/15 21:00 UTC
e_window_start = pd.Timestamp("2024-11-06 14:30")
e_window_end   = pd.Timestamp("2024-11-15 21:00")
ax2.axvspan(e_window_start, e_window_end, color=color_etf, alpha=0.10,
            label="_nolegend_")
ax2.text(pd.Timestamp("2024-11-10 12:00"), 207,
         "VAW adjustment\n~10 days",
         ha="center", va="center", fontsize=10, color="#003",
         fontweight="bold")

# Big horizontal arrow showing the gap (in days)
gap_days = (e_window_end - k_window_end).days
ax.annotate("",
            xy=(e_window_end, 98), xytext=(k_window_end, 98),
            arrowprops=dict(arrowstyle="<->", color="black", lw=1.5))
ax.text(k_window_end + (e_window_end - k_window_end)/2, 102,
        f"≈ {gap_days} days lead",
        ha="center", va="bottom", fontsize=11, fontweight="bold")

ax.set_title(
    f"Multi-day Type B COMPRESSION: Kalshi reaches equilibrium in ~1 night; "
    f"VAW takes ~{gap_days} more days to fully integrate\n"
    f'Contract: "{CONTRACT_TITLE}"  ×  {ETF} ({ETF_NAME})',
    fontsize=12, fontweight="bold"
)
ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
ax.set_xlabel("Date (UTC) — red band = Kalshi adjustment window; blue band = VAW adjustment window",
              fontsize=10)
plt.setp(ax.xaxis.get_majorticklabels(), rotation=0)

fig.tight_layout()
out5 = PLOT_DIR / "ecdjt312_vaw_multiday_compression.png"
fig.savefig(out5, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Saved → {out5}")

print("\nDone.")
