"""
hasbrouck.py   (attempt2)
================================================================================
Price discovery on the Method B cointegrated pair: which market -- the Kalshi
prediction market or the sector-ETF basket -- moves first toward the common
efficient probability. Runs a VECM, then Gonzalo-Granger component shares and
Hasbrouck (1995) information shares.

Only legitimate because Method B's basket and Kalshi cointegrate (ADF/EG); this
is the payoff step of the whole sub-project.

  STEP 1  load the cointegrated pair (implied_p basket, kalshi), daily, 16:00 ET.
  STEP 2  VECM, coint_rank=1 -> beta (cointegrating vector), alpha (error-
          correction speeds), Omega (residual covariance).
  STEP 3  read alpha: the series that does NOT adjust (alpha ~ 0) leads.
  STEP 4  Gonzalo-Granger component shares (from alpha_perp; order-invariant).
  STEP 5  Hasbrouck information shares via Cholesky of Omega, both orderings
          -> lower/upper bounds + midpoint.

Honest caveat: 24 daily points is very thin for a VECM/IS (these are normally
run on thousands of intraday bars), and Johansen did not confirm cointegration.
Treat the shares as indicative, not definitive.

INPUT   methodB_pair.csv   (or a pair csv passed as argv[1])
OUTPUT  prints the VECM, GG shares, and Hasbrouck IS bounds
================================================================================
"""
import os
import sys
import numpy as np
import pandas as pd
from statsmodels.tsa.vector_ar.vecm import VECM

HERE = os.path.dirname(os.path.abspath(__file__))
PAIR = os.path.join(HERE, sys.argv[1] if len(sys.argv) > 1 else "methodB_pair.csv")
NAMES = ["basket", "kalshi"]


def hasbrouck_is(psi, Omega, order):
    """Information share of each market for a given Cholesky ordering.
       psi = common-factor row vector (long-run impact), Omega = residual cov."""
    p = np.asarray(order)
    M = np.linalg.cholesky(Omega[np.ix_(p, p)])      # lower-triangular factor
    psi_o = psi[p]
    num = (psi_o @ M) ** 2                            # per-column contribution
    denom = float(psi_o @ Omega[np.ix_(p, p)] @ psi_o)
    is_o = num / denom
    out = np.empty(2)
    out[p] = is_o                                     # map back to original order
    return out


def main():
    pair = pd.read_csv(PAIR, parse_dates=["date"]).set_index("date")
    Y = pair[["implied_p", "kalshi"]].values

    # ---- STEP 2: VECM ----
    res = VECM(Y, k_ar_diff=1, coint_rank=1, deterministic="ci").fit()
    beta = res.beta[:, 0]
    beta_n = beta / beta[0]                            # normalise so basket coeff = 1
    alpha = res.alpha[:, 0]
    Omega = np.cov(res.resid, rowvar=False)

    print("STEP 2  VECM (rank 1, k_ar_diff=1), n = %d daily obs" % len(pair))
    print("  cointegrating vector beta (normalised): basket %+.3f , kalshi %+.3f" % (beta_n[0], beta_n[1]))
    print("      -> equilibrium: basket %+.3f*kalshi is stationary" % (-beta_n[1]))
    print("  adjustment speeds alpha: basket %+.3f , kalshi %+.3f" % (alpha[0], alpha[1]))

    # ---- STEP 3: read alpha ----
    leader = NAMES[int(abs(alpha[0]) > abs(alpha[1]))]   # larger |alpha| = follower
    print("\nSTEP 3  smaller |alpha| = leads (does not correct). "
          "|alpha_basket|=%.3f , |alpha_kalshi|=%.3f -> %s leads" %
          (abs(alpha[0]), abs(alpha[1]), leader))

    # ---- STEP 4: Gonzalo-Granger component shares ----
    a_perp = np.array([alpha[1], -alpha[0]])             # orthogonal to alpha
    if a_perp.sum() != 0:
        gg = a_perp / a_perp.sum()
    else:
        gg = np.array([np.nan, np.nan])
    print("\nSTEP 4  Gonzalo-Granger component share (order-invariant):")
    print("  basket %5.1f%%   kalshi %5.1f%%" % (100 * gg[0], 100 * gg[1]))

    # ---- STEP 5: Hasbrouck information shares (both orderings) ----
    psi = a_perp.astype(float)                           # common-factor row ~ alpha_perp
    is_a = hasbrouck_is(psi, Omega, [0, 1])              # basket ordered first
    is_b = hasbrouck_is(psi, Omega, [1, 0])              # kalshi ordered first
    lo = np.minimum(is_a, is_b); hi = np.maximum(is_a, is_b); mid = 0.5 * (lo + hi)
    rho = Omega[0, 1] / np.sqrt(Omega[0, 0] * Omega[1, 1])
    print("\nSTEP 5  Hasbrouck information share (residual corr = %+.2f):" % rho)
    print("  %-8s  %7s  %7s  %7s" % ("market", "lower", "upper", "mid"))
    for i, nm in enumerate(NAMES):
        print("  %-8s  %6.1f%%  %6.1f%%  %6.1f%%" % (nm, 100 * lo[i], 100 * hi[i], 100 * mid[i]))

    print("\nCaveat: 24 daily obs is very thin for VECM/IS and Johansen did not")
    print("confirm cointegration -- read these as indicative, not definitive.")


if __name__ == "__main__":
    main()
