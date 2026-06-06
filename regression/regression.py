"""
Screen prediction-market contracts by how strongly their daily probability
change co-moves (CONTEMPORANEOUSLY) with each Vanguard sector ETF's return:

    etf_return(t) ~ const + prob_change(t)

This is a *screening* step: pairs with strong same-day co-movement are the
candidates for which we later pull high-frequency data to study the actual
lead-lag direction.

Ranking note: for screening we care about co-movement STRENGTH, not the raw
coefficient. In a one-regressor OLS, |std_coef| = sqrt(R^2) = |correlation|,
so we rank by R^2. The raw coef is not comparable across contracts because
each contract's prob_change has a different variance. We also report std_coef
(standardized / comparable) and filter the printed summary to significant
pairs (p < P_THRESHOLD).
"""

import os
import pandas as pd
import statsmodels.api as sm

# ---- config ---------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
CONTRACTS_CSV = os.path.join(HERE, "contract_daily_prices.csv")
ETF_CSV = os.path.join(HERE, "..", "etf_data", "vanguard_sector_etf_total_returns.csv")
OUT_CSV = os.path.join(HERE, "regression_screen_results.csv")

MIN_OBS = 10        # skip pairs with fewer overlapping days than this
P_THRESHOLD = 0.05  # significance cutoff for the printed summary
TOP_N = 30          # how many rows to print

# ---- load -----------------------------------------------------------------
contracts = pd.read_csv(CONTRACTS_CSV, parse_dates=["trade_date"])
etf = pd.read_csv(ETF_CSV, parse_dates=["date"])

# contract probability = yes price in cents / 100
contracts = contracts.dropna(subset=["close_yes_price"])
contracts = contracts.drop_duplicates(subset=["ticker", "trade_date"])
contracts = contracts.sort_values(["ticker", "trade_date"])
contracts["prob"] = contracts["close_yes_price"] / 100.0
# day-over-day change within each contract
contracts["prob_change"] = contracts.groupby("ticker")["prob"].diff()

# wide ETF returns: date -> return per ETF
etf_wide = etf.pivot_table(
    index="date", columns="ticker", values="daily_total_return"
)
etf_tickers = list(etf_wide.columns)


def run_ols(y, x):
    """Fit y ~ const + x and return a dict of stats, or None if degenerate."""
    df = pd.concat({"x": x, "y": y}, axis=1).dropna()
    if len(df) < MIN_OBS or df["x"].nunique() < 2:
        return None
    model = sm.OLS(df["y"], sm.add_constant(df["x"])).fit()
    coef = model.params["x"]
    sx, sy = df["x"].std(), df["y"].std()
    return {
        "n_obs": int(len(df)),
        "coef": coef,
        "abs_coef": abs(coef),
        # standardized (beta) coefficient -> comparable across contracts
        "std_coef": coef * sx / sy if sy > 0 else float("nan"),
        "t_stat": model.tvalues["x"],
        "p_value": model.pvalues["x"],
        "r_squared": model.rsquared,
    }


# ---- regressions ----------------------------------------------------------
rows = []
for ticker, g in contracts.groupby("ticker"):
    title = g["title"].iloc[0]
    sector = g["sector_relevance"].iloc[0]
    g = g.dropna(subset=["prob_change"]).set_index("trade_date").sort_index()
    x = g["prob_change"]
    if x.empty:
        continue
    for etf_ticker in etf_tickers:
        res = run_ols(etf_wide[etf_ticker], x)
        if res is None:
            continue
        res.update(
            {
                "contract_ticker": ticker,
                "contract_title": title,
                "sector_relevance": sector,
                "etf": etf_ticker,
            }
        )
        rows.append(res)

cols = [
    "contract_ticker", "etf", "n_obs",
    "coef", "abs_coef", "std_coef", "t_stat", "p_value", "r_squared",
    "sector_relevance", "contract_title",
]
# rank by co-movement strength (R^2), not raw |coef|
results = pd.DataFrame(rows)[cols].sort_values("r_squared", ascending=False)
results.to_csv(OUT_CSV, index=False)

print(f"Ran {len(results)} regressions (MIN_OBS={MIN_OBS}).")
print(f"Full results saved to: {OUT_CSV}\n")

sig = results[results["p_value"] < P_THRESHOLD]
print("=" * 80)
print(f"Top {TOP_N} significant pairs (p < {P_THRESHOLD}), ranked by R^2 "
      f"(co-movement strength)  ({len(sig)} significant of {len(results)} total)")
print("=" * 80)
show = ["contract_ticker", "etf", "n_obs", "coef", "std_coef",
        "t_stat", "p_value", "r_squared", "contract_title"]
with pd.option_context(
    "display.max_columns", None, "display.width", 200, "display.max_colwidth", 45
):
    print(sig.head(TOP_N)[show].to_string(index=False))
