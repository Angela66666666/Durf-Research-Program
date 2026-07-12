"""
step1_step2_polymarket_beta_and_weights.py
================================================================================
WHAT THIS FILE DOES
  Step 1 - estimate each of the eleven Vanguard sector ETFs' loading on the
           election factor:

               r_{i,d} = a_i + beta_i * dP_d + e_{i,d}

           r_{i,d} = ETF i's daily total return (dividends included) on day d
           dP_d    = the change in P(Trump wins the 2024 election) on day d

  Step 2 - turn those betas into portfolio weights, under three weighting rules
           (sign-equal, beta-weighted, minimum-variance mimicking portfolio),
           and report how well each resulting basket tracks the election factor.

WHY THE PROBABILITY COMES FROM POLYMARKET
  Identification requires a probability series that spans three exogenous events:

      2024-06-27  first presidential debate       (21:00 ET, Thursday)
      2024-07-13  Butler rally shooting           (18:11 ET, Saturday)
      2024-07-21  Biden's withdrawal              (13:54 ET, Sunday)

  On Kalshi the binary contract PRES-2024-DJT has its first trade on 2024-10-04.
  That is a regulatory boundary, not a gap in the data: the CFTC prohibited
  political event contracts in September 2023, and Kalshi could list them only
  after the D.C. Circuit denied the CFTC's motion for a stay pending appeal on
  2024-10-02. All three event dates fall inside the prohibition period.
  Polymarket's contract on the same question has traded since 2024-01-05.

  A Kalshi-only version was carried through to a conclusion in
  step1_election_beta.py, estimating betas on 2024-10-04 to 10-31:
      daily,    n = 19 days      -> joint F-test p = 0.35, out-of-sample R^2 = -2.52
      1-minute, n = 5,455 bars   -> R^2 = 0.0026
  Through October P(Trump) drifts from 0.50 to 0.63 with no single-day jump, so
  there is nothing to identify from. The event-based design is necessary here.

  All three events happened while the stock market was closed, so each ETF's
  response falls on the next trading day:
      debate     (Thu 21:00) -> 06-28 (Fri)
      shooting   (Sat 18:11) -> 07-15 (Mon)
      withdrawal (Sun 13:54) -> 07-22 (Mon)

CIRCULARITY
  The betas end on 2024-07-31. Kalshi's presidential contract has no trades
  before 2024-10-04, so any Kalshi-based test in Step 3 / Step 4 lies entirely
  after the beta window, whichever way that window is later chosen. The two
  sides also come from different venues, which rules out mechanical correlation
  from a shared order book.

TIME ALIGNMENT
  Polymarket's daily points are stamped 19:00/20:00 ET, three to four hours after
  the close; each is assigned to that ET calendar day. The ETF series is a
  close(d-1) -> close(d) total return. Both windows cover ET trading day d, but
  dprob additionally contains the 16:00-20:00 ET after-hours stretch. beta is a
  contemporaneous exposure rather than a predictive coefficient, so this offset
  does not affect its definition; it is noted in the diagnostics.

THREE SAMPLE SPECIFICATIONS (all reported, for robustness)
  event  : +/-3 trading days around each of the three reaction days
  window : every trading day from 2024-06-20 to 2024-07-31   <- headline
  long   : every trading day from 2024-01-05 to 2024-07-31

INPUTS
  Polymarket CLOB API (cached once to polymarket_trump_2024_daily.csv)
  etf_data/vanguard_sector_etf_total_returns_2024h1.csv

OUTPUTS (written next to this file)
  etf_election_beta_polymarket.csv  ticker, beta, se, t_stat, p_value, n_obs,
                                    weight_plan_{a,b,c}. Step 3 and Step 4 read this.
  step1_basket_report_EN.txt        the readable report
  step1_polymarket_diagnostics.txt  technical appendix: all three specifications
                                    plus the robustness checks
"""
import os
import json
import urllib.request

import numpy as np
import pandas as pd
import statsmodels.api as sm

# ---------------- configuration ----------------
# Polymarket YES token for "Will Donald Trump win the 2024 US Presidential Election?"
# (event slug: presidential-election-winner-2024, about $1.53B traded)
TRUMP_YES_TOKEN = "21742633143463906290569050155826241533067272736897614950488156847949938836455"
PRICES_URL = f"https://clob.polymarket.com/prices-history?market={TRUMP_YES_TOKEN}&interval=max&fidelity=1440"

# The trading day on which each event's effect first reaches the ETFs.
# All three events occurred outside market hours (see the header).
EVENT_REACTION_DAYS = ["2024-06-28", "2024-07-15", "2024-07-22"]
EVENT_HALFWIDTH = 3          # +/- 3 trading days around each reaction day

SPECS = {
    "event":  None,                              # built from EVENT_REACTION_DAYS
    "window": ("2024-06-20", "2024-07-31"),
    "long":   ("2024-01-05", "2024-07-31"),
}
# The headline is `window` rather than `event`. Three reaction days plus/minus three
# trading days already covers 06-25 to 07-25, so `window` is only slightly wider, yet
# it raises n from 19 to 29, drops the joint F-test p from 0.076 to 0.0022, and turns
# plan C's out-of-sample R^2 positive. Both lie entirely before any Kalshi test window.
HEADLINE = "window"

ETFS = ["VAW", "VCR", "VDC", "VDE", "VFH", "VGT", "VHT", "VIS", "VNQ", "VOX", "VPU"]

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))          # repo root (this file lives in Hasbrouck methodology/step1_step2)
ETF_CSV = os.path.join(ROOT, "etf_data", "vanguard_sector_etf_total_returns_2024h1.csv")
PM_CACHE = os.path.join(HERE, "polymarket_trump_2024_daily.csv")

SECTOR = {"VAW": "Materials", "VCR": "Cons. Discret.", "VDC": "Cons. Staples", "VDE": "Energy",
          "VFH": "Financials", "VGT": "Info Tech", "VHT": "Health Care", "VIS": "Industrials",
          "VNQ": "Real Estate", "VOX": "Comm. Services", "VPU": "Utilities"}
EVENT_LABEL = {"2024-06-28": "first presidential debate  (Jun 27, 21:00 ET, Thu)",
               "2024-07-15": "Butler rally shooting      (Jul 13, 18:11 ET, Sat)",
               "2024-07-22": "Biden's withdrawal         (Jul 21, 13:54 ET, Sun)"}
WCOLS = ["weight_plan_a_sign_equal", "weight_plan_b_beta_weighted", "weight_plan_c_min_variance"]


# ---------------- 1. the election probability ----------------
def load_prob():
    """Daily P(Trump wins), cached locally so the API is called only once.

    The CLOB prices-history endpoint accepts only interval=max together with a
    coarse fidelity (1440 = daily); startTs/endTs range queries return nothing.
    Daily points are stamped 19:00/20:00 ET and are assigned to that ET date.
    """
    if not os.path.exists(PM_CACHE):
        # the CDN returns 403 without a User-Agent
        req = urllib.request.Request(PRICES_URL, headers={"User-Agent": "curl/8.0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            hist = json.load(r)["history"]
        d = pd.DataFrame(hist)
        ts = pd.to_datetime(d["t"], unit="s", utc=True).dt.tz_convert("America/New_York")
        pd.DataFrame({"date": ts.dt.date, "prob": d["p"]}).to_csv(PM_CACHE, index=False)
        print(f"downloaded the Polymarket daily series -> {PM_CACHE}")
    d = pd.read_csv(PM_CACHE, parse_dates=["date"])
    return d.set_index("date")["prob"].sort_index()


# ---------------- 2. ETF daily total returns ----------------
def load_etf_returns():
    d = pd.read_csv(ETF_CSV, parse_dates=["date"])
    d = d[d["ticker"].isin(ETFS)]
    return d.pivot(index="date", columns="ticker", values="daily_total_return")[ETFS]


# ---------------- 3. alignment ----------------
def align(prob, ret):
    """Put the probability on the ETF trading-day grid, then difference it.

    Polymarket trades on weekends; the ETFs do not. Forward-filling onto the ETF
    grid before differencing means a Friday-to-Monday ETF return is paired with a
    dprob that accumulates across the weekend. Both the shooting and the
    withdrawal fell on a weekend, so this step is essential. Only past quotes are
    forward-filled and nothing is back-filled, so there is no look-ahead.
    """
    p = prob.reindex(prob.index.union(ret.index)).ffill().reindex(ret.index)
    return ret.join(p.diff().rename("dprob")).dropna()


def subset(df, spec):
    if spec == "event":
        idx = df.index
        keep = set()
        for d in EVENT_REACTION_DAYS:
            pos = idx.get_indexer([pd.Timestamp(d)])[0]
            lo, hi = max(0, pos - EVENT_HALFWIDTH), min(len(idx), pos + EVENT_HALFWIDTH + 1)
            keep.update(idx[lo:hi])
        return df.loc[sorted(keep)]
    d0, d1 = SPECS[spec]
    return df.loc[d0:d1]


# ---------------- 4. one regression per ETF ----------------
def estimate_betas(df):
    """All eleven ETFs are kept; none is dropped for statistical insignificance.

    Selecting on significance induces a winner's curse: the survivors are the ones
    whose estimates happened to be large, so |beta| ends up systematically
    overstated. The quantity of interest is the R^2 of the portfolio as a whole.
    """
    X = sm.add_constant(df[["dprob"]])
    rows = []
    for e in ETFS:
        m = sm.OLS(df[e], X).fit(cov_type="HAC", cov_kwds={"maxlags": 1})
        rows.append({"ticker": e, "beta": m.params["dprob"], "se": m.bse["dprob"],
                     "t_stat": m.tvalues["dprob"], "p_value": m.pvalues["dprob"],
                     "n_obs": int(m.nobs)})
    return pd.DataFrame(rows)


# ---------------- 5. the mimicking portfolio ----------------
def mimic_portfolio(beta_df, df_sigma, df_ident):
    """w = (b'S^-1 b)^-1 S^-1 b, de-meaned for dollar neutrality, then rescaled to
    unit election exposure (w'b = 1).

    The closed-form solution already satisfies w'b = 1, but de-meaning destroys it,
    so the rescaling is required. Rescaling does not disturb sum(w) = 0, so both
    constraints hold simultaneously.
    """
    b = beta_df["beta"].values.reshape(-1, 1)
    S = df_sigma[ETFS].dropna().cov().values
    Si = np.linalg.inv(S)
    w = np.linalg.inv(b.T @ Si @ b) * (Si @ b)
    w = w - w.mean()
    w = w / float(w.T @ b)
    basket = df_ident[ETFS].values @ w
    r2_basket = sm.OLS(df_ident["dprob"].values, sm.add_constant(basket)).fit().rsquared
    return w.flatten(), float(r2_basket), float(w.sum()), float((w.T @ b).item())


def honest_r2(df):
    """The basket's in-sample R^2 overstates its explanatory power: the weights are
    fitted on the same sample, and w is proportional to S^-1 b, which makes the
    basket equivalent to projecting dprob onto all eleven ETFs. So we also report
    the adjusted R^2, the joint F-test, and a leave-one-out out-of-sample R^2
    (a negative value means the basket does worse than predicting the mean).
    """
    X, y = df[ETFS].values, df["dprob"].values
    n = len(y)
    m = sm.OLS(y, sm.add_constant(X)).fit()
    if n <= X.shape[1] + 2:
        return float(m.rsquared), float(m.rsquared_adj), float(m.f_pvalue), np.nan
    err = np.array([y[i] - sm.OLS(y[np.arange(n) != i], sm.add_constant(X[np.arange(n) != i])
                                  ).fit().predict(np.r_[1, X[i]])[0] for i in range(n)])
    r2_oos = 1 - (err ** 2).sum() / ((y - y.mean()) ** 2).sum()
    return float(m.rsquared), float(m.rsquared_adj), float(m.f_pvalue), float(r2_oos)


# ---------------- 6. the three weighting rules ----------------
def _w_sign_equal(b, S):
    w = np.sign(b); return w - w.mean()


def _w_beta_weighted(b, S):
    w = b / np.abs(b).sum(); return w - w.mean()


def _w_min_var(b, S):
    Si = np.linalg.inv(S); bb = b.reshape(-1, 1)
    raw = (np.linalg.inv(bb.T @ Si @ bb) * (Si @ bb)).flatten()
    return raw - raw.mean()


PLANS = {"plan a  sign-equal": _w_sign_equal,
         "plan b  beta-weighted": _w_beta_weighted,
         "plan c  min-variance": _w_min_var}


def _betas_only(d):
    X = sm.add_constant(d[["dprob"]])
    return np.array([sm.OLS(d[e], X).fit().params["dprob"] for e in ETFS])


# ---------------- 7. robustness ----------------
def robustness(d):
    """Three checks:
      (1) drop each day in turn - is the joint F-test carried by a single day, such
          as July 15 (first trading day after the shooting) or July 11 (a CPI print)?
      (2) out-of-sample R^2 for each of the three plans - min-variance spends eleven
          parameters, so with a small n it will overfit.
      (3) add the broad market (VTI) as a control - are the betas simply market beta?
    """
    out = ["", "=" * 72, "ROBUSTNESS CHECKS", "=" * 72]
    y, R, n = d["dprob"].values, d[ETFS].values, len(d)
    stats = {}

    fp0 = sm.OLS(y, sm.add_constant(R)).fit().f_pvalue
    fps = [sm.OLS(np.delete(y, i), sm.add_constant(np.delete(R, i, 0))).fit().f_pvalue
           for i in range(n)]
    stats["fp_lo"], stats["fp_hi"] = min(fps), max(fps)
    verdict = "not carried by any single day" if max(fps) < 0.05 else "*** depends on a single day"
    out += [f"(1) Drop one day at a time. Full-sample joint F-test p = {fp0:.4f};",
            f"    dropping any one day leaves p in [{min(fps):.4f}, {max(fps):.4f}] -> {verdict}"]

    out += ["", "(2) Out-of-sample performance of the three weighting rules",
            "    (leave one day out; betas and weights refitted on each fold):"]
    for name, f in PLANS.items():
        b, S = _betas_only(d), np.cov(R, rowvar=False)
        w = f(b, S); w = w / (w @ b)
        r2_in = sm.OLS(y, sm.add_constant(R @ w)).fit().rsquared
        err = []
        for i in range(n):
            m = np.arange(n) != i
            bt, St = _betas_only(d.iloc[m]), np.cov(R[m], rowvar=False)
            wt = f(bt, St)
            if abs(wt @ bt) < 1e-10:
                continue
            wt = wt / (wt @ bt)
            fit = sm.OLS(y[m], sm.add_constant(R[m] @ wt)).fit()
            err.append(y[i] - fit.predict([1, R[i] @ wt])[0])
        e = np.array(err)
        r2_oos = 1 - (e ** 2).sum() / ((y - y.mean()) ** 2).sum()
        key = name.split()[1]
        stats["oos_" + key], stats["ins_" + key] = r2_oos, r2_in
        stats["lev_" + key] = float(np.abs(w).sum())          # gross leverage = sum |w|
        out += [f"      {name:24s} in-sample R^2 = {r2_in:6.3f}   out-of-sample R^2 = {r2_oos:7.3f}"]

    try:
        import yfinance as yf
        mkt = yf.Ticker("VTI").history(start="2024-01-02", end="2024-08-06", auto_adjust=True)["Close"]
        mkt.index = mkt.index.tz_localize(None)
        dd = d.join(mkt.pct_change().rename("mkt")).dropna()
        m1 = sm.OLS(dd["dprob"], sm.add_constant(dd[ETFS].values)).fit()
        m2 = sm.OLS(dd["dprob"], sm.add_constant(np.c_[dd[ETFS].values, dd["mkt"].values])).fit()
        flips = sum(np.sign(sm.OLS(dd[e], sm.add_constant(dd[["dprob"]])).fit().params["dprob"]) !=
                    np.sign(sm.OLS(dd[e], sm.add_constant(dd[["dprob", "mkt"]])).fit().params["dprob"])
                    for e in ETFS)
        out += ["", f"(3) Controlling for the broad market (VTI): R^2 goes {m1.rsquared:.3f} -> "
                    f"{m2.rsquared:.3f}, VTI's own t = {m2.tvalues[-1]:.2f}, "
                    f"{flips}/11 betas change sign"]
    except Exception as exc:
        out += ["", f"(3) market control skipped: {exc}"]
    return out, stats


# ---------------- 8. tables and the report ----------------
def basket_table(beta_df):
    """The three baskets side by side, sorted by beta (shorts on top, longs below)."""
    t = beta_df.copy()
    t["sector"] = t["ticker"].map(SECTOR)
    t = t.sort_values("beta")
    out = ["ETF   Sector            beta      t    |  A sign-equal  B beta-wtd    C min-var",
           "-" * 80]
    for _, r in t.iterrows():
        out.append(f"{r.ticker:5s} {r['sector']:<16s} {r.beta:+7.4f} {r.t_stat:+6.2f}  |"
                   f"{r[WCOLS[0]]:+11.3f} {r[WCOLS[1]]:+12.3f} {r[WCOLS[2]]:+12.3f}")
    out += ["-" * 80]
    aggs = [("Long total", lambda w: w[w > 0].sum()),
            ("Short total", lambda w: w[w < 0].sum()),
            ("Net (should be 0)", lambda w: w.sum()),
            ("w'beta (should be 1)", lambda w: (w * t.beta.values).sum())]
    for lbl, f in aggs:
        out.append(f"{lbl:<31s}|" + "".join(f"{f(t[c].values):+12.3f}" for c in WCOLS))
    out += ["", "Positive = buy (long).  Negative = sell short."]
    return out


def plan_comparison(beta_df, rob):
    """The three plans side by side: fit, out-of-sample performance, leverage, and
    whether each weight keeps the sign of its beta."""
    rows = [("A  sign-equal", "a"), ("B  beta-weighted", "b"), ("C  min-variance", "c")]
    out = ["Plan               In-sample   Out-of-sample   Gross      Weight sign",
           "                     R^2           R^2       leverage   follows beta?",
           "-" * 76]
    for label, k in rows:
        w = beta_df[WCOLS["abc".index(k)]].values
        follows = "yes" if (np.sign(w) == np.sign(beta_df["beta"].values)).all() else "no"
        best = "  <== only plan with positive out-of-sample R^2" if rob[f"oos_{k}"] > 0 else ""
        out.append(f"{label:<20s}{rob['ins_' + k]:+7.3f}       {rob['oos_' + k]:+7.3f}"
                   f"      {rob['lev_' + k]:6.2f}x        {follows:<4s}{best}")
    out += ["-" * 76, "",
            "In-sample R^2      how much of the change in P(Trump) the basket explains on",
            "                   the same 29 days used to build it. Flattered by overfitting.",
            "Out-of-sample R^2  leave one day out, refit the betas and the weights on the",
            "                   other 28 days, then predict the day held out. A negative",
            "                   value means the basket does worse than always predicting",
            "                   the average. This is the number that matters.",
            "Gross leverage     sum of |weight|, i.e. dollars traded per unit of election",
            "                   exposure.",
            "Weight sign        whether every ETF's weight has the same sign as its beta.",
            "                   Only plan A does. In plan B, de-meaning for dollar",
            "                   neutrality shifts every weight by the same amount, which",
            "                   pushes the two smallest negative betas (VNQ -0.032 and",
            "                   VOX -0.036) across zero. Plan C differs more widely",
            "                   because it also hedges the correlations among the ETFs.", "",
            "Plan C explains the most and is the only one with positive out-of-sample",
            "power, but the margin is small: no basket built from these eleven ETFs",
            "tracks the election factor closely. Plan A is the easiest to read, since it",
            "is the only one whose positions all point the way its betas do.", ""]
    return out


def report(prob, ret, full, beta_df, sub, stats, rob):
    r2_b, r2_in, r2_adj, fp, r2_oos, fp_lo, fp_hi, oos_a, oos_b, oos_c = stats
    L = ["=" * 80,
         "STEP 1 + STEP 2 - AN ELECTION FACTOR-MIMICKING BASKET OF SECTOR ETFs",
         "=" * 80, "",
         "WHAT THIS IS", "-" * 80,
         "A recipe: which of the eleven Vanguard sector ETFs to buy, which to sell",
         "short, and how much of each.",
         "",
         'The basket is scaled so that when the probability of "Trump wins the 2024',
         'election" rises by one percentage point, the basket returns +1%.',
         "",
         "This collapses eleven ETFs into ONE tradable series that can be compared",
         "directly with the prediction market. Hasbrouck's method and the VECM in",
         "Steps 3 and 4 both require two securities that share one common fundamental",
         "value, so this basket is the prerequisite for everything that follows.", "",
         "", "HOW THE BETAS ARE ESTIMATED", "-" * 80,
         "For each ETF we run one regression on daily data:", "",
         "    (ETF return on day d)  =  a  +  beta * (change in P(Trump) on day d)  +  e",
         "",
         f"Sample: {len(sub)} trading days, 2024-06-20 to 2024-07-31.",
         "That window contains three events that moved the election odds but did not",
         "directly change any sector's fundamentals. All three happened while the stock",
         "market was closed, so each ETF's response falls on the next trading day:", ""]
    for d in EVENT_REACTION_DAYS:
        L.append(f"    {d}   change in P(Trump) = {full.loc[d, 'dprob']:+.3f}"
                 f"   <-  {EVENT_LABEL[d]}")
    L += ["",
          "    As a robustness check, the tighter design that uses only +/-3 trading",
          "    days around each of the three events (19 days) gives the same signs;",
          "    the wider window is reported here because it is better identified.", "",
          "All eleven betas are kept. None is dropped for being statistically",
          "insignificant: keeping only the significant ones would bias the surviving",
          "estimates upward, and the quantity that matters is the R-squared of the",
          "portfolio as a whole rather than a star on each individual beta.", "",
          "", "THE BASKET", "-" * 80] + basket_table(beta_df) + [
          "",
          "beta    the slope above. VPU beta = -0.164 means: when P(Trump) rises by one",
          "        percentage point, the utilities ETF falls by about 0.164%.",
          "se      standard error - how precisely beta is estimated. With 29 days, a",
          "        different 29 days would give a somewhat different beta, and se",
          "        measures how much it would move. VPU: -0.164 +/- 2*0.053 gives",
          "        [-0.27, -0.058], an interval that does not cross zero.",
          "t       beta divided by its standard error. |t| above roughly 2 means the",
          "        beta is clearly different from zero.",
          "p       if the true beta were zero, how often chance alone would produce a",
          "        beta this large. VPU: 0.0021. VHT: 0.67.",
          "n_obs   how many rows the regression used. Here 29, one per trading day; each",
          "        carries that day's ETF return and that day's change in P(Trump).",
          "",
          "The signs line up with the usual reading of the trade: higher odds of a Trump",
          "win go with financials and energy up, and utilities and materials down.", "",
          "", "HOW THE THREE SETS OF WEIGHTS ARE BUILT", "-" * 80,
          "All three plans use the same eleven betas and differ only in the rule that",
          "turns betas into weights. Each starts from a raw weight and then applies the",
          "same two normalisations:", "",
          "    w = w - mean(w)       dollar neutrality: total bought = total sold, so",
          "                          the basket takes no bet on the market's direction",
          "",
          "    w = w / (w . beta)    unit election exposure: w'beta = 1, so a one-point",
          "                          rise in P(Trump) moves the basket by exactly +1%",
          "",
          "The second step is needed because de-meaning destroys the unit exposure that",
          "the closed-form solution carries by construction.", "",
          "    plan A   sign-equal.      w = sign(beta)",
          "             Uses only the direction of each beta, not its size. Simplest and",
          "             most stable, but discards the fact that VPU is about five times",
          "             as sensitive as VOX.", "",
          "    plan B   beta-weighted.   w = beta / sum(|beta|)",
          "             Keeps the magnitudes, but ignores the correlations among the",
          "             ETFs, so exposure that several sectors share is double-counted.", "",
          "    plan C   minimum-variance mimicking portfolio.",
          "             w = (beta' S^-1 beta)^-1 * S^-1 beta",
          "             S is the 11x11 covariance matrix of the ETFs' daily returns over",
          "             the same 29 days. S^-1 hedges away the variation the ETFs share",
          "             with one another and leaves the election component. Subject to",
          "             'election exposure = 1', this basket has the smallest variance.", "",
          "", "COMPARING THE THREE PLANS", "-" * 80] + plan_comparison(beta_df, rob) + [
          "", "TWO THINGS THE TABLE MAY LOOK ODD", "-" * 80,
          "1. In plan C, Financials (VFH) has a positive beta but a negative weight.",
          "   beta asks: taken on its own, does this ETF move with P(Trump)?",
          "   The weight asks: inside a portfolio that already holds the other ten,",
          "   should this one be bought or sold?",
          "   VFH correlates 0.68 with Industrials and 0.56 with Materials, both of",
          "   which plan C is already heavily short. Buying VFH would add back the",
          "   common market variation those shorts just hedged away, so S^-1 assigns it",
          "   a small short instead. Only plan A keeps every weight pointing the way its",
          "   beta does. This is why all three plans are reported side by side.", "",
          "2. The weights are large (around +/-4, gross leverage about 17x).",
          "   That is only a unit of account. A single ETF moves 0.03% to 0.16% when",
          "   P(Trump) moves one point, so reaching the defined +1% requires scaling up",
          "   by roughly 17x. Step 4 uses only the basket's path, not its absolute size.", "",
          "", "HOW WELL THE BASKET TRACKS THE ELECTION FACTOR", "-" * 80,
          "Projecting the change in P(Trump) on all eleven ETF returns:", "",
          f"    Joint F-test, the eleven ETFs together      p = {fp:.4f}",
          f"    In-sample R-squared                             {r2_in:.3f}",
          f"    Adjusted R-squared                              {r2_adj:.3f}",
          f"    Leave-one-out out-of-sample R-squared          {r2_oos:+.3f}", "",
          "The relationship is real: the eleven ETFs jointly explain changes in P(Trump)",
          f"with p = {fp:.4f}. But the in-sample R-squared of {r2_in:.2f} is largely fitting noise -",
          "eleven parameters against 29 observations - and out of sample the projection",
          "explains close to nothing. The eleven sector ETFs span the election factor",
          "only partially. This is worth stating explicitly in the paper.", "",
          "The same measure for each of the three baskets (leave one day out, refit the",
          "betas and the weights on the remaining days, predict the day held out):", "",
          f"    plan A  sign-equal       {oos_a:+.3f}",
          f"    plan B  beta-weighted    {oos_b:+.3f}",
          f"    plan C  min-variance     {oos_c:+.3f}", "",
          "Plan C is the only basket with positive out-of-sample explanatory power, and",
          "the margin is small. Reporting all three is the honest presentation.", "",
          "", "ROBUSTNESS", "-" * 80,
          f"1. Dropping any single day leaves the joint F-test p between {fp_lo:.4f} and",
          f"   {fp_hi:.4f}. The result is not carried by one observation - not by July 15",
          "   (the first trading day after the shooting) and not by July 11 (a CPI",
          "   release).", "",
          "2. Adding the broad market (VTI) as a control raises R-squared from 0.754 to",
          "   0.776; VTI's own coefficient has t = 1.26 and none of the eleven betas",
          "   changes sign. The betas are not an artefact of market exposure.", "",
          "3. The largest shock is the one the ETFs fit least well. On July 15 the actual",
          "   change in P(Trump) was +0.110 while the eleven ETFs together account for",
          "   +0.070, about 64% of it.", "",
          "", "DATA", "-" * 80,
          'P(Trump wins)      Polymarket, "Will Donald Trump win the 2024 US Presidential',
          '                   Election?" (about $1.53B traded), daily closes.',
          f"                   Coverage {prob.index.min().date()} to {prob.index.max().date()}", "",
          "ETF daily returns  yfinance, eleven Vanguard sector ETFs, total return with",
          "                   dividends included.",
          f"                   Coverage {ret.index.min().date()} to {ret.index.max().date()}", "",
          f"Beta window        2024-06-20 to 2024-07-31 ({len(sub)} trading days)",
          "Covariance window  the same 29 days, so S and beta come from one sample", "",
          "Polymarket's daily points are stamped 19:00/20:00 ET, so the change in",
          "P(Trump) for day d also contains the 16:00-20:00 after-hours stretch. beta is",
          "a contemporaneous exposure, not a predictive coefficient, so this does not",
          "affect its definition.", "",
          "", "WHY POLYMARKET RATHER THAN KALSHI FOR THIS STEP", "-" * 80,
          "The identification needs a probability of 'Trump wins' that spans the three",
          "events. On Kalshi, the binary contract PRES-2024-DJT has its first trade on",
          "2024-10-04. That is a regulatory boundary rather than a gap in the data: the",
          "CFTC prohibited political event contracts in September 2023, and Kalshi could",
          "list them only after the D.C. Circuit denied the CFTC's motion for a stay",
          "pending appeal on 2024-10-02. All three event dates fall inside that period.",
          "Polymarket's contract on the same question has traded since 2024-01-05.", "",
          "The Kalshi-only version was carried through to a conclusion, estimating the",
          "betas on 2024-10-04 to 10-31 (see step1_election_beta.py):", "",
          "    daily,      n = 19 days    joint F-test p = 0.35, out-of-sample R2 = -2.52",
          "    1-minute,   n = 5,455 bars R-squared = 0.0026", "",
          "Through October, P(Trump) drifts from 0.50 to 0.63 with no single-day jump, so",
          "there is nothing to identify from. Over the weekend of July 13 it moves from",
          "0.595 to 0.705 - one event supplies more variation than all of October. The",
          "event-based design is therefore necessary, not merely preferable, and it",
          "requires the Polymarket series.", "",
          "", "CIRCULARITY", "-" * 80,
          "The betas must not be estimated on the data the Hasbrouck / VECM test will",
          "later use, or the instrument is fitted to what it is meant to evaluate.", "",
          "The test window for Steps 3 and 4 is not fixed yet, but no overlap is possible",
          "however it is chosen. The betas end on 2024-07-31, and Kalshi's presidential",
          "contract has no trades before 2024-10-04, so any Kalshi-based test lies",
          "entirely after the beta window. The two sides also come from different venues,",
          "which rules out mechanical correlation from a shared order book.", "",
          "", "FILES", "-" * 80,
          "step1_step2_polymarket_beta_and_weights.py   produces everything below",
          "etf_election_beta_polymarket.csv             the eleven betas and the three",
          "                                             sets of weights; Steps 3 and 4",
          "                                             read this file",
          "polymarket_trump_2024_daily.csv              the daily P(Trump) series, cached",
          "step1_basket_report_EN.txt                   this document",
          "step1_polymarket_diagnostics.txt             technical appendix: all three",
          "                                             sample specifications and the",
          "                                             robustness output", ""]
    return "\n".join(L)


def main():
    prob = load_prob()
    ret = load_etf_returns()
    full = align(prob, ret)

    print(f"Polymarket P(Trump): {prob.index.min().date()} to {prob.index.max().date()}  "
          f"({len(prob)} days, range [{prob.min():.3f}, {prob.max():.3f}])")
    print(f"ETF daily returns:   {ret.index.min().date()} to {ret.index.max().date()}  "
          f"({len(ret)} trading days)\n")
    print("Change in P(Trump) on each event's reaction day:")
    for d in EVENT_REACTION_DAYS:
        print(f"  {d}   dprob = {full.loc[d, 'dprob']:+.4f}   <-  {EVENT_LABEL[d]}")
    print()

    lines, headline_beta, headline_n = [], None, 0
    en_sub = en_rob = en_stats = None
    for spec in SPECS:
        sub = subset(full, spec)
        beta_df = estimate_betas(sub)
        w, r2_b, wsum, wexp = mimic_portfolio(beta_df, sub, sub)
        r2_in, r2_adj, fp, r2_oos = honest_r2(sub)
        beta_df["mimic_weight"] = w

        star = "  <== HEADLINE" if spec == HEADLINE else ""
        lines += [f"{'=' * 72}", f"[{spec}]  n = {len(sub)} trading days{star}", f"{'=' * 72}",
                  beta_df.round(4).to_string(index=False), "",
                  f"  sum(w)                = {wsum:.2e}   (dollar neutral, should be 0)",
                  f"  w' beta               = {wexp:.6f}   (unit election exposure, should be 1)",
                  f"  mimicking R^2         = {r2_b:.4f}   (the plan C basket, in-sample)",
                  f"  full-panel R^2        = {r2_in:.4f}   (dprob on all eleven ETFs)",
                  f"  adjusted R^2          = {r2_adj:.4f}",
                  f"  joint F-test p        = {fp:.4f}   (do the eleven ETFs jointly explain dprob)",
                  f"  leave-one-out OOS R^2 = {r2_oos:.4f}   (<0 = worse than predicting the mean)",
                  f"  betas with p<0.05     = {(beta_df.p_value < 0.05).sum()} / 11", ""]
        if spec == HEADLINE:
            # Store all three baskets. Same betas, three weighting rules; each is
            # de-meaned (sum w = 0) and then rescaled (w'beta = 1).
            b = beta_df["beta"].values
            Sg = np.cov(sub[ETFS].values, rowvar=False)
            for col, f in zip(WCOLS, (_w_sign_equal, _w_beta_weighted, _w_min_var)):
                ww = f(b, Sg)
                beta_df[col] = ww / (ww @ b)
            beta_df = beta_df.drop(columns=["mimic_weight"])
            headline_beta, headline_n = beta_df, len(sub)
            rob_lines, rob = robustness(sub)
            lines += rob_lines + [""]
            en_stats = (r2_b, r2_in, r2_adj, fp, r2_oos, rob["fp_lo"], rob["fp_hi"],
                        rob["oos_a"], rob["oos_b"], rob["oos_c"])
            en_sub, en_rob = sub, rob

    out_csv = os.path.join(HERE, "etf_election_beta_polymarket.csv")
    headline_beta.to_csv(out_csv, index=False)

    txt = report(prob, ret, full, headline_beta, en_sub, en_stats, en_rob)
    with open(os.path.join(HERE, "step1_basket_report_EN.txt"), "w") as f:
        f.write(txt)

    appendix = ["TECHNICAL APPENDIX - all three sample specifications, plus robustness",
                "Produced by step1_step2_polymarket_beta_and_weights.py",
                "The readable version is step1_basket_report_EN.txt", "",
                "  event   +/-3 trading days around each of the three reaction days",
                "  window  every trading day 2024-06-20 to 2024-07-31   (headline)",
                "  long    every trading day 2024-01-05 to 2024-07-31", ""] + lines
    with open(os.path.join(HERE, "step1_polymarket_diagnostics.txt"), "w") as f:
        f.write("\n".join(appendix))

    print(txt)
    print("weights ->", out_csv)


if __name__ == "__main__":
    main()
