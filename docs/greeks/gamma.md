---
title: "Gamma — the second derivative"
prereqs: "Delta — sensitivity to price"
arrives_at: "∂²V/∂S² — the sensitivity of delta itself, and the reason dealer positioning creates market regimes"
code_ref: "trading/packages/gex/src/gex/greeks.py — bs_gamma"
---

# Gamma — the second derivative

> **Status:** Draft pending.

**Scope:** Gamma as $\partial \Delta / \partial S = \partial^2 V / \partial S^2$. ATM options have the highest gamma; gamma collapses for deep ITM / deep OTM and for long-dated options. Derive the P&L of a delta-hedged position:

$$
\text{PnL} \approx \frac{1}{2} \Gamma (\Delta S)^2 - \Theta \Delta t
$$

— you get paid for realized variance and pay theta. Then the dealer-hedging implication: long gamma → buy low, sell high (dampening); short gamma → sell low, buy high (amplifying). This sets up Part 5.

**You'll be able to reason about:**

- Why gamma-scalping is a legitimate strategy under high realized-vs-implied-vol spread.
- Why short-dated options have punishingly high gamma (and theta).
- The exact link between option P&L and realized variance — the $\Gamma \epsilon^2$ term.

**Implemented at:** `trading/packages/gex/src/gex/greeks.py` — `bs_gamma(spot, strike, tau, iv, rate)`.

---

**Next:** [Theta, vega, rho →](theta-vega-rho.md)
