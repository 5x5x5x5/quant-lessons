---
title: "Triple-barrier labeling"
prereqs: "The labeling problem; Volatility as a measurable thing"
arrives_at: "volatility-scaled directional labels that respect exit logic"
code_ref: "trading/packages/afml/src/afml/labeling.py — apply_triple_barrier"
---

# Triple-barrier labeling

> **Status:** Draft pending.

**Scope:** Three barriers per event:

- **Upper** (profit-take): $+\text{pt\_mult} \cdot \sigma$
- **Lower** (stop-loss): $-\text{sl\_mult} \cdot \sigma$
- **Vertical** (time cap): `vertical_bars` bars after entry

Label = $+1$ if upper is hit first, $-1$ if lower, $\text{sign}(\text{return})$ if vertical. Vol-scaling makes thresholds comparable across regimes (a 2σ move in 2017 and 2020 are both "2σ" even though the dollar amount differs). Side adjustment: for shorts, the sign of the measured return flips, so a profitable short is still labeled $+1$.

**You'll be able to reason about:**

- Why the same function handles long and short sides via the `side` adjustment — the return series is sign-flipped, everything else stays.
- Why the vertical barrier is essential (otherwise you hold until a barrier is hit, possibly never).
- How to tune `pt_mult` vs `sl_mult` asymmetrically for strategies with skewed risk preferences.

**Implemented at:** `trading/packages/afml/src/afml/labeling.py:52` — `apply_triple_barrier(prices, events, sides, config, vol)`. Output schema: `event_idx, exit_idx, ret, label, barrier_hit`.

---

**Next:** [Meta-labeling →](meta-labeling.md)
