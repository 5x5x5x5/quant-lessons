---
title: "Market makers and delta-hedging"
prereqs: "Delta — sensitivity to price"
arrives_at: "who sells options and how their risk management shapes the tape"
code_ref: "—"
---

# Market makers and delta-hedging

The GEX pipeline rests on a specific model of who sells options and how they manage the resulting risk. Get that model wrong and every downstream regime call is wrong — with the same magnitude, in the opposite direction. So it's worth being explicit.

## Who sells options?

When a retail trader buys a call, someone sells it. When a pension fund buys puts for downside protection, someone sells them. The aggregate seller across the entire options market is a loose collection of institutional participants, but the single dominant category is **options market makers**. Quantitative firms — Susquehanna, Citadel Securities, Optiver, IMC, and a handful of others — run the bulk of exchange-listed options flow.

Market makers are liquidity providers. They quote two-sided markets (a bid and an ask) on tens of thousands of contracts simultaneously. Their business model is earning the bid-ask spread, not taking directional views. A market maker who accidentally became long SPX by a million delta-units of exposure would be doing their job wrong.

This framing matters because it shapes how they hedge. A directional trader who buys a call is willing to be wrong — that's what taking a view means. A market maker who sells a call is **obligated** to neutralize the exposure they just acquired. They can't afford to be wrong; the position size across tens of thousands of contracts is too large, and their capital isn't set up for one-way risk.

## The customer-preferred flow assumption

The next assumption is less rigorous but empirically dominant:

> **Customers are net buyers of options on equity indices.**

Two threads support this. Retail and many institutional traders buy calls for leveraged upside exposure (lottery tickets, bullish plays, overwrite-hedging of underlying equity). Hedgers — pension funds, endowments, insurance companies, wealth managers — buy puts for downside protection on large equity books.

On single names, the picture is messier. Covered-call overwriters are net sellers of calls (the classic "income" strategy). Earnings straddles are two-sided. Dealer positioning on individual tickers is genuinely ambiguous and depends on who holds the name.

On indices (SPX, NDX, QQQ, SPY), the customer-net-buyer assumption is robust enough to encode in code. The trading project's `gex.py` assigns dealers **short gamma on calls** (`sign = -1` for C) and **long gamma on puts** (`sign = +1` for P). This is "dealers short customer-preferred flow" in signs. Flip the signs and you invert every regime call downstream.

The package-level CLAUDE.md calls this out explicitly as the project's sign convention and flags that single-name applications should revisit it. This isn't a detail — it's a structural assumption that sits at the foundation of everything else in Part 5.

## Delta-hedging in practice

A market maker who has sold an SPY call with $\Delta = 0.40$ has gained $-0.40$ share-equivalents of exposure per share covered by the contract. For a 100-share contract, that's $-40$ shares. To neutralize, the MM buys 40 shares of SPY. Their portfolio is now:

- Short 1 call (premium collected).
- Long 40 shares of SPY (purchased at the ask).
- First-order directional exposure: zero.

What they earn: the option's time decay (theta) plus any bid-ask spread captured in the initial trade. What they still have: gamma risk (delta will change as $S$ moves), vega risk (the IV could shift), rho (small), and all the second-order Greeks.

**Continuous rebalancing.** As $S$ moves, the call's delta changes. Every move requires a hedge adjustment: a few more shares bought, a few sold. In practice, rebalancing happens at discrete intervals (every few minutes, or every significant move). The cumulative cost of rebalancing — bid-ask spread, slippage, opportunity cost — is real. Theoretical Black-Scholes assumes continuous rebalancing is free; real-world MMs build the cost into their quotes.

## What the hedging flow actually looks like

Suppose dealers are **short calls** (as assumed for indices). Call delta is positive. Dealers' hedge is to be long the underlying — they buy stock when they sell calls. As the stock rises, call delta rises (gamma), so dealers' hedge requirement grows — they must **buy more stock**. As the stock falls, call delta falls, and dealers reduce their hedge — they **sell stock**.

Buying on the way up, selling on the way down. That's the short-gamma hedging signature: **dealers are forced to trade in the direction of the move**, amplifying it. Every upside move creates more upside pressure; every downside move creates more downside pressure. This is the mechanism behind "short gamma squeezes."

Now flip. Suppose dealers are **long calls** (less common for indices, but possible if customer flow shifts). Call delta hedge is short stock. As the stock rises, the dealers' long-call delta grows, so their short-stock hedge grows — they **sell stock on the way up**. As it falls, they **buy on the way down**. Selling into strength, buying into weakness — trend-dampening, mean-reverting hedging.

The same math produces the same two cases for puts. What matters is the sign of the aggregate dealer gamma position across all outstanding contracts, because every dealer has to hedge their total exposure, not one contract at a time.

## Why index options matter differently

Three reasons the index options market is where the regime story plays cleanly:

1. **Scale.** SPX and SPY options collectively carry billions of dollars in gamma. Dealer hedging flow is large enough to move the underlying index measurably.
2. **Customer flow is directionally consistent.** Net-long-options from hedgers and speculators on indices is well-established empirically.
3. **The single-asset simplicity.** SPX options trade against SPX futures and SPY shares — a relatively simple hedging universe. Single-name options might hedge with the ticker, the sector ETF, or a basket, and the hedging flow dilutes.

The regime classifier applies cleanly to SPX and QQQ. The signs would need revisiting for single-name work, a point the package CLAUDE.md explicitly notes.

## Where this goes next

The next lesson puts numbers on the dealer gamma position — quantifying how much dealers are long or short at each strike, aggregating to a total, and showing what flows that aggregate implies. The lesson after that derives the **gamma flip strike** — the specific strike where the aggregate crosses zero, separating long-gamma and short-gamma regimes.

By the end of Part 5, you'll be able to read a chain, compute total GEX, locate the flip, and name the regime — exactly what `classify_regime` in the code does from its gex/skew/term-structure inputs.

## What you can now reason about

- Why market makers are structurally different from directional traders — their business model requires delta-neutrality, which forces persistent hedging flow.
- The "dealers short customer-preferred flow" assumption and its scope: reliable on SPX/QQQ, ambiguous on single names, flip the signs for long-gamma customer regimes.
- Why short-gamma dealer positioning amplifies moves: hedging requires buying-into-strength and selling-into-weakness, which pushes the underlying in the same direction it's already moving.

## Implemented at

The sign convention lives in `trading/packages/gex/src/gex/gex.py:53`:

```python
signs = np.where(opt == "C", -1.0, 1.0)
```

— dealer short calls (`-1`), dealer long puts (`+1`). This line is the encoding of the assumption in this lesson. Every downstream regime call is downstream of this one line. The package-level `CLAUDE.md` notes it explicitly as the sign convention to revisit for single-name applications.

---

**Next:** [Dealer gamma — long vs short →](dealer-gamma.md)
