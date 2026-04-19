---
title: "Black-Scholes as a bridge"
prereqs: "Payoffs and put-call parity; Random walks and the null model"
arrives_at: "a closed-form price for European options under GBM, and the foundation for every Greek in Part 3"
code_ref: "trading/packages/gex/src/gex/greeks.py — bs_d1, bs_gamma, bs_delta_call"
---

# Black-Scholes as a bridge

Put-call parity relates call, put, stock, and cash. It does not tell you what a call actually costs. To price a call you need a model of how the underlying moves between now and expiry. Under GBM, that model has a closed-form solution — the Black-Scholes formula. It's the single equation that turns the random-walk null into a price.

The derivation proper takes a full chapter of stochastic calculus. What follows is enough sketch to see where the formula comes from and why it depends on only one unobservable input.

## The setup

Assume the underlying follows geometric Brownian motion ([Lesson 3](../measurable/random-walks.md)):

$$
\frac{dS}{S} = \mu\, dt + \sigma\, dW.
$$

Consider a European call $C(S, t)$ struck at $K$, expiring at $T$. The key observation, due to Black, Scholes, and Merton, is that you can construct a portfolio whose dynamics are **riskless**:

$$
\Pi = C - \Delta\, S, \qquad \Delta = \frac{\partial C}{\partial S}.
$$

Hold one call; short $\Delta$ shares. Because $\Delta$ is exactly the sensitivity of $C$ to $S$, first-order moves in $S$ cancel between the two legs. What remains — the differential $d\Pi$ — depends only on time and on $S$ through second-order effects (gamma and theta).

Applying Itô's lemma to $C$ and plugging in, the stochastic $dW$ terms drop out of $d\Pi$:

$$
d\Pi = \left(\frac{\partial C}{\partial t} + \frac{1}{2}\sigma^2 S^2 \frac{\partial^2 C}{\partial S^2}\right) dt.
$$

No $dW$. The portfolio has no randomness over an instant. No-arbitrage then forces $d\Pi$ to equal the risk-free rate times the portfolio value:

$$
d\Pi = r\,\Pi\, dt.
$$

Substituting and rearranging gives the **Black-Scholes PDE**:

$$
\frac{\partial C}{\partial t} + r S \frac{\partial C}{\partial S} + \frac{1}{2}\sigma^2 S^2 \frac{\partial^2 C}{\partial S^2} = r C.
$$

This is the engine. Everything else in Black-Scholes is boundary conditions and a change of variables.

## The closed form

For a European call with terminal condition $C(S, T) = \max(S - K, 0)$, the PDE has a closed-form solution:

$$
\boxed{C = S\, N(d_1) - K e^{-rT} N(d_2)}
$$

where $N(\cdot)$ is the standard normal CDF and

$$
d_1 = \frac{\log(S/K) + (r + \tfrac{1}{2}\sigma^2) T}{\sigma\sqrt{T}}, \qquad d_2 = d_1 - \sigma\sqrt{T}.
$$

A European put follows from put-call parity (or symmetry): $P = K e^{-rT} N(-d_2) - S\, N(-d_1)$.

Stare at this for a minute. Five inputs:

- $S$: current underlying price — **observable**.
- $K$: strike — **known** by contract.
- $r$: risk-free rate — **observable** (Treasury yields).
- $T$: time to expiry — **known**.
- $\sigma$: volatility over $[0, T]$ — **not observable**.

Four of the five inputs are market data or contract specs. The fifth — volatility — is the only input that requires an opinion. This is why practitioners say "vol is the price" in options markets: given the other four inputs, every premium is a statement about $\sigma$.

## Delta, gamma, and the Greeks in the formula

The partial derivatives that appear in the PDE are exactly the Greeks covered in Part 3. Two that come out of the call formula immediately:

$$
\Delta = \frac{\partial C}{\partial S} = N(d_1),
$$

the call's sensitivity to the underlying — and, conveniently, the same quantity that defines the hedging portfolio above. And

$$
\Gamma = \frac{\partial^2 C}{\partial S^2} = \frac{\phi(d_1)}{S \sigma \sqrt{T}},
$$

where $\phi$ is the standard normal PDF. These are not add-ons to the model. They are the coefficients of the hedging argument itself — the PDE is written in terms of $\Delta$, $\Gamma$, and the time derivative $\Theta = \partial C / \partial t$.

## The interpretation of $N(d_1)$ and $N(d_2)$

Two quantities worth naming, because they return everywhere:

- $N(d_2)$ is the **risk-neutral probability that the call finishes in the money** ($S_T > K$). Under the pricing measure, with the risk-free drift, this is the probability that exercise happens.
- $N(d_1)$ is also a probability, but in a different measure — it's the risk-neutral probability of finishing ITM when the underlying itself is used as the numéraire. The gap between $N(d_1)$ and $N(d_2)$ widens with $\sigma \sqrt{T}$ and reflects the convexity of the call payoff.

For small moves, $N(d_1) \approx \Delta$ — the sensitivity to $S$ tracks the probability of exercise. Traders use "delta" and "probability of ITM" interchangeably, and they're within a percent or two for reasonable parameter ranges. The distinction matters in edge cases (very long-dated options, deep ITM / OTM) but not in day-to-day intuition.

## What Black-Scholes requires, and what it gets wrong

The derivation leans on a specific list of assumptions. Every one of them is empirically wrong to some degree; the question is how wrong in the regime you care about.

1. **GBM with constant $\sigma$.** Real vol is stochastic, mean-reverts, spikes around events. BS assumes a single number.
2. **Continuous hedging.** The riskless portfolio requires adjusting $\Delta$ instantaneously as $S$ moves. In practice, you rebalance discretely and eat slippage.
3. **No jumps.** Real markets gap. BS prices assume Brownian (continuous) paths.
4. **No transaction costs.** Continuous hedging with non-zero costs is infinitely expensive.
5. **Known, constant risk-free rate.** Fine in low-rate regimes; more important in rate-volatile periods.
6. **European exercise.** For American options, an additional early-exercise premium applies (usually small for non-dividend-paying stocks).

Despite all of this, **the market uses BS as its common language**. Options aren't quoted at BS prices exactly — they're quoted at market prices that, inverted through BS, yield an **implied volatility**. Two traders who disagree on $\sigma$ can still agree on BS as the vocabulary for that disagreement. This is a deeper point than it sounds: BS is wrong in specific, understood ways, and its wrongness is encoded entirely in the *implied-vol surface* (Part 4). The surface's shape — the [term structure](../vol-surface/term-structure.md) and the [skew](../vol-surface/skew.md) — *is* the market's correction to the model.

## Vol is the price — and the implication

One more consequence. If $\sigma$ is the only unobservable in the formula, then asking "what is the option worth?" is equivalent to asking "what $\sigma$ does the market think is right over the life of this contract?" Equivalent means: invertible. Given a quoted premium and the other four inputs, there is a unique $\sigma$ that reproduces the quote. That $\sigma$ is the **implied volatility**. Options markets are vol markets wearing premium clothing.

This is why the trading project does not recompute option premiums from scratch in the GEX pipeline. It consumes quoted premiums, pairs them with quoted implied vols (or inverts premiums to get them), and feeds $\sigma$ into the Greeks formulas. No need to re-solve Black-Scholes; the market already did.

## What you can now reason about

- Why $\sigma$ is the only unobservable input to BS — the rest are market data or contract specs — and why practitioners say "vol is the price."
- Why the BS formula and the Greeks are not separate — $\Delta$ and $\Gamma$ are the coefficients of the hedging argument that produced the PDE.
- The exact list of BS's model assumptions and where each one fails (constant $\sigma$, continuous hedging, no jumps, no transaction costs). These are the seams where vol surface structure and exotic pricing diverge from BS.

## Implemented at

`trading/packages/gex/src/gex/greeks.py`:

- `bs_d1(spot, strike, rate, sigma, tenor_years)` at line 16 — computes $d_1$ vectorized over any input, using the formula exactly as above.
- `bs_gamma` at line 31 — returns $\phi(d_1) / (S\sigma\sqrt{T})$; same for calls and puts (gamma is symmetric).
- `bs_delta_call` at line 52 — returns $N(d_1)$; used for the 25-delta skew computation in [Part 4](../vol-surface/skew.md).

The module header notes: "Assumes no dividends, continuous compounding, European exercise. SPX/QQQ are European-style, so this is correct for the primary use case. Single names are American — treat as approximation (error is small for gamma)." That's the set of assumptions from this lesson, stated in code.

---

**Next:** [Delta — sensitivity to price →](../greeks/delta.md)
