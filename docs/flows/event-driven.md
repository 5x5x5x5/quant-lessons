---
title: "Event-driven special situations"
prereqs: "—"
arrives_at: "mechanical inefficiencies from earnings, rebalances, spin-offs, and forced flows"
code_ref: "pending — trading/packages/events/"
---

# Event-driven special situations

The strongest argument for event-driven strategies: **the inefficiency is structural, not behavioral.** Behavioral edges — patterns in chart shapes, retail sentiment, herd psychology — erode as people learn to trade them. Mechanical edges — forced buyers and sellers acting on fixed rules — don't erode in the same way. The rules don't know they're being traded, and the forced participants can't opt out.

Joel Greenblatt's 1990s work on special situations made this case for a generation of value investors. The same logic applies systematically today.

## Why mechanical inefficiencies persist

The standard argument for why any market inefficiency eventually disappears goes: traders notice it, pile in, and the extra demand arbs it away. This requires two things — someone to take the other side of the "wrong" trade, and that someone having a choice.

Mechanical inefficiencies violate the second requirement. When an index adds a stock, index funds *must* buy — they are tracking an index that now includes the name. Their buying isn't motivated by an opinion that the stock is mispriced; it's motivated by the mandate. When a company spins off a subsidiary, mutual funds often *must* sell the spinco — many have mandates against owning companies below a certain market cap, and the spinco is below the cutoff. This selling isn't opinion-driven either.

Anyone taking the opposite side of these forced flows is, by construction, capturing a premium from the forced participant. As long as the forced flows remain structural, the premium remains harvestable. No amount of alpha-seeking can remove them, because the forced participants can't alpha-seek.

The inefficiencies are smaller than they were in Greenblatt's era — more capital now competes for them — but they haven't gone to zero, and they persist across market cycles in ways that behavioral edges do not.

## Post-earnings announcement drift (PEAD)

The canonical academic anomaly: stocks with positive earnings surprises continue to drift up for weeks after the announcement; stocks with negative surprises drift down. The persistence defies efficient-markets intuition — why didn't the full reaction happen on the announcement day?

**Standardized Unexpected Earnings (SUE)** is the standard surprise metric:

$$
\text{SUE}_i = \frac{\text{EPS}_i - \mathbb{E}[\text{EPS}_i]}{\sigma_{\text{EPS}_i}}
$$

where $\text{EPS}_i$ is the actual reported earnings per share, and $\mathbb{E}[\text{EPS}_i]$ and $\sigma_{\text{EPS}_i}$ are the consensus estimate and its spread. High SUE = meaningful beat; low SUE = meaningful miss.

The implementation: each earnings season, rank companies by SUE, go long the top decile, short the bottom decile, hold for 60 days, rebalance as new earnings releases come in. Academic studies show this produces roughly 4-8 percentage-point annualized alpha after costs, depending on sample period and specification.

**Why it works (the argument).** Analysts and institutional investors don't update their models instantly. A large SUE surprise triggers gradual revisions over weeks — some analysts upgrade immediately, others follow over the next few weeks as confirmation arrives. The staggered repricing produces drift. The behavioral component doesn't fully explain it; institutional constraints (sector weights, position limits) also delay repricing.

**Why it's decayed.** PEAD was more profitable in the 1990s than today. Tighter institutional execution, faster information aggregation, and more explicitly-PEAD-targeted funds have compressed the alpha. Still alive, but smaller than historical papers suggest.

## Index rebalancing

S&P 500 reconstitution, Russell rebalancing, NASDAQ-100 quarterly adjustments — all follow public methodology, announced in advance with effective dates. Additions are bought by index funds in the days leading to the effective date; deletions are sold. Both flows are large and predictable.

**Long additions** 5 trading days before effective, close at effective +3. Additions typically rally into effective as passive demand materializes, then often give back some of the gain as the demand pulse completes.

**Short deletions** on the same schedule. Deleted names often have fundamental weakness (that's how they got deleted); the selling pressure amplifies it.

The detailed mechanics vary by index:

- **S&P 500**: committee-driven, announced ~5 business days before effective. Bulk of the rebalance flow concentrates in the closing auction of the effective day.
- **Russell**: rule-based (market cap rankings at reconstitution date), annual reconstitution in late June. Massive volume; transparent methodology.
- **NASDAQ-100**: rule-based, quarterly reweighting.

Strategies vary by index characteristic. Russell reconstitution is a single annual event with enormous volume and well-studied patterns. S&P additions/deletions happen a few times a year, with less volume but similar predictability.

## Spin-offs

A parent company distributes shares of a subsidiary ("spinco") to existing shareholders. The parent goes ex-spinco on a specific date; the spinco begins trading on or shortly after.

Greenblatt documented that spincos often outperform their parents over the first 12-24 months after separation. Several structural reasons:

- **Neglect.** Spincos are often small, underfollowed by analysts, and lacking in institutional interest. The price at separation reflects this neglect more than intrinsic value.
- **Forced selling.** Some institutional holders must sell spincos (mandate restrictions, index-weight concerns). The forced selling compresses price below fair value.
- **Management focus.** Freed from parent constraints, spinco management often operates more effectively. Operating improvements manifest over the following year.

A systematic spin-off strategy: long spinco + parent at separation, hold 12-24 months, rebalance as new spin-offs occur. Requires reading SEC filings to identify upcoming spinoffs and track effective dates.

## Tax-loss selling reversal

Each December, individual U.S. investors sell securities at a loss to offset capital gains. This **tax-loss selling** pushes down already-weak stocks further in November and December. Come January, the mechanical selling stops; stocks with strong underlying fundamentals that were beaten down by year-end selling often recover.

Classic implementation: in late November or early December, rank stocks by year-to-date return. Select the worst decile. Filter for positive fundamental signals (improving earnings trajectory, reasonable valuation, no major red flags). Buy and hold through late February or early March. Sell.

The January Effect literature documents this pattern in small caps particularly (small caps have a higher fraction of tax-sensitive individual holders). The effect has compressed over decades as passive investing has grown and the population of tax-sensitive individual holders has shrunk, but it hasn't disappeared.

## Merger arbitrage

Not in the original curriculum spec but worth naming. After an M&A announcement, the target typically trades below the deal price; the spread reflects the market's probability estimate of the deal completing. Merger arbitrageurs are long the target + short the acquirer (if stock-swap) and collect the spread on close.

Merger arb is its own discipline — deal-by-deal analysis, regulatory read, term negotiation — less purely systematic than PEAD or index rebalance. Include for completeness but recognize it requires more manual judgment.

## What the trading project plans

`packages/events/` is spec'd but not scaffolded. The intended architecture:

- One module per event type (`pead.py`, `index_rebalance.py`, `spinoffs.py`, `tax_loss.py`).
- Each module emits `signal(universe, date)` — returning a set of long/short tickers.
- Each module emits `size(signal, portfolio)` — sizing logic specific to that strategy.
- All modules share the `harness` primitives for walk-forward evaluation, cost modeling, metrics.

Data sources will be varied: SEC EDGAR for filings (spinoffs, corporate actions), earnings-calendar feeds (Nasdaq Data Link, commercial providers) for PEAD, index methodology documents for rebalance windows.

Unlike the GEX pipeline (which needs chain data) or microstructure (which needs L2), event-driven strategies are mostly buildable on retail-accessible data — the moat is in reading fundamentals, not in paying for sub-millisecond feeds.

## Capacity and crowding

One advantage of event-driven strategies: **high capacity**, relative to purely technical strategies. PEAD alone has ~500 earnings per quarter in the S&P 1500, each offering position-sizing room in the hundreds of millions of dollars for a liquid name. Index rebalance flows are in the billions. Spin-off universes are smaller but the individual names are often mid- to large-cap.

The practical implication: event-driven strategies can run at meaningful institutional scale without exhausting their own edges. The crowding risk is also lower — most systematic shops allocate limited headcount to event-driven work because it requires building specialized data pipelines that don't generalize elsewhere. The cost of entry is high; the capacity of the resulting strategy is high; the competitive field is sparser than for technicals.

## What you can now reason about

- Why structural inefficiencies (forced buying/selling by mandate-bound participants) persist in ways behavioral inefficiencies don't — the forced side can't respond to competitive pressure.
- The main event categories (PEAD, index rebalancing, spin-offs, tax-loss reversal) and the specific structural reason each one generates a harvestable premium.
- Why event-driven strategies tend to have higher capacity and lower crowding than comparable-Sharpe technical strategies — the data pipelines are specialized, the forced flows are inelastic.

## Implemented at

`packages/events/` is planned. When built, expect the structure outlined above:

- `pead.py` — SUE ranking, long top / short bottom decile, 60-day hold.
- `index_rebalance.py` — rebalance-calendar parser, long additions / short deletions around effective dates.
- `spinoffs.py` — EDGAR Form 10 parsing, long spinco + parent at separation.
- `tax_loss.py` — year-end scan of underperforming fundamentally-solid names.

Each module follows the shared `signal()` / `size()` interface, composes with `harness` for walk-forward evaluation, and treats the strategy code as thin glue (per the monorepo convention).

---

**Next:** [Cross-asset signals →](cross-asset.md)
