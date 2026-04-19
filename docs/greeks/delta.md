---
title: "Delta — sensitivity to price"
prereqs: "Black-Scholes as a bridge"
arrives_at: "∂V/∂S — the hedge ratio every market maker quotes"
code_ref: "trading/packages/gex/src/gex/greeks.py — bs_delta_call"
---

# Delta — sensitivity to price

> **Status:** Draft pending.

**Scope:** Delta as the first derivative of option value with respect to underlying. ATM call delta ≈ 0.5, deep ITM → 1, deep OTM → 0. Show that delta equals $N(d_1)$ for a European call and is also interpretable as the risk-neutral probability of finishing ITM. Introduce **delta-hedging**: shorting $\Delta$ shares against a long call neutralizes first-order P&L.

**You'll be able to reason about:**

- How market makers quote options and manage risk using delta.
- Why "delta-one" products (futures, stock itself) behave like $\Delta = 1$ options.
- The motivation for gamma: delta is not constant as $S$ moves.

**Implemented at:** `trading/packages/gex/src/gex/greeks.py` — `bs_delta_call(spot, strike, tau, iv, rate)`.

---

**Next:** [Gamma — the second derivative →](gamma.md)
