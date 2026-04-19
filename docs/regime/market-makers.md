---
title: "Market makers and delta-hedging"
prereqs: "Delta — sensitivity to price"
arrives_at: "who sells options and how their risk management shapes the tape"
code_ref: "—"
---

# Market makers and delta-hedging

> **Status:** Draft pending.

**Scope:** Options market makers provide two-sided liquidity and take the other side of customer flow. They are not directional — they hedge. The dealer delta-hedging loop: sell a call → collect premium → short Δ shares → as $S$ moves, adjust delta → capture bid-ask spread, pay slippage. Introduce the sign convention used in this repo: **dealers are short customer-preferred flow** — short calls (customers net-long calls on indices), long puts (customers buy puts for hedging).

**You'll be able to reason about:**

- Why MM flow is dominant near key strikes at expiry — OI × gamma × spot² concentrates hedging demand.
- The distinction between **customer flow** and **dealer flow**, and why they push in opposite directions.
- Why single-name options have different dealer positioning than index options — customer flow skews differently (more covered-call overwriting, less put-hedging).

**Implemented at:** — (the convention is documented in `packages/gex/CLAUDE.md` and encoded in the sign of per-strike GEX aggregation.)

---

**Next:** [Dealer gamma — long vs short →](dealer-gamma.md)
