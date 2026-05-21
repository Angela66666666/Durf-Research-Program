import pandas as pd
import statsmodels.api as sm

df = pd.read_csv("merged_data.csv")

X = df["trump_prob_change"]
Y = df["xle_return"]

X = sm.add_constant(X)

model = sm.OLS(Y, X).fit()

print(model.summary())
