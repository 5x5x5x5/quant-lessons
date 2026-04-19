---
title: "Implied vol vs realized"
prereqs: "Black-Scholes as a bridge"
arrives_at: "the market's forecast of σ, and why it typically exceeds realized"
code_ref: "—"
---

# Implied vol vs realized

> **Status:** Draft pending.

**Scope:** Implied volatility = the $\sigma$ input to Black-Scholes that reproduces the market price of an option. It's a **forecast**: "if returns were log-normal with this σ going forward, the option would be worth this much." Contrast with **realized** vol (historical std of returns). Introduce the **variance risk premium**: IV > realized on average because option sellers demand a premium for bearing tail risk.

**You'll be able to reason about:**

- Why short-vol strategies have positive *expected* return but punishing tail risk.
- How VIX is constructed — a 30-day model-free IV estimate from SPX options weighted across strikes.
- Why a *single* IV number is reductive — the surface varies by strike and maturity (next two lessons).

**Implemented at:** — (IV is input to `greeks.py`; it's consumed, not computed, in the GEX pipeline.)

---

**Next:** [Term structure of volatility →](term-structure.md)
