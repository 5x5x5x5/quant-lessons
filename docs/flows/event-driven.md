---
title: "Event-driven special situations"
prereqs: "—"
arrives_at: "mechanical inefficiencies from earnings, rebalances, spin-offs, and forced flows"
code_ref: "pending — trading/packages/events/"
---

# Event-driven special situations

> **Status:** Draft pending. Package not yet built.

**Scope:** Strategies whose edge comes from structural (not behavioral) inefficiencies — so they don't evaporate when known:

- **PEAD** (post-earnings announcement drift): rank by SUE (standardized unexpected earnings), long top decile / short bottom.
- **Index rebalancing**: forced buying of additions, forced selling of deletions — front-runnable windows of a few days.
- **Spin-offs**: parent and spinco behave predictably around separation (Greenblatt's classic playbook).
- **Tax-loss reversal**: Nov/Dec scan of YTD worst decile with improving fundamentals, hold through February.

**You'll be able to reason about:**

- Why systematic event-driven strategies have higher capacity and lower crowding risk than technical ones.
- The data sources: SEC EDGAR for filings, index methodology PDFs for rebalance rules, SUE datasets for earnings.
- The one-module-per-event architecture planned for the events package: each module emits `signal()` / `size()` against a shared interface.

**Implemented at:** pending — `trading/packages/events/` spec'd in root `CLAUDE.md`, not yet scaffolded.

---

**Next:** [Cross-asset signals →](cross-asset.md)
