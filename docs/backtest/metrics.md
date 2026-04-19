---
title: "Sharpe, Sortino, max drawdown"
prereqs: "Returns, compounding, log-returns; Volatility as a measurable thing"
arrives_at: "the metrics every strategy report lists, and their failure modes"
code_ref: "trading/packages/harness/src/harness/metrics.py"
---

# Sharpe, Sortino, max drawdown

A strategy produces a return series. You want one or two numbers that summarize "did this work." The metrics catalog below is the minimum viable set — the numbers every backtest report needs, and the ones every allocator expects. Each has a clean definition, a specific thing it measures, and a specific failure mode. The failure modes are what this lesson is really about.

## Sharpe ratio

The definition:

$$
\text{Sharpe} = \frac{\bar r - r_f}{\sigma_r} \sqrt{A}
$$

where $\bar r$ is mean per-period excess return, $\sigma_r$ is its standard deviation, $r_f$ is the risk-free rate per period, and $A$ is the annualization factor (252 for daily U.S. equity, 52 for weekly, 12 for monthly).

Interpretation: **how many standard deviations away from zero (or the risk-free rate) is the strategy's mean return, annualized?** A Sharpe of 1.0 means the strategy's average return is one unit of its own volatility. Sharpe of 2.0 is twice as many standard deviations of edge per unit of risk. Higher is better.

Reference levels, roughly:

| Sharpe | Typical interpretation |
|--------|------------------------|
| < 0 | Losing money |
| 0 – 0.5 | Poor; barely differs from noise |
| 0.5 – 1.0 | Modest; viable with scale |
| 1.0 – 1.5 | Good; tradeable book |
| 1.5 – 2.5 | Very good; institutional quality |
| > 2.5 | Exceptional; scrutinize for look-ahead |

Real-world backtest Sharpes often appear larger than real-world live Sharpes. This is not mysterious — [deflated Sharpe](deflated-sharpe.md) in a later lesson explains why.

### Sharpe's failure modes

1. **Symmetric vol penalty.** Sharpe punishes upside volatility exactly as much as downside. A strategy with occasional huge positive returns and steady losses has a lower Sharpe than a strategy with no volatility and tiny steady gains — even though the first strategy might have better utility for most investors.

2. **No tail sensitivity.** Sharpe only uses first and second moments (mean and variance). Two strategies with the same Sharpe can have wildly different distributions. One might have thin, symmetric tails; the other might have a fat left tail that blows up once a decade. Sharpe sees them as equivalent.

3. **iid assumption.** The formula assumes returns are independent across time. When they aren't — momentum strategies have positive autocorrelation; mean-reversion has negative — Sharpe under- or over-reports the risk-adjusted return.

4. **Non-normal returns bias.** For strategies with negatively skewed returns (most short-vol / tail-risk strategies), observed Sharpe *in quiet periods* overstates long-run Sharpe, because the tail event that would correct the picture hasn't arrived yet.

5. **Multiple testing.** If you try many strategies, the best-Sharpe one is likely the *luckiest*, not the *best*. The deflated-Sharpe lesson puts a number on this.

## Sortino ratio

A partial fix for the symmetric-vol problem. Use only the downside deviation:

$$
\text{Sortino} = \frac{\bar r - \tau}{\sigma_\text{down}} \sqrt{A}, \qquad \sigma_\text{down} = \sqrt{\mathbb{E}\!\left[\min(r - \tau, 0)^2\right]}.
$$

Here $\tau$ is a target return (usually zero). $\sigma_\text{down}$ uses only the below-target deviations, so positive-return volatility no longer penalizes the metric. Sortino is always ≥ Sharpe when the distribution is symmetric, and strictly greater when the distribution has positive skew.

Sortino is more aligned with most investors' actual utility (they like upside vol and dislike downside vol). It retains many of Sharpe's other failure modes — no tail sensitivity beyond the second downside moment, iid assumption, multiple-testing bias.

## Max drawdown

$$
\text{MaxDD} = \min_{t \le T}\left(\frac{V_t - \max_{s \le t} V_s}{\max_{s \le t} V_s}\right)
$$

where $V_t$ is the equity curve at time $t$. The "peak-to-trough worst loss" expressed as a non-positive fraction (−0.15 means 15% drawdown).

Max drawdown is the metric **most investors actually care about**. "What's the worst I could have lost holding this?" is the question that drives allocation decisions. A strategy with Sharpe 2.0 and max DD of 40% is a harder sell than Sharpe 1.2 and max DD of 15%.

Pair max drawdown with recovery time — how long to regain the prior peak — for the full loss picture. A 20% DD that recovers in a month is a different experience than a 20% DD that takes three years to climb out of.

## Turnover

Mean absolute position change per period:

$$
\text{Turnover} = \mathbb{E}\!\left[|p_t - p_{t-1}|\right].
$$

A strategy that holds one position indefinitely has turnover 0. A strategy that flips fully every day has turnover 2 (|+1 - (-1)|, averaged). Turnover doesn't directly appear in Sharpe, but it controls **costs**: transaction costs scale with turnover, and gross-Sharpe minus costs can differ dramatically from gross Sharpe alone.

Two strategies with identical gross Sharpe but different turnover will have different net-of-costs Sharpe. The lower-turnover one often wins in live trading by a wider margin than the backtest suggested. This is why the harness's `apply_costs` function explicitly applies a per-turnover-unit cost — to produce net-of-friction returns that the Sharpe is computed on.

## Capacity

A strategy is **capacity-limited** if scaling up its notional size significantly degrades its returns via slippage. Two effects drive this:

1. **Market impact.** Your own orders move prices against you. Almgren-Chriss and similar models parameterize this; `packages/harness/src/harness/costs.py:AlmgrenChriss` implements a standard version.
2. **Liquidity.** Some edges exist in illiquid corners of the market where only small sizes can be transacted. When you try to scale, the edge disappears.

The capacity estimate in `metrics.py:capacity_estimate` is a stub. The intended method: compute how large a notional position you can take before slippage erodes 50% of the realized Sharpe. Above capacity, you're trading noise plus friction.

## Deflated Sharpe (preview)

If you try 100 strategies and pick the best-Sharpe one, you've cherry-picked. Bailey & López de Prado's deflated Sharpe ratio corrects for this:

$$
\text{DSR} = \mathbb{P}(\text{true SR} > 0 \mid \text{observed SR}, N \text{ trials})
$$

— the probability that the true Sharpe exceeds zero, given the observed statistic and the number of trials. [The dedicated lesson](deflated-sharpe.md) covers the derivation. For now: single-number Sharpes are optimistic; DSR is the honest discount.

## Choosing the right metric

No single metric dominates. A typical strategy report lists all of them:

- **Sharpe** for the risk-adjusted return headline.
- **Sortino** for a downside-only view.
- **Max DD + recovery time** for the "what's the worst case" question.
- **Turnover + net-of-costs Sharpe** for the real-world picture.
- **Higher moments** (skewness, kurtosis) when return distributions deviate from Gaussian.
- **DSR** when hyperparameter sweeps are involved.

Reporting only Sharpe is not wrong — but it hides things. The more of the above you can provide, the more faithful the picture.

## Annualization, precisely

The $\sqrt{A}$ factor comes from the iid-variance-adds argument in [Lesson 2](../measurable/volatility.md). Standard conventions:

- Daily equity returns: $A = 252$ (trading days per year). Some practitioners use $A = 250$ or $A = 260$ (conservatively); the difference is immaterial.
- Weekly: $A = 52$.
- Monthly: $A = 12$.
- Already-annualized inputs: $A = 1$.
- Crypto (24/7): $A = 365$.

Getting $A$ wrong is a frequent embarrassment. The metrics functions default to $A = 252$ and accept overrides, so the annualization choice is explicit, not assumed.

## What you can now reason about

- Why a Sharpe of 2.0 with 40% max DD is different from Sharpe 1.5 with 15% max DD — different investors, different utility, different decisions.
- Why turnover matters even when it's not in the Sharpe formula — it controls net-of-costs returns, and gross Sharpe minus costs can be much lower than gross Sharpe alone.
- The five failure modes of Sharpe (symmetric vol penalty, no tail sensitivity, iid assumption, non-normal bias, multiple testing) and which of them the other metrics partially address.

## Implemented at

`trading/packages/harness/src/harness/metrics.py`:

- Line 19: `sharpe(returns, annualization=252, risk_free=0)` — annualized Sharpe with a zero-variance edge case.
- Line 38: `sortino(returns, annualization=252, target=0)` — downside deviation variant.
- Line 57: `max_drawdown(equity)` — peak-to-trough worst fraction.
- Line 71: `turnover(positions)` — mean absolute position change.
- Line 83: `deflated_sharpe(returns, num_trials, annualization=252)` — **stub**, raises `NotImplementedError`.
- Line 104: `capacity_estimate(...)` — **stub**, also unimplemented.
- Line 120: `expected_max_sharpe(num_trials, std)` — the Bailey-López de Prado helper used by DSR, partially in place.

The stubs are the curriculum's to-do list. DSR is the single highest-value one to implement — it changes what a strategy report can honestly claim.

---

**Next:** [Walk-forward vs k-fold →](walk-forward.md)
