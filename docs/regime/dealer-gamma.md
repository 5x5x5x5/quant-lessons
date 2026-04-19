---
title: "Dealer gamma — long vs short"
prereqs: "Market makers and delta-hedging; Gamma — the second derivative"
arrives_at: "the feedback loop that creates market regimes — long gamma dampens, short gamma amplifies"
code_ref: "trading/packages/gex/src/gex/gex.py — per_strike_gex, total_gex"
---

# Dealer gamma — long vs short

> **Status:** Draft pending.

**Scope:** Aggregate dealer gamma across all outstanding options, signed by the dealer's position in each contract. Define **Gamma Exposure (GEX)** per 1% spot move:

$$
\text{GEX}_K = \Gamma_K \cdot \text{OI}_K \cdot \text{contract multiplier} \cdot S^2 \cdot 0.01
$$

Summed across strikes, this is dollar hedging flow per 1% move. When dealers are **net long gamma**, their hedging is mean-reverting: a move up forces them to sell into strength; a move down forces them to buy weakness. When **net short gamma**, the sign flips — they sell into weakness and buy strength, amplifying moves. This is the mechanism behind SPX "pinning" near strikes and "melt-up / melt-down" conditions.

**You'll be able to reason about:**

- Why `$GEX per 1% move` is the right reporting unit — the scale you care about is dollars, not raw gamma.
- Why the sign convention matters (flip it and you flip every regime call).
- The asymmetry between index GEX (mostly short-gamma on dealers below the flip) and single-name (customer positioning varies; often long-gamma for dealers).

**Implemented at:** `trading/packages/gex/src/gex/gex.py` — `per_strike_gex`, `total_gex`.

---

**Next:** [The gamma flip strike →](gamma-flip.md)
