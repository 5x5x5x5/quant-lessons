---
title: "Cross-asset signals"
prereqs: "Volatility as a measurable thing"
arrives_at: "multi-asset confirmation — credit, rates, FX, commodities as regime filters for equity setups"
code_ref: "pending — trading/packages/macro/"
---

# Cross-asset signals

> **Status:** Draft pending. Package not yet built.

**Scope:** Equities don't trade in isolation. Credit spreads (HYG/LQD), the dollar (DXY), the yield curve (2s10s, 5y5y breakevens), commodities (copper/gold), USD/JPY — these often *lead* equity regimes more reliably than equity technicals lead themselves. Rolling z-scores on cross-asset factors surface regime shifts. **Divergence detector**: equity making new highs while credit makes lower highs flags a regime at risk. A 4-state classifier (risk on/off × inflating/disinflating) is a natural lens. Trade filter: require ≥2 of 3 cross-asset confirming prints before any equity entry.

**You'll be able to reason about:**

- Why single-asset technicals miss regime shifts that cross-asset flows lead.
- The data sources: FRED API for macro time series, yfinance for liquid ETFs (HYG, LQD, DXY, TLT, GLD, copper futures).
- Why this is a **filter**, not a standalone strategy — it vetoes or confirms, it doesn't decide direction on its own.

**Implemented at:** pending — `trading/packages/macro/` spec'd in root `CLAUDE.md`, not yet scaffolded.

---

**End of curriculum.** [← Back to home](../index.md)
