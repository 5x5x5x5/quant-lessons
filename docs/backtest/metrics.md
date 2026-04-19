---
title: "Sharpe, Sortino, max drawdown"
prereqs: "Returns, compounding, log-returns; Volatility as a measurable thing"
arrives_at: "the metrics every strategy report lists, and their failure modes"
code_ref: "trading/packages/harness/src/harness/metrics.py"
---

# Sharpe, Sortino, max drawdown

> **Status:** Draft pending.

**Scope:** Sharpe = $\text{mean} / \text{std} \times \sqrt{\text{annualization}}$. Sortino = mean over *downside* std. Max drawdown = peak-to-trough worst loss on the equity curve. Discuss why Sharpe penalizes vol symmetrically (including upside), why Sortino fixes that partially, and why max DD is the number most allocators actually care about. Brief mention of CVaR and higher moments where tail risk is load-bearing.

**You'll be able to reason about:**

- Why reporting Sharpe without max DD hides tail risk.
- Why Sharpe = 1.0 on daily returns is very different from 1.0 on monthly (different annualization, different underlying distribution).
- The annualization factor 252 (U.S. equity trading days) and when it's wrong (crypto: 365; intraday: varies).

**Implemented at:** `trading/packages/harness/src/harness/metrics.py` — `sharpe`, `sortino`, `max_drawdown`, `turnover`, `capacity_estimate` (stub), `deflated_sharpe` (stub).

---

**Next:** [Walk-forward vs k-fold →](walk-forward.md)
