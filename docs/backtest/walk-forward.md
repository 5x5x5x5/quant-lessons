---
title: "Walk-forward vs k-fold"
prereqs: "Sharpe, Sortino, max drawdown"
arrives_at: "time-respecting cross-validation — train on past, test on future, advance the anchor"
code_ref: "trading/packages/harness/src/harness/backtest.py"
---

# Walk-forward vs k-fold

> **Status:** Draft pending.

**Scope:** Naive k-fold shuffles and is wrong for time series — training data can include information from the future relative to the test set. **Walk-forward**: train on $[0, t]$, test on $(t, t + h]$, advance $t$ by a stride. **Expanding** train windows grow with each step; **sliding** windows have fixed lookback. Stride and overlap decisions. Why walk-forward is the outer evaluation loop, not an inner model-selection loop.

**You'll be able to reason about:**

- Why you shouldn't tune hyperparameters on the full-sample Sharpe — a classic in-sample / out-of-sample mistake that looks innocent.
- The tradeoff between expanding (more data, newer data gets small weight) and sliding (adaptive, forgets old regimes).
- Why even walk-forward needs a final held-out period before deflated-Sharpe accounting is honest.

**Implemented at:** `trading/packages/harness/src/harness/backtest.py` — `WalkForwardConfig`, `WalkForward.split`.

---

**Next:** [Purging, embargo, and label horizons →](purging-embargo.md)
