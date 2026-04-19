---
title: "The gamma flip strike"
prereqs: "Dealer gamma — long vs short"
arrives_at: "the strike at which cumulative dealer gamma crosses zero — a practical regime marker"
code_ref: "trading/packages/gex/src/gex/gex.py — gamma_flip_strike"
---

# The gamma flip strike

> **Status:** Draft pending.

**Scope:** Define the gamma flip as the strike where **cumulative** dealer GEX crosses zero — not where per-strike GEX changes sign. Above the flip, dealers are long gamma in aggregate; hedging is mean-reverting. Below it, they're short gamma; hedging amplifies. The distinction between "per-strike sign flip" and "cumulative zero crossing" is load-bearing — the trading repo's initial implementation got it wrong and was fixed in commit `1e90d49`.

**You'll be able to reason about:**

- Why the flip is typically *not* at the ATM strike — it's wherever cumulative OI balances.
- How the flip moves as OI accumulates approaching expiry (dealer book grows → flip tightens toward ATM).
- Why knowing the flip + current spot is the single most actionable read from the GEX pipeline.

**Implemented at:** `trading/packages/gex/src/gex/gex.py` — `gamma_flip_strike(per_strike, spot)`. See commit `1e90d49` for the correctness fix that turned a per-strike sign-flip into a cumulative-GEX zero crossing.

---

**Next:** [Sharpe, Sortino, max drawdown →](../backtest/metrics.md)
