import pandas as pd
import os

def find_project_root(target_folder="regression"):
    current = os.path.dirname(os.path.abspath(__file__))
    for _ in range(5):
        if target_folder in os.listdir(current):
            return current
        current = os.path.dirname(current)
    raise FileNotFoundError("未找到regression文件夹")

root_path = find_project_root("regression")
csv_path = os.path.join(root_path, "regression", "regression_screen_results.csv")

screen_df = pd.read_csv(csv_path)
print("CSV内全部列名：", screen_df.columns.tolist())

p_col = "p_value"
beta_col = "std_coef"
t_col = "t_stat"
n_col = "n_obs"
ticker_col = "etf"

# ---- 关键改动1：不再跨事件族混用，只锁定"270-268"这一对合约 ----
# KXECDJT270 = Will Trump win 270-268 (GA, NC, PA)
# KXECKH270  = Will Harris win 270-268 (MI, PA, WI)
# 二者是同一个"险胜/险负"临界点的镜像事件，是目前池子里能找到的
# 最接近"谁赢"这个问题本身的一对合约（仍是margin threshold的近似代理，
# 不是真正的P(Trump当选)二元合约，这一局限在报告里需要写明）
TRUMP_TICKER = "KXECDJT270"
HARRIS_TICKER = "KXECKH270"

pair_df = screen_df[screen_df["contract_ticker"].isin([TRUMP_TICKER, HARRIS_TICKER])].copy()

missing = set(screen_df[ticker_col].unique()) - set(pair_df[ticker_col].unique())
if missing:
    raise ValueError(f"以下ETF在270-268这对合约里缺数据，需要人工确认: {missing}")

# ---- 关键改动2：符号对齐 ----
# P(Harris赢) ≈ 1 - P(Trump赢)，所以 ΔP(Harris) ≈ -ΔP(Trump)
# Harris侧的系数要乘以-1，才能换算成"对P(Trump赢)的暴露"
pair_df["side"] = pair_df["contract_ticker"].map({
    TRUMP_TICKER: "Trump",
    HARRIS_TICKER: "Harris",
})
pair_df["aligned_beta"] = pair_df.apply(
    lambda r: r[beta_col] if r["side"] == "Trump" else -r[beta_col],
    axis=1,
)
pair_df["se"] = pair_df[beta_col] / pair_df[t_col]  # std_coef / t_stat

# ---- 关键改动3：不按显著性筛选，11个ETF全部保留 ----
# 每个ETF同时有Trump侧和Harris侧两个（已对齐符号的）估计，
# 两者理论上应互为镜像，取|t_stat|更大（估计更可靠）的一侧作为最终beta，
# 但两个估计都完整保留在输出里，供后续核对/敏感性分析用
def pick_more_reliable(group):
    best = group.loc[group[t_col].abs().idxmax()]
    return pd.Series({
        "beta": best["aligned_beta"],
        "chosen_side": best["side"],
        "chosen_contract": best["contract_ticker"],
        "t_stat": best[t_col],
        "se": best["se"],
        "n_obs": best[n_col],
        "p_value": best[p_col],
    })

beta_df = (
    pair_df.groupby(ticker_col, group_keys=True)
    .apply(pick_more_reliable)
    .reset_index()
    .rename(columns={ticker_col: "ticker"})
)

# 同时导出两侧原始估计，方便对比/写方法局限说明
diagnostic_df = pair_df[[ticker_col, "contract_ticker", "side", beta_col,
                          "aligned_beta", t_col, "se", n_col, p_col]].sort_values(ticker_col)

beta_df.to_csv("etf_beta_significant_june_july.csv", index=False)
diagnostic_df.to_csv("etf_beta_diagnostic_both_sides.csv", index=False)

print("==== Step1修正版（单一合约270-268 + 符号对齐 + 不筛显著性）====")
print(beta_df)
print("\n注意：这仍是margin-threshold合约的近似代理，不是真正的P(Trump当选)二元合约，")
print("报告里需要写明这个局限，建议同时报告模拟组合的R²而不是逐个beta的显著性。")
