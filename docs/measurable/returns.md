---
title: "Returns, compounding, log-returns"
prereqs: "none"
arrives_at: "the units every strategy speaks"
code_ref: "trading/packages/afml/src/afml/labeling.py:41 — rolling_vol"
---

# Returns, compounding, log-returns

A stock that moves from $100 to $102 has produced a 2% gain. This is the **arithmetic return**:

$$
r_t = \frac{p_t - p_{t-1}}{p_{t-1}} = \frac{p_t}{p_{t-1}} - 1.
$$

Arithmetic returns work well for a single period. They fail as soon as periods must be combined.

## Limitations of arithmetic returns

A stock that gains 10% on Monday and loses 10% on Tuesday ends at $100 \times 1.10 \times 0.90 = 99$, not at the starting price. Arithmetic returns do not add; they **compound**. Over $n$ periods:

$$
p_n = p_0 \prod_{t=1}^{n} (1 + r_t).
$$

Multiplicative compounding is cumbersome. More importantly, the *average* of arithmetic returns systematically overstates the long-run compounded return: the arithmetic mean is always at least the geometric mean, with equality only when every return is identical (this is Jensen's inequality applied to $\log(1+r)$). Reporting a strategy's mean daily return without correction overstates annualized performance.

## Log returns simplify the algebra

The **log return** over one period is defined as:

$$
\ell_t = \log\!\left(\frac{p_t}{p_{t-1}}\right) = \log p_t - \log p_{t-1}.
$$

Under this definition, multi-period compounding reduces to addition:

$$
\log\frac{p_n}{p_0} = \sum_{t=1}^{n} \ell_t.
$$

Three properties follow:

1. **Additive across time.** The sum of daily log returns equals the total log return. Averages are well-behaved: the mean daily log return times $n$ is the $n$-day log return (in expectation under iid assumptions, and exactly in realization).
2. **Symmetric.** A $+10\%$ log move is exactly reversed by a $-10\%$ log move. Arithmetic returns are not symmetric — a 10% gain followed by a 10% loss yields a 1% net loss.
3. **Closer to Gaussian.** Log prices under geometric Brownian motion are Gaussian by construction. Real markets deviate from GBM, but log returns are closer to normal than arithmetic returns are. Models that assume normality have smaller specification errors on log returns.

## Where the difference matters

For small moves, $\log(1 + r) \approx r - r^2/2$, so log and arithmetic returns agree to first order. A 1% daily return gives $r = 0.01$ and $\ell \approx 0.00995$ — a difference of 5 basis points out of 100.

The gap grows with move size:

| Arithmetic $r$ | Log $\ell$ | Difference |
|---------------|-----------|------------|
| $+1\%$        | $+0.995\%$ | 5 bp       |
| $+10\%$       | $+9.53\%$  | 47 bp      |
| $-10\%$       | $-10.54\%$ | 54 bp      |
| $-30\%$       | $-35.67\%$ | 567 bp     |

For daily bars in liquid markets, the two conventions produce similar results. For weekly or longer bars, for drawdown accounting, and for nonlinear statistics (particularly volatility, covered in the next lesson), log returns are preferred.

## Convention used in the trading project

The [triple-barrier method](../ml/triple-barrier.md) in this project computes labels using arithmetic returns: `(p_t / p_0 - 1) * side`. This follows AFML ch. 3.1 and matches how the barriers are stated — as multiples of a rolling-vol target also computed from arithmetic returns. Both quantities must be expressed in the same units to avoid miscalibration.

When reading the code, note that arithmetic returns are used throughout the labeling pipeline so that barriers and vol share units. Annualized performance metrics (Sharpe, Sortino) computed over a series of such returns remain close to log-based versions at daily horizons.

## Summary

The reader can now reason about:

- Why a strategy's cumulative return differs from the mean daily return times the number of days.
- Why a Sharpe computed on log returns can differ from one computed on arithmetic returns, even for identical data.
- Why options pricing models (covered in the next part) assume log-normal terminal prices rather than normal ones.

## Implemented at

`trading/packages/afml/src/afml/labeling.py:41` — `rolling_vol(prices, span=100)` computes the EWM standard deviation of arithmetic `pct_change` returns. The docstring cites AFML ch. 3.1 explicitly. This choice is important: downstream, `apply_triple_barrier` at line 52 compares `(p/p0 - 1)` against `mult * sigma`, so vol must be expressed in arithmetic-return units for the thresholds to be consistent.

---

**Next:** [Volatility as a measurable thing →](volatility.md)
