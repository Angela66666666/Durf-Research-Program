import pandas as pd
import numpy as np

# 1. 读取Step1输出的显著ETF β
beta_df = pd.read_csv("etf_beta_significant_june_july.csv")
tickers = beta_df["ticker"].tolist()
beta_arr = beta_df["beta"].values

# 2. 区分多头、空头分组
mask_long = beta_arr > 0
mask_short = beta_arr < 0

long_tickers = beta_df.loc[mask_long, "ticker"].tolist()
short_tickers = beta_df.loc[mask_short, "ticker"].tolist()
n_long = len(long_tickers)
n_short = len(short_tickers)

# 分配原始权重
w_raw = np.zeros(len(tickers))
# 正向ETF等额分配
for idx, tick in enumerate(tickers):
    if tick in long_tickers:
        w_raw[idx] = 1 / n_long
    elif tick in short_tickers:
        w_raw[idx] = -1 / n_short

# 3. 美元中性调整：减去权重均值
w_mean = np.mean(w_raw)
w_adj = w_raw - w_mean

# 4. 汇总输出表格
weight_res = pd.DataFrame({
    "ticker": tickers,
    "beta": beta_arr,
    "raw_sign_equal_weight": w_raw,
    "final_dollar_neutral_weight": w_adj
})

# 保存权重文件给Step3调用
weight_res.to_csv("etf_sign_equal_port_weights.csv", index=False)

print("==== Sign-Equal 符号等权组合权重 ====")
print(weight_res.round(6))

# 校验美元中性
long_sum = weight_res[weight_res["final_dollar_neutral_weight"] > 0]["final_dollar_neutral_weight"].sum()
short_sum = weight_res[weight_res["final_dollar_neutral_weight"] < 0]["final_dollar_neutral_weight"].sum()
print(f"\n多头总权重：{long_sum:.4f}")
print(f"空头总权重：{short_sum:.4f}")