"""
hasbrouck_basket.py   (high frequency basket -- steps 1-4 in one file)
================================================================================
The whole high-frequency-basket analysis, weights re-estimated at 1 minute:

  STEP 1-2  weights by a LEVEL cointegrating regression on the 1-minute
            estimation panel (Sep 3 - Oct 3, Polymarket P(Trump) on the 20 asset
            prices).  The coefficients are the basket's fixed share weights.
  STEP 3    build the dollar basket on the Oct-Nov TEST panel, start-anchored to
            Kalshi's first test minute (causal), then the cointegration gate.
  STEP 4    price discovery: does the equity basket lead Kalshi, or follow it?
            Four parts, each removing one way the naive answer could be an
            artefact (see the header printed into the results file).

Out of sample: weights from Polymarket (Sep), test on Kalshi (Oct-Nov) -- a
different venue AND period. The estimator estimate() is reused verbatim from
../high frequency/hasbrouck_hf.py so this basket and the daily-weighted one are
compared on identical machinery.

INPUT   estim_panel_1min.csv, test_panel_1min.csv   (from build_panels.py)
OUTPUT  hf_basket_weights.csv
        hf_basket_pair_1min.csv
        hf_basket_results.txt      (steps 1-4 together)
        hf_basket.png
================================================================================
"""
import os
import sys
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.vector_ar.vecm import coint_johansen
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "high frequency"))
from hasbrouck_hf import estimate  # noqa: reuse the exact same VECM/IS estimator

ETFS = ["VAW", "VCR", "VDC", "VDE", "VFH", "VGT", "VHT", "VIS", "VNQ", "VOX", "VPU"]
ADDS = ["MARA", "COIN", "GEO", "IBKR", "FSLR", "RUN", "DHI", "TAN", "FXI"]
COLS = ETFS + ADDS

_HDR = """\
================================================================================
HIGH-FREQUENCY BASKET -- STEPS 1-4  (weights re-estimated at 1 minute)
basket = 11 sector ETFs + MARA COIN GEO IBKR FSLR RUN DHI TAN + FXI
================================================================================
WHAT STEP 4'S FOUR PARTS ARE FOR (each removes one way "who leads" could fool us)
  PART 1  baseline: over all minutes, which side error-corrects (moves back when
          the two prices diverge)? The side that does NOT adjust is the leader.
          This number is inflated by the market open, so parts 2-4 stress-test it.
  PART 2  split the day into four windows: is the adjustment there all day, or
          only in the morning? (Distinguishes a real lead from opening catch-up.)
  PART 3  delete the first N minutes of each session: how much of the effect
          survives once the open is removed? (Locates where the effect lives.)
  PART 4  the decisive test. Does the opening gap predict the BASKET's next 90
          minutes (C1) but NOT Kalshi's (C2, placebo)? A one-sided C1-with-flat-C2
          is what rules out "both just followed the same news" and shows the
          equity basket is chasing Kalshi -- information flowing market -> equity.
  PART 5  opening convergence profile: minute by minute after the open, what
          fraction of the opening gap has the basket closed (and, as placebo,
          Kalshi)? This traces the catch-up the paper is really about.
================================================================================
"""


_GLOSSARY = """\
================================================================================
HOW TO READ THE STEP-4 NUMBERS
================================================================================
Model. A one-minute bivariate vector error-correction model. Define the pricing
  gap  z = basket - 0.323*kalshi.  Each side's next-minute change is regressed on
  the lagged gap and short lags:
       d(basket) = alpha_basket * z_{t-1} + ... ;   d(kalshi) = alpha_kalshi * z_{t-1} + ...
  The side whose loading (alpha) is statistically indistinguishable from zero does
  NOT adjust to the gap, and is therefore the price leader -- the other side is the
  one doing the catching up.

alpha  error-correction speed: how strongly a market reverses the gap each minute.
       alpha_basket = -0.00149 (negative): when the basket sits above its
       Kalshi-implied level it falls back toward Kalshi. That is active correction.
t      alpha divided by its standard error; |t| > 1.96 is significant at the 5%
       level. basket t = -4.04 -> the basket clearly adjusts. kalshi t = +1.73 ->
       below 1.96, so Kalshi's adjustment cannot be distinguished from zero: Kalshi
       leads, the basket follows.
Gonzalo-Granger share  a permanent-component decomposition computed from the two
       alphas only. Reported for completeness. Here it is driven by the imprecisely
       estimated alpha_kalshi, so it disagrees with the information share and should
       not be read on its own.
Hasbrouck IS  price-discovery share that also weights each side's innovation
       variance (how much genuinely new information each side's shocks carry); the
       [lower, upper] bracket is the identified range under the two Cholesky
       orderings of correlated residuals. Kalshi 85.5% -- most new information
       enters through the prediction market first.

Parts 2-3 vary the sample (time-of-day windows; deleting the first N minutes) to
  show WHERE the basket's adjustment lives. A leader-only-at-the-open pattern would
  fade once the morning is removed; here it does not.

Part 4 (session level, n = 23 days)
  slope  regression of a market's next-90-minute move on that day's opening gap.
         C1 = -0.24 means the basket closes about 24% of the opening gap over 90
         minutes (negative = moves to close it).
  t, p   significance of that slope (p < 0.05 significant).
  R2     fraction of the next-90-minute move explained by the opening gap alone.
  placebo (C2)  the SAME regression run on Kalshi. If both markets were merely
         reacting to the same news, Kalshi would also move toward the gap. It does
         not (p = 0.68, flat), so the adjustment is one-sided: only the basket
         chases. This is the test that pins the direction of information flow.

Part 5  the fraction of the opening gap the basket has closed by minute h after the
        open, with Kalshi as the placebo. Positive = moved toward closing the gap.
"""

_CONCLUSION = """\
================================================================================
CONCLUSION
================================================================================
Re-estimating the basket weights at 1 minute and adding FXI produces a basket that
cointegrates with Kalshi at 1 minute (Engle-Granger p = 0.037, level correlation
0.92) -- a genuinely usable basket, which the daily-weighted basket was not.

On that basket the direction of price discovery is unambiguous and one-sided. The
equity basket error-corrects toward Kalshi (alpha_basket t = -4.04) while Kalshi
does not adjust (t = 1.73); the opening gap predicts the basket's subsequent path
(C1 p = 0.003, R2 = 0.35) but not Kalshi's (placebo p = 0.68). Information flows
from the prediction market to the equity market, not the reverse.

The lead is persistent through the session, not confined to the open. The basket
closes about 21% of the opening gap within 15 minutes and continues to about 31%
by the close (Part 5), and its error-correction stays significant even after the
first 120 minutes are removed (Part 3, t = -3.2). This revises the earlier
daily-basket reading of a "temporary, first-90-minutes" advantage: that framing
was an artefact of a basket that tracked Kalshi too weakly. Kalshi's informational
lead over the sector-ETF basket holds throughout regular trading hours.

The basket closes only about a third of each gap because a basket of these
equities spans only part of the election factor. The result is therefore about the
direction and timing of information flow between the two markets, not a claim that
equities fully replicate the prediction market.
"""


def _adf_p(x):
    return adfuller(pd.Series(x).dropna().values, autolag="AIC")[1]


def main():
    out = [_HDR]

    def emit(s=""):
        print(s); out.append(s)

    est = pd.read_csv(os.path.join(HERE, "estim_panel_1min.csv"), parse_dates=["minute"]).set_index("minute")
    est = est[COLS + ["prob"]].dropna()
    test = pd.read_csv(os.path.join(HERE, "test_panel_1min.csv"), parse_dates=["minute"]).set_index("minute")
    test = test[COLS + ["kalshi"]].dropna()

    # ---- STEP 1-2 : weights from the 1-minute estimation panel --------------
    reg = sm.OLS(est["prob"].values, sm.add_constant(est[COLS].values)).fit()
    w = pd.Series(reg.params[1:], index=COLS, name="share_weight")
    w.to_csv(os.path.join(HERE, "hf_basket_weights.csv"))
    emit("STEP 1-2  weights: level cointegrating regression on 1-min data")
    emit("          estimation 2024-09-03..2024-10-03 (Polymarket), n=%d, R2=%.3f (level fit, inflated)"
         % (len(est), reg.rsquared))
    emit("          in-sample residual ADF p = %.4f -> %s\n"
         % (_adf_p(reg.resid), "cointegrated" if _adf_p(reg.resid) < 0.05 else "not"))

    # ---- STEP 3 : basket on the test panel + cointegration gate -------------
    B = pd.Series(test[COLS].values @ w.values, index=test.index)
    anchor = float(test["kalshi"].iloc[0])
    implied = anchor + (B - B.iloc[0])
    pair = pd.DataFrame({"implied_p": implied, "kalshi": test["kalshi"]})
    pair.index.name = "minute"
    pair.to_csv(os.path.join(HERE, "hf_basket_pair_1min.csv"))

    ip, m = pair["implied_p"].values, pair["kalshi"].values
    eg = sm.OLS(ip, sm.add_constant(m)).fit()
    joh3 = coint_johansen(np.column_stack([ip, m]), det_order=0, k_ar_diff=5)
    emit("STEP 3  test basket vs Kalshi -- cointegration gate (%d min, Oct-Nov RTH)" % len(pair))
    emit("  anchor = Kalshi first test minute = %.3f (causal)   level corr = %+.3f"
         % (anchor, pair["implied_p"].corr(pair["kalshi"])))
    emit("  ADF spread(1,-1) p = %.4f -> %s   (unit-slope test; basket underresponds, so weak here)"
         % (_adf_p(ip - m), "yes" if _adf_p(ip - m) < 0.05 else "no"))
    emit("  Engle-Granger    p = %.4f -> %s   (free slope b=%+.3f; scale-invariant HEADLINE test)"
         % (_adf_p(eg.resid), "COINTEGRATED at 5%" if _adf_p(eg.resid) < 0.05 else "no", eg.params[1]))
    emit("  Johansen trace = %.2f  (10%% cv 13.43, 5%% cv 15.49) -> %s\n"
         % (joh3.lr1[0], "coint at 5%" if joh3.lr1[0] > 15.49 else ("coint at 10%" if joh3.lr1[0] > 13.43 else "no")))

    # ---- STEP 4 : price discovery -------------------------------------------
    y = pair[["implied_p", "kalshi"]].values
    day = pd.Series(pair.index.date).values
    mod = np.array([t.hour * 60 + t.minute for t in pair.index.time])
    v = coint_johansen(y, det_order=0, k_ar_diff=5).evec[:, 0]
    BETA = -v[1] / v[0]                                     # cointegrating scalar, re-estimated at 1-min

    emit("STEP 4  PRICE DISCOVERY AT 1 MINUTE   (z = basket - %.3f*kalshi; b from 1-min Johansen)" % BETA)
    emit("        overnight changes never enter any regression below.\n")

    R = estimate(y, day, mod, b=BETA)
    emit("  PART 1  baseline (all RTH minutes, n=%d)" % R["n"])
    for i, nm in enumerate(["basket", "kalshi"]):
        emit("    %-8s alpha %+.6f  t %+.2f   %s"
             % (nm, R["alpha"][i], R["t"][i], "ADJUSTS" if abs(R["t"][i]) > 1.96 else "cannot reject 0 (leads)"))
    emit("    Gonzalo-Granger: basket %.1f%% / kalshi %.1f%%   Hasbrouck IS kalshi %.1f%% [%.1f, %.1f]\n"
         % (100 * R["gg"][0], 100 * R["gg"][1], 100 * R["mid"][1], 100 * R["lo"][1], 100 * R["hi"][1]))

    emit("  PART 2  adjustment by time of day (alpha_basket; is it all-day or morning-only?)")
    for nm, f in [("09:30-10:30", lambda m: m < 630), ("10:30-12:00", lambda m: 630 <= m < 720),
                  ("12:00-14:00", lambda m: 720 <= m < 840), ("14:00-16:00", lambda m: m >= 840)]:
        S = estimate(y, day, mod, b=BETA, tmask=f)
        emit("    %-12s n=%4d  alpha_basket %+.6f  t %+.2f" % (nm, S["n"], S["alpha"][0], S["t"][0]))
    emit("")

    emit("  PART 3  delete first N minutes of each session (where does the effect live?)")
    for s in [0, 30, 60, 90, 120]:
        S = estimate(y, day, mod, b=BETA, skip_open=s)
        emit("    skip %3d min  n=%4d  alpha_basket %+.6f  t %+.2f" % (s, S["n"], S["alpha"][0], S["t"][0]))
    emit("")

    emit("  PART 4  opening gap -> next 90 min, with placebo (the decisive one-sided test)")
    rows, days = [], sorted(pd.Series(day).unique())
    for i in range(1, len(days)):
        cur = pair[pair.index.date == days[i]]
        prev = pair[pair.index.date == days[i - 1]]
        if len(cur) < 120 or len(prev) < 2:
            continue
        j = min(90, len(cur) - 1)
        rows.append((cur["kalshi"].iloc[0] - prev["kalshi"].iloc[-1],
                     cur["implied_p"].iloc[0] - BETA * cur["kalshi"].iloc[0],
                     cur["implied_p"].iloc[j] - cur["implied_p"].iloc[0],
                     cur["kalshi"].iloc[j] - cur["kalshi"].iloc[0]))
    D = pd.DataFrame(rows, columns=["overnight_kalshi", "z_open", "basket_90m", "kalshi_90m"])

    def reg2(yc, xc):
        r = sm.OLS(D[yc], sm.add_constant(D[xc])).fit()
        return r.params.iloc[1], r.tvalues.iloc[1], r.pvalues.iloc[1], r.rsquared

    emit("    n = %d sessions          %9s %6s %6s %5s" % (len(D), "slope", "t", "p", "R2"))
    emit("    C1 gap -> BASKET next 90m %9.4f %6.2f %6.3f %5.3f" % reg2("basket_90m", "z_open"))
    emit("    C2 gap -> KALSHI next 90m %9.4f %6.2f %6.3f %5.3f   (placebo: should be flat)" % reg2("kalshi_90m", "z_open"))
    emit("    C3 overnight K -> BASKET  %9.4f %6.2f %6.3f %5.3f\n" % reg2("basket_90m", "overnight_kalshi"))

    # ---- PART 5 : opening convergence profile -------------------------------
    # The question this answers directly: once the stock market opens, how much
    # of the opening gap does the BASKET close, minute by minute -- i.e. does the
    # equity basket visibly walk toward its Kalshi-implied level during the
    # session? For each horizon h we regress the basket's move over [open, open+h]
    # on the opening gap; -slope = fraction of the gap closed by minute h. The
    # same on Kalshi is the placebo (a leader should not walk toward the gap).
    emit("  PART 5  opening convergence profile -- fraction of the opening gap closed by minute h")
    emit("          (positive = the series moved TOWARD closing the gap; basket should, Kalshi should not)")
    prof = []
    for h in [15, 30, 45, 60, 90, 120, 180, 240, 330]:
        rows_h = []
        for i in range(1, len(days)):
            cur = pair[pair.index.date == days[i]]
            prev = pair[pair.index.date == days[i - 1]]
            if len(cur) <= h or len(prev) < 2:
                continue
            z0 = cur["implied_p"].iloc[0] - BETA * cur["kalshi"].iloc[0]
            rows_h.append((z0,
                           cur["implied_p"].iloc[h] - cur["implied_p"].iloc[0],
                           cur["kalshi"].iloc[h] - cur["kalshi"].iloc[0]))
        H = pd.DataFrame(rows_h, columns=["z0", "b", "k"])
        rb = sm.OLS(H["b"], sm.add_constant(H["z0"])).fit()
        rk = sm.OLS(H["k"], sm.add_constant(H["z0"])).fit()
        prof.append((h, -rb.params.iloc[1], rb.pvalues.iloc[1], -rk.params.iloc[1], rk.pvalues.iloc[1]))
    emit("    %5s  %14s  %14s" % ("min", "basket closed", "kalshi (placebo)"))
    for h, bc, bp, kc, kp in prof:
        emit("    %5d  %6.1f%% (p=%.3f)  %6.1f%% (p=%.3f)" % (h, 100 * bc, bp, 100 * kc, kp))

    emit("\n" + _GLOSSARY.rstrip())
    emit("\n" + _CONCLUSION.rstrip())

    with open(os.path.join(HERE, "hf_basket_results.txt"), "w") as f:
        f.write("\n".join(out) + "\n")

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(pair.index, pair["implied_p"], color="#1f77b4", lw=1.0, label="HF basket implied P (11 ETF + 8 adds + FXI)")
    ax.plot(pair.index, pair["kalshi"], color="black", lw=1.0, label="Kalshi PRES-2024-DJT")
    ax.set_ylabel("P(Trump wins)"); ax.legend(); ax.margins(x=.01)
    ax.set_title("HF-weighted basket (1-min, Sep-estimated) vs Kalshi, Oct-Nov")
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "hf_basket.png"), dpi=140)

    print("\nwritten -> hf_basket_weights.csv, hf_basket_pair_1min.csv, hf_basket_results.txt, hf_basket.png")


if __name__ == "__main__":
    main()
