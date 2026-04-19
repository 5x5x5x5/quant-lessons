---
title: "Random walks and the null model"
prereqs: "Volatility as a measurable thing"
arrives_at: "the baseline hypothesis every strategy must beat, and the assumption every option-pricing model leans on"
code_ref: "—"
---

# Random walks and the null model

Every strategy you build competes against a specific claim: **tomorrow's price is today's price plus noise**. That claim has a name — the random walk — and it shapes the math of almost every model downstream.

The random walk is not a prediction. It's a *baseline*. If your strategy produces returns indistinguishable from noise on top of a walk, you have no edge. If it reliably deviates, you might.

## From coin flips to continuous paths

Imagine a coin-flip game on log-prices. At each step $t$, the log-price changes by $+\sigma$ with probability $1/2$ or $-\sigma$ with probability $1/2$. After $n$ steps:

$$
\log S_n - \log S_0 = \sum_{t=1}^{n} \epsilon_t, \qquad \epsilon_t \in \{+\sigma, -\sigma\}.
$$

Two things happen as $n$ grows:

1. The *mean* of the sum stays at zero (fair coin).
2. The *standard deviation* of the sum grows as $\sigma \sqrt{n}$ — the same $\sqrt{T}$ law from [the previous lesson](volatility.md).

Shrink the step size and shrink the time between steps, keeping the total variance per unit time fixed. The Central Limit Theorem gives you a limit distribution that is Gaussian, with variance growing linearly in time. That limit is **Brownian motion**:

$$
W_t \sim \mathcal{N}(0, t), \qquad W_{t+s} - W_t \sim \mathcal{N}(0, s), \text{ independent of } \mathcal{F}_t.
$$

Two properties to internalize: Brownian increments are independent (memoryless), and their variance is proportional to the time elapsed (the $\sqrt{T}$ law in continuous form).

## Drift and the log-price walk

Actual markets drift upward over long horizons (the equity risk premium). The cleanest model that combines drift + Gaussian noise + the fact that prices can't go negative is **geometric Brownian motion** (GBM). In terms of price:

$$
dS_t = \mu S_t\, dt + \sigma S_t\, dW_t.
$$

Equivalently, on log-price (this is what the arithmetic of log-returns gives you):

$$
d(\log S_t) = \left(\mu - \tfrac{1}{2}\sigma^2\right) dt + \sigma\, dW_t.
$$

The $-\frac{1}{2}\sigma^2$ correction is the one piece of GBM that surprises people. The reason it appears: $\log S_t$ is a concave function of $S_t$, so applying Itô's lemma (or equivalently, a second-order Taylor expansion) to compute the drift on log-prices from the drift on prices picks up a variance term. Consequence: the **geometric mean** of returns (which is what you actually compound) is less than the arithmetic mean by approximately $\sigma^2/2$. Ignore this and your long-horizon forecasts from a daily-return estimate will be systematically too high.

## What this model assumes, and where it fails

GBM is clean. Markets are not. The places the model breaks matter because they're where strategies live:

- **Fat tails.** GBM predicts that 4-sigma daily moves happen roughly once every 15,000 trading days. In reality, SPY sees several per decade. Equity returns have higher kurtosis than a Gaussian — the tails are fatter and the peak is taller.
- **Volatility clustering.** GBM assumes constant $\sigma$. As the previous lesson noted, $\sigma$ itself is serially correlated in real data. Models that capture this (GARCH, stochastic vol) are GBM's empirical children.
- **Leverage effect.** Negative returns increase future vol more than positive returns of the same magnitude. GBM is symmetric; markets aren't.
- **Jumps.** GBM paths are continuous — no gaps. Real prices gap overnight, around earnings, at the open after news. Jump-diffusion and Lévy processes are the statistical patches.
- **Short-horizon autocorrelation.** GBM increments are independent. Intraday returns exhibit weak negative autocorrelation (mean reversion on 1-5 minute bars); some regimes show positive autocorrelation at longer horizons. Small in magnitude, but non-zero.

These are not footnotes — they are the subject matter of most serious quant research. Recognize them as **places GBM is wrong**, not as reasons to distrust the model entirely. The model is still the right baseline; the strategies are the deviations from it.

## Why the null matters for backtesting

Here is the operational point. When you compute the Sharpe ratio of a strategy, you are asking: **how many standard deviations away from zero is the mean return?** The "standard deviation" in the denominator implicitly assumes something like iid Gaussian noise around a constant mean — the random-walk null. The more your strategy's returns deviate from iid (autocorrelated, non-Gaussian, heteroskedastic), the less a Sharpe of 1.0 means what you think it means.

This is not academic. Strategies that concentrate their edge into rare large wins (event-driven, short-vol) produce non-Gaussian return distributions that a Sharpe ratio systematically under- or over-rewards. [Deflated Sharpe](../backtest/deflated-sharpe.md) in Part 6 partially corrects for this with skewness and kurtosis terms. Not fully — no single number captures a non-iid return series — but enough to be honest about.

## Options pricing and the log-normal assumption

Black-Scholes, covered in [Part 2](../options/black-scholes.md), starts from GBM. The option price at expiry depends on the terminal distribution of $S_T$, which under GBM is **log-normal** (not normal):

$$
\log S_T \sim \mathcal{N}\!\left(\log S_0 + (\mu - \tfrac{1}{2}\sigma^2) T, \; \sigma^2 T\right).
$$

Two consequences worth sitting with:

1. Terminal price is always non-negative (log-normal has support on $(0, \infty)$). Prices can't go below zero under GBM, which matches the real world for cash equities.
2. Options pricing models that assume a single constant $\sigma$ for all strikes produce a flat implied vol surface. The observed surface is not flat (Part 4: skew, smile, term structure). The deviations from GBM show up as a shape on the vol surface — that shape is itself tradable information.

## What "alpha" means under the null

You'll read "alpha" in papers, in strategy writeups, in performance attribution. Mathematically, alpha is the systematic return you earn *above* what the null would predict. If you regress your returns on market returns:

$$
r_\text{strat} = \alpha + \beta\, r_\text{market} + \epsilon,
$$

then $\alpha$ is the intercept — the expected return when market returns are zero. A strategy with a statistically significant non-zero $\alpha$ is earning something the market exposure alone doesn't explain. **That's the thing a random walk cannot produce.** Finding real $\alpha$ is hard, which is why everything in Part 6 (Sharpe, walk-forward, deflated Sharpe) exists: to avoid being fooled by noise into thinking you found it.

## What you can now reason about

- Why options pricing models assume log-normal terminal prices, not normal ones — and why the $-\sigma^2/2$ correction appears on the drift of log-price.
- Why forecasting next-day return is structurally hard: you're predicting deviations from a walk whose expectation over a single day is tiny relative to its noise.
- Why "my strategy has Sharpe > 2" is less impressive than it sounds if the returns are highly non-Gaussian or serially correlated — the null has assumed them away, so the statistic is measuring something that isn't quite what you want.

## Implemented at

The null is assumed, not computed. You'll find it everywhere:

- `trading/packages/harness/src/harness/metrics.py:19` — `sharpe(returns)` compares mean to std, implicitly against a zero-mean iid null.
- `trading/packages/gex/src/gex/greeks.py` — uses Black-Scholes, which lives inside GBM.
- `trading/packages/afml/src/afml/structural.py` — `cusum_events`, `chow_dfc_stat` are **tests** for deviation from the random-walk null. Their job is to flag when the null breaks.

The random walk is the baseline every piece of code above is either leaning on or testing.

---

**Next:** [The options contract →](../options/contracts.md)
