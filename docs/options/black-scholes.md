---
title: "Black-Scholes as a bridge"
prereqs: "Payoffs and put-call parity; Random walks"
arrives_at: "a closed-form price for European options under GBM, and the foundation for every Greek in Part 3"
code_ref: "trading/packages/gex/src/gex/greeks.py — bs_d1, bs_gamma, bs_delta_call"
---

# Black-Scholes as a bridge

> **Status:** Draft pending.

**Scope:** Sketch the Black-Scholes derivation from GBM + no-arbitrage + continuous delta-hedging. Not the full PDE — enough to see where $\sigma$ enters and why it's the only unobservable input. Arrive at the closed form for a European call:

$$
C = S N(d_1) - K e^{-rT} N(d_2)
$$

where $d_1 = \frac{\log(S/K) + (r + \sigma^2/2)T}{\sigma\sqrt{T}}$ and $d_2 = d_1 - \sigma\sqrt{T}$.

**You'll be able to reason about:**

- Why $\sigma$ is the only unobservable input (the rest — $S$, $K$, $r$, $T$ — are market data).
- Why practitioners say "vol is the price" in options markets.
- The limits of the model: constant $\sigma$ across strikes and time (false — see skew), continuous hedging (infeasible), no jumps (empirically false).

**Implemented at:** `trading/packages/gex/src/gex/greeks.py` — `bs_d1`, `bs_gamma`, `bs_delta_call`. Pricing isn't recomputed in the GEX pipeline; these are used for Greeks at quoted IVs.

---

**Next:** [Delta: sensitivity to price →](../greeks/delta.md)
