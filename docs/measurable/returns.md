---
title: "Returns, compounding, log-returns"
prereqs: "none"
arrives_at: "the units every strategy speaks"
code_ref: "trading/packages/afml/src/afml/labeling.py:41 — rolling_vol"
---

# Returns, compounding, log-returns

A stock goes from $100 to $102. You made two percent. That feeling is the **arithmetic return**:

$$
r_t = \frac{p_t - p_{t-1}}{p_{t-1}} = \frac{p_t}{p_{t-1}} - 1.
$$

It is honest for a single period. It breaks the instant you want to combine periods.

## The problem with arithmetic returns

Suppose your stock gains 10% on Monday and loses 10% on Tuesday. Flat? No — you are at $100 \times 1.10 \times 0.90 = 99$. Arithmetic returns do not add; they **compound**. Over $n$ periods:

$$
p_n = p_0 \prod_{t=1}^{n} (1 + r_t).
$$

Products are clumsy. Worse, the *average* of arithmetic returns systematically overstates the long-run compounded return: the arithmetic mean is always at least the geometric mean, with equality only when every return is identical. (Jensen's inequality applied to $\log(1+r)$, if you want a name.) Report a strategy's mean daily return and you are already lying about its annualized performance.

## Log returns make the math clean

Define the **log return** over one period:

$$
\ell_t = \log\!\left(\frac{p_t}{p_{t-1}}\right) = \log p_t - \log p_{t-1}.
$$

Now multi-period compounding telescopes into **addition**:

$$
\log\frac{p_n}{p_0} = \sum_{t=1}^{n} \ell_t.
$$

Three wins:

1. **Additive across time.** The sum of daily log returns equals the total log return. Averages behave: the mean daily log return times $n$ is exactly the $n$-day log return (in expectation under iid, exactly in realization).
2. **Symmetric.** A $+10\%$ log move is exactly reversed by a $-10\%$ log move. Arithmetic returns are not symmetric — a 10% gain followed by a 10% loss is a 1% net loss.
3. **Closer to Gaussian.** Log prices under a geometric Brownian motion *are* Gaussian by construction. Real markets are not GBM, but log returns are closer to normal than arithmetic returns are, with thinner tails on the upside and fatter tails on the downside. Models that assume normality work less badly on logs.

## When the difference actually matters

For small moves, $\log(1 + r) \approx r - r^2/2$, so log and arithmetic returns agree to first order. A 1% daily return gives $r = 0.01$ and $\ell \approx 0.00995$ — differing by 5 basis points out of 100.

The gap grows with move size:

| Arithmetic $r$ | Log $\ell$ | Difference |
|---------------|-----------|------------|
| $+1\%$        | $+0.995\%$ | 5 bp       |
| $+10\%$       | $+9.53\%$  | 47 bp      |
| $-10\%$       | $-10.54\%$ | 54 bp      |
| $-30\%$       | $-35.67\%$ | 567 bp     |

For daily bars in liquid markets, either convention gets you roughly the same intuition. For weekly or longer bars, for drawdown accounting, or for any nonlinear statistic (**volatility especially**, see the next lesson), use logs.

## What the trading project actually uses

The [triple-barrier method](../ml/triple-barrier.md) in this project computes labels using arithmetic returns: `(p_t / p_0 - 1) * side`. That is the convention in AFML ch. 3.1, and it matches the way the barriers themselves are stated — as multiples of a rolling-vol target also computed from arithmetic returns. Keeping both in the same units is the point; mixing would quietly miscalibrate every label.

This is a deliberate choice, not a bug. When you read the code, remember: **arithmetic returns everywhere inside the labeling pipeline, so barriers and vol compare in the same units**. Annualized performance metrics (Sharpe, Sortino) over a *series* of such returns are still close enough to the log-based versions to not distort, at daily horizon.

## What you can now reason about

- Why a strategy's cumulative return is not the mean daily return times the number of days.
- Why a paper reports Sharpe of 1.2 on log returns and you get 1.19 on arithmetic — same strategy, different unit convention.
- Why options pricing (next part of this curriculum) assumes log-normal terminal prices, not normal.

## Implemented at

`trading/packages/afml/src/afml/labeling.py:41` — `rolling_vol(prices, span=100)` computes EWM std of arithmetic `pct_change` returns. The docstring cites AFML ch. 3.1 explicitly. The choice is load-bearing: downstream, `apply_triple_barrier` at line 52 compares `(p/p0 - 1)` against `mult * sigma`, so vol **must** be in arithmetic-return units or the thresholds will not mean what they claim.

---

**Next:** [Volatility as a measurable thing →](volatility.md)
