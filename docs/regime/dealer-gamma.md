---
title: "Dealer gamma — long vs short"
prereqs: "Market makers and delta-hedging; Gamma — the second derivative"
arrives_at: "the feedback loop that creates market regimes — long gamma dampens, short gamma amplifies"
code_ref: "trading/packages/gex/src/gex/gex.py — per_strike_gex, total_gex"
---

# Dealer gamma — long vs short

The market-makers lesson sketched *why* dealers hedge. This lesson quantifies *how much*. Aggregating gamma across every outstanding option, signed by dealer position, produces a single number that summarizes the market's hedging regime. Call it **GEX** — gamma exposure.

## The aggregation formula

For a single contract at strike $K$ with open interest $\text{OI}_K$ and implied vol $\sigma_K$, the dealer's gamma position is:

$$
G_K = \text{sign}_K \cdot \Gamma_K \cdot \text{OI}_K \cdot \text{multiplier}
$$

where:

- $\Gamma_K$ is the Black-Scholes gamma per share, computed from $S$, $K$, $\sigma_K$, $T$, $r$ (from [Lesson 8](../greeks/gamma.md)).
- $\text{OI}_K$ is open interest — the number of contracts outstanding at that strike.
- $\text{multiplier}$ is the contract size (100 for standard U.S. equity options).
- $\text{sign}_K$ is the dealer-position sign under the "dealers short customer-preferred flow" assumption: $-1$ for calls, $+1$ for puts.

$G_K$ has units of *shares per dollar of spot move*. Useful but awkward. To get something reportable, convert to **dollars of hedging flow per 1% move**:

$$
\text{GEX}_K = G_K \cdot S^2 \cdot 0.01.
$$

Two factors of $S$: the first converts gamma from shares-per-dollar to dollars-of-hedge-per-dollar (multiply by $S$); the second converts a 1% move from "dollars" to a fraction of spot (so the move equals $0.01 \cdot S$, and gamma times the square of that move is a second $S$ factor). The final $0.01$ is the 1% scaling.

## Summing across the chain

Total GEX across all strikes and both option types:

$$
\text{Total GEX} = \sum_K \left( \text{GEX}_K^{(\text{call})} + \text{GEX}_K^{(\text{put})} \right).
$$

For SPX in a typical non-stressed regime, this sum might be positive (dealers net long gamma) by tens of billions of dollars per 1%. During stressed regimes, it can go negative — dealers net short gamma by similar magnitudes. Those are the two regime extremes the classifier picks up.

The fact that the sum is in "dollars per 1% move" is load-bearing. It tells you directly: **if SPX moves 1%, aggregate dealer hedging flow is $X dollars of stock in the direction of the move (if short gamma) or against the move (if long gamma).** That quantity has an intuitive dimension — it's comparable to daily trading volume and to individual market-maker capacities.

## Per-strike structure

Summing gives one number. Looking strike-by-strike gives you the shape. A typical SPX chain snapshot looks like this:

```
per-strike GEX
 large +ve                     large -ve
     ┌─┐                           ┌─┐
     │ │                           │ │
     │ │  small +ve                │ │
┌┐┌┐ │ │┌┐                    ┌┐  │ │┌┐┌┐
┼┴┴┴─┴─┴┴┴──────────┼────────┴┴───┴─┴┴┴┴─→ strike
                                  │
                                 spot
```

Dealers' long-put exposure is concentrated in OTM puts (strikes well below spot), contributing positive per-strike GEX. Their short-call exposure is concentrated in OTM calls (strikes well above spot), contributing negative per-strike GEX. Near-the-money contributions depend on OI specific to the day but are smaller than the wings.

The shape has implications. Walking strikes from low to high, the running cumulative sum of GEX starts positive (from OTM puts), grows toward its peak near the money, then falls as the OTM call contributions come in negative. Where the cumulative sum crosses zero is the [gamma flip strike](gamma-flip.md) — the subject of the next lesson.

## What "long gamma" regime means operationally

When total GEX is strongly positive, dealers are net long gamma. Recall what long-gamma hedging looks like from [Lesson 8](../greeks/gamma.md): every move generates a positive-convexity scalp, paid for with theta. The dealer's hedge is mean-reverting — sell into strength, buy into weakness.

Empirically, long-gamma regimes are characterized by:

- **Low realized volatility.** Hedging flow actively dampens moves.
- **Mean reversion.** Price tends to return to a range. "Pinning" near large strikes around expiration is a classic long-gamma phenomenon.
- **Successful short-vol strategies.** If realized < implied (which it often is in long-gamma regimes), short-vol positions harvest the premium without getting run over.

These are the "boring" market regimes where nothing happens for weeks. They persist as long as the dealer-gamma aggregate stays positive.

## What "short gamma" regime means operationally

When total GEX is strongly negative, dealers are net short gamma. Hedging is trend-amplifying — buy into strength, sell into weakness.

Empirically, short-gamma regimes are characterized by:

- **Higher realized volatility.** Hedging flow actively amplifies moves.
- **Trend persistence.** Moves in one direction attract more hedging in the same direction. "Gamma squeeze" is the extreme case.
- **Short-vol blowups.** If realized > implied (common in short-gamma), short-vol positions lose. Volmageddon 2018 and COVID 2020 were short-gamma events.

The regime classifier flips to `short_gamma` when total GEX is negative, among other triggers. The short-gamma tag doesn't mean every day is chaos — it's a prior that the hedging environment is amplifying rather than damping.

## The time-to-expiry dimension

Gamma is largest for short-dated options and falls for long-dated ones (from the $1/\sqrt{T}$ in the formula). Consequently, **short-dated OI dominates total GEX**. A weekly 0DTE contract contributes far more gamma per unit of OI than a monthly, which contributes far more than a LEAPS. When the zero-days-to-expiration options are near the money, they can drive the whole aggregate. This is why 0DTE contracts — which have grown to half or more of SPX options volume as of the mid-2020s — have changed the dynamics of the GEX surface: more weight is concentrated in ultra-short-dated contracts whose gamma evaporates by end of day, creating a churning, intraday-sensitive GEX picture.

Most GEX calculations, including this project's, aggregate across all tenors without distinction. A more refined model would bucket by expiry window (weekly, monthly, quarterly) and track each bucket's hedging flow separately. For a first-pass regime classifier, the unified aggregate is sufficient.

## Why SPY and SPX can differ

A subtle point. SPY and SPX both track the S&P 500, but their options markets have different open interest profiles. SPX options are European cash-settled, used heavily by institutional hedgers and risk-managers. SPY options are American physically-settled, used more by retail and tactical traders.

The two chains' GEX profiles can diverge meaningfully. SPX GEX often looks cleaner and more stable; SPY GEX oscillates more with retail flow. When researchers talk about "dealer gamma regimes," they usually mean SPX. When live trading against SPY, expect noisier per-strike GEX oscillations — the cumulative-crossing definition of the flip strike in the next lesson was specifically adopted to handle this noise correctly.

## What you can now reason about

- Why GEX is reported in "dollars per 1% move" instead of raw shares per dollar — the conversion factor $S^2 \cdot 0.01$ produces a quantity with intuitive economic interpretation.
- Why the sign of total GEX splits market behavior into two regimes: long gamma (dampening, mean-reverting, low realized vol) and short gamma (amplifying, trending, high realized vol).
- How 0DTE growth has reshaped the GEX surface — most gamma now lives in contracts that will be worthless by end of day.

## Implemented at

`trading/packages/gex/src/gex/gex.py`:

- Line 22: `per_strike_gex(chain, spot, rate)` computes signed contributions per strike. Key line is 53:
  ```python
  signs = np.where(opt == "C", -1.0, 1.0)
  contribution = signs * oi * gammas * CONTRACT_MULTIPLIER * (spot**2) * PERCENT_MOVE
  ```
- Line 64: `total_gex(per_strike)` sums across all strikes to produce the single regime scalar.

The `classify_regime` logic reads `total_gex < 0` as one of its short-gamma triggers, alongside spot-below-flip and skew-z-crushed.

---

**Next:** [The gamma flip strike →](gamma-flip.md)
