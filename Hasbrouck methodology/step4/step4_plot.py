"""
step4_plot.py
================================================================================
Plot the calibrated basket implied probability against Kalshi, one weight plan
per panel, sharing a continuous bar-index x-axis with day boundaries marked.
Each panel has its own y-axis because plan A and especially plan C stray well
outside [0,1]. Kalshi bars carried forward (stale) are drawn lighter so the
sparse early period is visible.

Input : step4_pair.csv   (from step4_align.py)
Output: step4_pair.png
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

MODE = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in ("high_frequency", "daily") else "high_frequency"

HERE = os.path.dirname(os.path.abspath(__file__))
PAIR = os.path.join(HERE, f"step4_pair_{MODE}.csv")
OUT = os.path.join(HERE, f"step4_pair_{MODE}.png")

PLAN_COLS = {
    "implied_p_A_sign_equal":    ("plan A sign-equal",    "#1f77b4"),
    "implied_p_B_beta_weighted": ("plan B beta-weighted", "#2ca02c"),
    "implied_p_C_min_variance":  ("plan C min-variance",  "#d62728"),
}


def main():
    d = pd.read_csv(PAIR, parse_dates=["ts_et"]).sort_values(["date", "ts_et"]).reset_index(drop=True)
    d["x"] = range(len(d))
    firsts = d.groupby("date", sort=True).first()
    bounds = d.groupby("date", sort=True)["x"].min().values
    labels = [f"{ds}\n{ts.strftime('%H:%M')}" for ds, ts in zip(firsts.index, firsts["ts_et"])]

    mk = "o" if MODE == "daily" else None          # markers when there are only ~24 points
    lw = 1.4 if MODE == "daily" else 0.9
    fig, axes = plt.subplots(len(PLAN_COLS), 1, figsize=(19, 12), sharex=True)
    for ax, (col, (lbl, c)) in zip(axes, PLAN_COLS.items()):
        ax.plot(d["x"], d[col], color=c, lw=lw, marker=mk, ms=4, label=f"ETF basket implied P - {lbl}")
        # Kalshi: stale bars lighter, fresh bars solid black
        ax.plot(d["x"], d["kalshi_prob"], color="0.75", lw=0.8, zorder=1)
        fresh = d["market_fresh"].values.astype(bool)
        kf = np.where(fresh, d["kalshi_prob"], np.nan)
        ax.plot(d["x"], kf, color="black", lw=1.0, marker=mk, ms=3, label="Kalshi (fresh)", zorder=2)
        ax.axhline(0, color="0.6", lw=0.6); ax.axhline(1, color="0.6", lw=0.6)
        for b in bounds:
            ax.axvline(b, color="0.85", lw=0.5, ls="--", zorder=0)
        ax.set_ylabel("P(Trump wins)")
        ax.grid(axis="y", color="0.93", lw=0.6)
        ax.legend(loc="upper left", fontsize=9, framealpha=0.9)
        ax.margins(x=0)

    axes[-1].set_xticks(bounds)
    axes[-1].set_xticklabels(labels, fontsize=7.5)
    axes[-1].set_xlim(0, len(d) - 1)
    grain = "1-min bars" if MODE == "high_frequency" else "daily close-to-close"
    axes[0].set_title(f"Step 4 [{MODE}] - calibrated basket implied probability vs Kalshi, {grain}, ET "
                      "(grey = Kalshi carried forward on stale bars)")

    fig.tight_layout()
    fig.savefig(OUT, dpi=140)
    print("written ->", OUT)


if __name__ == "__main__":
    main()
