---
title: "Meta-labeling"
prereqs: "Triple-barrier labeling"
arrives_at: "direction vs sizing decomposition — and the capstone strategy's reason to exist"
code_ref: "trading/packages/afml/src/afml/meta.py — MetaLabeler; trading/strategies/meta_rsi2.py"
---

# Meta-labeling

> **Status:** Draft pending.

**Scope:** Split the trading decision into two:

1. **Primary model** decides direction: $+1$, $0$, $-1$.
2. **Secondary model** decides *whether* to take the trade and *at what size*: probability $\to [0, 1]$ multiplier.

The secondary's training target is binary: "was the primary's bet profitable?" — derived from triple-barrier labels via `meta_label`. Features for the secondary describe when the primary works vs fails: vol regime, trailing hit rate, time-of-day, day-of-week, regime tags from the GEX pipeline. Covers why a mediocre primary + smart secondary often lifts Sharpe more than a better primary, and the calibration trade-off that makes soft sizing (Kelly) more punishing than hard sizing when probabilities are biased.

**You'll be able to reason about:**

- Why "primary + secondary" beats "better primary" in practice — the secondary's conditional information is different from the primary's marginal information.
- How to evaluate secondary models: PR-AUC, F1 on the minority class, **never** raw accuracy.
- The sizing decision (`probability_to_size`) — hard threshold vs soft ramp vs Kelly, and the calibration stakes.

**Implemented at:** `trading/packages/afml/src/afml/meta.py` — `MetaLabeler`. `trading/strategies/meta_rsi2.py` — full pipeline composed against an RSI(2) primary with a linear-ramp sizer. `trading/scripts/sweep_meta_rsi2.py` — stability probe.

---

**Next:** [Microstructure and order flow →](../flows/microstructure.md)
