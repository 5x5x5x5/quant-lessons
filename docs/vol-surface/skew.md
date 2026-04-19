---
title: "Skew and the smile"
prereqs: "Implied vol vs realized"
arrives_at: "asymmetric pricing of downside vs upside risk — the 25-delta put/call skew"
code_ref: "trading/packages/gex/src/gex/skew.py"
---

# Skew and the smile

Term structure varies IV across expiries. **Skew** varies IV across strikes, at a single expiry. Black-Scholes assumes a single $\sigma$ prices every strike. The market disagrees. The shape of that disagreement is information.

## The stylized picture

Plot ATM IV, OTM put IVs, and OTM call IVs for SPX, same expiry, 30 days out. You get this:

```
IV  ·
     ·
      ·
        ·
           · · · ·
                     ·
                       ·
       ──────────────────────→ strike
      OTM put     ATM     OTM call
```

OTM puts trade at higher IV than ATM, which trade at higher IV than OTM calls. The curve is downward-sloping in strike. This is the classic **equity index skew**.

Single-name equities often show a different shape — IV is elevated on both wings, producing a "smile":

```
IV  ·                     ·
     ·                   ·
      ·                 ·
       ·               ·
        ·  · · · · ·  ·
       ──────────────────────→ strike
```

The shapes have structural reasons. Index skew exists because hedgers persistently demand downside protection; smile exists for single names partly because large surprise moves can happen in either direction (earnings, M&A, etc.), and the tails on both sides carry similar insurance premium.

## Why the skew exists — the historical reason

Before October 1987, the IV surface was roughly flat across strikes. After, it wasn't. The 1987 crash taught market participants that large downside moves occur with higher probability than Black-Scholes (log-normal tails) would predict, and the demand for OTM put protection ballooned. That demand never fully subsided. Dealers now quote OTM puts at a premium to reflect the persistent bid for protection and the perceived fat left tail. Every equity index has carried skew since.

The asymmetry has a second cause: **leverage effect**. When stocks fall, their implied leverage rises (same debt, smaller equity), making the equity riskier. Realized volatility tends to rise on large down moves and fall on large up moves. A model that captures this — stochastic volatility with a negative correlation between returns and vol — naturally produces a skewed implied-vol surface.

## The 25-delta skew measure

There are many ways to quantify skew. The most common in practice, and the one this project uses:

$$
\text{skew}_{25\Delta} = \text{IV}(25\Delta \text{ put}) - \text{IV}(25\Delta \text{ call}).
$$

A 25-delta put is an OTM put with delta $-0.25$ (roughly a 75%-OTM put, interpretation-of-delta from [Lesson 7](../greeks/delta.md)). A 25-delta call is the corresponding OTM call with delta $+0.25$. The skew is the spread between their IVs.

For a typical equity index in calm markets, this spread is in the 2–4 vol-point range. In stressed conditions, it can widen to 6–10 points. In euphoric / short-vol-complacent markets, it can compress toward zero — a flat skew often precedes volatility events, because flat skew means the market has stopped paying for downside protection.

Why 25-delta specifically? It's a compromise: far enough OTM to be in the "insurance" region of the distribution, but close enough in that enough liquidity exists for reliable IV quotes. 10-delta and 50-delta alternatives exist; 25-delta is the most common convention.

## Delta-space interpolation

Option chains don't quote a "25-delta strike" directly — they quote strikes at fixed prices (e.g., 400, 405, 410). To get the IV at exactly 25-delta, you need to interpolate. The standard technique: map each quoted strike to its delta (using BS with the strike's own IV), then interpolate IV across the delta axis.

Working in delta-space rather than strike-space is not incidental. Delta is a natural reparameterization of the surface: the "25-delta point" on SPX moves with $S$, so the skew stays in the same part of the risk distribution regardless of where spot is today. Strike-based measures (e.g., "IV at $S \times 0.9$") conflate spot moves with skew moves, which is usually not what you want.

The implementation in `skew.py` walks the chain, computes each contract's delta from its strike and IV (via `bs_d1` + cumulative normal), then linearly interpolates IV at the target delta. Linear interpolation is adequate for normal-shaped surfaces; for fitting tail shapes more carefully, practitioners swap in SABR or SVI parameterizations. The repo notes this as a future upgrade.

## Skew z-score as a regime input

Like term structure, raw skew levels matter less than where they sit relative to their own history. A rolling z-score:

$$
z_\text{skew}(t) = \frac{\text{skew}_{25\Delta}(t) - \overline{\text{skew}}_\text{252d}}{\sigma_\text{skew, 252d}}.
$$

Three interesting values of $z_\text{skew}$:

- **Highly positive $z$**: skew is historically steep. Puts are expensive relative to their own history. Either a stress scenario is priced in, or hedgers have been buying aggressively without a vol event yet materializing.
- **Near zero $z$**: skew is at its historical norm. No signal from this axis.
- **Highly negative $z$**: skew is flattening or inverting. Put protection is unusually cheap relative to history. This is the interesting case — it often precedes volatility events, because it means hedgers have stopped paying for protection (complacency) or active selling of skew is compressing the spread.

The regime classifier uses a negative threshold on $z_\text{skew}$: when skew z-score is deeply negative (default threshold $-2.0$), it is treated as a short-gamma trigger. The logic is that flat/inverting skew is historically associated with vol events that follow shortly after, so the regime flips to "prepare for movement."

## When skew fails as a signal

Not every move in skew is informative. Two regular cases to be aware of:

- **Earnings season for single names**: pre-earnings skew shifts reflect the upcoming event, not a structural regime change. Index skew is less affected because index ATM IV absorbs earnings effects diffusely.
- **Dealer inventory rebalancing**: large-ticket customer orders can push individual strikes' IVs without signaling anything about market risk tolerance. Dealers' positions and hedging needs drive quoted prices; not everything is a macro signal.

The regime classifier partially mitigates by using index-level skew (SPX), where idiosyncratic effects are diluted. At the single-name level, skew as a standalone signal is noisier.

## Smile vs skew — parameterizing the surface

For a complete treatment, practitioners fit a parametric shape to the IV surface across strikes and expiries. Two standard families:

- **SVI** (Stochastic Volatility Inspired): five parameters per expiry, fit to strike-IV pairs. Fast, popular in risk systems.
- **SABR**: four parameters including a $\beta$ that controls whether the surface is skew-like or smile-like. Common in FX and interest-rate vols.

For the trading project's regime classification, a parametric fit isn't needed — the 25-delta skew is a scalar summary that captures enough of the surface's asymmetry. If a future strategy requires finer-grained surface information (e.g., trading the butterfly, or hedging across specific strike buckets), swapping in SVI or SABR is the natural upgrade path.

## What you can now reason about

- Why the equity index IV surface is downward-sloping in strike (skew) while single-name surfaces often form a smile — they reflect different customer flow and different structural risk profiles.
- Why skew is typically measured in delta-space, not strike-space — delta moves with spot, so the measurement is invariant to where the market sits today.
- Why *flattening* of skew, not steepening, often precedes volatility events — it's the market becoming complacent about downside risk.

## Implemented at

`trading/packages/gex/src/gex/skew.py`:

- Line 26: `interpolate_iv_at_delta(chain, target_delta, option_type, spot, rate)`. Filters to the shortest expiry with ≥21 DTE (weekly-options noise exclusion), maps each contract to its delta, linearly interpolates IV at the target delta.
- Line 64: `skew_25d(chain, spot, rate)` — the headline scalar, `IV(25d put) - IV(25d call)`.

The regime classifier in `regime.py:classify_regime` consumes `skew_25d_z` (rolling z-score of the daily skew) and triggers the short-gamma regime when z ≤ -2.0.

---

**Next:** [Market makers and delta-hedging →](../regime/market-makers.md)
