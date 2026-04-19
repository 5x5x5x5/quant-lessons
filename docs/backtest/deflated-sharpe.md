---
title: "Deflated Sharpe"
prereqs: "Sharpe, Sortino, max drawdown; Walk-forward vs k-fold"
arrives_at: "the multiple-testing-corrected Sharpe — the number you can actually report"
code_ref: "trading/packages/harness/src/harness/metrics.py — deflated_sharpe (NotImplementedError stub)"
---

# Deflated Sharpe

> **Status:** Draft pending.

**Scope:** Try 100 strategies; the best one by Sharpe isn't the best strategy — it's the luckiest. Bailey & López de Prado 2014 derive the **expected maximum Sharpe** under the null across $N$ iid trials:

$$
\mathbb{E}[\max \text{SR}] \approx \sigma \left[(1 - \gamma)\Phi^{-1}\!\left(1 - \tfrac{1}{N}\right) + \gamma \Phi^{-1}\!\left(1 - \tfrac{1}{Ne}\right)\right]
$$

where $\gamma$ is Euler-Mascheroni. **Deflated Sharpe** asks: what is the probability that the true Sharpe exceeds zero given the observed statistic and the deflation? Includes a non-normality correction (skewness, kurtosis in the denominator).

**You'll be able to reason about:**

- Why "Sharpe > 1" is meaningless without disclosing how many strategies were tried.
- How sharply $\mathbb{E}[\max \text{SR}]$ grows in $N$ — even the null is deceptive.
- Why the harness `deflated_sharpe` is a `NotImplementedError` stub and what it needs — non-normality terms plus the E[max SR] piece this lesson derives.

**Implemented at:** `trading/packages/harness/src/harness/metrics.py` — `deflated_sharpe` raises `NotImplementedError`; `expected_max_sharpe(num_trials, std_across_trials)` is the helper already written, used internally by the full DSR.

---

**Next:** [The labeling problem →](../ml/labeling-problem.md)
