import pandas as pd
import numpy as np
import os

def find_project_root(target_folder="regression"):
    current = os.path.dirname(os.path.abspath(__file__))
    for _ in range(5):
        if target_folder in os.listdir(current):
            return current
        current = os.path.dirname(current)
    raise FileNotFoundError("未定位到项目根目录")

root_path = find_project_root("regression")
beta_csv = os.path.join(root_path, "etf_beta_significant_june_july.csv")
beta_df = pd.read_csv(beta_csv)
beta_df = beta_df.drop_duplicates(subset=["ticker"], keep="first")

all_tickers = beta_df["ticker"].tolist()
print("待处理全部ETF：", all_tickers)

def load_hf_panel(tk_list, root_dir, resample_freq="1min"):
    ret_dict = {}
    hf_base = os.path.join(root_dir, "leadlag", "etf_hf")
    valid_tickers = []
    for tk in tk_list:
        print(f"【进度】处理 {tk}_hf.parquet")
        parquet_path = os.path.join(hf_base, f"{tk}_hf.parquet")
        df = pd.read_parquet(parquet_path, columns=["timestamp_utc", "mid"])
        
        # 时区标准化
        df["dt"] = pd.to_datetime(df["timestamp_utc"])
        df["dt_utc"] = df["dt"].dt.tz_localize("UTC")
        df["dt_et"] = df["dt_utc"].dt.tz_convert("US/Eastern")
        
        # 过滤美股交易时段 9:30-16:00 ET
        hour = df["dt_et"].dt.hour
        minute = df["dt_et"].dt.minute
        trading_mask = ((hour > 9) | ((hour == 9) & (minute >= 30))) & (hour < 16)
        df_trade = df[trading_mask].copy()
        df_trade = df_trade.set_index("dt_et")["mid"]
        
        # 关键修复：重采样统一时间刻度，取区间最后一笔mid价格
        resampled_mid = df_trade.resample(resample_freq).last().dropna()
        # 计算重采样后对数收益率
        log_ret = np.log(resampled_mid / resampled_mid.shift(1)).dropna()
        
        if len(log_ret) < 30:
            print(f"⚠️ {tk} 重采样后有效样本过少，剔除")
            continue
        ret_dict[tk] = log_ret
        valid_tickers.append(tk)
        print(f"✅ {tk} 处理完成，重采样后样本量：{len(log_ret)}")
    
    if len(ret_dict) == 0:
        raise Exception("无任何ETF存在充足有效高频数据")
    
    print("\n全部有效标的：", valid_tickers)
    print("按统一1分钟时间轴对齐...")
    # 外对齐填充，再删除全空行，保证全部标的共享时间轴
    panel = pd.DataFrame(ret_dict).dropna(how="all")
    overlap_len = len(panel.dropna())
    print(f"公共有效观测点总数：{overlap_len}")
    
    if overlap_len < 30:
        raise Exception(f"公共重叠观测仅{overlap_len}行，不足以求解协方差")
    return panel, valid_tickers

# 重采样1分钟频度，可改为"5min"、"10min"
ret_panel, valid_tickers = load_hf_panel(all_tickers, root_path, resample_freq="1min")
beta_valid = beta_df[beta_df["ticker"].isin(valid_tickers)].copy()
tickers = beta_valid["ticker"].tolist()
beta_vec = beta_valid["beta"].values.reshape(-1, 1)

# 最小方差权重求解
Sigma = ret_panel.cov().values
try:
    Sigma_inv = np.linalg.inv(Sigma)
except np.linalg.LinAlgError:
    raise Exception("协方差矩阵奇异不可逆，标的收益率线性相关")

term1 = beta_vec.T @ Sigma_inv @ beta_vec
term1_inv = np.linalg.inv(term1)
term2 = Sigma_inv @ beta_vec
w_raw = term1_inv * term2

# 美元中性调整
w_mean = np.mean(w_raw)
w_adj = w_raw - w_mean

result_df = pd.DataFrame({
    "ticker": tickers,
    "beta": beta_valid["beta"].values,
    "raw_minvar_weight": w_raw.flatten(),
    "final_dollar_neutral_weight": w_adj.flatten()
})

out_csv = os.path.join(root_path, "regression", "etf_mimic_port_weights.csv")
result_df.to_csv(out_csv, index=False)

print("\n==== Plan C 最小方差权重计算完成 ====")
print(result_df.round(6))

long_total = result_df[result_df["final_dollar_neutral_weight"] > 0]["final_dollar_neutral_weight"].sum()
short_total = result_df[result_df["final_dollar_neutral_weight"] < 0]["final_dollar_neutral_weight"].sum()
print(f"\n多头总权重：{long_total:.4f}")
print(f"空头总权重：{short_total:.4f}")
print("多空权重绝对值相等，满足美元中性对冲约束")