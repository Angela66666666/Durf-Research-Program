"""
分析和可视化 leadlag_profile_results.csv 的结果。

输出：
  leadlag/plots/irf_<pair>_<direction>.png  —  IRF 脉冲响应图
  leadlag/plots/summary_heatmap.png         —  显著对汇总热图
  终端打印分层解读
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from pathlib import Path

HERE     = Path(__file__).parent
PROF_CSV = HERE / "leadlag_profile_results.csv"
UNIF_CSV = HERE / "leadlag_unified_results.csv"
PLOT_DIR = HERE / "plots"
PLOT_DIR.mkdir(exist_ok=True)

# ── 读取数据 ────────────────────────────────────────────────────────────────────
df = pd.read_csv(PROF_CSV)

# ── 第一步：筛选出值得关注的显著结果 ────────────────────────────────────────────
# 条件：p < 0.05 且交易量 >= 100 笔（排除稀疏噪声合约）
peak = (
    df.loc[df.groupby(["contract_ticker", "etf", "direction"])["p_value"].idxmin()]
    .sort_values("p_value")
    .reset_index(drop=True)
)

sig = peak[(peak["p_value"] < 0.05) & (peak["n_kalshi_trades"] >= 100)].copy()

print("=" * 80)
print("第一层：哪些合约对有统计显著的 lead-lag 关系？")
print("=" * 80)
print(f"满足条件（p<0.05，交易量>=100）的合约对方向组合：{len(sig)} 个\n")

show_cols = ["contract_ticker", "etf", "direction", "horizon_sec",
             "n_kalshi_trades", "coef", "t_stat", "p_value"]
with pd.option_context("display.width", 230, "display.max_colwidth", 45,
                       "display.float_format", "{:.4f}".format):
    print(sig[show_cols].to_string(index=False))

# ── 第二步：区分 Kalshi 领先 vs ETF 领先 ────────────────────────────────────────
print("\n" + "=" * 80)
print("第二层：方向分布")
print("=" * 80)
dir_count = sig["direction"].value_counts()
for d, n in dir_count.items():
    label = "Kalshi → ETF（Kalshi 预测 ETF）" if d == "kalshi_leads_etf" else "ETF → Kalshi（ETF 预测 Kalshi）"
    print(f"  {label}：{n} 个")

# ── 第三步：按合约类型归组 ────────────────────────────────────────────────────────
print("\n" + "=" * 80)
print("第三层：按合约类型归组")
print("=" * 80)

def classify(ticker):
    t = ticker.upper()
    if "FEDDECISION" in t or "RATECUT" in t:
        return "联储利率决议"
    if "ECDJT" in t:
        return "Trump 行政令相关"
    if "538APPROVE" in t or "AAAGASM" in t or "ECKH" in t:
        return "其他政治/市场合约"
    return "其他"

sig["category"] = sig["contract_ticker"].apply(classify)
for cat, grp in sig.groupby("category"):
    print(f"\n  【{cat}】")
    for _, row in grp.iterrows():
        sign_note = "正相关" if row["coef"] > 0 else "负相关"
        peak_t    = int(row["horizon_sec"])
        print(f"    {row['contract_ticker']} × {row['etf']}"
              f"  {row['direction']}  峰值@{peak_t}s  "
              f"t={row['t_stat']:.2f}  p={row['p_value']:.4f}  "
              f"({sign_note}, coef={row['coef']:.4f})")

# ── IRF 图函数 ─────────────────────────────────────────────────────────────────
def plot_irf(ticker: str, etf: str, direction: str, ax=None, title_override=None):
    sub = df[
        (df["contract_ticker"] == ticker) &
        (df["etf"] == etf) &
        (df["direction"] == direction)
    ].sort_values("horizon_sec")

    if sub.empty:
        return None

    horizons = sub["horizon_sec"].values
    coefs    = sub["coef"].values
    se       = sub["coef"].abs() / sub["t_stat"].abs().replace(0, np.nan)
    n_trades = sub["n_kalshi_trades"].iloc[0]
    best_p   = sub["p_value"].min()
    best_h   = sub.loc[sub["p_value"].idxmin(), "horizon_sec"]

    own_fig = ax is None
    if own_fig:
        fig, ax = plt.subplots(figsize=(9, 4))

    # 置信带（±1.96 SE）
    ax.fill_between(horizons, coefs - 1.96 * se, coefs + 1.96 * se,
                    alpha=0.20, color="#2196F3")
    ax.plot(horizons, coefs, color="#1565C0", linewidth=1.8)
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")

    # 标出最优峰值
    ax.axvline(best_h, color="#E53935", linewidth=1, linestyle=":")
    ax.scatter([best_h], [coefs[horizons == best_h][0]],
               color="#E53935", zorder=5, s=40)

    ax.set_xlabel("时间窗口 Δ（秒）", fontsize=10)
    dir_zh = "Kalshi 领先 ETF" if direction == "kalshi_leads_etf" else "ETF 领先 Kalshi"
    ax.set_ylabel("回归系数 β", fontsize=10)
    title = title_override or f"{ticker}\n× {etf}  |  {dir_zh}"
    ax.set_title(title, fontsize=10)
    ax.text(0.99, 0.96,
            f"交易量={n_trades}笔  最优Δ={best_h}s  p={best_p:.4f}",
            transform=ax.transAxes, ha="right", va="top", fontsize=8, color="#555")
    ax.grid(axis="y", linestyle=":", alpha=0.5)

    if own_fig:
        plt.tight_layout()
        fname = f"irf_{ticker[:20]}_{etf}_{direction[:3]}.png".replace("/", "_")
        out   = PLOT_DIR / fname
        plt.savefig(out, dpi=150)
        plt.close()
        return out


# ── 第四步：画出最关键合约对的 IRF 图 ──────────────────────────────────────────
# 选出 p 最小的前 N 个（两个方向都画，如果都显著）
TOP_N   = 8
top_sig = sig.head(TOP_N)

saved_plots = []
for _, row in top_sig.iterrows():
    path = plot_irf(row["contract_ticker"], row["etf"], row["direction"])
    if path:
        saved_plots.append(path)
        print(f"\n  [IRF图] 保存 → {path.name}")

# ── 第五步：汇总拼图（最重要的 Fed 利率合约）──────────────────────────────────
fed_sig = sig[sig["category"] == "联储利率决议"].head(6)

if len(fed_sig) > 0:
    ncols = 2
    nrows = int(np.ceil(len(fed_sig) / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(14, 4 * nrows))
    axes = np.array(axes).flatten()

    for ax_i, (_, row) in enumerate(fed_sig.iterrows()):
        plot_irf(row["contract_ticker"], row["etf"], row["direction"], ax=axes[ax_i])

    for ax_i in range(len(fed_sig), len(axes)):
        axes[ax_i].set_visible(False)

    fig.suptitle("联储利率决议合约：IRF 脉冲响应函数（事件驱动，秒级）",
                 fontsize=13, fontweight="bold", y=1.01)
    plt.tight_layout()
    out = PLOT_DIR / "irf_fed_contracts_panel.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\n  [拼图] 保存 → {out.name}")

# ── 第六步：读 unified 结果做补充说明 ──────────────────────────────────────────
if UNIF_CSV.exists():
    unif = pd.read_csv(UNIF_CSV)
    sig_unif = unif[unif["p_value"] < 0.05].sort_values("p_value")

    print("\n" + "=" * 80)
    print("附：统一回归（分钟级，k=-5到+5）显著结果")
    print("=" * 80)
    print(f"显著系数数: {len(sig_unif)}  /  总数: {len(unif)}")
    k_counts = sig_unif.groupby(["direction","k"]).size().reset_index(name="n")
    print("\n各 k 值显著数量：")
    print(k_counts.to_string(index=False))

    print("\n最显著的前 15 条：")
    ucols = ["contract_ticker","etf","k","direction","coef","t_stat","p_value","n_obs"]
    with pd.option_context("display.width",200,"display.max_colwidth",40,
                           "display.float_format","{:.4f}".format):
        print(sig_unif[ucols].head(15).to_string(index=False))

print("\n" + "=" * 80)
print(f"全部图表已保存至 → {PLOT_DIR.resolve()}")
print("=" * 80)
