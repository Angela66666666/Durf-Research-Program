"""
step1_election_beta.py
================================================================================
WHAT THIS FILE DOES
  The Kalshi-only version of Step 1: estimate each of the eleven Vanguard sector
  ETFs' loading on the election factor,

      r_{i,t} = a_i + beta_i * dP_t + e_{i,t}

  where dP_t is the daily change in P(Trump wins) and r_{i,t} is ETF i's daily
  total return. It also builds the minimum-variance mimicking portfolio and
  reports its R^2.

WHY IT IS KEPT
  This specification does not identify the betas. It is retained as the record of
  what a Kalshi-only design produces, and belongs in the paper's appendix. The
  specification actually used is step1_step2_polymarket_beta_and_weights.py.

  Result: no beta reaches p < 0.05, the joint F-test gives p = 0.35, and the
  leave-one-out out-of-sample R^2 is -2.52 (worse than predicting the mean).
  Through October, P(Trump) drifts slowly from 0.50 to 0.63 with no single-day
  jump, so nineteen daily observations carry almost no identifying variation.

CHOICE OF CONTRACT
  P(Trump wins) can only come from a binary win/lose contract. On Kalshi the only
  one is PRES-2024-DJT. Electoral-vote-count contracts are not monotone in
  P(Trump wins): KXECDJT270 pays only if Trump wins by exactly 270-268, and on
  2024-11-06, the day Trump actually won 312-226, PRES-2024-DJT went from 95c to
  97c while KXECDJT270 collapsed from 38c to 1c.

IDENTIFICATION VS TEST WINDOWS (avoiding circularity)
  IDENT: 2024-10-04 to 2024-10-31   estimate beta. PRES-2024-DJT's first trade is
                                    2024-10-04: Kalshi could list presidential
                                    contracts only after the D.C. Circuit denied
                                    the CFTC's motion for a stay on 2024-10-02.
  SIGMA: 2024-09-04 to 2024-10-31   estimate the covariance matrix.
  TEST : from 2024-11-01            where Steps 3 and 4 would run.
  The three do not overlap, so neither beta nor Sigma carries information from the
  test period.

INPUTS
  prediction-market-analysis/data/kalshi/trades/trades_*.parquet
  etf_data/vanguard_sector_etf_total_returns.csv

OUTPUTS (written next to this file)
  etf_election_beta.csv        ticker, beta, se, t_stat, p_value, n_obs
  etf_mimic_diagnostics.txt    the mimicking portfolio's R^2 and weight checks
"""
import os
import numpy as np
import pandas as pd
import statsmodels.api as sm
import duckdb

# ---------------- configuration ----------------
CONTRACT = "PRES-2024-DJT"        # Kalshi's only binary "Trump wins the election" contract
IDENT_START, IDENT_END = "2024-10-04", "2024-10-31"   # beta
SIGMA_START, SIGMA_END = "2024-09-04", "2024-10-31"   # Sigma, also before the test window

ETFS = ["VAW", "VCR", "VDC", "VDE", "VFH", "VGT", "VHT", "VIS", "VNQ", "VOX", "VPU"]

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TRADES = os.path.join(ROOT, "prediction-market-analysis", "data", "kalshi", "trades", "trades_*.parquet")
ETF_CSV = os.path.join(ROOT, "etf_data", "vanguard_sector_etf_total_returns.csv")


# ---------------- 1. the daily election probability ----------------
def load_prob(ticker, d0, d1):
    """The last trade of each ET calendar day, as that day's closing probability.
    ET throughout, consistent with the rest of the project."""
    con = duckdb.connect()
    q = f"""
    SELECT (created_time AT TIME ZONE 'America/New_York')::date AS date,
           arg_max(yes_price, created_time) / 100.0             AS prob
    FROM   read_parquet('{TRADES}')
    WHERE  ticker = '{ticker}'
      AND  (created_time AT TIME ZONE 'America/New_York')::date BETWEEN DATE '{d0}' AND DATE '{d1}'
    GROUP  BY 1 ORDER BY 1
    """
    df = con.execute(q).df()
    con.close()
    return df.set_index(pd.to_datetime(df["date"]))["prob"]


# ---------------- 2. ETF daily returns ----------------
def load_etf_returns(d0, d1):
    d = pd.read_csv(ETF_CSV, parse_dates=["date"])
    d = d[(d["date"] >= d0) & (d["date"] <= d1) & d["ticker"].isin(ETFS)]
    return d.pivot(index="date", columns="ticker", values="daily_total_return")[ETFS]


# ---------------- 3. alignment ----------------
def align(prob, ret):
    """Put the Kalshi probability on the ETF trading-day grid.

    Kalshi trades on weekends; the ETFs do not. Forward-filling onto the ETF grid
    before differencing pairs a Friday-to-Monday ETF return with a dprob that
    accumulates across the weekend, so nothing is lost. Only past quotes are
    forward-filled and nothing is back-filled, so there is no look-ahead.
    """
    p = prob.reindex(prob.index.union(ret.index)).ffill().reindex(ret.index)
    dprob = p.diff()
    return ret.join(dprob.rename("dprob")).dropna()


# ---------------- 4. one regression per ETF ----------------
def estimate_betas(df):
    """All eleven ETFs are kept; none is dropped for statistical insignificance.
    Selecting on significance induces a winner's curse, and the quantity of
    interest is the R^2 of the portfolio as a whole."""
    X = sm.add_constant(df[["dprob"]])
    rows = []
    for e in ETFS:
        m = sm.OLS(df[e], X).fit(cov_type="HAC", cov_kwds={"maxlags": 1})
        rows.append({"ticker": e, "beta": m.params["dprob"], "se": m.bse["dprob"],
                     "t_stat": m.tvalues["dprob"], "p_value": m.pvalues["dprob"],
                     "n_obs": int(m.nobs)})
    return pd.DataFrame(rows)


# ---------------- 5. the mimicking portfolio and its R^2 ----------------
def mimic_portfolio(beta_df, sigma_ret, df_ident):
    b = beta_df["beta"].values.reshape(-1, 1)
    Sigma = sigma_ret[ETFS].dropna().cov().values

    w_raw = np.linalg.inv(b.T @ np.linalg.inv(Sigma) @ b) * (np.linalg.inv(Sigma) @ b)
    w = w_raw - w_raw.mean()                 # dollar neutrality: sum(w) = 0
    w = w / float(w.T @ b)                   # unit election exposure: w'beta = 1
                                             # (de-meaning destroys the unit exposure that
                                             #  the closed form carries, so rescale)

    basket = df_ident[ETFS].values @ w       # the basket's daily return over the ident window
    m = sm.OLS(df_ident["dprob"].values, sm.add_constant(basket)).fit()
    return w.flatten(), float(m.rsquared), float(w.sum()), float((w.T @ b).item())


def honest_r2(df_ident):
    """The basket's in-sample R^2 badly overstates its explanatory power: the
    weights are fitted on the same sample, and w is proportional to Sigma^-1 beta,
    which makes the basket equivalent to projecting dprob onto all eleven ETFs.
    With n = 19 and k = 11 that projection fits almost by construction, so we also
    report:
      - the adjusted R^2 (penalising the parameter count)
      - the joint F-test (do the eleven ETFs together explain dprob at all)
      - a leave-one-out out-of-sample R^2 (<0 means worse than predicting the mean)
    """
    X, y = df_ident[ETFS].values, df_ident["dprob"].values
    m = sm.OLS(y, sm.add_constant(X)).fit()
    err = np.array([y[i] - sm.OLS(y[np.arange(len(y)) != i],
                                  sm.add_constant(X[np.arange(len(y)) != i])
                                  ).fit().predict(np.r_[1, X[i]])[0] for i in range(len(y))])
    r2_oos = 1 - (err ** 2).sum() / ((y - y.mean()) ** 2).sum()
    return float(m.rsquared), float(m.rsquared_adj), float(m.f_pvalue), float(r2_oos)


def main():
    prob = load_prob(CONTRACT, IDENT_START, IDENT_END)
    ret_ident = load_etf_returns(IDENT_START, IDENT_END)
    ret_sigma = load_etf_returns(SIGMA_START, SIGMA_END)

    df = align(prob, ret_ident)
    print(f"contract {CONTRACT}   probability range [{prob.min():.2f}, {prob.max():.2f}]   "
          f"{len(prob)} Kalshi trading days")
    print(f"identification window {IDENT_START} to {IDENT_END}   {len(df)} usable observations")
    print(f"covariance window     {SIGMA_START} to {SIGMA_END}   "
          f"{len(ret_sigma.dropna())} observations\n")

    beta_df = estimate_betas(df)
    print(beta_df.round(4).to_string(index=False))

    w, r2, wsum, wexp = mimic_portfolio(beta_df, ret_sigma, df)
    beta_df["mimic_weight"] = w

    out = os.path.join(HERE, "etf_election_beta.csv")
    beta_df[["ticker", "beta", "se", "t_stat", "p_value", "n_obs"]].to_csv(out, index=False)

    r2_in, r2_adj, fp, r2_oos = honest_r2(df)
    diag = (f"contract              = {CONTRACT}\n"
            f"ident window          = {IDENT_START} to {IDENT_END}   (n = {len(df)}, k = 11)\n"
            f"sigma window          = {SIGMA_START} to {SIGMA_END}\n"
            f"sum(w)                = {wsum:.2e}   (dollar neutral, should be 0)\n"
            f"w' beta               = {wexp:.6f}   (unit election exposure, should be 1)\n"
            f"\n--- how well the basket tracks the election factor ---\n"
            f"mimicking R^2         = {r2:.4f}    (the basket, in-sample -- overstates)\n"
            f"full-panel R^2        = {r2_in:.4f}    (dprob on all eleven ETFs, in-sample)\n"
            f"adjusted R^2          = {r2_adj:.4f}    (penalising the eleven parameters)\n"
            f"joint F-test p        = {fp:.4f}    (do the eleven ETFs jointly explain dprob)\n"
            f"leave-one-out OOS R^2 = {r2_oos:.4f}    (<0 = worse than predicting the mean)\n"
            f"\n--- betas ---\n"
            f"max |beta|            = {beta_df.beta.abs().max():.4f}\n"
            f"max |t|               = {beta_df.t_stat.abs().max():.4f}\n"
            f"betas with p<0.05     = {(beta_df.p_value < 0.05).sum()} / 11\n"
            f"\nConclusion: a daily window of n = 19 cannot identify the election beta.\n"
            f"Through October, P(Trump) drifts from 0.50 to 0.63 with no single-day shock.\n"
            f"The three exogenous event dates (6/27, 7/13, 7/21) do carry identifying\n"
            f"variation, but Kalshi had no presidential contract then: PRES-2024-DJT's\n"
            f"first trade is 2024-10-04, two days after the D.C. Circuit denied the CFTC's\n"
            f"motion for a stay pending appeal. See step1_step2_polymarket_beta_and_weights.py.\n")
    with open(os.path.join(HERE, "etf_mimic_diagnostics.txt"), "w") as f:
        f.write(diag)
    print("\n" + diag)
    print("betas ->", out)


if __name__ == "__main__":
    main()
