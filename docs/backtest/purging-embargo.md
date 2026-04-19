---
title: "Purging, embargo, and label horizons"
prereqs: "Walk-forward vs k-fold"
arrives_at: "leak-free CV on overlapping labels — the AFML ch.7 fix"
code_ref: "trading/packages/afml/src/afml/cv.py — PurgedKFold"
---

# Purging, embargo, and label horizons

> **Status:** Draft pending.

**Scope:** Financial ML labels often have **horizons** — triple-barrier's vertical barrier is 5 days, so a sample at time $t$ carries information from $[t, t+5]$. A train sample whose horizon extends into the test fold leaks information, even if $t$ itself is in the train set. **Purging** drops overlapping train samples. **Embargo** adds a buffer after the test fold to block serial-correlation leakage. Walk through the AFML algorithm and why embargo as a small percentage of sample size is a reasonable default.

**You'll be able to reason about:**

- Why naive-k-fold Sharpes on triple-barrier labels are biased upward — the leak is silent.
- The ~1-2% embargo heuristic and why it's usually enough in liquid markets.
- Why the trading project uses `WalkForward` for outer evaluation and `PurgedKFold` for inner model selection — they solve different leakage geometries.

**Implemented at:** `trading/packages/afml/src/afml/cv.py` — `PurgedKFold(n_splits, t1, embargo_pct)` extends `sklearn.BaseCrossValidator`.

---

**Next:** [Deflated Sharpe →](deflated-sharpe.md)
