---
title: "Theta, vega, rho"
prereqs: "Gamma — the second derivative"
arrives_at: "the remaining first-order sensitivities — time, implied vol, and rates"
code_ref: "trading/packages/gex/src/gex/greeks.py"
---

# Theta, vega, rho

Delta and gamma get the top billing because they track the underlying — the thing the options market is actually about. But the Black-Scholes PDE has four partial derivatives, and the other two — $\Theta$ (time) and there's one implicit in $\sigma$ (vega) — are equally load-bearing for any hedging book. Rho (rates) is usually a footnote for short-dated equity options, but a necessary one.

## Theta — time decay

$$
\Theta = \frac{\partial V}{\partial t}.
$$

Theta measures how much an option's value changes per unit of time elapsed, holding everything else constant. For long options, $\Theta < 0$: as time passes, with $S$ and $\sigma$ unchanged, the option loses value.

Why? Because time value is exactly the premium you pay for *future* uncertainty, and less future means less uncertainty. An ATM call with 30 days to go has more time value than an ATM call with 2 days to go; the difference is collected as theta, day by day.

For a European call under Black-Scholes, theta splits into two contributions:

$$
\Theta_\text{call} = -\frac{S \phi(d_1) \sigma}{2\sqrt{T}} - r K e^{-rT} N(d_2).
$$

The first term is the gamma-scalping-cost term (large for ATM short-dated options — a familiar face). The second is a smaller rates term. The first term dominates for most practical positions.

Theta is **expressed in dollars per day** by convention (divide the analytical $\Theta$ by 365 to get "theta per calendar day" or by 252 to get "theta per trading day"; conventions vary). Traders quote positions by their net daily theta — "this book earns $50k per day in theta" means the sum of theta across all positions, multiplied by contract sizes.

### The theta-gamma trade-off

[The previous lesson](gamma.md) showed that a delta-hedged long option earns $\tfrac{1}{2}\Gamma (dS)^2$ from motion and loses $|\Theta| dt$ from time. The break-even is realized variance equals implied variance. Both $\Theta$ and $\Gamma$ peak for ATM short-dated options — the same "explosive" region. You don't get one without the other.

Short options (short calls, short puts, covered calls, credit spreads) are **long theta, short gamma**. Every quiet day earns the position the theta decay of the options it shorted. Every move costs gamma. Short-vol strategies live in this trade.

The stylized "iron condor sells time" framing is literally true: you are capturing theta at the expense of bearing gamma risk across the tails. When the underlying stays in the condor's wings, theta prints; when it breaks through, gamma cost breaks the trade.

## Vega — sensitivity to implied vol

$$
\mathcal{V} = \frac{\partial V}{\partial \sigma}.
$$

Vega measures how much an option's value changes per unit change in **implied volatility**. Not realized — the number that comes out of inverting the BS formula against market premium.

For a European call or put (they have the same vega):

$$
\mathcal{V} = S \phi(d_1) \sqrt{T}.
$$

Units: typically quoted as "dollars per 1 vol point," i.e., per 1 percentage point change in implied vol. If vega = $0.30$, a 1 vol-point rise in IV (say from 20% to 21%) changes the option's value by $\$0.30$.

### Where vega is large

$\phi(d_1) \sqrt{T}$ says:

- **ATM** options have the highest vega (just like gamma and theta).
- **Long-dated** options have higher vega than short-dated ones — the $\sqrt{T}$ factor grows with expiry. A 1-year option has roughly $\sqrt{365/30} \approx 3.5\times$ the vega of a 30-day option at otherwise matched parameters. (LEAPS are vega monsters.)
- Very deep ITM or OTM options have low vega — their value is insensitive to small changes in $\sigma$ because the payoff is already nearly certain or nearly certainly zero.

### Vol hedging

A delta-hedged book is not vol-hedged. If implied vol rises by 1 point across the board, every long option in the book gains value by its vega; every short option loses by its vega. The net **vega position** of the book is the signed sum. A vol-hedged book has net vega near zero, typically achieved by offsetting long and short options at similar strikes and expiries.

Delta neutralizes first-order underlying moves; vega hedging neutralizes first-order implied-vol moves. A market maker running a proper book manages both. When neither is hedged, the position is called "naked," and the P&L is the sum of directional P&L + vol P&L + gamma-scalping P&L — three risk factors for a single position.

### Vega risk vs vol surface risk

An important subtlety: vega as defined above assumes a **parallel shift** in implied vol — the whole surface moves up or down by one point. In reality, IV moves regime by regime: the short end moves differently from the long end (term structure change), OTM puts move differently from OTM calls (skew change). Each of those is a separate risk factor not captured by a single vega number. Real vol books quote vega *bucketed* by expiry and by delta bucket, and they hedge the buckets separately.

## Rho — sensitivity to rates

$$
\rho = \frac{\partial V}{\partial r}.
$$

Rho measures sensitivity to the risk-free rate. For a European call:

$$
\rho_\text{call} = K T e^{-rT} N(d_2).
$$

Note the $T$ up front — rho scales with time to expiry. For a put, rho is negative. Higher rates increase the forward price of the underlying (higher $Se^{rT}$), making calls more valuable and puts less valuable.

For most short-dated equity options, rho is small enough to ignore. A 1% change in rates might change a 30-day option's price by a few cents. For long-dated options (LEAPS), rho is non-negligible; for rate-vol linked products (some structured notes, some vol derivatives), it's central.

You will not hear professional options traders talking about rho in daily conversation the way they talk about delta and vega. Rho becomes urgent in specific regimes — when rates are moving meaningfully (2022-era Fed cycle, for example), when expiries are long, when the book contains rate-sensitive overlays.

## Second-order Greeks — where they bite

Every first-order Greek has its own sensitivity to other inputs. Most are ignorable; a few matter for specific regimes.

### Charm: $\partial \Delta / \partial t$

How delta changes with time, holding $S$ constant. For short-dated options with strikes near the money, charm is small at the start of the day but grows as expiry approaches. The practical effect: ATM options' deltas drift across an expiry session even when the underlying is flat. This "charm flow" contributes to the end-of-day hedging dance on 0DTE and expiry-Friday sessions. Dealers with known positions can forecast their own hedging needs from charm, and market structure occasionally reflects those flows visibly.

### Vanna: $\partial \Delta / \partial \sigma$

How delta changes with implied vol. Not obvious: a change in vol reshapes the option's delta profile, because $d_1$ depends on $\sigma$. Practical consequence: when IV spikes sharply on a news event, a delta-hedged book suddenly has the wrong hedge. Vol hedging and delta hedging interact through vanna.

### Volga (volvol): $\partial \mathcal{V} / \partial \sigma$

How vega changes with vol — the second derivative of price with respect to $\sigma$. For strangles and risk reversals, volga determines whether the position is long or short vol-of-vol. Strategies that explicitly trade vol convexity (dispersion trading, variance swaps, some VIX-futures trades) are volga trades.

For a starting quant, the rule of thumb is: worry about delta and vega every day, gamma and theta every trade, rho when rates are moving, second-order Greeks when you have a reason to think the surface is reshaping.

## What you can now reason about

- Why being short options is mathematically equivalent to being long theta and short gamma — the decay you collect is paid for by the risk you take.
- The difference between vega (parallel IV shift) and vol-surface risk (term-structure and skew changes) — a single vega number hides a lot of structure.
- Why traders mostly ignore rho for short-dated equity options but track it carefully for LEAPS and in rate-volatile regimes.

## Implemented at

`trading/packages/gex/src/gex/greeks.py` — the current module exports `bs_d1`, `bs_gamma`, and `bs_delta_call`. Theta, vega, and rho are not computed because the GEX pipeline's regime classification operates on gamma, not on vol or time sensitivity. When a future strategy needs them — a vega-hedged overlay, a theta-driven expiry play — they extend the same module using the same BS scaffolding already in place.

---

**Next:** [Implied vol vs realized →](../vol-surface/implied-vol.md)
