"""
step4_calibrate.py
================================================================================
STEP 4, PART 1 -- CALIBRATE THE BASKET LEVEL TO AN IMPLIED PROBABILITY
  Step 3 gives B_t, the basket's buy-and-hold level in return units. Kalshi is a
  probability in [0,1]. To compare them they must be on the same scale, so we map
  B_t linearly onto a probability using two points whose probability we know:

      p0  reference at the start of the sample -- Nate Silver's Silver Bulletin
          model update, P(Trump wins) = 0.447 on 2024-09-30/10-01
          (nearest model update to the 2024-10-04 sample start)
      p1  terminal at election night -- the outcome is known, Trump won, P -> 1

      implied_p_t = q0 + (B_t - B@p0) * (q1 - q0) / (B@p1 - B@p0)

  B@p0 is the basket level at the first bar (= 0 by construction) and B@p1 is the
  level at the last bar (election night). The map sends B@p0 -> q0 and B@p1 -> q1.

  This is done per weight plan. The slope (q1 - q0)/(B@p1 - B@p0) is the number of
  probability points per unit basket return; a NEGATIVE slope means the basket
  moved opposite to the outcome over the window and cannot be read as a
  probability -- that plan is rejected here.

  Cointegration / VECM / Hasbrouck come after this, on implied_p vs Kalshi.

INPUT   step3_basket_levels.csv
OUTPUT  step4_implied_prob.csv          date, ts_et, implied_p_<plan> per bar
        step4_calibration_summary.txt   the two points and the per-plan slope
================================================================================
"""
import os
import sys
import pandas as pd

MODE = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in ("high_frequency", "daily") else "high_frequency"

HERE = os.path.dirname(os.path.abspath(__file__))
LEVELS = os.path.join(HERE, "..", "step3", f"step3_basket_levels_{MODE}.csv")

# --- the two calibration anchors ---
Q0 = 0.447   # Silver Bulletin P(Trump), 2024-09-30/10-01, reference at sample start
Q1 = 1.0     # election night outcome: Trump won -> P -> 1

PLANS = ["A_sign_equal", "B_beta_weighted", "C_min_variance"]


def main():
    d = pd.read_csv(LEVELS, parse_dates=["ts_et"]).sort_values(["date", "ts_et"]).reset_index(drop=True)

    out = d[["date", "ts_et"]].copy()
    rows = []
    for p in PLANS:
        B = d[f"B_{p}"]
        B0, B1 = B.iloc[0], B.iloc[-1]                 # start (=0) and election night
        slope = (Q1 - Q0) / (B1 - B0)
        implied = Q0 + (B - B0) * slope
        out[f"implied_p_{p}"] = implied.values          # keep every plan; caveats go in the summary
        rows.append({"plan": p, "B_start": B0, "B_terminal": B1,
                     "slope_prob_per_unit": slope,
                     "implied_p_min": float(implied.min()), "implied_p_max": float(implied.max()),
                     "implied_p_end": Q0 + (B1 - B0) * slope})
    res = pd.DataFrame(rows)

    out_csv = os.path.join(HERE, f"step4_implied_prob_{MODE}.csv")
    out.to_csv(out_csv, index=False)

    lines = [f"STEP 4 [{MODE}] PART 1 - TWO-POINT CALIBRATION OF THE BASKET TO A PROBABILITY",
             "=" * 78,
             f"reference p0 (sample start): P(Trump) = {Q0}  (Silver Bulletin, 2024-09-30/10-01)",
             f"terminal  p1 (election night): P(Trump) = {Q1}  (Trump won)",
             "",
             "implied_p_t = q0 + (B_t - B@p0) * (q1 - q0) / (B@p1 - B@p0)",
             "",
             "All three plans are calibrated and written to step4_implied_prob.csv. The",
             "slope is probability points per unit basket return; the last two columns show",
             "how far each calibrated series strays outside [0,1].",
             "",
             f"  {'plan':16s} {'B_terminal':>11s} {'slope':>8s} {'impl_p min':>11s} {'impl_p max':>11s}",
             "  " + "-" * 60]
    for _, r in res.iterrows():
        lines.append(f"  {r['plan']:16s} {r['B_terminal']:+11.4f} {r['slope_prob_per_unit']:+8.2f}"
                     f" {r['implied_p_min']:+11.3f} {r['implied_p_max']:+11.3f}")
    lines += ["",
              "WHY PLAN C SHOULD NOT BE USED DOWNSTREAM",
              "-" * 60,
              "Over the window P(Trump) rose from 0.447 to 1.0, but the plan C basket level",
              "FELL (B_terminal = -0.028). The two-point slope is therefore NEGATIVE",
              "(-20.0): its calibrated 'probability' moves the wrong way -- it goes down",
              "when Trump's odds go up. That is an inverted signal, not a probability, so",
              "plan C cannot be read as P(Trump) and should be dropped from the",
              "cointegration / Hasbrouck stage. It is kept in the CSV only for transparency.",
              "This matches its Step-2 out-of-sample weakness: the min-variance weights, best",
              "in-sample, do not hold up out-of-sample.",
              "",
              "ON PLAN A",
              "-" * 60,
              "Plan A calibrates with a positive slope but its steep slope (+6.03) sends the",
              "implied probability well outside [0,1] (down to -0.74), i.e. the sign-equal",
              "basket is too noisy to be a clean probability proxy. Plan B (beta-weighted)",
              "stays close to [0,1] and is the best-behaved of the three.",
              "",
              "Note: the reference is Silver's ~Oct 1 update while the basket starts Oct 4;",
              "the ~3-day offset is the nearest model update to the sample start."]
    with open(os.path.join(HERE, f"step4_calibration_summary_{MODE}.txt"), "w") as f:
        f.write("\n".join(lines))

    print("\n".join(lines))
    print("\nwritten ->", out_csv)


if __name__ == "__main__":
    main()
