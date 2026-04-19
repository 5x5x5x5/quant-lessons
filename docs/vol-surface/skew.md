---
title: "Skew and the smile"
prereqs: "Implied vol vs realized"
arrives_at: "asymmetric pricing of downside vs upside risk — the 25-delta put/call skew"
code_ref: "trading/packages/gex/src/gex/skew.py"
---

# Skew and the smile

> **Status:** Draft pending.

**Scope:** Observed IV across strikes is not flat. For equity indices, OTM puts trade at higher IV than OTM calls — the **skew**. Origin: 1987 crash reshaped demand for tail protection; persistent demand from hedgers keeps puts bid. The **25-delta skew** measures the IV difference between the 25-delta put and 25-delta call. Its rolling z-score is a regime input. Single-name equity options often look **smile-shaped** (high IV on both wings) rather than skewed — different customer flow.

**You'll be able to reason about:**

- Why the Black-Scholes constant-$\sigma$ assumption is empirically wrong at every maturity.
- The risk profile of "selling naked OTM puts" — picking up pennies in front of a steamroller.
- How skew z-score feeds the regime classifier as a short-gamma trigger (deeply negative z = skew crushing = stress).

**Implemented at:** `trading/packages/gex/src/gex/skew.py` — `interpolate_iv_at_delta`, `skew_25d`.

---

**Next:** [Market makers and delta-hedging →](../regime/market-makers.md)
