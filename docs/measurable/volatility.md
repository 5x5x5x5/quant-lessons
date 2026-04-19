---
title: "Volatility as a measurable thing"
prereqs: "Returns, compounding, log-returns"
arrives_at: "σ — the denominator of every Sharpe ratio and the unit of every vol-scaled barrier"
code_ref: "trading/packages/afml/src/afml/labeling.py:41 — rolling_vol"
---

# Volatility as a measurable thing

> **Status:** Draft pending.

**Scope:** Define volatility as the standard deviation of returns. Contrast **realized** (computable from price history) with **implied** (forward-looking, priced into options — covered in Part 4). Cover sample std vs exponentially-weighted moving (EWM) std, and why rolling windows matter when regimes shift.

**You'll be able to reason about:**

- Why σ annualizes as $\sigma_\text{ann} = \sigma_\text{period} \sqrt{T}$ under iid returns — and where that breaks.
- Why EWM catches regime shifts faster than a fixed-window rolling std.
- The connection to options pricing: implied vol is the market's forecast of realized.

**Implemented at:** `trading/packages/afml/src/afml/labeling.py:41` — `rolling_vol` computes EWM std of arithmetic returns for barrier calibration.

---

**Next:** [Random walks and the null model →](random-walks.md)
