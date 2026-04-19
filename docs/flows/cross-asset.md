---
title: "Cross-asset signals"
prereqs: "Volatility as a measurable thing"
arrives_at: "multi-asset confirmation — credit, rates, FX, commodities as regime filters for equity setups"
code_ref: "pending — trading/packages/macro/"
---

# Cross-asset signals

Equities do not trade in isolation. Credit spreads widen before equity risk premiums reprice. The dollar moves before emerging-markets equities respond. The yield curve inverts before recessions. The copper-to-gold ratio signals growth versus risk-off conditions years before equity markets reflect them.

Each of these relationships is a lead-lag that single-chart technical analysis misses. A strategy that incorporates cross-asset signals before taking equity positions operates, on average, with more information than one that does not.

## The core concept

Asset classes are connected by economic mechanisms, not only by sentiment. When these mechanisms activate, related assets move in coordinated ways. The timing is not simultaneous: different market participants operate on different time scales, and different market microstructures respond at different speeds. The resulting lead-lag relationships form the basis of cross-asset signals.

Three commonly cited lead-lag patterns:

1. **Credit spreads lead equity.** HYG/LQD ratios widen (high-yield debt underperforming investment-grade) before equity risk premiums reprice. Credit traders are more forward-looking about corporate default risk than equity traders, who often wait for earnings releases.

2. **Yield curve leads recession.** The 2s10s spread (2-year Treasury yield minus 10-year) has historically inverted approximately 12 months before recessions. Equity markets typically peak closer to recession onset, so the curve leads equity market tops.

3. **Dollar leads emerging markets.** A strengthening dollar (rising DXY) compresses emerging-markets equities through currency translation and pressure on dollar-denominated debt. EM equity returns often track DXY with a short lag.

These patterns are not physical laws. Each has regimes in which it breaks down. For example, the 2s10s inversion signal was arguably disrupted during 2019-2020 by QE's effect on term premia. A cross-asset signal framework should be robust to regime breaks rather than dependent on any single relationship.

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

Each series contributes a different view. Credit spreads and curve slope are economic indicators, reflecting credit risk and growth expectations. DXY, JPY, and copper-gold are cross-asset risk-on/off indicators, reflecting global risk tolerance. Volatility is a separate regime layer.

No single series is dispositive. The value of a cross-asset dashboard lies in the joint signal, which is more stable than any individual axis.

## Rolling z-scores as a standard form

Raw levels of these series are not comparable across each other or across time. The dollar index in the 1990s represents different economic conditions than the dollar index in the 2020s. The standard preprocessing is a rolling z-score:

$$
z_t = \frac{x_t - \bar x_\text{lookback}}{\sigma_{x, \text{lookback}}}.
$$

Typical lookback windows are 63 days (one quarter) for short-term regime and 252 days (one year) for longer-term regime. Both are informative, and dashboards commonly report both.

Z-scores make signals comparable across series. A $z = +2$ on credit spreads and $z = +2$ on DXY convey equivalent regime information despite differing absolute levels. Thresholds for "unusual" values transfer across series.

## Divergence detectors

The most commonly cited cross-asset signal is equity-credit divergence:

- Equity is making a new high or is near one.
- Credit spreads are not making a new low or are not near one.

The joint condition indicates that equity is pricing continued risk-on while credit is beginning to reprice risk. Historically, such divergences have preceded equity corrections by weeks to months. The 2007-2008, late-2018, and early-2020 corrections all followed clear prior credit-equity divergences.

A mechanical implementation:

1. Compute rolling 63-day maxima for the equity level and for the negative of credit spreads.
2. Flag when equity is within 5% of its rolling high and credit is more than 2 standard deviations from its rolling low.
3. Use the flag as a filter on new equity long trades — vetoing or downweighting entries during divergences.

Similar divergence detectors exist for other pairs (equity versus DXY, equity versus 2s10s). Individually each is imperfect; collectively they provide useful regime information.

## Four-state regime classifier

One summary of cross-asset state uses a 2×2 matrix:

|                | Risk-on          | Risk-off         |
|----------------|------------------|------------------|
| **Inflating**  | Reflation        | Stagflation      |
| **Disinflating** | Goldilocks     | Deflationary bust |

The four states are identified by combining:

- **Risk-on/off**: equity direction, credit spread direction, DXY direction.
- **Inflating/disinflating**: 5y5y breakevens direction, commodity complex direction.

Each state implies different trade filters:

- **Goldilocks** (risk-on, disinflating): favorable regime for equity momentum and long growth.
- **Reflation** (risk-on, inflating): favorable regime for commodities, real assets, value over growth.
- **Stagflation** (risk-off, inflating): unfavorable for both stocks and bonds; gold and commodities may still perform.
- **Deflationary bust** (risk-off, disinflating): favorable regime for long duration (TLT, long-dated Treasuries) and shorts on risk assets.

The classification is approximate, and the boundaries are fuzzy. It is valuable as an organizing principle rather than a precise switch. The statement "the regime is Goldilocks" is more useful for position sizing than "the market is neutral on the 12-month horizon."

## Cross-asset as filter, not primary

A key design point: cross-asset signals serve poorly as primaries but well as filters. The lead-lags are real but noisy, with false signals and regime-dependent timing. A primary strategy based purely on "credit-equity divergence fires → short equity" would underperform; the timing of corrections following divergences ranges from weeks to months, and other factors typically dominate over those horizons.

The effective pattern: use a conviction-based primary (technical, fundamental, microstructure) and require cross-asset confirmation before execution. "Take the primary signal unless cross-asset regime is risk-off" is preferable to "take the primary only when cross-asset is risk-on," which would reject too many valid trades.

A reasonable veto threshold: require at least 2 of 3 cross-asset confirming prints before equity entries, where confirming means z-scores directionally consistent with the primary's bias. This filter is lenient enough to avoid excessive rejections while still detecting material regime breaks.

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

## Summary

The reader can now reason about:

- Why lead-lag exists between asset classes: different participants operate on different information sets and time scales, producing coordinated but not simultaneous moves.
- Why rolling z-scores make cross-asset signals comparable across series and across decades: absolute levels reflect regime, while z-scores reflect surprise within regime.
- Why cross-asset signals work better as filters than as primaries: the timing of lead-lag is too variable to drive entries, but regime information is reliable enough to veto poor setups.

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

The curriculum has progressed from [returns and log-returns](../measurable/returns.md) through the Greeks, dealer positioning, backtest discipline, ML for finance, and into the broader strategy universe. Each lesson references [the trading project](https://github.com/5x5x5x5/trading), either pointing to code that implements the concept or to package stubs that will.

The repository implementation is a subset of the curriculum. AFML primitives, the GEX pipeline, the walk-forward harness, and the meta-labeling capstone are built. Macro, events, and microstructure packages are specified but pending. Deflated Sharpe is stubbed.

For extending the repository, the lessons indicate where new code should be placed. For understanding existing code, the lessons document the rationale for each design decision.

[← Back to home](../index.md)
