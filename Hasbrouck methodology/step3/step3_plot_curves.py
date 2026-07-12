"""
step3_plot_curves.py
================================================================================
Plot the three Step-3 basket LEVEL series (one weight plan per panel) in one
figure. Step 3 has no probability and no Kalshi yet -- these are the raw
buy-and-hold NAV curves B_t in return units. The x-axis is a continuous bar
index so the trading sessions sit side by side with no overnight gaps; a dashed
line marks each day's boundary and the bottom tick shows that day's date and its
first bar time.

Input : step3_basket_levels.csv   (from step3_build_basket.py)
Output: step3_basket_levels.png
"""
import os
import sys
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

MODE = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in ("high_frequency", "daily") else "high_frequency"

HERE = os.path.dirname(os.path.abspath(__file__))
LEVELS = os.path.join(HERE, f"step3_basket_levels_{MODE}.csv")
OUT = os.path.join(HERE, f"step3_basket_levels_{MODE}.png")

PLAN_COLS = {
    "B_A_sign_equal":    ("plan A sign-equal",    "#1f77b4"),
    "B_B_beta_weighted": ("plan B beta-weighted", "#2ca02c"),
    "B_C_min_variance":  ("plan C min-variance",  "#d62728"),
}


def main():
    d = pd.read_csv(LEVELS, parse_dates=["ts_et"]).sort_values(["date", "ts_et"]).reset_index(drop=True)
    d["x"] = range(len(d))

    firsts = d.groupby("date", sort=True).first()
    bounds = d.groupby("date", sort=True)["x"].min().values
    labels = [f"{ds}\n{ts.strftime('%H:%M')}" for ds, ts in zip(firsts.index, firsts["ts_et"])]

    mk = "o" if MODE == "daily" else None
    lw = 1.4 if MODE == "daily" else 0.9
    fig, axes = plt.subplots(len(PLAN_COLS), 1, figsize=(19, 12), sharex=True)
    for ax, (col, (lbl, c)) in zip(axes, PLAN_COLS.items()):
        ax.plot(d["x"], d[col], color=c, lw=lw, marker=mk, ms=4, label=f"ETF basket level - {lbl}")
        ax.axhline(0, color="0.6", lw=0.7)
        for b in bounds:
            ax.axvline(b, color="0.85", lw=0.5, ls="--", zorder=0)
        ax.set_ylabel("basket level B_t (cum. return)")
        ax.grid(axis="y", color="0.93", lw=0.6)
        ax.legend(loc="upper left", fontsize=9, framealpha=0.9)
        ax.margins(x=0)

    axes[-1].set_xticks(bounds)
    axes[-1].set_xticklabels(labels, fontsize=7.5)
    axes[-1].set_xlim(0, len(d) - 1)
    grain = "1-min bars" if MODE == "high_frequency" else "daily close-to-close"
    axes[0].set_title(f"Step 3 [{MODE}] - ETF basket buy-and-hold level (overnight gaps included), {grain}, ET")

    fig.tight_layout()
    fig.savefig(OUT, dpi=140)
    print("written ->", OUT)


if __name__ == "__main__":
    main()
