---
title: "Implied vol vs realized"
prereqs: "Black-Scholes as a bridge"
arrives_at: "the market's forecast of σ, and why it typically exceeds realized"
code_ref: "—"
---

# Implied vol vs realized

Black-Scholes takes five inputs and produces a price. Four — $S$, $K$, $r$, $T$ — are observable or contractual. The fifth, $\sigma$, is not. The market resolves this by letting observed option premiums define $\sigma$: inverting the formula against market prices yields the **implied volatility** (IV). IV represents a forecast — the market's consensus estimate of realized volatility over the option's remaining life.

This lesson covers what IV measures, how it differs from realized volatility, and the variance risk premium that persists between them.

## Inverting Black-Scholes

Given a market premium $C^\text{mkt}$ for a call with known $S$, $K$, $r$, $T$, the task is to find $\sigma$ such that:

$$
C_\text{BS}(S, K, r, T, \sigma) = C^\text{mkt}.
$$

The Black-Scholes formula is monotonic in $\sigma$ (call price is strictly increasing in vol), so the inversion has a unique solution. Numerical solvers find it in microseconds. The resulting $\sigma$ is the option's implied volatility.

Every option on the chain has its own implied volatility. If Black-Scholes were fully accurate, every option on a given underlying would share a single IV. In practice, IVs vary across strikes (skew, smile) and expiries (term structure). These deviations are the subject of the next two lessons.

## IV is a forecast, not a measurement

The distinction between IV and anything computable from price history is fundamental. IV answers: what volatility over the next $T$ days would justify the current price? It is inherently forward-looking.

IV combines three components in practice:

1. The market's estimate of future realized volatility.
2. A risk premium for bearing volatility risk (sellers require compensation for tail events).
3. Supply-demand imbalances specific to the option (buyer demand for specific protection, dealer inventory effects).

These components cannot be separated from a single IV quote. Comparing IV to subsequent realized volatility across many observations does, however, allow estimation of the average gap between forecast and realization.

## The variance risk premium

A robust empirical pattern emerges: IV tends to exceed subsequent realized volatility on average, particularly for short-dated equity-index options. The difference is known as the variance risk premium (VRP).

| Approximate figures, SPX 30-day, decade-average |                   |
|-------------------------------------------------|-------------------|
| Mean VIX (implied)                              | ~18%              |
| Mean realized 30-day vol                        | ~14%              |
| Mean spread (premium)                           | ~4 percentage points |

The spread is not constant. It compresses to near zero (and occasionally inverts) in quiet regimes, and widens to 10 or more points around events. The unconditional average has remained meaningfully positive across multi-decade samples.

The economic interpretation is that selling options is economically equivalent to selling insurance. The seller receives a small premium in exchange for accepting convex losses in tail events. Risk-averse agents require more premium than actuarial fairness would imply; over time, options carry premiums above their expected payoffs, and sellers profit on average.

Short-volatility strategies harvest the VRP systematically. Writing naked puts, strangles, or variance swaps produces positive unconditional returns, subject to occasional tail losses that erase years of accumulated gains. Long-Term Capital in 1998, Volmageddon in February 2018, and COVID in March 2020 all had short-vol books as central participants. The VRP is real but not free; it compensates for a risk that materializes occasionally.

## VIX — a model-free IV

The CBOE Volatility Index (VIX) is the most widely-quoted implied-volatility summary. It reports a 30-day implied volatility estimate on the S&P 500 without assuming Black-Scholes. The construction:

$$
\text{VIX}^2 = \frac{2 e^{rT}}{T} \sum_{i} \frac{\Delta K_i}{K_i^2} Q(K_i) - \frac{1}{T}\left(\frac{F}{K_0} - 1\right)^2.
$$

Here $Q(K_i)$ is the OTM option price at strike $K_i$ (puts below forward, calls above), $\Delta K_i$ is the strike spacing, $F$ is the forward price, and $K_0$ is the first strike below $F$. The formula derives from static replication of a variance swap via a continuum of OTM options — a mathematical identity stating that the fair strike of a variance swap equals a specific weighted integral of OTM option prices.

Two points:

1. No Black-Scholes is required. The formula uses observed option prices directly and makes no assumption about the dynamics of $S$. This is why VIX is described as "model-free." The derivation assumes the variance-swap replication formula is exact, which requires a continuum of strikes and no jumps; in practice, discretization introduces small errors.
2. VIX is reported as a volatility, not a variance. It is the square root of the formula above, expressed in annualized vol points. A VIX of 20 corresponds to 20% annualized volatility.

VIX is computed in real time from a specific set of SPX options, using the two nearest maturities weighted to bracket 30 days. Analogous indices exist for 9-day (VIX9D) and 3-month (VIX3M), used in [the term structure lesson](term-structure.md) to measure the slope of the IV curve.

## Realized volatility estimators

If IV is a forecast, realized volatility is the measurement. The standard estimate is the EWM or rolling standard deviation of log returns, annualized by $\sqrt{252}$.

The true realized volatility of a process is a more subtle object than the sample std computed from daily closes. Three issues:

- **Sampling frequency.** Daily close-to-close returns miss intraday volatility. Higher-frequency estimators (Parkinson using high-low, Garman-Klass using OHLC, realized variance from intraday returns) use more of the data and have lower estimation error.
- **Jumps.** A close-to-close estimator combines continuous volatility and jumps into a single number. Bipower variation separates the two, at the cost of greater complexity.
- **Microstructure noise.** Very high-frequency returns carry bid-ask-bounce noise; realized variance overstates true volatility when sampled too finely without correction.

For comparison to IV, the standard choice is daily close-to-close log returns annualized by $\sqrt{252}$ over the same horizon as the IV target. This is not the sharpest estimator, but it is the most commonly reported, and IV-vs-RV comparisons require matched sampling.

## Summary

The two quantities serve distinct purposes:

- Realized volatility answers: how volatile was the underlying over the past $T$ days? Measurable and backward-looking.
- Implied volatility answers: how volatile does the market price the underlying to be over the next $T$ days? Forward-looking, with a risk premium included.

The spread between them — the VRP — is harvested by short-volatility strategies. Deviations from a single IV number constitute the IV surface, covered in the next two lessons. The regime classifier in `packages/gex/src/gex/regime.py` uses both IV level (via VIX) and slope (VIX/VIX3M) as regime inputs.

The reader can now reason about:

- Why the term "volatility" ambiguously references two distinct quantities — a measurement and a forecast — and how conflation leads to misreading options-market commentary.
- Why short-volatility strategies have positive expected returns but severe tail properties: they harvest a real premium that compensates for real tail risk.
- How VIX is constructed model-free from option prices via the variance-swap replication formula, and why it is a statement about the options market rather than about Black-Scholes specifically.

## Implemented at

The GEX pipeline consumes IV as input rather than recomputing it from quoted premiums. Data sources in `trading/packages/gex/src/gex/data/options.py` provide per-contract IV from the upstream chain feed. The VIX series is pulled via `data/vix.py::fetch_vix_history`, and the regime classifier in `regime.py:classify_regime` uses VIX/VIX3M and VIX9D/VIX slopes as inversion triggers. These slopes are the subject of [the next lesson](term-structure.md).

---

**Next:** [Term structure of volatility →](term-structure.md)
