---
title: "Deflated Sharpe"
prereqs: "Sharpe, Sortino, max drawdown; Walk-forward vs k-fold"
arrives_at: "the multiple-testing-corrected Sharpe — the number you can actually report"
code_ref: "trading/packages/harness/src/harness/metrics.py — deflated_sharpe (NotImplementedError stub)"
---

# Deflated Sharpe

A Sharpe of 1.5 on a single backtest is a meaningful result. A Sharpe of 1.5 as the best of 100 backtests is less informative than noise. The difference is multiple testing, and the Deflated Sharpe Ratio (DSR) is the statistical correction that turns a raw Sharpe into an honest headline.

DSR is one of the most consequential checks between "backtest looks promising" and "live trading stands a chance."

## The multiple-testing trap

Trying 100 strategy variants — different parameters, features, or signals — and selecting the best-Sharpe result without adjustment produces biased estimates. If the true Sharpe of every strategy is zero (pure noise), the expected Sharpe of the best is substantially positive.

With 100 iid noise trials of 252 daily returns each, the expected maximum sample Sharpe is roughly 0.8. With 1,000 trials, approximately 1.0. With 10,000 trials — easily reached by automated hyperparameter grids — more than 1.2.

These Sharpe ratios can be generated from pure random data by trying enough trials. The best-of-N sample is not a sample from the underlying distribution; it is a sample from the maximum of N draws, which has a fundamentally different (and much higher) mean.

## Expected maximum Sharpe under the null

Bailey & López de Prado derived an approximation for the expected maximum Sharpe across $N$ iid trials, assuming the true Sharpe of each is zero with cross-trial standard deviation $\sigma_{SR}$:

$$
\mathbb{E}[\max \text{SR}] \approx \sigma_{SR} \left[ (1 - \gamma) \Phi^{-1}\!\left(1 - \tfrac{1}{N}\right) + \gamma\, \Phi^{-1}\!\left(1 - \tfrac{1}{N e}\right) \right]
$$

where:

- $\gamma \approx 0.5772$ is the Euler-Mascheroni constant.
- $\Phi^{-1}$ is the inverse standard normal CDF (the quantile function).
- $\sigma_{SR}$ is the standard deviation of *true* Sharpe ratios across the trials (often estimated from the empirical spread across trials, or assumed from theory).

The intuition: drawing $N$ iid samples from a distribution yields a maximum of approximately $\sigma_{SR}$ times the $(1 - 1/N)$ quantile of the standard normal. The Euler-Mascheroni blend captures a correction in the precise location of the expected maximum for iid samples. The derivation appears in Bailey & López de Prado, *The Deflated Sharpe Ratio*, 2014.

A key observation: $\mathbb{E}[\max \text{SR}]$ grows rapidly in $N$. For $\sigma_{SR} = 0.5$ (a reasonable value for a cross-section of strategy variants):

| $N$ | $\mathbb{E}[\max \text{SR}]$ (approximate) |
|-----|--------------------------------------------|
| 1 | 0.00 |
| 10 | 0.66 |
| 100 | 1.22 |
| 1,000 | 1.59 |
| 10,000 | 1.92 |

After 1,000 strategy trials, the expected best-case Sharpe under pure noise is 1.59. Reporting an unadjusted Sharpe of 1.5 from a grid search of this size falls within the null distribution's expected range.

## Non-normality correction

A second correction. Sharpe's sampling distribution assumes Gaussian returns; real returns have skew and kurtosis. The denominator of the Sharpe test statistic understates variance for non-Gaussian distributions, inflating the reported statistic.

The correction uses sample skewness $\hat\gamma_3$ and excess kurtosis $\hat\gamma_4$:

$$
\sigma(SR) \approx \sqrt{\frac{1 - \hat\gamma_3 \cdot SR + \frac{\hat\gamma_4}{4} \cdot SR^2}{T - 1}}
$$

where $T$ is the sample size (number of observations used to compute Sharpe). This is the "Mertens-Bailey" variance approximation for Sharpe ratios under non-normality. Negative skew and fat tails both widen the confidence interval on the Sharpe.

## The DSR itself

Put it together. Given:

- An observed Sharpe $\widehat{SR}$ for a specific strategy.
- $N$ the number of strategies tried (including unsuccessful ones).
- $\sigma_{SR}$ the cross-trial std of trial Sharpes.
- $\hat\gamma_3$, $\hat\gamma_4$ sample skew and excess kurtosis of the selected strategy's returns.
- $T$ the number of return observations in the sample.

The **Deflated Sharpe Ratio** is:

$$
\text{DSR} = \Phi\!\left( \frac{(\widehat{SR} - \mathbb{E}[\max \text{SR}]) \sqrt{T - 1}}{\sqrt{1 - \hat\gamma_3 \widehat{SR} + \frac{\hat\gamma_4}{4} \widehat{SR}^2}} \right).
$$

DSR is a probability in $(0, 1)$: the probability that the true Sharpe of the selected strategy exceeds zero, conditional on (a) the observed statistic, (b) the number of trials, and (c) the non-normality of the returns. Values near 1 indicate that the observed Sharpe substantially exceeds what the null would produce. Values near 0.5 are indistinguishable from chance. Values below 0.5 indicate that the observed Sharpe is below the null's expected level (which can occur for weak strategies with positive raw Sharpe).

A common threshold: a strategy is "statistically meaningful" when $\text{DSR} > 0.95$. Below this threshold, the Sharpe should be treated with skepticism.

## Worked interpretation

Suppose you ran 200 strategy variants, and the best one had:

- $\widehat{SR} = 1.8$ (annualized, on $T = 1{,}260$ daily observations = 5 years).
- Sample skewness $\hat\gamma_3 = -0.5$ (mild negative skew, typical for short-vol strategies).
- Sample excess kurtosis $\hat\gamma_4 = 2.0$ (fatter tails than normal).
- Cross-trial $\sigma_{SR} = 0.4$.

Compute $\mathbb{E}[\max \text{SR}]$ for $N = 200$, $\sigma_{SR} = 0.4$: approximately $1.24$.

Compute the denominator: $\sqrt{1 - (-0.5)(1.8) + (2.0/4)(1.8)^2} = \sqrt{1 + 0.9 + 1.62} = \sqrt{3.52} \approx 1.88$.

Plug in: $(1.8 - 1.24) \cdot \sqrt{1259} / 1.88 \approx 0.56 \cdot 35.5 / 1.88 \approx 10.6$.

$\Phi(10.6) \approx 1.0$ (within rounding). DSR = effectively 1 — the observed Sharpe is very significantly above the multiple-testing null.

Now change one input. Suppose the strategy had $\widehat{SR} = 1.3$ instead of 1.8. Recompute:

Denominator: $\sqrt{1 + 0.65 + 0.85} = \sqrt{2.5} \approx 1.58$.

Plug: $(1.3 - 1.24) \cdot 35.5 / 1.58 \approx 1.35$.

$\Phi(1.35) \approx 0.91$. DSR = 0.91 — below the 0.95 threshold. The 1.3 Sharpe is plausibly at the edge of what the best-of-200 null would produce; it doesn't meet the statistical bar for "real edge."

These numbers are tightly spaced by design. Raw Sharpe changes of 0.5 can shift DSR from "probably real" to "probably noise" on N = 200 trials.

## What counts as a trial

Operationalizing DSR requires care in counting $N$. The value should be the total number of distinct strategy variants considered, not only the ones retained for the final report. Trials include:

- Every hyperparameter combination in any grid search.
- Every signal tried and discarded.
- Every feature set tried and discarded.
- Every manual parameter adjustment made after viewing intermediate results (for example, trying `pt_mult = 1.5` after observing results for `pt_mult = 2.0`).

The last category is the most difficult to track. Each time backtest output is examined and a change is made, a trial has been consumed. DSR assumes trials are counted. Researchers commonly address this by pre-registering the parameter space — declaring in advance which combinations will be tried — so that $N$ is a known quantity.

Without pre-registration, a conservative lower bound on $N$ is the number of combinations in the final grid plus any combinations tried in prior sessions. The true upper bound is typically much larger. DSR with overstated $N$ is conservative; with understated $N$, it is optimistic. Conservative estimates are preferred.

## The harness implementation

The trading project's `harness.metrics.deflated_sharpe` is a `NotImplementedError` stub. The module includes partial machinery — `expected_max_sharpe(num_trials, std_across_trials)` at line 120 — but the full DSR with the non-normality correction is not yet implemented.

This item remains on the curriculum's to-do list. When implemented, the sweep script in `scripts/sweep_meta_rsi2.py` should report DSR at the tested $N$ in addition to the distribution of raw Sharpes. The distinction between "25/25 cells beat primary" and "25/25 cells beat the multiple-testing-adjusted null" separates the current sweep from a deployment-grade stability check.

## Summary

The reader can now reason about:

- Why reporting a Sharpe without disclosing the number of strategies tried is misleading: multiple-testing bias is substantial at realistic grid-search sizes.
- The two corrections that convert a raw Sharpe into a DSR: multiple testing (comparison with $\mathbb{E}[\max \text{SR}]$) and non-normality (adjusted variance via skewness and kurtosis).
- Why trial counting is operationally difficult: every discarded variant counts, including manual adjustments. Pre-registration of the search space is the cleanest remedy.

## Implemented at

`trading/packages/harness/src/harness/metrics.py`:

- Line 83: `deflated_sharpe(returns, num_trials, annualization)` — currently `raise NotImplementedError`. Docstring summarizes the required derivation (non-normality correction + E[max SR] expression).
- Line 120: `expected_max_sharpe(num_trials, std_across_trials)` — the Bailey-López de Prado E[max SR] formula implemented and exported for diagnostics. This is ready to wire into the full DSR when it's written.

Writing the full DSR is the one outstanding piece that matters most for the trading project's statistical discipline. Until it exists, the project's Sharpe reports are honest about their assumptions but incomplete on the discount.

---

**Next:** [The labeling problem →](../ml/labeling-problem.md)
