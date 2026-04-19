---
title: "Microstructure and order flow"
prereqs: "The options contract (for terminology); Volatility as a measurable thing (for regime framing)"
arrives_at: "the signal layer that lives below OHLCV — ticks, L2 depth, trade direction"
code_ref: "pending — trading/packages/microstructure/"
---

# Microstructure and order flow

Everything in this curriculum so far assumes you care about bars — daily, hourly, maybe 5-minute. Microstructure is what happens *inside* a bar. At this scale, the tape doesn't move smoothly; it ticks. Every tick is a transaction between a buyer and a seller, happening at a specific price in a specific order book, possibly triggering a chain of further transactions. Read at this scale, the tape tells a different story than the bar chart does.

This is where prop traders live. Retail almost never does, because the data is expensive, the latency matters, and the backtest fidelity is hard to achieve. The edge is real but the moat to get there is real too.

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

The **best bid** and **best ask** (Level 1) are what most quote feeds report. The **depth** behind them (Level 2, sometimes deeper) is where the information lives. Which side has more size? Where do the orders thin out? A 100,000-share buy order submitted into a book with only 50,000 of ask depth will blow through multiple price levels, producing a price spike visible on the bar chart as "the close ran up." Knowing the depth tells you that in advance.

## Trade classification: Lee-Ready

When a trade prints on the tape at some price $P$, was the aggressor the buyer or the seller? Equivalently, did someone hit the bid (sell aggression), or lift the ask (buy aggression)?

The answer isn't in the raw tick feed directly — trades print without a tag. The **Lee-Ready algorithm** infers direction from price location and timing:

1. If the trade price is above the midpoint, classify as a buy (lifted the ask, or above-mid in the nearest tick).
2. If below the midpoint, classify as a sell.
3. If exactly at the midpoint, use the tick rule: compare to the previous trade's price. Higher → buy; lower → sell. If equal, use the previous classification.

Lee-Ready (1991) is the default classification in equity microstructure research. Accuracy is high for active stocks (>90% for liquid names) but degrades for illiquid names or during fast markets where quotes lag trades.

Modern alternatives (BVC, tick-sign, direct venue-tagged classifications) exist and offer marginal improvements. For a first implementation, Lee-Ready is the right starting point.

## Volume footprint

Given trade-direction classification, aggregate volume at each price level and split into bid-volume vs ask-volume. A **footprint chart** visualizes this:

```
price     bid-vol    ask-vol
101.00     100        500      ← ask-heavy at this level
100.98     200        450
100.96     300        250
100.94     450        200
100.92     500        150      ← bid-heavy at this level
```

The pattern across a bar (say, a 5-minute interval) shows where buying was aggressive and where selling was aggressive. A bar that closes up with bid-heavy volume at the bottom and ask-heavy at the top tells a different story than a bar that closes up with ask-heavy throughout: the first suggests short-covering absorbed, the second suggests continued demand.

Reading footprints well is a skill. The interpretation space is rich — stacked imbalances (multiple consecutive price levels all heavily ask-biased), absorption (heavy volume without price movement at a key level), and divergence (price makes a new high while cumulative ask-volume decays) are all patterns practitioners track.

## Cumulative delta

Sum the signed volume (+ask_volume, -bid_volume) across a period to get **cumulative delta**. When cumulative delta rises, more aggressive buying than selling happened. When it falls, the opposite.

The useful signal is when cumulative delta **diverges** from price. If price makes a new intraday high but cumulative delta doesn't, the move was thin — more short-covering than genuine demand, likely to fade. Likewise, a new low on thin cumulative delta often retraces.

Delta divergence is among the most-cited microstructure signals in retail education. The reality is that it works in some regimes (typically ranging or late-trend) and fails in others (early-trend or sudden-regime-change breakouts). It's not a free signal, but it's a meaningful input to a broader signal set.

## Market Profile / TPO

Another view on the same underlying data. **Time-price opportunity (TPO)** charts show, for a given session, the set of price levels traded during each 30-minute period. Over a full session, each price level gets a count of how many 30-minute slots it was traded in.

From the count distribution:

- **Point of Control (POC)**: the price level traded for the most time.
- **Value Area High (VAH)** and **Low (VAL)**: the upper and lower bounds of the 70% band (typically) around the POC.
- **Single prints**: price levels that traded in only one 30-minute period, often at session extremes.

Market Profile interpretation is old-school (Peter Steidlmayer's 1980s work) but durable. The key intuition: **prices that traded heavily in the past tend to act as magnets in the future.** POCs from yesterday's session often draw price back to them today. Single-print extremes are areas where price passed through without finding counterparty agreement, often fast-filled if revisited.

## Why this edge is durable

Microstructure strategies — as distinct from technical analysis on bar charts — have durable edge for three reasons:

1. **Data costs create a moat.** Clean L2 tick data from exchanges is expensive (Databento starts at thousands per month for SPX alone; direct exchange feeds are five to six figures annually). This prices most retail out of the game. The strategies that survive the cost are the ones that make back multiples of data cost in P&L; the ones that don't, die. Adverse selection keeps the competitive field small.

2. **Latency matters.** A signal computed on yesterday's close is available to everyone. A signal computed from this millisecond's order book is available only to infrastructure that can do that computation fast. Co-location in exchange data centers is not optional for the sharpest strategies.

3. **Simulation is hard.** Backtesting a microstructure strategy requires simulating your own order interaction with the book — queue position, fill probability, slippage, adverse selection. Cheap simulators use midpoint fills and systematically overstate strategy quality; a strategy that looks profitable on midpoint fills often bleeds in reality. Building a faithful L2 simulator is a significant engineering effort on its own.

The first two moats shrink over time (data gets cheaper, hosted services offer co-location); the third stays.

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

A cheaper entry point: free or low-cost data sources provide enough microstructure information for *some* strategies:

- **1-minute OHLCV with volume**: Yahoo, IEX, Alpaca free-tier. Too coarse for real microstructure work, but volume-at-price can be approximated.
- **Level 1 tick data**: tick-level trades without book depth. Lee-Ready works (tick rule fallback dominates when book state isn't known).
- **IBKR delayed L2**: 15-minute delayed Level 2 for most U.S. equities, free. Insufficient for live trading; useful for building and sanity-checking strategy logic.

A strategy built on these substrates won't compete with prop shops. But it can still exhibit meaningful alpha patterns — especially in less-liquid markets (small caps, some crypto pairs) where the moat against institutions is smaller.

## What you can now reason about

- Why microstructure edge is considered durable despite public awareness — the data-cost moat, latency requirement, and simulation fidelity are all structural barriers.
- Why the Lee-Ready algorithm is the default trade-classification method and where it fails (illiquid names, fast markets where quotes lag).
- The distinction between volume footprint (price-level bid vs ask volume) and TPO (price-level time counts) — different aggregations of the same underlying tick data, producing different interpretive frameworks.

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
