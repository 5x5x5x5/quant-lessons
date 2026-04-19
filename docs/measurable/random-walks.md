---
title: "Random walks and the null model"
prereqs: "Volatility as a measurable thing"
arrives_at: "the baseline hypothesis every strategy must beat, and the assumption every option-pricing model leans on"
code_ref: "—"
---

# Random walks and the null model

> **Status:** Draft pending.

**Scope:** Build the random walk from first principles — discrete iid increments → Brownian motion in the continuous limit → geometric Brownian motion (GBM) on log-price with drift $\mu$ and volatility $\sigma$. Note where real markets violate GBM: fat tails, volatility clustering, autocorrelation at intraday horizons.

**You'll be able to reason about:**

- Why options pricing assumes log-normal *terminal* prices, not normal.
- Why next-day return prediction is "hard" — you're predicting deviation from a walk whose expectation is ~0 over short horizons.
- What "alpha" means mathematically: expected return beyond the drift implied by the null.

**Implemented at:** — (GBM is the null; the assumption is implicit in every Black-Scholes call and every Sharpe-vs-zero test.)

---

**Next:** [The options contract →](../options/contracts.md)
