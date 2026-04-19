---
title: "Payoffs and put-call parity"
prereqs: "The options contract"
arrives_at: "the no-arbitrage equation linking calls, puts, stock, and cash"
code_ref: "—"
---

# Payoffs and put-call parity

> **Status:** Draft pending.

**Scope:** Payoff diagrams for single options, spreads (verticals, calendars), and combinations (straddles, strangles, risk reversals). Derive put-call parity:

$$
C - P = S - K e^{-rT}
$$

from the no-arbitrage argument: two portfolios with identical payoffs at expiry must have identical prices today. Parity is **model-free** — it doesn't require Black-Scholes or any distribution assumption.

**You'll be able to reason about:**

- Why you can synthesize a long-stock position from options (synthetic long = long call + short put + bond).
- The equivalence of hedging equity exposure with protective puts versus covered calls.
- Why parity violations (very rare, usually momentary) are arbitrage signals.

**Implemented at:** — (parity is foundational; the repo uses it implicitly in how it treats calls and puts as sides of the same contract.)

---

**Next:** [Black-Scholes as a bridge →](black-scholes.md)
