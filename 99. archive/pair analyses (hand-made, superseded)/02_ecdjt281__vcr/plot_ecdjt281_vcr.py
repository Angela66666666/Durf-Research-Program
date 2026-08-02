"""
Visualize the lead-lag relationship between:
  - Kalshi contract: "Will Trump win 281-257 - AZ, GA, NC, PA?"
    (ticker: KXECDJT281)
  - ETF: VCR (Vanguard Consumer Discretionary)

Four figures:
  1. Full-window overview (2024-11-04 → 2024-11-15)
  2. Three intraday event zooms during US market hours
  3. Tick-level zooms at second resolution
  4. Election-night special: Nov 5 21:00 UTC → Nov 6 21:00 UTC,
     showing Kalshi overnight swing while VCR is closed,
     followed by VCR gap-open and intraday catch-up.
"""

import duckdb
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

HERE       = Path(__file__).parent                 # leadlag/pair_analyses/02_ecdjt281__vcr/
LEADLAG    = HERE.parent.parent                    # leadlag/
KALSHI     = LEADLAG / "kalshi_hf_cache.parquet"
ETF_HF     = LEADLAG / "etf_hf" / "VCR_hf.parquet"
PLOT_DIR   = HERE / "plots"
PLOT_DIR.mkdir(exist_ok=True)

TICKER         = "KXECDJT281"
CONTRACT_TITLE = "Will Trump win 281-257 - AZ, GA, NC, PA?"
ETF            = "VCR"
ETF_NAME       = "Vanguard Consumer Discretionary ETF"
DATE_START     = "2024-11-04"
DATE_END       = "2024-11-15"

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

# ── Load VCR HF mid prices ─────────────────────────────────────────────────────
etf = con.execute(f"""
    SELECT timestamp_utc AS ts_utc, mid
    FROM read_parquet('{ETF_HF}')
    WHERE timestamp_utc >= TIMESTAMP '{DATE_START} 00:00:00'
      AND timestamp_utc <= TIMESTAMP '{DATE_END} 23:59:59'
    ORDER BY 1
""").df()
etf["ts_utc"] = pd.to_datetime(etf["ts_utc"])
print(f"Loaded {len(etf):,} VCR ticks")

etf_1m = etf.set_index("ts_utc")["mid"].resample("1min").last().dropna().reset_index()
print(f"VCR resampled to {len(etf_1m):,} 1-min bars")

color_kalshi = "#D32F2F"
color_etf    = "#1565C0"

# ────────────────────────────────────────────────────────────────────────────────
# FIGURE 1 — Full window overview
# ────────────────────────────────────────────────────────────────────────────────
fig, ax1 = plt.subplots(figsize=(14, 6))

ax1.set_xlabel("Date (UTC)", fontsize=11)
ax1.set_ylabel("Kalshi probability  P(Trump wins 281-257) (%)",
               color=color_kalshi, fontsize=11)
ax1.plot(kalshi["ts_utc"], kalshi["prob"] * 100,
         color=color_kalshi, linewidth=0.9, alpha=0.9,
         label="Kalshi probability")
ax1.tick_params(axis="y", labelcolor=color_kalshi)
ax1.set_ylim(0, 105)
ax1.grid(axis="y", linestyle=":", alpha=0.4)

ax2 = ax1.twinx()
ax2.set_ylabel("VCR mid price (USD)", color=color_etf, fontsize=11)
ax2.plot(etf_1m["ts_utc"], etf_1m["mid"],
         color=color_etf, linewidth=1.0, alpha=0.85,
         label="VCR price")
ax2.tick_params(axis="y", labelcolor=color_etf)

# Annotate key dates
election_day = pd.Timestamp("2024-11-05 23:00:00")   # polls start closing
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
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=0)

fig.tight_layout()
out1 = PLOT_DIR / "ecdjt281_vcr_overview.png"
fig.savefig(out1, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Saved → {out1}")

# ────────────────────────────────────────────────────────────────────────────────
# FIGURE 2 — Three intraday event zooms during US market hours
# ────────────────────────────────────────────────────────────────────────────────
events = [
    {
        "title": "Nov 5, 2024 — Election Day afternoon (pre-poll-close jitters)",
        "t0":    "2024-11-05 15:00",
        "t1":    "2024-11-05 21:00",
        "marks": [
            ("2024-11-05 14:30", "US equity open\n(9:30 ET)"),
            ("2024-11-05 21:00", "US equity close\n(16:00 ET)"),
        ],
        "story": ("Kalshi P(Trump 281-257) cluster-jumps ±8-10pp through the afternoon "
                  "as exit-poll rumors circulate."),
    },
    {
        "title": "Nov 6, 2024 — Morning after election (VCR gap-open & catch-up)",
        "t0":    "2024-11-06 14:30",
        "t1":    "2024-11-06 17:30",
        "marks": [
            ("2024-11-06 14:30", "US equity open — VCR gap-up"),
        ],
        "story": ("VCR gaps up at open absorbing the overnight result. Kalshi has already "
                  "declined from its overnight peak as the specific 281-257 outcome "
                  "looks less likely (Trump path is wider)."),
    },
    {
        "title": "Nov 6, 2024 — Afternoon dramatic Kalshi swings (4 → 25 → 4 in seconds)",
        "t0":    "2024-11-06 18:00",
        "t1":    "2024-11-06 21:00",
        "marks": [],
        "story": ("Two large Kalshi spikes at 18:34 (+24pp in 34 sec) and 18:57 (+23pp). "
                  "Late-day swing at 20:50."),
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
            alpha=0.9, label="Kalshi")
    ax.set_ylabel("Kalshi  P(Trump 281-257) (%)",
                  color=color_kalshi, fontsize=10)
    ax.tick_params(axis="y", labelcolor=color_kalshi)
    ax.grid(axis="y", linestyle=":", alpha=0.4)

    ax2.plot(e_win_10s["ts_utc"], e_win_10s["mid"],
             color=color_etf, linewidth=1.0, alpha=0.85, label="VCR")
    ax2.set_ylabel("VCR mid price (USD)", color=color_etf, fontsize=10)
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
out2 = PLOT_DIR / "ecdjt281_vcr_event_zooms.png"
fig.savefig(out2, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Saved → {out2}")

# ────────────────────────────────────────────────────────────────────────────────
# FIGURE 3 — TICK-LEVEL zooms (raw VCR ticks, raw Kalshi trades)
# ────────────────────────────────────────────────────────────────────────────────
tick_events = [
    {
        "title":  "Nov 6 18:30-19:15 UTC — Kalshi spike 4 → 25 → 4 in 34 seconds (cf. Sep 18 FOMC anomaly in Pair #01)",
        "t0":     "2024-11-06 18:30:00",
        "t1":     "2024-11-06 19:15:00",
        "marks":  [],
        "narr":   ("Compare VCR tick-by-tick around the 18:34 spike. Did anyone trust the 25¢ print?"),
    },
    {
        "title":  "Nov 6 20:30-21:00 UTC — Late-day Kalshi swing (4 → 19 → 4) at close",
        "t0":     "2024-11-06 20:30:00",
        "t1":     "2024-11-06 21:00:00",
        "marks":  [
            ("2024-11-06 21:00", "Market close (16:00 ET)"),
        ],
        "narr":   ("Closing-hour Kalshi volatility. Does VCR move synchronously?"),
    },
    {
        "title":  "Nov 5 16:30-17:00 UTC — Election Day morning Kalshi cluster jumps",
        "t0":     "2024-11-05 16:30:00",
        "t1":     "2024-11-05 17:00:00",
        "marks":  [],
        "narr":   ("Pre-poll-close exit-poll-driven Kalshi swings during VCR's active session."),
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
            alpha=0.95, label="Kalshi trade")
    # Annotate each Kalshi trade with its yes_price
    for _, row in k_win.iterrows():
        ax.annotate(f"{int(row['yes_price'])}¢",
                    xy=(row["ts_utc"], row["prob"] * 100),
                    xytext=(4, 6), textcoords="offset points",
                    fontsize=6.5, color=color_kalshi, alpha=0.9)
    ax.set_ylabel("Kalshi  P(Trump 281-257) (%)",
                  color=color_kalshi, fontsize=10)
    ax.tick_params(axis="y", labelcolor=color_kalshi)
    ax.grid(axis="y", linestyle=":", alpha=0.4)

    # Every single VCR tick, no resampling
    ax2.plot(e_win["ts_utc"], e_win["mid"],
             color=color_etf, linewidth=0.7, alpha=0.85,
             label=f"VCR every tick ({len(e_win):,})")
    ax2.set_ylabel("VCR mid price (USD)", color=color_etf, fontsize=10)
    ax2.tick_params(axis="y", labelcolor=color_etf)

    for mark_t_str, mark_label in ev["marks"]:
        mark_t = pd.Timestamp(mark_t_str)
        if t0 <= mark_t <= t1:
            ax.axvline(mark_t, color="black", linestyle="--", linewidth=1, alpha=0.6)
            ax.text(mark_t, ax.get_ylim()[1] * 0.97, "  " + mark_label,
                    fontsize=8, va="top", ha="left", color="black")

    ax.set_title(f"{ev['title']}\n{ev['narr']}\n"
                 f"({len(k_win)} Kalshi trades, {len(e_win):,} VCR ticks)",
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
out3 = PLOT_DIR / "ecdjt281_vcr_tick_zooms.png"
fig.savefig(out3, dpi=160, bbox_inches="tight")
plt.close(fig)
print(f"Saved → {out3}")

# ────────────────────────────────────────────────────────────────────────────────
# FIGURE 4 — Election-night special:
# Nov 5 19:00 UTC (14:00 ET, pre-close) → Nov 6 21:00 UTC (16:00 ET, market close)
# Shows the unique pattern: Kalshi runs alone overnight; VCR gaps at open.
# ────────────────────────────────────────────────────────────────────────────────
t0 = pd.Timestamp("2024-11-05 19:00:00")
t1 = pd.Timestamp("2024-11-06 21:00:00")
k_night = kalshi[(kalshi["ts_utc"] >= t0) & (kalshi["ts_utc"] <= t1)].copy()
e_night = etf[(etf["ts_utc"] >= t0) & (etf["ts_utc"] <= t1)].copy()
e_night_1m = (e_night.set_index("ts_utc")["mid"]
                       .resample("1min").last().dropna().reset_index())

fig, ax = plt.subplots(figsize=(15, 7))
ax2 = ax.twinx()

# Kalshi — full overnight
ax.plot(k_night["ts_utc"], k_night["prob"] * 100,
        color=color_kalshi, marker="o", markersize=2.5, linewidth=0.8,
        alpha=0.9, label="Kalshi")
ax.set_ylabel("Kalshi  P(Trump 281-257) (%)",
              color=color_kalshi, fontsize=11)
ax.tick_params(axis="y", labelcolor=color_kalshi)
ax.set_ylim(-2, 102)
ax.grid(axis="y", linestyle=":", alpha=0.4)

# VCR
ax2.plot(e_night_1m["ts_utc"], e_night_1m["mid"],
         color=color_etf, linewidth=1.4, alpha=0.85, label="VCR")
ax2.set_ylabel("VCR mid price (USD)", color=color_etf, fontsize=11)
ax2.tick_params(axis="y", labelcolor=color_etf)

# Shade VCR closed periods
nov5_close = pd.Timestamp("2024-11-05 21:00:00")
nov6_open  = pd.Timestamp("2024-11-06 14:30:00")
ax.axvspan(nov5_close, nov6_open, color="grey", alpha=0.12,
           label="VCR closed (overnight)")
ax.text(nov5_close + (nov6_open - nov5_close) / 2, 95,
        "VCR market CLOSED\n(Kalshi runs alone)",
        ha="center", va="top", fontsize=11, color="#555", fontweight="bold")

# Key event markers
markers = [
    ("2024-11-05 23:00", "Polls close (East)\n18:00 ET"),
    ("2024-11-06 03:00", "Kalshi peak (98¢)\n22:00 ET\nKey states called"),
    ("2024-11-06 14:30", "US equity open\nVCR GAP UP"),
]
for mt_str, lbl in markers:
    mt = pd.Timestamp(mt_str)
    ax.axvline(mt, color="black", linestyle="--", linewidth=1, alpha=0.7)
    ax.text(mt, 70, "  " + lbl, fontsize=9, va="center", ha="left")

ax.set_title(
    f'Election-night SPECIAL: {TICKER} surges to 98¢ overnight while VCR is closed\n'
    f'Contract: "{CONTRACT_TITLE}"  ×  {ETF} ({ETF_NAME})',
    fontsize=12, fontweight="bold"
)
ax.xaxis.set_major_locator(mdates.HourLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d %H:%M"))
ax.set_xlim(t0, t1)
ax.set_xlabel("Time (UTC) — grey shaded = VCR market closed", fontsize=10)
plt.setp(ax.xaxis.get_majorticklabels(), rotation=0, fontsize=9)

fig.tight_layout()
out4 = PLOT_DIR / "ecdjt281_vcr_election_night.png"
fig.savefig(out4, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Saved → {out4}")

# ────────────────────────────────────────────────────────────────────────────────
# FIGURE 5 — Multi-day Type B compression (added in correction pass)
# Kalshi 281 surges overnight then falls (specific-path mismatch);
# VCR rises smoothly over ~5 days as broader Trump-trade gets priced.
# Despite Kalshi-281's noisier signal, the COMPRESSION asymmetry is real:
# Kalshi 281 reaches its overnight peak in 1 night; VCR takes 5 days to reach its peak.
# ────────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 7))
ax2 = ax.twinx()

k_hr = (kalshi.set_index("ts_utc")["prob"]
              .resample("1h").mean().dropna().reset_index())
e_hr = (etf.set_index("ts_utc")["mid"]
            .resample("1h").last().dropna().reset_index())

ax.plot(k_hr["ts_utc"], k_hr["prob"] * 100,
        color=color_kalshi, linewidth=1.8, alpha=0.95,
        label="Kalshi (hourly avg)")
ax.set_ylabel("Kalshi  P(Trump 281-257) (%)",
              color=color_kalshi, fontsize=11)
ax.tick_params(axis="y", labelcolor=color_kalshi)
ax.set_ylim(0, 105)
ax.grid(axis="y", linestyle=":", alpha=0.3)

ax2.plot(e_hr["ts_utc"], e_hr["mid"],
         color=color_etf, linewidth=1.8, alpha=0.85,
         label="VCR (hourly close)")
ax2.set_ylabel("VCR mid price (USD)", color=color_etf, fontsize=11)
ax2.tick_params(axis="y", labelcolor=color_etf)

# Kalshi's compressed peak window: overnight 11/5 → 11/6 morning
k_window_start = pd.Timestamp("2024-11-05 19:00")
k_window_end   = pd.Timestamp("2024-11-06 06:00")
ax.axvspan(k_window_start, k_window_end, color=color_kalshi, alpha=0.18)
ax.text(k_window_start + (k_window_end - k_window_start)/2, 70,
        "Kalshi 281 surges\nto 98¢ peak\n(~1 night)",
        ha="center", va="center", fontsize=9.5, color="#900",
        fontweight="bold")

# VCR's spread adjustment window: 11/6 → 11/12
e_window_start = pd.Timestamp("2024-11-06 14:30")
e_window_end   = pd.Timestamp("2024-11-12 21:00")
ax2.axvspan(e_window_start, e_window_end, color=color_etf, alpha=0.10)
ax2.text(pd.Timestamp("2024-11-09 12:00"), 365,
         "VCR adjustment\n~5 days",
         ha="center", va="center", fontsize=10, color="#003",
         fontweight="bold")

# Arrow showing the gap
gap_days = (e_window_end - k_window_end).days
ax.annotate("",
            xy=(e_window_end, 95), xytext=(k_window_end, 95),
            arrowprops=dict(arrowstyle="<->", color="black", lw=1.5))
ax.text(k_window_end + (e_window_end - k_window_end)/2, 100,
        f"≈ {gap_days} days lead",
        ha="center", va="bottom", fontsize=11, fontweight="bold")

ax.set_title(
    f"Multi-day Type B COMPRESSION: Kalshi 281 reaches its overnight peak in 1 night;\n"
    f"VCR takes ~{gap_days} more days to fully price the Trump-trade consumer rally\n"
    f'Contract: "{CONTRACT_TITLE}"  ×  {ETF} ({ETF_NAME})',
    fontsize=11.5, fontweight="bold"
)
ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
ax.set_xlabel("Date (UTC) — red band = Kalshi peak window; blue band = VCR adjustment window",
              fontsize=10)
plt.setp(ax.xaxis.get_majorticklabels(), rotation=0)

fig.tight_layout()
out5 = PLOT_DIR / "ecdjt281_vcr_multiday_compression.png"
fig.savefig(out5, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Saved → {out5}")

print("\nDone.")
