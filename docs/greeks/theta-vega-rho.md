---
title: "Theta, vega, rho"
prereqs: "Gamma — the second derivative"
arrives_at: "the remaining first-order sensitivities — time, implied vol, and rates"
code_ref: "trading/packages/gex/src/gex/greeks.py"
---

# Theta, vega, rho

> **Status:** Draft pending.

**Scope:** Theta ($\partial V/\partial t$): time decay, fastest near expiry for ATM options. Vega ($\partial V/\partial \sigma$): sensitivity to *implied* vol, not realized. Rho ($\partial V/\partial r$): typically small for short-dated equity options, material for long-dated and rate-sensitive regimes. Touch on **second-order Greeks** (vanna, volga, charm) and where they bite (vol surface dynamics, end-of-day charm flows on expiry Friday).

**You'll be able to reason about:**

- Why "short options" is equivalent to "long theta, short gamma" — and the symmetry under realized-vs-implied vol.
- The distinction between **vega risk** (parallel IV shift) and **vanna/volga risk** (vol surface reshape).
- When rho matters: longer-dated options, rate-sensitive regimes, fixed-income overlays.

**Implemented at:** `trading/packages/gex/src/gex/greeks.py` — current implementation covers delta and gamma; theta/vega/rho would extend the same module when a strategy needs them.

---

**Next:** [Implied vol vs realized →](../vol-surface/implied-vol.md)
