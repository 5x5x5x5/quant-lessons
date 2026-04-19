---
title: "Cross-asset signals"
prereqs: "Volatility as a measurable thing"
arrives_at: "multi-asset confirmation — credit, rates, FX, commodities as regime filters for equity setups"
code_ref: "pending — trading/packages/macro/"
---

# Cross-asset signals

Equities don't trade in isolation. Credit spreads widen before equity risk premiums reprice. The dollar moves before emerging-markets equities do. The yield curve inverts before recessions. Copper-to-gold ratio signals growth vs risk-off years in advance of the stock market picking it up.

Every one of these relationships is a lead/lag that technical analysts miss because they look at a single chart. A strategy that checks cross-asset signals before placing equity trades is, on average, operating with better information than one that doesn't.

## The core insight

Asset classes are connected by economic mechanisms, not just sentiment. When these mechanisms kick in, related assets move in coordinated ways. The timing isn't simultaneous — different market participants operate on different time scales, and different market microstructures respond at different speeds. That produces lead/lag, which is the raw material of cross-asset signals.

Three commonly-cited lead/lag patterns:

1. **Credit spreads lead equity.** HYG / LQD ratios widen (high-yield debt performing worse than investment-grade) before equity risk premiums reprice. Credit traders are forward-looking about corporate default risk; equity traders often wait for earnings releases.

2. **Yield curve leads recession.** The 2s10s spread (2-year Treasury yield minus 10-year) inverts ~12 months before recessions historically. Equity markets typically peak closer to recession onset, so the curve leads equity tops.

3. **Dollar leads emerging markets.** A stronger dollar (DXY rising) compresses emerging-market equities through currency translation and dollar-denominated debt pressure. EM equity returns often mirror DXY with a short lag.

These aren't rules of physics. Each pattern has regimes where it breaks — most famously, the 2s10s was arguably "broken" in 2019-2020 by QE's effect on term premia. A cross-asset signal framework should be robust to occasional regime breaks, not lean on any single relationship.

## The standard cross-asset universe

For an equity-focused macro dashboard, the following series are the standard toolkit:

| Series | What it tells you |
|--------|-------------------|
| HYG / LQD | Credit spread (high-yield vs investment-grade bond ETFs) |
| DXY | U.S. dollar strength |
| 2s10s spread | Yield curve slope |
| 5y5y breakevens | Long-term inflation expectations |
| TLT | Long-duration Treasuries (rate sensitivity) |
| GLD / HG=F | Gold / copper (risk vs growth) |
| USD/JPY | Yen pair — risk-on/off proxy |
| VIX | Equity IV level (from Part 4) |
| VIX / VIX3M | Equity IV term structure slope |

Each contributes a different view. Credit spreads and curve slope are "economic" — reflecting real credit risk and growth expectations. DXY, JPY, and copper-gold are "cross-asset risk-on/off" — how is global risk tolerance moving. Vol is its own regime layer.

No single feed is load-bearing. The value of a cross-asset dashboard is the **joint signal**, which is more stable than any individual axis.

## Rolling z-scores as a standard form

Raw levels of these series aren't comparable across each other or across regimes. The dollar index in the 90s means something different than the dollar index in the 2020s. The standard preprocessing is a rolling z-score:

$$
z_t = \frac{x_t - \bar x_\text{lookback}}{\sigma_{x, \text{lookback}}}
$$

Typical lookback windows: 63 days (a quarter) for short-term regime, 252 days (a year) for longer-term regime. Both are informative; the typical dashboard reports both side by side.

Z-scores make signals comparable: "$z$ on credit spreads is +2 and $z$ on DXY is +2" are equally-informative regime statements, even though absolute levels differ. The thresholds (what $z$ counts as "unusual") transfer across series.

## Divergence detectors

The single most-cited cross-asset signal is **equity-credit divergence**:

- Equity is making a new high (or near-high).
- Credit spreads are *not* making a new low (or near-low).

The joint condition says: equity is pricing in continued risk-on while credit is starting to reprice risk. Historically, divergences of this shape often preceded equity corrections by weeks to months. 2007-08, late 2018, and early 2020 all featured clear prior credit-equity divergence.

Implementing this mechanically:

1. Compute rolling 63-day highs (rolling max) of both equity level and the negative of credit spreads.
2. Flag when equity is within 5% of its rolling high and credit is more than 2 standard deviations from its rolling low.
3. Use the flag as a filter on new equity long trades — veto or downweight entries during divergences.

Similar divergence detectors exist on other pairs (equity vs DXY, equity vs 2s10s). They are imperfect individually and useful collectively.

## The 4-state regime classifier

One way to summarize cross-asset state: a 2×2 matrix.

|                | Risk-on          | Risk-off         |
|----------------|------------------|------------------|
| **Inflating**  | Reflation        | Stagflation      |
| **Disinflating** | Goldilocks     | Deflationary bust |

Map the four states by combining:

- **Risk-on/off**: equity direction, credit spread direction, DXY direction.
- **Inflating/disinflating**: 5y5y breakevens direction, commodity complex direction.

Each state implies different trade filters:

- **Goldilocks** (risk-on, disinflating): best regime for equity momentum, long growth.
- **Reflation** (risk-on, inflating): best regime for commodities, real assets, value over growth.
- **Stagflation** (risk-off, inflating): tough for both stocks and bonds; gold and commodities can still work.
- **Deflationary bust** (risk-off, disinflating): best regime for long duration (TLT, long-dated Treasuries), shorts on risk assets.

The classification is approximate and boundaries are fuzzy. Its value is as an organizing principle, not a precise switch. "We're in Goldilocks" is a more useful frame for position-sizing than "the market is neutral on the 12-month horizon."

## Cross-asset as a filter, not a strategy

A key design point: cross-asset signals make **poor primaries** but **excellent filters**. The lead/lags are real but noisy, with false signals and regime-dependent timing. A primary strategy built purely on "credit-equity divergence fires → short equity" would under-perform — the timing of the correction after a divergence can be anywhere from weeks to months, and other factors typically dominate over those horizons.

What works better: use a conviction-based primary (technicals, earnings, microstructure, whatever), then **require cross-asset confirmation** before executing. "Go long equity on my primary signal, *unless* cross-asset regime says risk-off" is a better trade than "go long only when cross-asset says risk-on" (the latter misses too many valid trades).

A reasonable veto threshold: **require $\ge 2$ of 3 cross-asset confirming prints** before equity entries. Confirming = z-scores in the direction consistent with the primary's bias. This keeps the filter lenient enough to not veto too many trades, while still catching obvious regime breaks.

## What the trading project plans

`packages/macro/` is spec'd but not scaffolded. The intended shape:

- Data sources: FRED API for economic series (2s10s, 5y5y, yield curve, CPI), yfinance for liquid ETFs (HYG, LQD, TLT, DXY, GLD).
- `MacroDashboard.snapshot(as_of_date)` returning current levels + z-scores across the universe.
- `detect_divergence(series_a, series_b, lookback)` for pair-wise divergences.
- `classify_4state(dashboard)` for the regime grid.
- `veto_filter(primary_signal, dashboard, min_confirming=2)` for the pre-execution gate.
- Plotly Dash or Streamlit for visualization; static Parquet / DuckDB storage for history.
- Cron or GitHub Actions for daily EOD refresh.

Data freshness matters less than for microstructure — cross-asset signals are measured in days to weeks, so EOD refresh is sufficient. This makes `packages/macro/` one of the easier packages to scaffold once other priorities allow.

## What you can now reason about

- Why lead/lag exists between asset classes — different participants operating on different information and time scales produce coordinated-but-not-simultaneous moves.
- Why rolling z-scores make cross-asset signals comparable across series and across decades — absolute levels reflect regime, z-scores reflect surprise within regime.
- Why cross-asset signals work better as filters than as primaries — the timing of their lead/lag is too variable to drive entries, but the regime information is reliable enough to veto bad setups.

## Implemented at

`packages/macro/` is planned, not yet built. Root CLAUDE.md specifies the scope. When scaffolded, expect:

- Daily EOD refresh of the cross-asset universe.
- Rolling z-score computation at 63-day and 252-day lookbacks.
- Divergence-detector functions for major pairs.
- 4-state regime classifier.
- Integration point: a `veto_filter` consumable by other strategies in the monorepo to pre-gate their entries.

Of the three pending packages (microstructure, events, macro), macro is the lowest barrier to build — data is free or cheap, computation is trivial, integration is clean. Probable next package to scaffold after the current slate of implementations stabilizes.

---

## End of the curriculum

You've walked from [returns and log-returns](../measurable/returns.md) through the Greeks, dealer positioning, backtest discipline, ML for finance, and out into the broader strategy universe. Every lesson pointed back into [the trading project](https://github.com/5x5x5x5/trading) — either at specific code that implements the concept, or at package stubs that will.

The implementation in the repo is a subset of the curriculum. AFML primitives, GEX pipeline, walk-forward harness, meta-labeling capstone — built. Macro, events, and microstructure — spec'd, pending. Deflated Sharpe — stubbed.

If you want to extend the repo, the lessons tell you where the code should go. If you want to understand the code, the lessons tell you why each decision was made.

[← Back to home](../index.md)
