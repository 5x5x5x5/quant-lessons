---
title: "Theta, vega, rho"
prereqs: "Gamma — the second derivative"
arrives_at: "the remaining first-order sensitivities — time, implied vol, and rates"
code_ref: "trading/packages/gex/src/gex/greeks.py"
---

# Theta, vega, rho

Delta and gamma receive the most attention because they track the underlying. The Black-Scholes PDE has additional partial derivatives — $\Theta$ (time) and an implicit one in $\sigma$ (vega) — that are equally important for managing a hedging book. Rho (rate sensitivity) is typically secondary for short-dated equity options but is necessary to complete the picture.

## Theta — time decay

$$
\Theta = \frac{\partial V}{\partial t}.
$$

Theta measures how much an option's value changes per unit of elapsed time, with other inputs held constant. For long options, $\Theta < 0$: value declines as time passes, with $S$ and $\sigma$ unchanged.

The intuition: time value represents the premium paid for future uncertainty, and remaining time decreases as expiry approaches. An ATM call with 30 days to expiry carries more time value than an ATM call with 2 days; the difference is realized as theta, day by day.

For a European call under Black-Scholes, theta decomposes into two terms:

$$
\Theta_\text{call} = -\frac{S \phi(d_1) \sigma}{2\sqrt{T}} - r K e^{-rT} N(d_2).
$$

The first term is the gamma-scalping-cost term, large for ATM short-dated options. The second is a smaller rates term. The first term dominates in most practical positions.

Theta is conventionally reported in dollars per day. Dividing the analytical $\Theta$ by 365 gives theta per calendar day; dividing by 252 gives theta per trading day. Conventions vary. Traders describe positions by their net daily theta — for example, "this book earns \$50k per day in theta" is the sum of theta across positions, multiplied by contract sizes.

### Theta-gamma trade-off

[The previous lesson](gamma.md) showed that a delta-hedged long option earns $\tfrac{1}{2}\Gamma (dS)^2$ from motion and loses $|\Theta| dt$ from time, with break-even when realized variance equals implied variance. Both $\Theta$ and $\Gamma$ peak for ATM short-dated options — the same region. The two Greeks cannot be separated.

Short-option positions (short calls, short puts, covered calls, credit spreads) are long theta and short gamma. Quiet days accrue theta; each move costs gamma. Short-volatility strategies operate in this trade-off.

The characterization of an iron condor as "selling time" is literally correct: the position captures theta while bearing gamma risk in the tails. When the underlying remains within the condor's wings, theta accrues; when it breaks through, gamma cost dominates.

## Vega — sensitivity to implied volatility

$$
\mathcal{V} = \frac{\partial V}{\partial \sigma}.
$$

Vega measures how much an option's value changes per unit change in implied volatility — the $\sigma$ recovered by inverting Black-Scholes against a market premium, not the realized volatility of the underlying.

For a European call or put (vega is identical for the two):

$$
\mathcal{V} = S \phi(d_1) \sqrt{T}.
$$

Units are conventionally "dollars per 1 vol point" — the P&L change per 1 percentage point change in IV. A vega of \$0.30 means a 1-point rise in IV (from 20% to 21%, for example) changes the option's value by \$0.30.

### Where vega is large

$\phi(d_1) \sqrt{T}$ implies:

- ATM options have the highest vega, as they do for gamma and theta.
- Long-dated options have higher vega than short-dated options — the $\sqrt{T}$ factor grows with expiry. A 1-year option has approximately $\sqrt{365/30} \approx 3.5\times$ the vega of a 30-day option at otherwise matched parameters. LEAPS are particularly vega-heavy.
- Very deep ITM or OTM options have low vega — their value is insensitive to small changes in $\sigma$ because the payoff is nearly certain or nearly zero.

### Vol hedging

A delta-hedged book is not vol-hedged. If implied vol rises uniformly by 1 point, each long option gains value by its vega and each short option loses by its vega. The book's net vega position is the signed sum. A vol-hedged book has net vega near zero, typically achieved by offsetting long and short options at similar strikes and expiries.

Delta neutralizes first-order moves in the underlying; vega hedging neutralizes first-order moves in implied volatility. A properly managed market-maker book controls both. Without either, the position carries directional, vol, and gamma-scalping P&L simultaneously — three risk factors in one position.

### Vega risk versus vol-surface risk

A subtlety: vega as defined above assumes a parallel shift in implied volatility — the entire surface moves up or down uniformly. In practice, IV evolves regime by regime. The short end moves differently from the long end (term-structure changes), and OTM puts move differently from OTM calls (skew changes). Each is a separate risk factor not captured by a single vega number. Vol-trading books quote vega bucketed by expiry and delta, hedging buckets separately.

## Rho — sensitivity to rates

$$
\rho = \frac{\partial V}{\partial r}.
$$

Rho measures sensitivity to the risk-free rate. For a European call:

$$
\rho_\text{call} = K T e^{-rT} N(d_2).
$$

The $T$ in the numerator implies that rho scales with time to expiry. For a put, rho is negative. Higher rates raise the forward price of the underlying ($Se^{rT}$), increasing call value and decreasing put value.

For most short-dated equity options, rho is small enough to ignore. A 1% rate move typically changes a 30-day option's price by a few cents. For long-dated options (LEAPS), rho becomes non-negligible; for rate-vol-linked products (certain structured notes and vol derivatives), rho is central.

Rho rarely appears in daily options-trading discussions at the level of delta or vega. It becomes significant when rates are moving meaningfully (the 2022 Fed cycle is a representative example), when expiries are long, or when the book includes rate-sensitive overlays.

## Second-order Greeks

Each first-order Greek has its own sensitivity to other inputs. Most are negligible; a few are material in specific regimes.

### Charm: $\partial \Delta / \partial t$

How delta changes with time, holding $S$ constant. For short-dated options with near-the-money strikes, charm is small early in the day but grows as expiry approaches. ATM option deltas drift across an expiry session even when the underlying is flat; this "charm flow" contributes to end-of-day hedging dynamics on 0DTE and expiry-Friday sessions. Dealers with known positions can forecast their own hedging requirements from charm, and market structure occasionally shows these flows visibly.

### Vanna: $\partial \Delta / \partial \sigma$

How delta changes with implied volatility. A change in vol reshapes the delta profile because $d_1$ depends on $\sigma$. When IV spikes sharply on a news event, a delta-hedged book is suddenly mis-hedged at first order; vol and delta hedging interact through vanna.

### Volga (vol-of-vol): $\partial \mathcal{V} / \partial \sigma$

How vega changes with vol — the second derivative of price with respect to $\sigma$. For strangles and risk reversals, volga determines whether the position is long or short vol convexity. Strategies that explicitly trade vol convexity (dispersion trading, variance swaps, some VIX-futures strategies) are volga trades.

A practical heuristic: manage delta and vega continuously, gamma and theta per trade, rho when rates are moving, and second-order Greeks when the surface is reshaping.

## Summary

The reader can now reason about:

- Why short-option positions are mathematically equivalent to long theta and short gamma — the decay captured is compensation for the risk taken.
- The distinction between vega (parallel IV shift) and vol-surface risk (term-structure and skew changes) — a single vega number hides substantial structure.
- Why rho is typically secondary for short-dated equity options but is tracked carefully for LEAPS and in rate-volatile regimes.

## Implemented at

`trading/packages/gex/src/gex/greeks.py` — the current module exports `bs_d1`, `bs_gamma`, and `bs_delta_call`. Theta, vega, and rho are not computed because the GEX pipeline's regime classification operates on gamma alone. Future strategies requiring these sensitivities (a vega-hedged overlay, a theta-driven expiry play) would extend the same module using the existing Black-Scholes scaffolding.

---

**Next:** [Implied vol vs realized →](../vol-surface/implied-vol.md)
