import pandas as pd
import numpy as np
import statsmodels.api as sm
import yfinance as yf

# ====================== 1. 配置参数 ======================
# 三大事件日期
event_dates = [
    "2024-06-27",  # 第一场辩论
    "2024-07-13",  # 刺杀事件
    "2024-07-21"   # 拜登退选
]
window = 3  # 事件窗口：事件当天前后3天 [-3, +3]
start_date = "2024-06-20"
end_date = "2024-07-31"

# 你的行业ETF列表（和项目etf_hf保持一致）
etf_list = [
    "XLE", "XLF", "XLV", "XLP", "XLY",
    "XLI", "XLK", "XLB", "XLC", "XLU", "XBI"
]

# ====================== 2. 下载6-7月ETF日线收益 ======================
def download_etf_daily(tickers, s, e):
    df_all = pd.DataFrame()
    for tick in tickers:
        data = yf.download(tick, start=s, end=e)
        data["ticker"] = tick
        data["ret"] = data["Adj Close"].pct_change()
        data = data.reset_index()[["Date", "ticker", "ret"]].dropna()
        df_all = pd.concat([df_all, data], ignore_index=True)
    df_all["Date"] = pd.to_datetime(df_all["Date"]).dt.date
    return df_all

etf_daily = download_etf_daily(etf_list, start_date, end_date)

# ====================== 3. 读取Kalshi数据（你本地CSV，6-7月每日Δprob） ======================
# 格式要求CSV三列：Date, prob, delta_prob
# delta_prob = 当日收盘概率 - 前一日收盘概率
kalshi_raw = pd.read_csv("kalshi_june_july.csv")
kalshi_raw["Date"] = pd.to_datetime(kalshi_raw["Date"]).dt.date
kalshi = kalshi_raw[["Date", "delta_prob"]].dropna()

# ====================== 4. 合并ETF收益 + Kalshi概率变动 ======================
df_merge = pd.merge(etf_daily, kalshi, on="Date", how="inner")

# ====================== 5. 只保留三大事件前后窗口数据 ======================
def get_event_window_data(df, events, win):
    keep_dates = set()
    for ed in events:
        ed_dt = pd.to_datetime(ed).date()
        for offset in range(-win, win+1):
            keep_dates.add(ed_dt + pd.Timedelta(days=offset))
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    df_event = df[df["Date"].isin(keep_dates)].copy()
    return df_event

df_event_sample = get_event_window_data(df_merge, event_dates, window)

# ====================== 6. 逐只ETF回归，计算β ======================
beta_result = []
for tick in etf_list:
    sub = df_event_sample[df_event_sample["ticker"] == tick].copy()
    if len(sub) < 10:
        print(f"{tick} 事件样本过少，跳过")
        continue
    # 自变量：delta_prob；因变量：ETF当日收益
    X = sm.add_constant(sub["delta_prob"])
    y = sub["ret"]
    model = sm.OLS(y, X)
    res = model.fit()
    beta = res.params["delta_prob"]
    pval = res.pvalues["delta_prob"]
    beta_result.append({
        "ticker": tick,
        "beta": beta,
        "p_value": pval,
        "significant": 1 if pval < 0.05 else 0
    })

beta_df = pd.DataFrame(beta_result)
# 只保留显著的ETF（大选有敏感度）
beta_significant = beta_df[beta_df["significant"] == 1].copy()

# ====================== 7. 保存β文件，给Step2用 ======================
beta_df.to_csv("etf_beta_full_june_july.csv", index=False)
beta_significant.to_csv("etf_beta_significant_june_july.csv", index=False)

print("==== Step1 完成，输出β结果 ====")
print(beta_df.round(4))

