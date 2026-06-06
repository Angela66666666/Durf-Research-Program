import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.api import VAR

df_result = pd.read_csv("./prediction-market-analysis/regression_screen_results.csv")
sig_pairs = df_result[df_result["p_value"] < 0.05].copy()

df_contract = pd.read_csv("prediction-market-analysis/contract_daily_prices.csv")
df_etf = pd.read_csv("prediction-market-analysis/vanguard_sector_etf_total_returns.csv")

df_contract["date"] = pd.to_datetime(df_contract["trade_date"])
df_etf["date"] = pd.to_datetime(df_etf["date"])

df_contract["prob"] = df_contract["close_yes_price"] / 100
df_contract["prob_change"] = df_contract.groupby("ticker")["prob"].diff()


best_pair = sig_pairs.iloc[0]
contract = best_pair["contract_ticker"]
etf = best_pair["etf"]

print("✅  selected for VAR:")
print("Contract:", contract)
print("ETF:", etf)


c_data = df_contract[df_contract["ticker"] == contract][["date", "prob_change"]].dropna()
e_data = df_etf[df_etf["ticker"] == etf][["date", "daily_total_return"]].dropna()


data = pd.merge(c_data, e_data, on="date").dropna()
data = data.set_index("date")  


model = VAR(data)
results = model.fit(maxlags=2) 

print("\n" + "="*50)
print("📊 VAR MODEL RESULTS")
print("="*50)
print(results.summary())

print("\n" + "="*50)
print("🔍 GRANGER CAUSALITY TEST")
print("="*50)
granger = results.test_causality('daily_total_return', 'prob_change')
print("Granger Test (Contract → ETF):")
print("P-value:", granger.pvalue)
print("Significant:", granger.pvalue < 0.05)

with open("VAR_RESULTS.txt", "w") as f:
    f.write(str(results.summary()))
    f.write(f"\nGranger p-value: {granger.pvalue}")
    f.write(f"\nSignificant: {granger.pvalue < 0.05}")

print("VAR_RESULTS.txt printed")