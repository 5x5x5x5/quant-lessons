---
title: "Term structure of volatility"
prereqs: "Implied vol vs realized"
arrives_at: "the slope of IV across maturities — normally upward (contango), inverted in crises"
code_ref: "trading/packages/gex/src/gex/termstructure.py"
---

# Term structure of volatility

A single implied-vol number is a lie. There is no single $\sigma$ that prices the whole options chain — options at different expiries trade at different IVs. The pattern of IV across expiries is the **term structure**, and its slope is one of the most reliable regime signals in the market.

## Plotting the curve

Take the S&P 500 and pull ATM IVs across expiries: 1 week, 2 weeks, 1 month, 3 months, 6 months, 1 year. Plot them. In a quiet market, the curve is **upward-sloping** (contango — the blue line). In a crisis, the short end spikes above the long end (backwardation — the pink line):

![Term structure of IV: contango (upward-sloping, typical quiet regime) vs backwardation (inverted, crisis regime). X-axis is log-scaled days to expiry.](../assets/figures/term_structure.png){ loading=lazy }

**Contango** is the standard state — longer horizons price higher uncertainty, and the variance risk premium is usually larger for longer expiries in absolute terms. **Backwardation** is a crisis marker: short-term uncertainty is so high that near-dated options trade at higher IV than far-dated, because longer horizons imply some belief in mean reversion ("this storm will eventually pass") so far-dated IVs don't track the short-term spike.

The slope of the curve changes regime fast and mean-reverts slowly.

## The VIX family

CBOE publishes IV indices at specific maturities on the S&P 500:

| Index | Horizon |
|-------|---------|
| VIX9D | 9 days |
| VIX | 30 days |
| VIX3M | 3 months |
| VIX6M | 6 months |

Each uses the same model-free variance-swap formula from [the previous lesson](implied-vol.md), scaled to its own target horizon. The two ratios that get watched most are:

- $\text{VIX9D} / \text{VIX}$ — short-end slope. When greater than 1, intraday panic is pricing above 30-day IV. A sharp, fast signal of short-horizon stress.
- $\text{VIX} / \text{VIX3M}$ — classic medium slope. When greater than 1, 30-day IV is above 3-month IV. The most-watched backwardation indicator.

In contango, both ratios are less than 1. Inversion flips either or both above 1.

## Why inversion is a regime signal

Empirically, an inverted term structure correlates with:

- **Short-gamma dealer positioning** (Part 5) — the hedging feedback loop that amplifies moves.
- **Higher realized volatility** in the days that follow.
- **Lower mean-reversion** — trends that might normally reverse have more follow-through.

Mechanism: demand for short-dated protection (puts expiring this week) is most elastic during acute stress. Customers buy puts; dealers sell them; the implied vol of those puts bids up sharply, inverting the short end. Because the long end doesn't move as much (buyers don't panic-hedge year-out exposure), the slope flips. The inversion *is* the footprint of panic hedging flow.

The signal is noisy. Sometimes VIX/VIX3M crosses 1.0 on a sleepy day because of a minor market blip and reverts within hours. Sometimes it crosses 1.0 and stays there for weeks. The **persistence** of the inversion matters as much as its presence.

## Thresholds and noise tolerance

Raw threshold at exactly 1.0 is noisy — small rounding errors, stale data, intraday feeds that don't sync perfectly can push a ratio fractionally above 1.0 without meaningful regime change. A small buffer helps:

$$
\text{is\_inverted} \;=\; \text{short\_slope} > 1.02 \;\; \text{or} \;\; \text{med\_slope} > 1.02.
$$

The `1.02` threshold is a noise tolerance: a 2% cushion avoids constant flip-flopping around the 1.0 boundary. There's nothing sacred about 2% — it's a calibration choice. On a smoother data source you might drop to 1.01; on a noisier one you might go to 1.03. What matters is that the threshold is *above* unity by enough to ignore plausible measurement error, and *below* the values that actually signal stress (empirically >1.05 for serious events).

## Rolling z-scores

Absolute levels aren't the only useful read. "The short end is inverted" is one kind of signal; "the short end just inverted for the first time in six months" is a different, often sharper, signal. A rolling z-score captures the latter:

$$
z_t = \frac{\text{slope}_t - \bar{\text{slope}}_\text{252d}}{\sigma_\text{slope, 252d}}.
$$

Large positive $z$ means the slope is unusually high relative to its own trailing year. Useful for detecting regime shifts that haven't crossed a raw threshold yet. The trading project computes these alongside the raw ratios.

## Term structure versus the VIX level

A common mistake: treating "VIX is high" and "VIX term structure is inverted" as the same signal. They're not.

- VIX high, contango: elevated vol that the market expects to persist (or even grow). Still "ordered."
- VIX high, inverted: acute short-term stress that the market expects to mean-revert. The **shape** says something the level doesn't.

In practice, both pieces of information matter. The regime classifier in this project uses the shape (inversion) as one trigger for `vol_inverted` regime; the level is not explicitly a trigger, though it indirectly affects sizing in any strategy that scales positions by vol.

## The shape of the full surface

Term structure is one axis of the implied-vol surface. The other is strike — IV varies across strikes at a single expiry, too. That's [skew](skew.md), covered in the next lesson. Both axes are "deviations from Black-Scholes's constant-σ assumption," and both are tradable. Dispersion trading, calendar spreads, skew trades, volatility carry strategies — all are expressions of one of these two shapes.

For this project's purposes, the single signal being consumed from term structure is **the two slopes and their inversion flag**. That's it. The richness of the full surface is real, but the regime classifier is intentionally simple — one number from term structure, one from skew, one from dealer gamma.

## What you can now reason about

- Why a single "IV" number hides a full surface's worth of structure, and why the slope of that surface across expiries can be the signal even when the level isn't.
- What "contango" and "backwardation" mean in vol terms, and why backwardation is a short-gamma / high-realized-vol regime marker.
- Why thresholds like 1.02 appear instead of 1.0 in regime rules — noise tolerance is a calibration decision, not a theoretical one.

## Implemented at

`trading/packages/gex/src/gex/termstructure.py`:

- Line 23: `compute_term_structure(vix9d, vix, vix3m)` returns the two slopes and the inversion flag for a single EOD snapshot.
- Line 39: `rolling_inversion_flags(series, lookback_days=252)` builds the same ratios across history plus the 252-day rolling z-scores. Output columns: `short_slope`, `med_slope`, `short_slope_z`, `med_slope_z`, `is_inverted`.

The `regime.py::classify_regime` function consumes these via the `short_slope` and `med_slope` arguments and uses a `1.02` inversion threshold to trigger the `vol_inverted` regime tag.

---

**Next:** [Skew and the smile →](skew.md)
