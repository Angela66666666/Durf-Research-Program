
## The model says price _levels_ are linear in p — so dollar changes line up with Δp

If each sector ETF has a fundamental value conditional on the outcome,

```
Pᵢ,t = pₜ · Vᵢ(win) + (1 − pₜ) · Vᵢ(lose) + (non-election component)
```

then the price level is **affine in the probability**, and the election-driven move is

```
ΔPᵢ,t = (Vᵢ(win) − Vᵢ(lose)) · Δpₜ      — dollars per probability point
```

The election beta is naturally a _dollar_ quantity: the value gap between the two worlds. A simple return divides that by `Pᵢ,t`, so its "beta" is `(Vᵢ_win − Vᵢ_lose)/Pᵢ,t` — a moving target that drifts with the price level for reasons unrelated to the election. A log return adds a further concavity on top. Both distort the exact linearity that makes the two-point affine anchor legitimate.

The Kalshi side makes the parallel obvious: the contract _is_ an Arrow–Debreu security paying $1, so its dollar price change is exactly Δp. The ETF-side object that mirrors it is the dollar gain, scaled by the value gap.

## What this changes in the construction

**The basket should be a fixed-share dollar P&L portfolio, not a cumulated-return index.** Set share counts `nᵢ` at the window start and track

```
Bₜ = Σᵢ nᵢ · Pᵢ,t
```

This is exactly linear in each price, hence (in the two-state model) exactly affine in `pₜ` — the two-point anchor then has zero approximation error by construction. A rebalanced return-weighted index compounds multiplicatively, which breaks that exact affinity; cumulating _log_ returns breaks it further with an `exp`. Correspondingly, the betas in Step 2 should be estimated in dollar terms (`ΔPᵢ` on `Δp`), and the mimicking-portfolio algebra `w = (β'Σ⁻¹β)⁻¹Σ⁻¹β` run with dollar-change covariances, yielding share weights directly.

**How much it matters in practice: little for the numbers, a lot for the logic.** Over Sep–Nov the ETF price levels moved maybe 5–10%, so `return × P₀` versus dollar gain differ at second order — betas and lead-lag results would barely change. But the affine calibration (the anchoring step you asked about earlier) and the "cointegrating slope ≈ 1 against the 45° line" interpretation are only _exactly_ right in dollar space. Since the whole point of that construction was interpretability, use the specification in which it's exact rather than approximately-true.

## Two honest caveats

1. **Why finance defaults to returns doesn't apply here.** Returns are preferred because they're scale-free and comparable across assets and time — but comparability across ETFs is already handled by the β weights, and the window is short enough that dollar-change nonstationarity (P&L variance scaling with price level) is a non-issue. The repo's log-return convention in `leadlag_common.py` exists for the joint-lag regressions across many pairs, where scale-free is right; the basket level is a different object with a different job, and shouldn't inherit that convention reflexively.
    
2. **`V_win` and `V_lose` aren't constants.** They drift with non-election news (earnings, rates, oil), so even in dollar space the affinity holds only _conditional on other factors_ — which is exactly what the long-short, market-neutral construction is there to absorb. The residual drift is why the cointegration test has an error-correction term to estimate at all rather than an identity.
    

So: estimate betas as dollars-per-probability-point, build the basket as fixed-share dollar P&L, anchor that level with the two points, and the mapping from basket to implied probability is exact within the model rather than a linearization of it.