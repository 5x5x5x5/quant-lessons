---
title: "Black-Scholes as a bridge"
prereqs: "Payoffs and put-call parity; Random walks and the null model"
arrives_at: "a closed-form price for European options under GBM, and the foundation for every Greek in Part 3"
code_ref: "trading/packages/gex/src/gex/greeks.py — bs_d1, bs_gamma, bs_delta_call"
---

# Black-Scholes as a bridge

Put-call parity relates call, put, stock, and cash but does not determine the absolute price of a call. Pricing requires a model for the dynamics of the underlying between now and expiry. Under GBM, the resulting valuation has a closed-form solution — the Black-Scholes formula — which converts the random-walk null into a specific price.

A complete derivation requires a chapter of stochastic calculus. What follows sketches the construction, establishes the closed form, and identifies the single unobservable input.

## Setup

Assume the underlying follows geometric Brownian motion ([Lesson 3](../measurable/random-walks.md)):

$$
\frac{dS}{S} = \mu\, dt + \sigma\, dW.
$$

Consider a European call $C(S, t)$ struck at $K$, expiring at $T$. The central observation, due to Black, Scholes, and Merton, is that a specific portfolio has locally riskless dynamics:

$$
\Pi = C - \Delta\, S, \qquad \Delta = \frac{\partial C}{\partial S}.
$$

The portfolio consists of one call, hedged by a short position of $\Delta$ shares. Because $\Delta$ is the sensitivity of $C$ to $S$, first-order changes in $S$ cancel between the two legs. The remaining differential $d\Pi$ depends on time and on second-order effects in $S$ (gamma and theta).

Applying Itô's lemma to $C$ and substituting, the stochastic $dW$ terms cancel:

$$
d\Pi = \left(\frac{\partial C}{\partial t} + \frac{1}{2}\sigma^2 S^2 \frac{\partial^2 C}{\partial S^2}\right) dt.
$$

The portfolio has no instantaneous randomness. No-arbitrage requires $d\Pi$ to equal the risk-free rate times the portfolio value:

$$
d\Pi = r\,\Pi\, dt.
$$

Substituting and rearranging yields the **Black-Scholes PDE**:

$$
\frac{\partial C}{\partial t} + r S \frac{\partial C}{\partial S} + \frac{1}{2}\sigma^2 S^2 \frac{\partial^2 C}{\partial S^2} = r C.
$$

This equation governs the option price. The remainder of the Black-Scholes derivation supplies boundary conditions and performs a change of variables.

## Closed form

For a European call with terminal condition $C(S, T) = \max(S - K, 0)$, the PDE has the closed-form solution:

$$
\boxed{C = S\, N(d_1) - K e^{-rT} N(d_2)}
$$

where $N(\cdot)$ is the standard normal CDF and

$$
d_1 = \frac{\log(S/K) + (r + \tfrac{1}{2}\sigma^2) T}{\sigma\sqrt{T}}, \qquad d_2 = d_1 - \sigma\sqrt{T}.
$$

The European put follows from put-call parity: $P = K e^{-rT} N(-d_2) - S\, N(-d_1)$.

The formula takes five inputs:

- $S$: current underlying price — observable.
- $K$: strike — known by contract.
- $r$: risk-free rate — observable (Treasury yields).
- $T$: time to expiry — known.
- $\sigma$: volatility over $[0, T]$ — not directly observable.

Four of the five inputs are market data or contract specifications. The fifth, volatility, requires a forecast or estimate. Practitioners summarize this by saying "vol is the price" in options markets: given the other four inputs, every premium is equivalent to a statement about $\sigma$.

## Greeks from the formula

The partial derivatives appearing in the PDE are the Greeks covered in Part 3. Two follow directly from the call formula:

$$
\Delta = \frac{\partial C}{\partial S} = N(d_1),
$$

the call's sensitivity to the underlying, which is also the hedging ratio in the portfolio above. And

$$
\Gamma = \frac{\partial^2 C}{\partial S^2} = \frac{\phi(d_1)}{S \sigma \sqrt{T}},
$$

where $\phi$ is the standard normal PDF. These quantities are not supplementary; they are the coefficients in the hedging argument. The PDE itself is expressed in terms of $\Delta$, $\Gamma$, and the time derivative $\Theta = \partial C / \partial t$.

## Interpretation of $N(d_1)$ and $N(d_2)$

Two quantities recur in subsequent material:

- $N(d_2)$ is the risk-neutral probability that the call finishes in the money ($S_T > K$) — the probability of exercise under the pricing measure.
- $N(d_1)$ is a probability under a different measure: the risk-neutral probability of finishing ITM using the underlying itself as numéraire. The gap between $N(d_1)$ and $N(d_2)$ widens with $\sigma \sqrt{T}$ and reflects the convexity of the call payoff.

For small $\sigma \sqrt{T}$, $N(d_1) \approx \Delta$ and the sensitivity to $S$ tracks the probability of exercise closely. Practitioners often use "delta" and "probability of ITM" interchangeably, which is accurate to within a percentage point or two for short-dated contracts. The distinction becomes material for long-dated options and for deep ITM or OTM positions.

## Black-Scholes assumptions and their empirical violations

The derivation relies on a specific set of assumptions. Each is violated empirically to some degree; the relevant question is how much the violation matters in a given regime:

1. **GBM with constant $\sigma$.** Real volatility is stochastic, mean-reverting, and spikes around events. Black-Scholes assumes a single $\sigma$.
2. **Continuous hedging.** The riskless-portfolio argument requires adjusting $\Delta$ continuously as $S$ moves. In practice, rebalancing is discrete and incurs slippage.
3. **No jumps.** Real markets gap. Black-Scholes prices assume continuous Brownian paths.
4. **No transaction costs.** Continuous hedging with non-zero costs is infeasible.
5. **Known, constant risk-free rate.** Acceptable in low-rate regimes; more significant during rate-volatile periods.
6. **European exercise.** American options carry an additional early-exercise premium (typically small for non-dividend-paying stocks).

Despite these violations, Black-Scholes remains the market's common language. Options are not quoted at Black-Scholes prices directly; they are quoted at market prices which, when inverted through the formula, yield an **implied volatility**. Two participants who disagree on $\sigma$ can still agree on Black-Scholes as the shared vocabulary for that disagreement. The model's inaccuracies are specific and understood, and they are encoded entirely in the implied-volatility surface covered in Part 4. The shape of that surface — [term structure](../vol-surface/term-structure.md) and [skew](../vol-surface/skew.md) — is the market's correction to the model.

## Vol as the price

Because $\sigma$ is the only unobservable input, asking for an option's value is equivalent to asking what $\sigma$ the market assigns over the contract's life. Given a quoted premium and the other four inputs, there is a unique $\sigma$ reproducing the quote. This $\sigma$ is the implied volatility, and options markets are effectively volatility markets expressed in premium units.

This is why the trading project does not recompute option premiums from first principles in the GEX pipeline. It consumes quoted premiums, pairs them with quoted implied volatilities (or inverts premiums to recover them), and passes $\sigma$ into the Greeks formulas.

## Summary

The reader can now reason about:

- Why $\sigma$ is the only unobservable input to Black-Scholes — the remaining four inputs are market data or contract specifications — and why practitioners describe vol as the price.
- Why the Black-Scholes formula and the Greeks are related: $\Delta$ and $\Gamma$ are the coefficients in the hedging argument that produced the PDE.
- The six Black-Scholes assumptions and the specific regime in which each breaks down (constant $\sigma$, continuous hedging, no jumps, no transaction costs, known rate, European exercise).

## Implemented at

`trading/packages/gex/src/gex/greeks.py`:

- `bs_d1(spot, strike, rate, sigma, tenor_years)` at line 16 — computes $d_1$ vectorized over any input.
- `bs_gamma` at line 31 — returns $\phi(d_1) / (S\sigma\sqrt{T})$; identical for calls and puts.
- `bs_delta_call` at line 52 — returns $N(d_1)$; used in the 25-delta skew computation in [Part 4](../vol-surface/skew.md).

The module header states: "Assumes no dividends, continuous compounding, European exercise. SPX/QQQ are European-style, so this is correct for the primary use case. Single names are American — treat as approximation (error is small for gamma)." These are the assumptions of this lesson, stated in code.

---

**Next:** [Delta — sensitivity to price →](../greeks/delta.md)
