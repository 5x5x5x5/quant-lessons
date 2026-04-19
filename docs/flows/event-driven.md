---
title: "Event-driven special situations"
prereqs: "—"
arrives_at: "mechanical inefficiencies from earnings, rebalances, spin-offs, and forced flows"
code_ref: "pending — trading/packages/events/"
---

# Event-driven special situations

The central argument for event-driven strategies is that the inefficiency is structural, not behavioral. Behavioral edges — patterns in chart shapes, retail sentiment, herd psychology — erode as participants learn to trade them. Mechanical edges — forced buyers and sellers acting under fixed rules — do not erode in the same way. The rules are insensitive to being traded, and the forced participants cannot opt out.

Joel Greenblatt's 1990s work on special situations framed this case for a generation of value investors. The same logic applies to systematic implementations today.

## Why mechanical inefficiencies persist

The standard argument for why any market inefficiency eventually disappears is: traders notice it, participate, and the additional demand eliminates the edge. This requires two conditions — a counterparty willing to take the other side of the inefficient trade, and that counterparty having a choice.

Mechanical inefficiencies violate the second condition. When an index adds a stock, index funds must buy — they track an index that now includes the name. The buying is not motivated by a view on fundamental value but by a mandate. When a company spins off a subsidiary, mutual funds often must sell the spinoff because many have mandates against owning companies below a certain market cap, and the spinoff falls below that cutoff. The selling is not opinion-driven either.

Any participant taking the opposite side of these forced flows captures a premium from the forced participant by construction. As long as the forced flows remain structural, the premium remains harvestable. No amount of alpha-seeking removes the effect, because the forced participants cannot alpha-seek.

The inefficiencies are smaller than they were in Greenblatt's era, as more capital now competes for them, but they remain non-zero and persist across market cycles in ways that behavioral edges do not.

## Post-earnings announcement drift (PEAD)

The canonical academic anomaly: stocks with positive earnings surprises continue to drift upward for weeks after the announcement, and stocks with negative surprises drift downward. The persistence of the drift appears inconsistent with efficient-markets intuition, which would predict that the full reaction is absorbed on announcement day.

**Standardized Unexpected Earnings (SUE)** is the standard surprise metric:

$$
\text{SUE}_i = \frac{\text{EPS}_i - \mathbb{E}[\text{EPS}_i]}{\sigma_{\text{EPS}_i}}
$$

where $\text{EPS}_i$ is the actual reported earnings per share, and $\mathbb{E}[\text{EPS}_i]$ and $\sigma_{\text{EPS}_i}$ are the consensus estimate and its dispersion. High SUE indicates a meaningful beat; low SUE indicates a meaningful miss.

Implementation: each earnings season, rank companies by SUE, take long positions in the top decile and short positions in the bottom decile, hold for 60 days, and rebalance as new earnings releases arrive. Academic studies show this produces approximately 4-8 percentage points of annualized alpha after costs, depending on sample period and specification.

The mechanism: analysts and institutional investors do not update their models instantly. A large SUE surprise triggers revisions over weeks — some analysts upgrade immediately, while others follow as confirmation arrives. The staggered repricing produces the observed drift. Institutional constraints (sector weights, position limits) also delay repricing beyond what pure behavioral explanations would predict.

The alpha has decayed: PEAD was more profitable in the 1990s than today. Tighter institutional execution, faster information aggregation, and more PEAD-targeted funds have compressed the effect. The anomaly remains but is smaller than historical papers report.

## Index rebalancing

S&P 500 reconstitution, Russell rebalancing, and NASDAQ-100 quarterly adjustments follow published methodology and are announced in advance with effective dates. Index funds buy additions in the days leading to the effective date and sell deletions. Both flows are large and predictable.

**Long additions** 5 trading days before effective, close at effective +3. Additions typically rally into the effective date as passive demand materializes, then give back some of the gain as the demand pulse completes.

**Short deletions** on the same schedule. Deleted names often have underlying fundamental weakness (which is typically why they were deleted); the additional selling pressure amplifies the move.

Detailed mechanics vary by index:

- **S&P 500**: committee-driven, announced approximately 5 business days before effective. Most rebalance flow concentrates in the closing auction of the effective day.
- **Russell**: rule-based (market cap rankings at reconstitution date), annual reconstitution in late June. Volume is large and the methodology is transparent.
- **NASDAQ-100**: rule-based, quarterly reweighting.

Strategies differ by index characteristic. Russell reconstitution is a single annual event with very high volume and well-studied patterns. S&P additions and deletions occur several times per year with lower volume but similar predictability.

## Spin-offs

A parent company distributes shares of a subsidiary ("spinco") to existing shareholders. The parent goes ex-spinco on a specific date, and the spinco begins trading on or shortly after.

Greenblatt documented that spinoffs often outperform their parents during the first 12-24 months following separation. Several structural factors contribute:

- **Neglect.** Spinoffs are often small, underfollowed by analysts, and lacking institutional interest. The price at separation reflects this neglect rather than intrinsic value.
- **Forced selling.** Some institutional holders must sell spinoffs due to mandate restrictions and index-weight concerns. Forced selling compresses prices below fair value.
- **Management focus.** Freed from parent-company constraints, spinoff management often operates more effectively. Operating improvements manifest over the following year.

A systematic spinoff strategy: take long positions in spinoff and parent at separation, hold for 12-24 months, and rebalance as new spinoffs occur. Implementation requires reading SEC filings to identify upcoming spinoffs and track effective dates.

## Tax-loss reversal

U.S. individual investors sell securities at a loss in December to offset capital gains. This tax-loss selling pushes weak stocks further down in November and December. Mechanical selling stops in January, and stocks with strong underlying fundamentals that were beaten down by year-end selling often recover.

Standard implementation: in late November or early December, rank stocks by year-to-date return, select the worst decile, filter for positive fundamental signals (improving earnings trajectory, reasonable valuation, no major red flags), and hold through late February or early March.

The January Effect literature documents this pattern, particularly in small caps, which have a higher fraction of tax-sensitive individual holders. The effect has compressed over decades as passive investing has grown and the population of tax-sensitive individual holders has shrunk, but it has not disappeared.

## Merger arbitrage

Not in the original curriculum spec but relevant. After an M&A announcement, the target typically trades below the deal price; the spread reflects the market's probability estimate of deal completion. Merger arbitrageurs take long positions in the target and (for stock-swap deals) short positions in the acquirer, collecting the spread on deal close.

Merger arb is its own discipline, involving deal-by-deal analysis, regulatory assessment, and term negotiation. It is less purely systematic than PEAD or index rebalancing and requires more manual judgment.

## What the trading project plans

`packages/events/` is spec'd but not scaffolded. The intended architecture:

- One module per event type (`pead.py`, `index_rebalance.py`, `spinoffs.py`, `tax_loss.py`).
- Each module emits `signal(universe, date)` — returning a set of long/short tickers.
- Each module emits `size(signal, portfolio)` — sizing logic specific to that strategy.
- All modules share the `harness` primitives for walk-forward evaluation, cost modeling, metrics.

Data sources will be varied: SEC EDGAR for filings (spinoffs, corporate actions), earnings-calendar feeds (Nasdaq Data Link, commercial providers) for PEAD, index methodology documents for rebalance windows.

Unlike the GEX pipeline (which needs chain data) or microstructure (which needs L2), event-driven strategies are mostly buildable on retail-accessible data — the moat is in reading fundamentals, not in paying for sub-millisecond feeds.

## Capacity and crowding

Event-driven strategies have high capacity relative to purely technical strategies. PEAD alone involves approximately 500 earnings per quarter in the S&P 1500, each offering position-sizing room in the hundreds of millions of dollars for liquid names. Index rebalance flows are in the billions. Spinoff universes are smaller, but individual names are often mid- to large-cap.

The practical consequence is that event-driven strategies can operate at institutional scale without exhausting their own edges. Crowding risk is also lower: most systematic firms allocate limited headcount to event-driven work because it requires specialized data pipelines that do not generalize to other strategies. High entry cost, high capacity, and a sparser competitive field are characteristic of this category.

## Summary

The reader can now reason about:

- Why structural inefficiencies (forced buying and selling by mandate-bound participants) persist in ways behavioral inefficiencies do not: the forced side cannot respond to competitive pressure.
- The main event categories (PEAD, index rebalancing, spin-offs, tax-loss reversal) and the specific structural source of each harvestable premium.
- Why event-driven strategies tend to have higher capacity and lower crowding than comparable-Sharpe technical strategies: the data pipelines are specialized, and the forced flows are inelastic.

## Implemented at

`packages/events/` is planned. When built, expect the structure outlined above:

- `pead.py` — SUE ranking, long top / short bottom decile, 60-day hold.
- `index_rebalance.py` — rebalance-calendar parser, long additions / short deletions around effective dates.
- `spinoffs.py` — EDGAR Form 10 parsing, long spinco + parent at separation.
- `tax_loss.py` — year-end scan of underperforming fundamentally-solid names.

Each module follows the shared `signal()` / `size()` interface, composes with `harness` for walk-forward evaluation, and treats the strategy code as thin glue (per the monorepo convention).

---

**Next:** [Cross-asset signals →](cross-asset.md)
