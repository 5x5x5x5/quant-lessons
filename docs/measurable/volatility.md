---
title: "Volatility as a measurable thing"
prereqs: "Returns, compounding, log-returns"
arrives_at: "σ — the denominator of every Sharpe ratio and the unit of every vol-scaled barrier"
code_ref: "trading/packages/afml/src/afml/labeling.py:41 — rolling_vol"
---

# Volatility as a measurable thing

Ask a trader what the market did today and you'll often hear two numbers: how much it moved, and how *wiggly* the path was. The first is return. The second is volatility. Volatility is not "how much the price changed" — it's "how spread out the changes were."

Formally, **volatility is the standard deviation of returns**:

$$
\sigma = \sqrt{\mathbb{E}\!\left[(r_t - \bar r)^2\right]}.
$$

This is the one number that appears in every risk metric you will compute, every option you will price, and every vol-scaled label you will generate. Getting it right matters.

## Realized vs implied

Two entirely different things share the word "volatility":

- **Realized volatility** is what we just defined — the std of observed returns. Computable from price history alone.
- **Implied volatility** is the $\sigma$ you back out of an option's market price by inverting Black-Scholes. It's a forecast — the market's guess about *future* realized vol — not a measurement.

This lesson is about realized vol. Implied vol gets its own part of the curriculum ([Part 4](../vol-surface/implied-vol.md)); the two diverge in important ways and conflating them will make most of what you read about options confusing.

## Sample std vs exponentially weighted std

Given $n$ recent returns, the textbook **sample standard deviation** weights every observation equally:

$$
\hat\sigma^2 = \frac{1}{n - 1} \sum_{t=1}^{n} (r_t - \bar r)^2.
$$

Equal weighting is wrong for markets. A return from yesterday is much more relevant to today's risk than a return from 100 days ago, but a sample std window of 100 days treats them as identical. When the regime shifts — February 2020, March 2023, any Fed day — a flat-weighted vol estimator takes its full window to "see" the change. By the time the estimate has moved, the information is stale.

The **exponentially-weighted moving (EWM) std** fixes this by giving recent observations more weight:

$$
\hat\sigma^2_t = (1 - \alpha)\, \hat\sigma^2_{t-1} + \alpha\, (r_t - \mu_t)^2,
\quad \alpha = \frac{2}{\text{span} + 1}.
$$

At `span=100`, today's squared deviation contributes about 2% and the weight decays geometrically backward. A regime shift propagates into the estimate almost immediately instead of being averaged out over a full window. The `span` parameter is the EWM equivalent of a rolling-window length; the conversion to $\alpha$ above is a pandas/polars convention.

## Annualization: why $\sqrt{T}$?

You usually care about annual vol (20% is "SPY in a normal year") but compute daily vol directly. The rule you hear quoted is:

$$
\sigma_\text{annual} = \sigma_\text{daily} \cdot \sqrt{252}.
$$

Where does the square root come from? If daily returns are iid, the variance of the $T$-day cumulative return is $T$ times the daily variance (variance adds under independence). Volatility, being the square root of variance, scales as $\sqrt{T}$. That gives the `252` for U.S. equities (trading days per year).

**The assumption is wrong in two ways**, and you should know where:

1. **Returns are not iid.** Markets exhibit volatility clustering: quiet periods and stressed periods group together (ARCH, GARCH effects). The daily variance is time-varying, which breaks the "variance adds" argument.
2. **Returns are not independent across time.** Intraday, they are weakly negatively autocorrelated (mean reversion on short horizons); over multi-month horizons, a small positive autocorrelation shows up in some regimes. Real variance of $T$-day cumulative return is *not* exactly $T \cdot \sigma^2_\text{daily}$.

For daily frequencies and modestly long horizons, $\sqrt{T}$ is close enough that nobody bothers correcting. For monthly-to-annual, or for regime-switching strategies, the error matters.

## Volatility clustering — the stylized fact

One empirical observation shapes almost every model you'll meet downstream: **big moves follow big moves, and calm follows calm**. Volatility is itself serially correlated even when returns aren't. A random-walk null can't produce this pattern; GARCH-family models exist specifically to capture it.

Practical consequence: when realized vol spikes, your probability of another big move tomorrow is elevated. Strategies that ignore this produce backtests that look smoother than live trading, because stress episodes get averaged into calm ones during training.

## A concrete example

SPY daily returns, 2020 calendar year:

- Full-year sample std of arithmetic returns: ~2.1% per day → annualized ~33%.
- EWM (`span=100`) std through March 2020: peaks near ~5% per day → annualized ~80%.
- EWM through December 2020: ~0.8% per day → annualized ~13%.

The full-year sample std is the average of those regimes. If you're sizing a position based on "current" risk, the average is the wrong number — you want the EWM.

## What the trading project actually uses

The triple-barrier labeling pipeline computes a per-event vol target that the barriers are calibrated against. It does so with an EWM std of **arithmetic** returns:

```python
def rolling_vol(prices: pl.Series, span: int = 100) -> pl.Series:
    returns = prices.pct_change()
    return returns.ewm_std(span=span)
```

Two choices encoded here:

- **EWM, not sample.** The project is explicitly willing to let recent data dominate. This keeps barrier thresholds adaptive: a 2σ barrier in 2017 is a smaller dollar amount than a 2σ barrier in March 2020, by design.
- **Arithmetic, not log.** As covered in [the previous lesson](returns.md), barriers compare `p_t / p_0 - 1` against `mult * sigma`; both must be in arithmetic-return units or the thresholds don't mean what they claim.

## What you can now reason about

- Why a strategy's live Sharpe often looks different from its backtest Sharpe even when nothing changed — vol regime shifted and sample std took weeks to catch up.
- Why options traders care more about realized-vs-implied spreads than the level of either — vol is a *forecast* when implied, a *measurement* when realized, and they tell different stories.
- Why the $\sqrt{T}$ rule works well enough day-to-day but breaks in regimes you especially care about (post-spike backward projection, multi-month holding).

## Implemented at

`trading/packages/afml/src/afml/labeling.py:41` — `rolling_vol(prices, span=100)`. EWM std of arithmetic returns; used by `apply_triple_barrier` on the same line 52 file to scale barrier thresholds per event. The docstring cites AFML ch. 3.1 to make the arithmetic-return choice explicit.

---

**Next:** [Random walks and the null model →](random-walks.md)
