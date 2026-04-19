---
title: "The gamma flip strike"
prereqs: "Dealer gamma — long vs short"
arrives_at: "the strike at which cumulative dealer gamma crosses zero — a practical regime marker"
code_ref: "trading/packages/gex/src/gex/gex.py — gamma_flip_strike"
---

# The gamma flip strike

A total GEX number characterizes the aggregate regime. The gamma-flip strike identifies where, along the strike axis, dealer positioning transitions from long gamma to short gamma. Combined with the current spot, this pair of scalars summarizes the two most actionable pieces of information the regime classifier needs.

The definition is subtle enough that the trading project's first implementation was incorrect. The corrected definition is the subject of this lesson.

## The incorrect definition

A naive first approach to the gamma flip: find the strike $K^*$ where per-strike GEX changes sign from positive to negative as strikes increase.

The reasoning: dealers' long-put contributions are positive, dealers' short-call contributions are negative, and the crossing is where the transition occurs.

This breaks on any chain where per-strike GEX is non-monotonic. SPY options, driven by retail flow across a wide strike range, can have per-strike GEX that oscillates — positive at strike 420, negative at 425, positive at 430, negative at 435. The first-adjacent-pair sign change identifies *a* crossing, but not a meaningful one. Regime classification becomes unstable under oscillation.

Commit `1e90d49` in the trading repo corrected this definition. The correct approach is cumulative.

## Correct definition: cumulative GEX crossing

Sort strikes in ascending order. Compute cumulative GEX:

$$
C_K = \sum_{K' \le K} \text{GEX}_{K'}.
$$

The gamma-flip strike $K^*$ is the value of $K$ at which $C_K$ crosses zero.

This definition is stable by construction: per-strike oscillations average out in the running sum. The running sum has a single smooth trajectory — it starts at zero (before any strikes), grows to a peak (accumulating put contributions and early call contributions), then decays and typically becomes negative as OTM call contributions dominate the tail. The zero-crossing marks the point at which net hedging flow changes sign, aggregated across all strikes at or below.

![Cumulative GEX versus strike for the same SPX snapshot from the previous lesson. Green shading marks the long-gamma region; pink marks short-gamma. The gamma-flip strike (orange) is where cumulative GEX crosses zero — here, above spot, as is typical in calm regimes.](../assets/figures/gex_cumulative_flip.png){ loading=lazy }

**Interpretation of the crossing.** At $K^*$, the contribution of all strikes up to $K^*$ cancels. Moving spot through $K^*$ shifts the net dealer gamma aggregate to the opposite side, which is why crossing the flip changes the regime. For a typical SPX profile (put-heavy below spot, call-heavy above spot), the cumulative begins positive and ends negative, so $K^*$ lies on the descending leg. In calm regimes, this leg sits just above spot; as dealer short-call positioning grows relative to long-put positioning, it moves closer to or below spot.

## Linear interpolation between strikes

Cumulative GEX is defined on discrete strikes (for example, 5-point increments). The running sum rarely crosses zero exactly at a quoted strike; it typically passes between two adjacent strikes. Linear interpolation locates the crossing more precisely:

Given adjacent strikes $K_{i-1} < K_i$ with cumulative GEX values $c_{i-1} > 0$ and $c_i < 0$ (or vice versa):

$$
K^* = K_{i-1} + \frac{-c_{i-1}}{c_i - c_{i-1}} (K_i - K_{i-1}).
$$

The result is a continuous scalar, updated daily, comparable to spot at any time. The implementation in `gex.py:gamma_flip_strike` performs this linear interpolation.

## One-sided chains

An edge case occurs when the chain is globally one-sided: all cumulative values positive, or all negative. This happens when dealer positioning is extremely skewed (in an illiquid single name, or in a chain with few strikes). The code returns `spot` in this case, signaling that no crossing exists and the classifier should defer to total GEX.

This fallback is appropriate: without a flip strike, the flip-versus-spot comparison has no defined answer, and total GEX alone becomes the regime indicator.

## Spot-versus-flip in regime classification

The classifier in `regime.py:classify_regime` uses the spot-versus-flip comparison as one of three short-gamma triggers:

- `spot < gamma_flip * 0.995` — spot has fallen below 99.5% of the flip strike. A 0.5% buffer avoids false triggers on small boundary crossings.
- `total_gex < 0` — the aggregate is negative.
- `skew_25d_z <= -2.0` — skew is compressing relative to history.

Any single trigger sets the `short_gamma` regime tag, unless term-structure inversion overrides with `vol_inverted`. The three triggers are not independent — they frequently co-occur — but each captures situations the others may miss. For example, a day with `total_gex > 0` may have spot below the flip under specific strike configurations.

## Dynamic flip location

The flip strike is not static. It changes daily as the options chain updates:

- **OI accumulation.** As expiry approaches, accumulated OI shifts the cumulative GEX curve and the flip location.
- **Volume at specific strikes.** Large customer trades at individual strikes change per-strike GEX and therefore the cumulative sum.
- **Time decay.** Gamma itself depends on time. Near expiry, short-dated gamma dominates, and the flip can move sharply.

In practice, the flip remains within a tight band of spot over daily horizons, moving by dollars or tens of dollars. Large fast moves in the flip correspond to material changes in market structure, typically around expiration Fridays or index-level events.

## Comparison with SpotGamma's "Zero Gamma"

Practitioners familiar with SpotGamma's methodology will note a distinction. SpotGamma's "Zero Gamma" level is computed by holding the chain's strikes and OI fixed and scanning spot until the total GEX crosses zero. The flip defined here holds spot fixed and scans strikes. These are different quantities in general.

For chains with gamma concentrated near current spot, the two estimates agree closely. For chains with more unusual dealer positioning, they diverge. The trading project uses the cheaper proxy; SpotGamma's scan is more expensive but arguably more accurate. For first-pass regime classification, the proxy is adequate; for more precise analysis, the full scan is the natural upgrade.

## Worked example

SPX at 5200. Cumulative GEX walked from low to high strikes:

| Strike | per-strike GEX ($B/1%) | Cumulative ($B/1%) |
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

Cumulative crosses zero between 5300 and 5350. Linearly interpolated, $K^* \approx 5312$. With spot at 5200, spot is $112 (2.2%) below the flip — indicating a short-gamma tilt.

The classifier's threshold is $0.995 \times 5312 \approx 5285$, so spot at 5200 is below that level and the short-gamma trigger fires.

## Summary

The reader can now reason about:

- Why the cumulative-crossing definition of the flip strike is more stable than a per-strike sign-change definition, particularly for retail-flow-driven chains such as SPY.
- How the flip strike updates daily with OI changes, time decay, and spot moves, and why it typically sits near spot across regimes.
- The operational meaning of "spot has crossed the flip": the aggregate hedging regime has shifted, and the classifier flags the condition as short-gamma with a 0.5% buffer for noise tolerance.

## Implemented at

`trading/packages/gex/src/gex/gex.py:69` — `gamma_flip_strike(per_strike, spot)` walks the cumulative sum of per-strike GEX sorted by strike, finds the first adjacent pair with a sign change, and linearly interpolates between them. It returns `spot` when no crossing exists (one-sided chain).

The module docstring records the history: the function was originally implemented using per-strike sign detection, which failed for SPY-like chains; commit `1e90d49` replaced it with the cumulative definition. The function's comment block documents the rationale.

---

**Next:** [Sharpe, Sortino, max drawdown →](../backtest/metrics.md)
