import pandas as pd
import numpy as np

# 1. 读取Step1输出的显著ETF β数据
beta_df = pd.read_csv("etf_beta_significant_june_july.csv")
tickers = beta_df["ticker"].tolist()
beta_vec = beta_df["beta"].values.reshape(-1, 1)

# 2. Beta加权原始权重：w_i = β_i / sum(|β_i|)
abs_beta_sum = np.sum(np.abs(beta_vec))
w_raw = beta_vec / abs_beta_sum

# 3. 美元中性调整 w_adjust = w - mean(w)
w_mean = np.mean(w_raw)
w_adj = w_raw - w_mean

# 4. 整理结果表
weight_res = pd.DataFrame({
    "ticker": tickers,
    "beta": beta_df["beta"].values,
    "raw_beta_weight": w_raw.flatten(),
    "final_dollar_neutral_weight": w_adj.flatten()
})

# 保存权重文件，供Step3使用
weight_res.to_csv("etf_beta_weighted_port_weights.csv", index=False)

# 输出结果
print("==== Beta加权组合权重 ====")
print(weight_res.round(6))

# 校验美元中性
long_total = weight_res[weight_res["final_dollar_neutral_weight"] > 0]["final_dollar_neutral_weight"].sum()
short_total = weight_res[weight_res["final_dollar_neutral_weight"] < 0]["final_dollar_neutral_weight"].sum()
print(f"\n多头总权重：{long_total:.4f}")
print(f"空头总权重：{short_total:.4f}")