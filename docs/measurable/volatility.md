---
title: "Volatility as a measurable thing"
prereqs: "Returns, compounding, log-returns"
arrives_at: "σ — the denominator of every Sharpe ratio and the unit of every vol-scaled barrier"
code_ref: "trading/packages/afml/src/afml/labeling.py:41 — rolling_vol"
---

# Volatility as a measurable thing

A market's daily activity can be described by two numbers: the total move and the dispersion of that move across the session. The first is return; the second is volatility. Volatility measures the variability of returns, not the magnitude of the final price change.

Formally, **volatility is the standard deviation of returns**:

$$
\sigma = \sqrt{\mathbb{E}\!\left[(r_t - \bar r)^2\right]}.
$$

This quantity appears in every risk metric, every option pricing formula, and every volatility-scaled label in the remainder of the curriculum.

## Realized versus implied volatility

Two distinct quantities share the name "volatility":

- **Realized volatility** — the standard deviation of observed returns, computable from price history alone.
- **Implied volatility** — the $\sigma$ extracted from an option's market price by inverting Black-Scholes. This is a forecast of future realized volatility, not a measurement of past prices.

This lesson addresses realized volatility. Implied volatility is covered in [Part 4](../vol-surface/implied-vol.md). The two differ in important ways, and conflating them leads to confusion when reading options-market commentary.

## Sample standard deviation versus exponentially weighted

Given $n$ recent returns, the sample standard deviation weights every observation equally:

$$
\hat\sigma^2 = \frac{1}{n - 1} \sum_{t=1}^{n} (r_t - \bar r)^2.
$$

Equal weighting is suboptimal for financial time series. A return from yesterday is typically more relevant to today's risk than a return from 100 days ago, but a sample std over a 100-day window treats them as identical. When a regime shift occurs, a flat-weighted estimator requires its full window to incorporate the change, and by then the estimate is stale relative to current conditions.

The **exponentially-weighted moving (EWM) standard deviation** addresses this by weighting recent observations more heavily:

$$
\hat\sigma^2_t = (1 - \alpha)\, \hat\sigma^2_{t-1} + \alpha\, (r_t - \mu_t)^2,
\quad \alpha = \frac{2}{\text{span} + 1}.
$$

With `span=100`, the current squared deviation contributes approximately 2% of the estimate, and weights decay geometrically backward. Regime shifts propagate into the estimate rapidly rather than being averaged across a long window. The `span` parameter is the EWM analogue of a rolling-window length; the conversion to $\alpha$ follows pandas and polars conventions.

## Annualization and the $\sqrt{T}$ rule

Annual volatility is typically the reporting convention (20% is representative for SPY in a normal year), even though daily data is the computed input. The standard conversion is:

$$
\sigma_\text{annual} = \sigma_\text{daily} \cdot \sqrt{252}.
$$

The derivation follows from two assumptions: if daily returns are iid, the variance of the $T$-day cumulative return equals $T$ times the daily variance (variance is additive under independence). Volatility, being the square root of variance, scales as $\sqrt{T}$. The factor 252 reflects U.S. equity trading days per year.

This derivation relies on two assumptions that are empirically violated:

1. **Returns are not iid.** Markets exhibit volatility clustering: quiet periods and stressed periods group together (ARCH and GARCH effects). Daily variance is time-varying, which breaks the additivity argument.
2. **Returns are not serially independent.** Intraday returns show weak negative autocorrelation (short-horizon mean reversion); at longer horizons, small positive autocorrelation appears in some regimes. The true variance of a $T$-day cumulative return is therefore not exactly $T \cdot \sigma^2_\text{daily}$.

For daily frequencies and moderate horizons, the $\sqrt{T}$ approximation is accurate enough that corrections are rarely applied in practice. For monthly-to-annual horizons and for regime-switching strategies, the approximation error becomes material.

## Volatility clustering

An empirical regularity that shapes most downstream models: large moves are followed by large moves, and calm periods are followed by calm periods. Volatility is serially correlated even when returns are not. A random-walk null model cannot reproduce this pattern, which motivated the GARCH family of models.

A practical consequence: when realized volatility spikes, the probability of another large move on the following day is elevated. Strategies that ignore clustering produce backtests that appear smoother than live trading, because stress episodes are averaged into calm ones during training.

## A concrete example

SPY daily returns during the 2020 calendar year:

- Full-year sample std of arithmetic returns: approximately 2.1% per day (annualized approximately 33%).
- EWM (`span=100`) std through March 2020: peaked near 5% per day (annualized approximately 80%).
- EWM through December 2020: approximately 0.8% per day (annualized approximately 13%).

The full-year sample std is an average across these regimes. For position sizing based on current risk conditions, the EWM is the appropriate estimator.

## Convention used in the trading project

The triple-barrier labeling pipeline computes a per-event vol target that the barriers are calibrated against. It uses an EWM standard deviation of arithmetic returns:

```python
def rolling_vol(prices: pl.Series, span: int = 100) -> pl.Series:
    returns = prices.pct_change()
    return returns.ewm_std(span=span)
```

Two design choices are encoded:

- **EWM rather than sample.** Recent data is intentionally given more weight. This keeps barrier thresholds adaptive: a 2σ barrier in 2017 represents a smaller dollar move than a 2σ barrier in March 2020.
- **Arithmetic rather than log.** As covered in [the previous lesson](returns.md), barriers compare `p_t / p_0 - 1` against `mult * sigma`, requiring both quantities to be expressed in arithmetic-return units.

## Summary

The reader can now reason about:

- Why a strategy's live Sharpe can differ from its backtest Sharpe when the volatility regime has shifted and a sample std estimator has not yet caught up.
- Why options traders focus on realized-versus-implied spreads rather than absolute volatility levels: the two quantities carry different information (forecast versus measurement).
- Why the $\sqrt{T}$ rule is accurate at daily horizons but breaks down for multi-month projections and post-spike regimes.

## Implemented at

`trading/packages/afml/src/afml/labeling.py:41` — `rolling_vol(prices, span=100)`. Computes the EWM standard deviation of arithmetic returns and is used by `apply_triple_barrier` (line 52 of the same file) to scale barrier thresholds per event. The docstring cites AFML ch. 3.1 to document the arithmetic-return convention.

---

**Next:** [Random walks and the null model →](random-walks.md)
