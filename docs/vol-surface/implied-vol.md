---
title: "Implied vol vs realized"
prereqs: "Black-Scholes as a bridge"
arrives_at: "the market's forecast of σ, and why it typically exceeds realized"
code_ref: "—"
---

# Implied vol vs realized

Black-Scholes takes five inputs and produces a price. Four of them — $S$, $K$, $r$, $T$ — are observable or contractual. The fifth, $\sigma$, is not. The market solves this elegantly: **observed option premiums define the $\sigma$**. The $\sigma$ you back out by inverting the BS formula against market price is **implied volatility** (IV). It is a forecast — the market's consensus guess about future realized vol over the option's remaining life.

This lesson is about what IV actually measures, how it differs from realized vol, and the single most persistent spread in options markets: the variance risk premium.

## Inverting Black-Scholes

You observe a market premium $C^\text{mkt}$ for a call with known $S$, $K$, $r$, $T$. Find the $\sigma$ such that

$$
C_\text{BS}(S, K, r, T, \sigma) = C^\text{mkt}.
$$

The BS formula is monotonic in $\sigma$ (higher vol = higher call price, always), so the inversion has a unique solution. Numerical solvers find it in microseconds. That $\sigma$ is the option's implied vol.

Every option on the chain has its own implied vol. If Black-Scholes were fully correct, every option on a given underlying would have the same IV — one $\sigma$ to price them all. In practice, IVs vary across strikes (skew, smile) and across expiries (term structure). The deviations from a constant IV *are* what the next two lessons cover.

## IV is a forecast, not a measurement

This is the subtle point that distinguishes IV from anything computable from price history. An option's IV answers the question: **what volatility over the next $T$ days would justify the price I am paying?** It is inherently forward-looking.

In practice it combines three things:

1. The market's best estimate of future realized vol.
2. A risk premium for bearing vol risk (sellers demand compensation for tail events).
3. Supply/demand imbalances specific to that option (buyer of specific protection, dealer inventory).

You cannot separate these components from a single IV quote. What you *can* do is compare IV to subsequent realized vol, over and over, and estimate an average gap.

## The variance risk premium

Do it, and a robust pattern appears: **IV tends to exceed subsequent realized vol on average**, especially for short-dated equity index options. The difference has a name — the variance risk premium (VRP).

| Approximate figures, SPX 30-day, decade-average |                   |
|-------------------------------------------------|-------------------|
| Mean VIX (implied)                              | ~18%              |
| Mean realized 30-day vol                        | ~14%              |
| Mean spread (premium)                           | ~4 percentage points |

The spread is not constant. It compresses to near zero (and occasionally inverts) in quiet, confident regimes; it blows out to 10+ points around events. But the unconditional average has been meaningfully positive across multi-decade samples.

Why does the premium exist? The economic argument: selling options is equivalent to selling insurance. The seller takes a small premium in exchange for accepting convex losses in tail events. Risk-averse agents demand more premium than actuarially fair to bear that risk. Over time, the insurance is more expensive than its expected payoff — and the sellers, on average, profit.

**Short-vol strategies systematically harvest the VRP.** Sell naked puts, sell strangles, sell variance swaps — the unconditional return is positive. The catch is the tail: occasional losses that wipe out years of accumulated small gains. Long-Term Capital in 1998, Volmageddon in February 2018, COVID in March 2020 — all had short-vol books as central characters. The VRP is real, but it is not free money; it is compensation for a risk that occasionally materializes.

## VIX — a model-free IV

VIX, the CBOE Volatility Index, is the market's best-known IV summary. It reports a 30-day implied volatility estimate on the S&P 500, and it does so **without assuming Black-Scholes**. The construction:

$$
\text{VIX}^2 = \frac{2 e^{rT}}{T} \sum_{i} \frac{\Delta K_i}{K_i^2} Q(K_i) - \frac{1}{T}\left(\frac{F}{K_0} - 1\right)^2.
$$

Here $Q(K_i)$ is the OTM option price at strike $K_i$ (puts below forward, calls above), $\Delta K_i$ is the strike spacing, $F$ is the forward price, and $K_0$ is the first strike below $F$. The formula comes from **static replication of a variance swap** via a continuum of OTM options — a mathematical identity that says: the fair strike of a variance swap equals a specific weighted integral of OTM option prices.

Two things to appreciate:

1. **No Black-Scholes.** The formula uses observed option prices directly and makes no assumption about the dynamics of $S$. This is why VIX is called "model-free." (It still assumes the variance swap replication formula is exact, which requires a continuum of strikes and no jumps; in practice the discretization introduces small errors.)
2. **It's a variance, not a vol.** VIX is the square root of the formula above, reported in annualized vol points. When the market says "VIX is 20," it means 20% annualized vol.

VIX is computed in real time from a specific set of SPX options (30 days out, using the two nearest maturities weighted to bracket exactly 30). Analogous indices exist for 9-day (VIX9D) and 3-month (VIX3M), which the [term structure lesson](term-structure.md) uses to measure the slope of the IV curve.

## Realized vol, the honest way

If IV is a forecast, realized vol is the measurement. Given a return series, the standard textbook estimate is the EWM or rolling std of log returns, annualized by $\sqrt{252}$.

But the "true" realized vol of a process is a more subtle object than the sample std you compute from daily closes. The issues:

- **Sampling frequency.** Daily close-to-close returns miss intraday volatility. Higher-frequency estimators (Parkinson using H-L, Garman-Klass using O/H/L/C, realized variance from intraday returns) use more of the data and have lower estimation error.
- **Jumps.** A close-to-close estimator blends continuous volatility and jumps together. Bipower variation separates the two, at the cost of more complex estimation.
- **Microstructure noise.** Very-high-frequency returns have noise from bid-ask bounce; realized variance overestimates true volatility if you sample too fast without correction.

For comparing to IV, the standard choice is daily close-to-close log returns annualized by $\sqrt{252}$, same sampling frequency as VIX's horizon. It's not the sharpest estimator, but it's the one people report, and IV-vs-RV comparisons need to use compatible units.

## Putting it together

The two quantities serve different purposes:

- **Realized vol** answers: how volatile was the underlying over the past $T$ days? Measurable, backward-looking.
- **Implied vol** answers: how volatile is the market pricing the underlying to be over the next $T$ days? Forward-looking, with a premium baked in.

The spread between them — the VRP — is what short-vol strategies harvest. The shape of the IV surface — term structure and skew, covered next — is what the deviations from "one number" look like. The regime classifier in `packages/gex/src/gex/regime.py` uses both IV level (via VIX) and slope (VIX/VIX3M) as regime inputs.

## What you can now reason about

- Why "vol" ambiguously refers to two entirely different things — a measurement and a forecast — and why conflating them is the fastest way to misread any options-market commentary.
- Why short-vol strategies have positive *expected* returns but awful tail properties — they are harvesting a real premium, for a real reason.
- How VIX is constructed model-free from option prices via the variance-swap replication formula, and why it is a statement about the option market, not about Black-Scholes specifically.

## Implemented at

The GEX pipeline consumes IV as an input — it does not recompute it from quoted premiums in this project. Sources in `trading/packages/gex/src/gex/data/options.py` provide IV per-contract from the upstream chain feed. The VIX series itself is pulled via `data/vix.py::fetch_vix_history`, and the regime classifier in `regime.py:classify_regime` uses VIX/VIX3M and VIX9D/VIX slopes as inversion triggers. Those slopes are the subject of [the next lesson](term-structure.md).

---

**Next:** [Term structure of volatility →](term-structure.md)
