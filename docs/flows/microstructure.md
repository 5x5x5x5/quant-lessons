---
title: "Microstructure and order flow"
prereqs: "The options contract (for terminology); Volatility as a measurable thing (for regime framing)"
arrives_at: "the signal layer that lives below OHLCV — ticks, L2 depth, trade direction"
code_ref: "pending — trading/packages/microstructure/"
---

# Microstructure and order flow

The curriculum to this point has assumed the analysis operates on bars — daily, hourly, or 5-minute. Microstructure is the activity within a bar. At this scale, prices move in discrete ticks rather than continuously. Each tick represents a transaction between a buyer and a seller at a specific price in a specific order book, potentially triggering a chain of further transactions. The view at this scale differs substantially from the bar-chart view.

Microstructure is the domain of proprietary trading firms. Retail participation is rare because the required data is expensive, latency matters, and backtest fidelity is difficult to achieve. The edge is real but the barriers to access are substantial.

## The order book

At any moment, a security's market state is summarized by the order book — a list of **bids** (buy orders at specific prices) and **asks** (sell orders at specific prices).

```
         size   price
ask 3:   2000   101.05
ask 2:   3500   101.03
ask 1:   1200   101.01   ← best ask (lowest sell price)
--------------- spread = $0.03
bid 1:    800   100.98   ← best bid (highest buy price)
bid 2:   1800   100.96
bid 3:   2500   100.94
```

The best bid and best ask (Level 1) are what most quote feeds report. The depth behind them (Level 2, sometimes deeper) contains the additional information. Which side has more size? Where do orders thin out? A 100,000-share buy order submitted into a book with only 50,000 of ask depth will traverse multiple price levels, producing a price spike visible on the bar chart as "the close ran up." Depth information identifies this condition in advance.

## Trade classification: Lee-Ready

When a trade prints at price $P$, which side was the aggressor — the buyer or the seller? Equivalently, was the bid hit (sell aggression) or the ask lifted (buy aggression)?

The raw tick feed does not carry this tag. The **Lee-Ready algorithm** infers direction from price location and timing:

1. If the trade price is above the midpoint, classify as a buy (ask lifted, or closest tick above mid).
2. If below the midpoint, classify as a sell.
3. If at the midpoint exactly, apply the tick rule: compare with the previous trade price. Higher previous trade implies buy; lower implies sell. When equal, carry forward the previous classification.

Lee-Ready (1991) is the standard classification method in equity microstructure research. Accuracy is high for active stocks (above 90% for liquid names) and degrades for illiquid names or fast markets where quotes lag trades.

Alternative methods (BVC, tick-sign, venue-tagged classifications) offer marginal improvements. For a first implementation, Lee-Ready is the appropriate starting point.

## Volume footprint

Given trade-direction classifications, aggregate volume at each price level into bid-volume and ask-volume components. A **footprint chart** visualizes the result:

```
price     bid-vol    ask-vol
101.00     100        500      ← ask-heavy at this level
100.98     200        450
100.96     300        250
100.94     450        200
100.92     500        150      ← bid-heavy at this level
```

The pattern across a bar (for example, a 5-minute interval) shows where buying and selling were aggressive. A bar that closes up with bid-heavy volume at the bottom and ask-heavy volume at the top differs from a bar that closes up with ask-heavy volume throughout: the first suggests absorbed short-covering, the second suggests continued demand.

Reading footprints effectively is a skill. The interpretive space includes stacked imbalances (multiple consecutive price levels all heavily ask-biased), absorption (heavy volume without price movement at a key level), and divergence (price makes a new high while cumulative ask-volume decays).

## Cumulative delta

Summing signed volume (+ask_volume, −bid_volume) across a period produces **cumulative delta**. Rising cumulative delta indicates more aggressive buying than selling; falling cumulative delta indicates the reverse.

The useful signal appears when cumulative delta diverges from price. If price makes a new intraday high but cumulative delta does not, the move is thin — more short-covering than genuine demand — and is likely to fade. Similarly, a new low on thin cumulative delta often retraces.

Delta divergence is among the most-cited microstructure signals in retail education. Its reliability varies by regime: it tends to work in ranging or late-trend markets and fails in early-trend or sudden-regime-change breakouts. The signal is not free, but it is a meaningful input to a broader signal set.

## Market Profile (TPO)

A related view of the same underlying data. **Time-price opportunity (TPO)** charts show, for a given session, the set of price levels traded during each 30-minute period. Over a full session, each price level receives a count of the 30-minute slots during which it was traded.

From the count distribution:

- **Point of Control (POC)**: the price level traded for the most time.
- **Value Area High (VAH)** and **Low (VAL)**: the upper and lower bounds of the band (typically 70%) around the POC.
- **Single prints**: price levels traded in only one 30-minute period, often at session extremes.

Market Profile interpretation originates in Peter Steidlmayer's 1980s work and remains relevant. The central intuition: prices that traded heavily in the past tend to act as magnets in the future. The prior session's POC often attracts price the following day. Single-print extremes — areas where price passed through without finding counterparty agreement — are often filled quickly when revisited.

## Sources of durable edge

Microstructure strategies, as distinct from technical analysis on bar charts, retain durable edge for three reasons:

1. **Data costs.** Clean L2 tick data from exchanges is expensive (Databento starts at thousands per month for SPX alone; direct exchange feeds are five to six figures annually). This cost excludes most retail participants. Strategies that survive the data cost generate returns that exceed it; those that do not are discontinued. Adverse selection keeps the competitive field small.

2. **Latency.** A signal computed on yesterday's close is available to all participants. A signal computed from the current order book is available only to infrastructure capable of producing it quickly. Co-location in exchange data centers is necessary for the sharpest strategies.

3. **Simulation difficulty.** Backtesting a microstructure strategy requires simulating order interaction with the book — queue position, fill probability, slippage, adverse selection. Midpoint-fill simulators systematically overstate strategy quality; a strategy that appears profitable at midpoint often loses money live. A faithful L2 simulator requires substantial engineering effort.

The first two barriers shrink over time as data becomes cheaper and co-location becomes more accessible. The third persists.

## What the trading project plans

`packages/microstructure/` is spec'd but not built. The rough outline from the root CLAUDE.md:

- Data source: Databento MBP-10 (expensive, necessary) or IBKR historical via `ib_insync`.
- Lee-Ready tick classification.
- Volume footprint in N-volume bars (not time bars — volume bars produce more stationary statistics).
- Cumulative delta, stacked-imbalance detector.
- TPO profile: VAH, VAL, POC, single prints.
- Signals: delta/price divergence, POC rejection.
- Fill simulator using L2 snapshots, not midpoint — or the backtest lies.

The package isn't scaffolded yet, and getting it right will require paid data. When it's built, it will plug into the same `harness` primitives the other strategies use — walk-forward, cost models, metrics — with its own specialized fill simulator.

## Retail-accessible microstructure

Lower-cost data sources provide enough microstructure information for some strategies:

- **1-minute OHLCV with volume**: Yahoo, IEX, Alpaca free tier. Too coarse for full microstructure work, but volume-at-price can be approximated.
- **Level 1 tick data**: tick-level trades without book depth. Lee-Ready is usable (the tick-rule fallback dominates when book state is unknown).
- **IBKR delayed L2**: 15-minute delayed Level 2 for most U.S. equities, free. Insufficient for live trading but useful for building and sanity-checking strategy logic.

Strategies built on these substrates will not compete with proprietary trading firms. They can still exhibit meaningful alpha patterns, particularly in less liquid markets (small caps, certain crypto pairs) where the barrier against institutional competition is smaller.

## Summary

The reader can now reason about:

- Why microstructure edge is considered durable despite public awareness: data cost, latency requirements, and simulation fidelity are all structural barriers.
- Why the Lee-Ready algorithm is the standard trade-classification method and where it fails (illiquid names, fast markets with lagging quotes).
- The distinction between volume footprint (price-level bid versus ask volume) and TPO (price-level time counts): different aggregations of the same underlying tick data producing different interpretive frameworks.

## Implemented at

`packages/microstructure/` is planned but not scaffolded. When it's built, expect:

- A `ChainSource`-like abstraction over L2 feeds (Databento, IBKR).
- `classify_lee_ready(ticks)` producing buy/sell tags.
- `volume_footprint(ticks, bar_rule="volume", bar_size=10000)` returning per-bar bid-vol vs ask-vol at each price level.
- `tpo_profile(ticks)` producing VAH, VAL, POC, single prints per session.
- `L2FillSimulator` (in harness, or in microstructure) for honest backtests.

The package will be scoped with the same "primitives, not engine" philosophy as the current `harness` — strategies compose against these, they don't become engines.

---

**Next:** [Event-driven special situations →](event-driven.md)
