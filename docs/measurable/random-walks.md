---
title: "Random walks and the null model"
prereqs: "Volatility as a measurable thing"
arrives_at: "the baseline hypothesis every strategy must beat, and the assumption every option-pricing model leans on"
code_ref: "—"
---

# Random walks and the null model

Every strategy competes against a specific null hypothesis: **tomorrow's price equals today's price plus noise**. This is the random walk, and it underlies the mathematics of most downstream models.

The random walk is a baseline, not a forecast. A strategy whose returns are indistinguishable from noise on top of a random walk has no identifiable edge. Reliable deviations from the walk indicate the presence of a signal.

## From coin flips to continuous paths

Imagine a coin-flip game on log-prices. At each step $t$, the log-price changes by $+\sigma$ with probability $1/2$ or $-\sigma$ with probability $1/2$. After $n$ steps:

$$
\log S_n - \log S_0 = \sum_{t=1}^{n} \epsilon_t, \qquad \epsilon_t \in \{+\sigma, -\sigma\}.
$$

Two properties hold as $n$ grows:

1. The mean of the sum remains zero (fair coin).
2. The standard deviation of the sum grows as $\sigma \sqrt{n}$ — the same $\sqrt{T}$ law from [the previous lesson](volatility.md).

Taking the limit as the step size and inter-step time approach zero (holding total variance per unit time fixed), the Central Limit Theorem gives a Gaussian limit distribution with variance growing linearly in time. This limit is **Brownian motion**:

$$
W_t \sim \mathcal{N}(0, t), \qquad W_{t+s} - W_t \sim \mathcal{N}(0, s), \text{ independent of } \mathcal{F}_t.
$$

Two properties follow: Brownian increments are independent (memoryless), and their variance is proportional to elapsed time (the continuous-form analogue of the $\sqrt{T}$ law).

## Drift and the log-price walk

Real markets drift upward over long horizons (the equity risk premium). A standard model combining drift, Gaussian noise, and the constraint that prices remain non-negative is **geometric Brownian motion** (GBM). In price space:

$$
dS_t = \mu S_t\, dt + \sigma S_t\, dW_t.
$$

The equivalent form on log-price is:

$$
d(\log S_t) = \left(\mu - \tfrac{1}{2}\sigma^2\right) dt + \sigma\, dW_t.
$$

The $-\tfrac{1}{2}\sigma^2$ correction on the drift deserves attention. It arises because $\log S_t$ is a concave function of $S_t$; applying Itô's lemma (equivalently, a second-order Taylor expansion) to compute the drift on log-prices from the drift on prices introduces a variance term. A consequence is that the **geometric mean** of returns (the compounded average) is less than the arithmetic mean by approximately $\sigma^2/2$. Long-horizon projections that use a daily-return estimate without this correction overstate expected compounded returns.

## Model assumptions and empirical violations

GBM is mathematically tractable. Markets are not fully consistent with its assumptions, and the deviations are where most quant strategies operate:

- **Fat tails.** GBM predicts that 4-sigma daily moves occur approximately once every 15,000 trading days. In practice, SPY has seen several per decade. Equity returns exhibit higher kurtosis than a Gaussian — fatter tails and a taller central peak.
- **Volatility clustering.** GBM assumes constant $\sigma$. As noted in the previous lesson, $\sigma$ is itself serially correlated in real data. GARCH and stochastic-volatility models extend GBM to capture this.
- **Leverage effect.** Negative returns increase future volatility more than positive returns of equal magnitude. GBM is symmetric in $\pm dW$; real markets are not.
- **Jumps.** GBM paths are continuous. Real prices gap overnight, around earnings, and at the open after news releases. Jump-diffusion and Lévy-process models address this gap.
- **Short-horizon autocorrelation.** GBM increments are independent. Intraday returns show weak negative autocorrelation (short-horizon mean reversion); some regimes exhibit positive autocorrelation at longer horizons. The magnitudes are small but non-zero.

These deviations form the subject matter of much quantitative research. They are specific failure modes of GBM rather than reasons to reject the model entirely. GBM remains a useful baseline; strategies exist as deviations from it.

## The null hypothesis and backtesting

When a Sharpe ratio is computed, the implicit question is: how many standard deviations is the mean return from zero? The denominator assumes iid Gaussian noise around a constant mean — the random-walk null. The further a strategy's returns deviate from iid (through autocorrelation, non-Gaussian distributions, or heteroskedasticity), the less reliable the standard Sharpe interpretation becomes.

This has practical consequences. Strategies that concentrate edge in rare large wins (event-driven, short-volatility) produce non-Gaussian return distributions that the Sharpe ratio systematically misweights. [Deflated Sharpe](../backtest/deflated-sharpe.md) in Part 6 partially corrects for this using skewness and kurtosis terms. No single statistic fully captures a non-iid return series, but the correction is material.

## Options pricing and the log-normal assumption

Black-Scholes, covered in [Part 2](../options/black-scholes.md), is built on GBM. The option price at expiry depends on the terminal distribution of $S_T$, which under GBM is log-normal:

$$
\log S_T \sim \mathcal{N}\!\left(\log S_0 + (\mu - \tfrac{1}{2}\sigma^2) T, \; \sigma^2 T\right).
$$

Two consequences follow:

1. Terminal price is always non-negative (log-normal has support on $(0, \infty)$). Under GBM, prices cannot go below zero, which is consistent with cash equities.
2. Pricing models that assume a single constant $\sigma$ across all strikes produce a flat implied-volatility surface. The observed surface is not flat (Part 4 covers skew, smile, and term structure). Deviations from GBM manifest as shape on the vol surface, and that shape carries tradable information.

## Alpha under the null

The term "alpha" appears in academic papers, strategy writeups, and performance attribution. Mathematically, alpha is the systematic return earned above what the null predicts. Regressing strategy returns on market returns:

$$
r_\text{strat} = \alpha + \beta\, r_\text{market} + \epsilon,
$$

gives $\alpha$ as the intercept: expected return when market returns are zero. A strategy with a statistically significant non-zero $\alpha$ earns returns not explained by market exposure alone. This is precisely the quantity a pure random walk cannot produce. Identifying real $\alpha$ is difficult, which motivates the rigor in Part 6 (Sharpe, walk-forward, deflated Sharpe).

## Summary

The reader can now reason about:

- Why options pricing models assume log-normal terminal prices rather than normal, and why the $-\sigma^2/2$ correction appears in the drift of log-price.
- Why next-day return forecasting is structurally difficult: the target is deviation from a walk whose single-period expectation is small relative to its noise.
- Why a Sharpe above 2 is less informative than it appears when returns are highly non-Gaussian or serially correlated — the standard statistic implicitly assumes these conditions away.

## Implemented at

The null is assumed throughout the trading repository rather than computed explicitly:

- `trading/packages/harness/src/harness/metrics.py:19` — `sharpe(returns)` compares mean to standard deviation, implicitly against a zero-mean iid null.
- `trading/packages/gex/src/gex/greeks.py` — uses Black-Scholes, which operates within GBM.
- `trading/packages/afml/src/afml/structural.py` — `cusum_events` and `chow_dfc_stat` test for deviations from the random-walk null, flagging structural breaks.

The random walk is the baseline that each of these files either assumes or tests against.

---

**Next:** [The options contract →](../options/contracts.md)
