---
title: "The gamma flip strike"
prereqs: "Dealer gamma — long vs short"
arrives_at: "the strike at which cumulative dealer gamma crosses zero — a practical regime marker"
code_ref: "trading/packages/gex/src/gex/gex.py — gamma_flip_strike"
---

# The gamma flip strike

A total GEX number tells you the aggregate regime. The **gamma flip strike** tells you *where*, along the strike axis, dealer positioning transitions from long gamma to short gamma. Combined with the current spot, this scalar summarizes the two most actionable pieces of information the regime classifier needs.

The definition is subtle enough that the trading project's first implementation got it wrong. The corrected definition is the subject of this lesson.

## The wrong definition (and why)

A naive first pass at "gamma flip": find the strike $K^*$ where the per-strike GEX changes sign from positive to negative as you walk up the strike ladder.

This seems reasonable. Dealers' long-put contributions are positive, dealers' short-call contributions are negative, and somewhere in the middle they cross. Where they cross must be where the "transition" happens.

It breaks on any chain where per-strike GEX isn't monotonic. SPY options — driven by retail flow across a wide strike band — can have per-strike GEX that oscillates: positive at strike 420, negative at 425, positive at 430, negative at 435. The first-adjacent-pair sign change finds *a* crossing, but not the meaningful one. The regime implication flips with every oscillation. You can't use an unstable definition to classify regimes.

Commit `1e90d49` in the trading repo fixed this. The right definition is cumulative.

## The correct definition: cumulative GEX crossing

Sort strikes ascending. Compute cumulative GEX:

$$
C_K = \sum_{K' \le K} \text{GEX}_{K'}.
$$

The gamma flip strike $K^*$ is the value of $K$ at which $C_K$ crosses zero (changes sign as you walk up the ladder).

This is more stable by construction. Per-strike oscillations average out in the running sum. The running sum has a single smooth trajectory — starts at zero (trivially, before any strikes), grows to a peak (accumulating put contributions and early call contributions), then decays and typically goes negative as the larger OTM call contributions dominate the tail. The zero-crossing is where the net hedging flow flips from "long gamma above this strike" to "short gamma above this strike," aggregated across all strikes at or below.

![Cumulative GEX versus strike for the same SPX snapshot from the previous lesson. Green shading marks the long-gamma region; pink marks short-gamma. The gamma-flip strike (orange) is where cumulative GEX crosses zero — here, above spot, as is typical in calm regimes.](../assets/figures/gex_cumulative_flip.png){ loading=lazy }

**Interpretation of the crossing.** At $K^*$, the contribution of all strikes up to $K^*$ exactly cancels. Moving spot through $K^*$ tilts the net dealer gamma aggregate toward the opposite side — this is why crossing the flip is regime-changing. For a typical SPX profile (put-heavy below spot, call-heavy above spot), the cumulative starts positive and ends negative, so $K^*$ lies on the descending leg. That leg usually sits *just above* spot in calm regimes; it moves closer to or below spot as dealer short-call positioning grows relative to long-put positioning.

## Linear interpolation between strikes

Cumulative GEX is defined on discrete strikes (5-point increments, say). It rarely crosses zero exactly at a quoted strike — it passes between two adjacent strikes. To locate the crossing more precisely, interpolate:

Given adjacent strikes $K_{i-1} < K_i$ with cumulative GEX values $c_{i-1} > 0$ and $c_i < 0$ (or vice versa):

$$
K^* = K_{i-1} + \frac{-c_{i-1}}{c_i - c_{i-1}} (K_i - K_{i-1}).
$$

This gives a continuous scalar, updated daily, that can be compared to spot at any time. The implementation in `gex.py:gamma_flip_strike` does exactly this linear interpolation.

## When cumulative GEX never crosses zero

Edge case: the chain is globally one-sided — all cumulative values are positive, or all negative. This can happen if dealer positioning is extremely skewed (say, in an illiquid single name, or a weird snapshot where the chain just has a few strikes). The code returns `spot` in this case, implicitly signaling "no crossing — regime call defaults to whatever total GEX says."

This is a sensible fallback: in the absence of a flip strike, the flip-vs-spot comparison has no well-defined answer, and the classifier should fall back to using total GEX alone.

## How spot vs flip feeds the regime call

The classifier in `regime.py:classify_regime` uses the comparison between spot and flip as one of three short-gamma triggers:

- `spot < gamma_flip * 0.995` — spot has fallen below 99.5% of the flip strike. A 0.5% buffer avoids flip-flopping on tiny moves around the boundary.
- `total_gex < 0` — the aggregate is negative.
- `skew_25d_z <= -2.0` — skew is compressing relative to history.

Any one of these triggers the `short_gamma` regime tag (unless term-structure inversion overrides with `vol_inverted`). The three are not independent — they frequently move together — but each catches situations the others might miss. A day might show `total_gex > 0` but have spot below flip in a specific strike configuration, for example.

## The flip as a dynamic marker

The flip isn't static. It moves daily as the options chain updates:

- **OI accumulation.** As expiry approaches without much trade, new trades pile up. The flip can drift.
- **Volume at specific strikes.** A large customer trade at a specific strike shifts the per-strike GEX, and so the cumulative, and so the flip.
- **Time decay.** Gamma itself is time-dependent. Near expiry, short-dated gamma dominates, and the flip can move sharply.

In practice, the flip tends to sit within a tight band of spot over days, moving by dollars or tens of dollars at a time. Large, fast moves in the flip correspond to large, fast changes in market structure — often around expiration Fridays or big index-level events.

## The SpotGamma "Zero Gamma" comparison

Practitioners familiar with SpotGamma's methodology will note a distinction. SpotGamma's "Zero Gamma" level is computed differently: it holds the chain's strikes and OI fixed and scans *spot* until the total GEX crosses zero. The flip here holds spot fixed and scans *strikes*. These are different quantities in general.

For chains where most of the gamma is concentrated near the current spot, the two estimates agree closely. For chains with exotic dealer positioning, they can diverge. The trading project's approach is the cheaper proxy; the SpotGamma scan is more expensive but arguably more accurate. For first-pass regime classification, the proxy is adequate; for finer work, the full scan is the upgrade.

## Worked interpretation

SPX at 5200. Cumulative GEX walked from low to high strikes:

| Strike | per-strike GEX ($M/1%) | Cumulative ($M/1%) |
|--------|------------------------|---------------------|
| 4900 | +$2B | +$2B |
| 4950 | +$3B | +$5B |
| 5000 | +$4B | +$9B |
| 5050 | +$5B | +$14B |
| 5100 | +$3B | +$17B |
| 5150 | 0 | +$17B |
| 5200 | -$2B | +$15B |
| 5250 | -$6B | +$9B |
| 5300 | -$8B | +$1B |
| 5350 | -$4B | -$3B |
| 5400 | -$2B | -$5B |

Cumulative crosses zero between 5300 and 5350. Linearly interpolated: $K^* \approx 5312$. With spot at 5200, spot is $112$ dollars (2.2%) **below** the flip. Regime call: spot well below flip, likely a short-gamma tilt.

The classifier's threshold is $0.995 \times 5312 \approx 5285$, so spot at 5200 is below that — the short-gamma trigger fires.

## What you can now reason about

- Why the cumulative-crossing definition of the flip strike is more stable than a per-strike-sign-change definition, especially for retail-flow-driven chains (SPY).
- How the flip strike updates daily with OI changes, time decay, and spot moves, and why it tends to sit near spot in most regimes.
- The operational meaning of "spot has crossed the flip": the aggregate hedging regime has tilted, and the classifier flags it as a short-gamma condition with a 0.5% buffer for noise tolerance.

## Implemented at

`trading/packages/gex/src/gex/gex.py:69` — `gamma_flip_strike(per_strike, spot)`. Walks the cumulative sum of per-strike GEX sorted by strike, finds the first adjacent pair with a sign change, linearly interpolates between them. Returns `spot` when there's no crossing (one-sided chain).

The module docstring documents the history: the function was originally implemented as a per-strike sign detection, which broke for SPY-like chains; commit `1e90d49` replaced it with the cumulative definition. The comment block in the function itself captures the full pedagogy of the choice.

---

**Next:** [Sharpe, Sortino, max drawdown →](../backtest/metrics.md)
