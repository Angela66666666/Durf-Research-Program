import pandas as pd
import numpy as np
import statsmodels.api as sm

df_result = pd.read_csv("./prediction-market-analysis/regression_screen_results.csv")
sig_pairs = df_result[df_result["p_value"] < 0.05].copy()
sig_pairs = sig_pairs.sort_values("r_squared", ascending=False)

print("pairs length：", len(sig_pairs))

df_contract = pd.read_csv("prediction-market-analysis/contract_daily_prices.csv")
df_etf = pd.read_csv("prediction-market-analysis/vanguard_sector_etf_total_returns.csv")

df_contract["date"] = pd.to_datetime(df_contract["trade_date"])
df_etf["date"] = pd.to_datetime(df_etf["date"])

df_contract["prob"] = df_contract["close_yes_price"] / 100
df_contract["prob_change"] = df_contract.groupby("ticker")["prob"].diff()

def lead_lag_reg(y, x, lag_num):
    df = pd.DataFrame({"y": y, "x": x})
    df["x_lag"] = df["x"].shift(lag_num)
    df = df.dropna()
    if len(df) < 10:
        return None
    X = sm.add_constant(df["x_lag"])
    return sm.OLS(df["y"], X).fit()

output = []

for _, row in sig_pairs.iterrows():
    contract = row["contract_ticker"]
    etf = row["etf"]
    title = row["contract_title"]

    c = df_contract[df_contract["ticker"] == contract][["date", "prob_change"]].dropna()
    e = df_etf[df_etf["ticker"] == etf][["date", "daily_total_return"]].dropna()

    merged = pd.merge(c, e, on="date", how="inner").dropna()
    if len(merged) < 20:
        continue

    x = merged["prob_change"]
    y = merged["daily_total_return"]

    m1 = lead_lag_reg(y, x, 1)
    m2 = lead_lag_reg(x, y, 1)

    if m1 is None or m2 is None:
        continue

    output.append({
        "contract": contract,
        "contract_title": title,
        "etf": etf,
        "n_days": len(merged),
        "r2_sync": row["r_squared"],

        "contract_lead_coef": m1.params["x_lag"],
        "contract_lead_p": m1.pvalues["x_lag"],

        "etf_lead_coef": m2.params["x_lag"],
        "etf_lead_p": m2.pvalues["x_lag"],
    })


final = pd.DataFrame(output)
final.to_csv("LEAD_LAG_FINAL_RESULT.csv", index=False)

print("LEAD_LAG_FINAL_RESULT.csv printed")