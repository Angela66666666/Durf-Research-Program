import pandas as pd
import numpy as np
import statsmodels.api as sm

# ==================================================
# LOAD DATA
# ==================================================

contracts = pd.read_csv("contract_daily_prices.csv")
etf = pd.read_csv("vanguard_sector_etf_total_returns.csv")

# ==================================================
# DATE FORMAT
# ==================================================

contracts['trade_date'] = pd.to_datetime(
    contracts['trade_date']
)

etf['date'] = pd.to_datetime(
    etf['date']
)

# ==================================================
# CREATE SHOCK VARIABLE
# Information shock proxy
# ==================================================

contracts['shock'] = (
    contracts['close_yes_price']
    - contracts['open_yes_price']
)

# Optional: log volume
contracts['log_volume'] = np.log1p(
    contracts['daily_volume']
)

# ==================================================
# MERGE DATA
# IMPORTANT:
# This assumes sector_relevance matches ETF ticker
# Example:
# VGT, VFH, VDE...
# ==================================================

merged = pd.merge(
    contracts,
    etf,
    left_on=['sector_relevance', 'trade_date'],
    right_on=['ticker', 'date'],
    how='inner'
)

print("Merged observations:", len(merged))

# ==================================================
# CLEAN DATA
# ==================================================

merged = merged.dropna(
    subset=['shock', 'daily_total_return']
)

# ==================================================
# BASIC REGRESSION
# ETF_return_t = alpha + beta * shock_t + error
# ==================================================

X = merged[['shock']]
X = sm.add_constant(X)

y = merged['daily_total_return']

model = sm.OLS(y, X).fit()

print("\n========== BASIC REGRESSION ==========")
print(model.summary())

# ==================================================
# LEAD-LAG REGRESSION
# ETF_return_(t+1) = alpha + beta * shock_t + error
# ==================================================

merged = merged.sort_values(
    ['ticker_y', 'date']
)

merged['next_day_return'] = (
    merged.groupby('ticker_y')['daily_total_return']
    .shift(-1)
)

lead_data = merged.dropna(
    subset=['next_day_return']
)

X2 = lead_data[['shock']]
X2 = sm.add_constant(X2)

y2 = lead_data['next_day_return']

lead_model = sm.OLS(y2, X2).fit()

print("\n========== LEAD-LAG REGRESSION ==========")
print(lead_model.summary())