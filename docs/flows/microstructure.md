---
title: "Microstructure and order flow"
prereqs: "The options contract (for terminology); Volatility (for regime framing)"
arrives_at: "the signal layer that lives below OHLCV — ticks, L2 depth, trade direction"
code_ref: "pending — trading/packages/microstructure/"
---

# Microstructure and order flow

> **Status:** Draft pending. Package not yet built.

**Scope:** Below daily and minute bars lies a richer signal layer. Define the order book (bid, ask, depth by level). **Lee-Ready algorithm** for classifying trades as buyer- or seller-initiated from tick data. **Volume footprint**: bid-volume vs ask-volume at each price level, highlighting imbalances. **Market Profile (TPO)**: VAH, VAL, POC, single prints — the distribution of time spent at each price. Fill simulation must use L2 snapshots or the backtest will systematically underestimate slippage.

**You'll be able to reason about:**

- Why daily-bar backtests can't capture microstructure edge — the signals live in the intra-bar sequencing.
- How cumulative delta divergence (price up, cumulative buyer-initiated volume flat) signals unconfirmed moves.
- Why POC rejection is a real signal — the most heavily traded price acts as a magnet until it doesn't.

**Implemented at:** pending — `trading/packages/microstructure/` is spec'd in root `CLAUDE.md` but not yet scaffolded.

---

**Next:** [Event-driven special situations →](event-driven.md)
