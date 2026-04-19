---
title: "Market makers and delta-hedging"
prereqs: "Delta — sensitivity to price"
arrives_at: "who sells options and how their risk management shapes the tape"
code_ref: "—"
---

# Market makers and delta-hedging

The GEX pipeline depends on a specific model of who sells options and how they manage the resulting risk. An incorrect model produces regime calls that are wrong by the same magnitude in the opposite direction, so the assumptions deserve explicit treatment.

## Who sells options

When a retail trader buys a call, a counterparty sells it. When a pension fund buys puts for downside protection, a counterparty sells them. In aggregate, the sell side of the options market comprises a range of institutional participants; the dominant category is options market makers. Quantitative firms — Susquehanna, Citadel Securities, Optiver, IMC, and others — handle the majority of exchange-listed options flow.

Market makers are liquidity providers. They quote two-sided markets (a bid and an ask) across tens of thousands of contracts simultaneously. Their business model is to earn the bid-ask spread, not to take directional views. A market maker with unhedged directional exposure in a large index like SPX has deviated from the business model.

This framing shapes hedging behavior. A directional trader who buys a call accepts being wrong as part of taking a view. A market maker who sells a call is obligated to neutralize the resulting exposure. Position sizes across tens of thousands of contracts are too large, and the firm's capital base is not structured for one-way risk.

## The customer-preferred flow assumption

The next assumption is less rigorous but empirically dominant:

> Customers are net buyers of options on equity indices.

Two patterns support this. Retail and many institutional traders buy calls for leveraged upside exposure (speculative positions, bullish directional bets, hedged overwrites of underlying equity). Hedgers — pension funds, endowments, insurance companies, wealth managers — buy puts for downside protection on large equity portfolios.

In single names, the picture is less clean. Covered-call overwriters are net sellers of calls (the standard "income" strategy). Earnings straddles are two-sided. Dealer positioning in individual tickers is ambiguous and depends on who holds the name.

In indices (SPX, NDX, QQQ, SPY), the customer-net-buyer assumption is robust enough to encode in code. The trading project's `gex.py` assigns dealers short gamma on calls (`sign = -1` for C) and long gamma on puts (`sign = +1` for P), corresponding to "dealers short customer-preferred flow." Inverting the signs would invert every regime call downstream.

The package-level CLAUDE.md documents this sign convention and flags that single-name applications should revisit it. The assumption is structural, not incidental — it is the foundation on which the rest of Part 5 rests.

## Delta-hedging in practice

A market maker who has sold an SPY call with $\Delta = 0.40$ has acquired $-0.40$ share-equivalents of exposure per share covered by the contract. For a 100-share contract, this is $-40$ shares. Neutralizing the exposure requires buying 40 shares of SPY. The resulting portfolio is:

- Short 1 call (premium received).
- Long 40 shares of SPY (purchased at the ask).
- First-order directional exposure: zero.

The market maker earns the option's time decay (theta) plus any bid-ask spread captured in the initial trade. The remaining risks include gamma (delta changes as $S$ moves), vega (sensitivity to IV), rho (small for short-dated positions), and higher-order Greeks.

**Continuous rebalancing.** As $S$ moves, the call's delta changes, requiring hedge adjustment. In practice, rebalancing occurs at discrete intervals — every few minutes, or upon each significant move. The cumulative cost of rebalancing (bid-ask spread, slippage, opportunity cost) is material. Theoretical Black-Scholes assumes continuous rebalancing is free; real market makers incorporate rebalancing costs into quoted prices.

## Hedging flow dynamics

Suppose dealers are short calls (the index assumption). Call delta is positive. Dealers hedge by being long the underlying — buying stock when they sell calls. As the stock rises, call delta rises (via gamma), so dealer hedge requirements grow, requiring additional stock purchases. As the stock falls, call delta falls, and dealers reduce their hedge by selling stock.

This pattern — buying on the way up, selling on the way down — is the short-gamma hedging signature: dealer hedging flow aligns with the direction of the move, amplifying it. Every upside move creates additional upside pressure; every downside move creates additional downside pressure. This is the mechanism behind short-gamma squeezes.

The reverse case: suppose dealers are long calls (less common for indices, but possible under certain customer flow patterns). The call delta hedge is now short stock. As the stock rises, dealers' long-call delta grows, requiring larger short-stock hedges (selling on the way up). As it falls, dealers buy on the way down. This pattern — selling into strength, buying into weakness — dampens trends and promotes mean reversion.

The same mechanics apply symmetrically to puts. The relevant quantity is the sign of aggregate dealer gamma across all outstanding contracts, since dealers hedge total exposure rather than one contract at a time.

## Why index options are distinctive

Three factors make the index options market the cleanest setting for regime analysis:

1. **Scale.** SPX and SPY options collectively carry billions of dollars in gamma. Dealer hedging flow is large enough to measurably affect the underlying index.
2. **Consistent directional customer flow.** Net-long-options positioning from hedgers and speculators on indices is well-established empirically.
3. **Simple hedging universe.** SPX options trade against SPX futures and SPY shares — a relatively straightforward hedging set. Single-name options might hedge against the ticker, the sector ETF, or a basket, which dilutes the observable flow.

The regime classifier applies cleanly to SPX and QQQ. Signs would need revisiting for single-name applications, as the package CLAUDE.md notes.

## Looking ahead

The next lesson quantifies the dealer gamma position — how much dealers are long or short at each strike, how those positions aggregate, and what flows the aggregate implies. The lesson after derives the gamma-flip strike, the specific strike at which the aggregate crosses zero and the regime transitions between long-gamma and short-gamma.

By the end of Part 5, the reader will be able to read a chain, compute total GEX, locate the flip, and identify the regime — the procedure implemented in `classify_regime` using GEX, skew, and term-structure inputs.

## Summary

The reader can now reason about:

- Why market makers differ structurally from directional traders: their business model requires delta-neutrality, producing persistent hedging flow.
- The "dealers short customer-preferred flow" assumption and its scope: reliable on SPX/QQQ, ambiguous on single names, with signs inverting under long-gamma customer regimes.
- Why short-gamma dealer positioning amplifies moves: hedging requires buying strength and selling weakness, pushing the underlying in the same direction it is already moving.

## Implemented at

The sign convention is encoded in `trading/packages/gex/src/gex/gex.py:53`:

```python
signs = np.where(opt == "C", -1.0, 1.0)
```

— dealer short calls (`-1`), dealer long puts (`+1`). This line encodes the assumption discussed in this lesson; every downstream regime call follows from it. The package-level `CLAUDE.md` documents it as the sign convention to revisit for single-name applications.

---

**Next:** [Dealer gamma — long vs short →](dealer-gamma.md)
