---
title: Quant Lessons
---

# Quant Lessons

A curriculum that builds from first principles to the primitives that power the [trading project](https://github.com/5x5x5x5/trading). Each lesson arrives at something concrete — a metric, an instrument, or a specific piece of code you can open and run.

## The arc

1. **[The measurable](measurable/returns.md)** — returns, volatility, random walks. The units all strategy code speaks.
2. **[Options, end-to-end](options/contracts.md)** — contracts, payoffs, the bridge from random walk to price.
3. **[The Greeks](greeks/delta.md)** — sensitivity, hedging, the feedback loop.
4. **[The vol surface](vol-surface/implied-vol.md)** — implied vs realized, term structure, skew.
5. **[Dealer positioning and regime](regime/market-makers.md)** — why regimes exist, what the gamma flip marks.
6. **[Backtest discipline](backtest/metrics.md)** — metrics that don't lie, CV that respects time.
7. **[ML for finance](ml/labeling-problem.md)** — why iid fails, and what to do instead.
8. **[Flows and frictions](flows/microstructure.md)** — order flow, events, cross-asset signals.

## Prerequisites

Calculus and basic probability. No options background assumed. No measure theory needed.

## How each lesson is shaped

Every lesson closes with a pointer into the [trading](https://github.com/5x5x5x5/trading) repo — *"implemented at `packages/...`"* — so the concept has somewhere concrete to land. Start with [Lesson 1 →](measurable/returns.md).
