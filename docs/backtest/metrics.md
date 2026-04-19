---
title: "Sharpe, Sortino, max drawdown"
prereqs: "Returns, compounding, log-returns; Volatility as a measurable thing"
arrives_at: "the metrics every strategy report lists, and their failure modes"
code_ref: "trading/packages/harness/src/harness/metrics.py"
---

# Sharpe, Sortino, max drawdown

A strategy produces a return series. The question of whether the strategy worked requires a small number of summary statistics. The metrics catalog below is the minimum viable set — the quantities that every backtest report should include, and the ones allocators expect. Each has a clean definition, a specific measurement target, and a specific failure mode. This lesson emphasizes the failure modes.

## Sharpe ratio

The definition:

$$
\text{Sharpe} = \frac{\bar r - r_f}{\sigma_r} \sqrt{A}
$$

where $\bar r$ is mean per-period excess return, $\sigma_r$ is its standard deviation, $r_f$ is the risk-free rate per period, and $A$ is the annualization factor (252 for daily U.S. equity, 52 for weekly, 12 for monthly).

Interpretation: how many standard deviations does the annualized mean return exceed zero (or the risk-free rate)? A Sharpe of 1.0 indicates that the strategy's average return equals one unit of its own volatility. A Sharpe of 2.0 indicates twice that edge per unit of risk. Higher values are better.

Approximate reference levels:

| Sharpe | Typical interpretation |
|--------|------------------------|
| < 0 | Losing money |
| 0 – 0.5 | Poor; barely differs from noise |
| 0.5 – 1.0 | Modest; viable with scale |
| 1.0 – 1.5 | Good; tradeable book |
| 1.5 – 2.5 | Very good; institutional quality |
| > 2.5 | Exceptional; warrants scrutiny for look-ahead bias |

Backtest Sharpes tend to exceed live-trading Sharpes. [Deflated Sharpe](deflated-sharpe.md) in a later lesson quantifies the gap.

### Failure modes of Sharpe

1. **Symmetric volatility penalty.** Sharpe penalizes upside volatility as heavily as downside. A strategy with occasional large positive returns and steady losses produces a lower Sharpe than one with no volatility and small steady gains, even when the first strategy has better utility for most investors.

2. **No tail sensitivity.** Sharpe uses only the first and second moments. Two strategies with identical Sharpes can have very different distributions — one with thin symmetric tails, the other with a fat left tail. Sharpe treats them as equivalent.

3. **iid assumption.** The formula assumes returns are independent across time. When they are not (momentum strategies have positive autocorrelation; mean-reversion has negative), Sharpe misreports the risk-adjusted return.

4. **Bias under non-normality.** For strategies with negatively skewed returns (many short-volatility and tail-risk strategies), the observed Sharpe in quiet periods overstates the long-run Sharpe, because the correcting tail event has not yet occurred.

5. **Multiple testing.** Given many strategies, the best-Sharpe one is likely the luckiest rather than the best. The deflated-Sharpe lesson quantifies this effect.

## Sortino ratio

A partial remedy for the symmetric-volatility issue. Only downside deviation enters the denominator:

$$
\text{Sortino} = \frac{\bar r - \tau}{\sigma_\text{down}} \sqrt{A}, \qquad \sigma_\text{down} = \sqrt{\mathbb{E}\!\left[\min(r - \tau, 0)^2\right]}.
$$

Here $\tau$ is a target return (usually zero). $\sigma_\text{down}$ includes only below-target deviations, so upside volatility no longer penalizes the metric. Sortino is always at least equal to Sharpe under symmetric distributions, and strictly greater under positive skew.

Sortino aligns more closely with most investors' utility (positive volatility is desirable, negative volatility is not). It retains many of Sharpe's other failure modes: no tail sensitivity beyond the second downside moment, iid assumption, and multiple-testing bias.

## Max drawdown

$$
\text{MaxDD} = \min_{t \le T}\left(\frac{V_t - \max_{s \le t} V_s}{\max_{s \le t} V_s}\right)
$$

where $V_t$ is the equity curve at time $t$. Max drawdown is the peak-to-trough worst loss, expressed as a non-positive fraction. A value of −0.15 corresponds to a 15% drawdown.

Max drawdown is the metric most allocators reference in practice. The question "what is the worst I could have lost holding this?" drives allocation decisions. A strategy with Sharpe 2.0 and max DD of 40% is typically harder to place than one with Sharpe 1.2 and max DD of 15%.

Max drawdown should be paired with recovery time — the duration required to regain the prior peak — for a complete loss profile. A 20% drawdown that recovers in a month differs materially from one that takes three years.

## Turnover

Mean absolute position change per period:

$$
\text{Turnover} = \mathbb{E}\!\left[|p_t - p_{t-1}|\right].
$$

A strategy that holds a position indefinitely has turnover 0. A strategy that flips fully each day has turnover 2 (|+1 − (−1)|, averaged). Turnover does not appear directly in Sharpe, but it controls costs: transaction costs scale with turnover, and gross Sharpe minus costs can differ materially from gross Sharpe alone.

Two strategies with identical gross Sharpe but different turnover will have different net-of-costs Sharpe. The lower-turnover strategy often performs better live than the backtest suggests. The harness's `apply_costs` function applies a per-turnover-unit cost so that net-of-friction returns enter the Sharpe calculation.

## Capacity

A strategy is capacity-limited when scaling its notional size materially degrades its returns through slippage. Two mechanisms contribute:

1. **Market impact.** Orders move prices against themselves. Almgren-Chriss and similar models parameterize this; `packages/harness/src/harness/costs.py:AlmgrenChriss` implements a standard version.
2. **Liquidity.** Some edges exist only in illiquid market segments where small sizes can be transacted. Scaling up eliminates the edge.

The capacity estimate in `metrics.py:capacity_estimate` is a stub. The intended method: determine the notional position at which slippage erodes 50% of the realized Sharpe. Above this capacity, trading amounts to noise plus friction.

## Deflated Sharpe (preview)

Selecting the best-Sharpe strategy from 100 trials is cherry-picking. Bailey & López de Prado's deflated Sharpe ratio corrects for this:

$$
\text{DSR} = \mathbb{P}(\text{true SR} > 0 \mid \text{observed SR}, N \text{ trials})
$$

— the probability that the true Sharpe exceeds zero given the observed statistic and the number of trials. [The dedicated lesson](deflated-sharpe.md) provides the derivation. At this point the summary is sufficient: raw Sharpes are optimistic, and DSR provides the honest discount.

## Selecting metrics

No single metric is complete. A standard strategy report includes:

- Sharpe for the risk-adjusted return headline.
- Sortino for a downside-only view.
- Max DD and recovery time for worst-case characterization.
- Turnover and net-of-costs Sharpe for the live-trading projection.
- Higher moments (skewness, kurtosis) when distributions deviate from Gaussian.
- DSR when hyperparameter sweeps are involved.

Reporting only Sharpe is not incorrect but omits information. More of the above produces a more faithful picture.

## Annualization conventions

The $\sqrt{A}$ factor derives from the additive-variance argument in [Lesson 2](../measurable/volatility.md). Standard conventions:

- Daily equity returns: $A = 252$ (trading days per year). Some practitioners use $A = 250$ or $A = 260$; the differences are immaterial.
- Weekly: $A = 52$.
- Monthly: $A = 12$.
- Already-annualized inputs: $A = 1$.
- Crypto (continuous trading): $A = 365$.

Incorrect annualization is a common source of error. The metrics functions default to $A = 252$ and accept overrides, so the annualization choice is explicit rather than assumed.

## Summary

The reader can now reason about:

- Why a Sharpe of 2.0 with 40% max DD differs materially from Sharpe 1.5 with 15% max DD for allocation purposes.
- Why turnover matters even when absent from the Sharpe formula: it controls net-of-costs returns, and gross Sharpe minus costs can be significantly lower than gross Sharpe alone.
- The five failure modes of Sharpe (symmetric vol penalty, no tail sensitivity, iid assumption, non-normal bias, multiple testing) and which are partially addressed by other metrics.

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
