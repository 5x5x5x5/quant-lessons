---
title: "Term structure of volatility"
prereqs: "Implied vol vs realized"
arrives_at: "the slope of IV across maturities — normally upward (contango), inverted in crises"
code_ref: "trading/packages/gex/src/gex/termstructure.py"
---

# Term structure of volatility

> **Status:** Draft pending.

**Scope:** IV across maturities using ATM options. **Contango** (far > near) is the normal state: longer horizons carry more uncertainty. **Backwardation / inversion** (near > far) is a crisis marker — short-dated protection is suddenly in demand. Introduce VIX9D (9-day), VIX (30-day), VIX3M (3-month). The regime classifier uses VIX/VIX3M > 1.02 as its `vol_inverted` trigger.

**You'll be able to reason about:**

- Why a single IV number is reductive — the slope carries regime information a level can't.
- How term-structure inversion historically precedes volatility events (Feb 2018, March 2020).
- Why the regime classifier uses 1.02 specifically and not 1.00 (noise tolerance vs sensitivity).

**Implemented at:** `trading/packages/gex/src/gex/termstructure.py` — `compute_term_structure`, `rolling_inversion_flags`.

---

**Next:** [Skew and the smile →](skew.md)
