---
title: "Meta-labeling"
prereqs: "Triple-barrier labeling"
arrives_at: "direction vs sizing decomposition — and the capstone strategy's reason to exist"
code_ref: "trading/packages/afml/src/afml/meta.py — MetaLabeler; trading/strategies/meta_rsi2.py"
---

# Meta-labeling

The most underused idea in financial ML. Split the trading decision into two questions, train two models to answer them separately, and let the second one *filter* the first.

## The two-question decomposition

Question 1 (primary): **What direction?** Long, short, or flat.

Question 2 (secondary): **Should we take this signal, and at what size?** A probability times a multiplier.

Every trading strategy answers both questions, usually implicitly. Meta-labeling makes them explicit. The primary model emits direction only. The secondary model decides whether the primary's direction is worth acting on.

Why the split matters: the two questions are answered using different information. Direction is often set by simple rules (RSI thresholds, MA crosses, mechanical calendar events). Sizing requires conditional reasoning — "given the primary signaled long, what's the probability this specific signal works?" Training a single model to do both well is harder than training two models to each do their own thing.

## Why a mediocre primary + smart secondary can win

The case for meta-labeling, phrased concretely:

Suppose your primary — say, RSI(2) on SPY — has a 46% hit rate across all its signals. Below coin-flip; not a tradeable primary in isolation.

Now build a secondary. Train it to predict, given features at signal time (vol regime, trailing performance, time of day, etc.), whether the primary's signal will hit the profit-take barrier. Apply the secondary to filter: take only signals where $P(\text{take}) > 0.55$. The filtered signals have a 56% hit rate.

Same primary. Same features available. Sharpe lifts from 0.73 to 2.72 in the stability sweep. The secondary didn't find a better direction signal — it found a better way to *use* the mediocre direction signal.

This pattern appears repeatedly. The reason: **conditional hit rates are often much higher than marginal hit rates**. Most primary signals have some conditions where they work and some where they don't. A secondary that identifies the "works" conditions compresses the strategy's exposure to high-probability signals only.

## The secondary's label

What does the secondary train on? Not the triple-barrier direction labels (−1, +1), but their **binarization**:

$$
\text{meta}_i = \begin{cases} 1 & \text{if label}_i = +1 \text{ (primary's bet worked)} \\ 0 & \text{otherwise} \end{cases}
$$

This is what `meta_label` in `afml.labeling` produces. The secondary is a binary classifier answering "did the primary's bet work?" — not "what direction should we bet?" The direction is already set by the primary.

Critically, **the side information is already baked into the triple-barrier label**. A profitable short has label +1 (see the side-adjustment in the previous lesson), so meta = 1. A losing long also has label different from +1, so meta = 0. The meta-label is direction-neutral in its semantics; it's just "worked" vs "didn't work."

## Features for the secondary

What goes into the feature matrix? Anything that discriminates when the primary works from when it doesn't. Good feature families:

- **Regime tags.** The `long_gamma` / `short_gamma` / `vol_inverted` regime from the GEX classifier is a strong conditional feature. Primaries often behave differently across regimes.
- **Trailing primary performance.** The hit rate of the primary over the last 20 signals is informative — a primary in a bad streak is more likely to produce another losing signal.
- **Entry conditions.** Vol regime at entry (percentile of current vol vs trailing 252 days), recent trend, recent volatility of volatility.
- **Calendar features.** Time-of-day, day-of-week, proximity to macro events. Mechanical flows around the close, mid-day doldrums, post-FOMC dynamics — each has signature patterns.
- **Price path features.** Short-window trailing return, recent absolute move size, distance from rolling-high.

The capstone strategy uses a small feature set (6 columns) by design — the goal is to demonstrate the pattern, not to optimize. Production meta-labelers typically have 20-50 features.

One structural warning: **features for the secondary must be available at primary-signal time**. A feature that "looks forward" past the primary signal is a leak, regardless of where it comes from. The primary's trailing hit rate must use labels from signals strictly prior to this one (shift by one), not inclusive.

## Classifier choice

AFML suggests starting simple. Gradient boosting (XGBoost, LightGBM, scikit-learn's `GradientBoostingClassifier`) works well because:

- Non-linear — handles regime interactions naturally.
- Robust to feature scale — no preprocessing needed.
- Tolerant of noisy features — regularization via tree depth / learning rate.
- Fast to train — suitable for walk-forward retraining.

Neural networks (small MLPs) are viable alternatives but usually don't outperform boosted trees on financial tabular data with limited samples. A JAX MLP might be educational; it rarely improves Sharpe meaningfully.

The critical hyperparameter is usually **regularization aggressiveness** (max_depth, learning_rate, n_estimators). Financial data is noisy; an under-regularized model memorizes noise and produces brittle predictions. Err conservative: small tree depth (3), moderate number of trees (200), lower learning rate (0.05-0.1).

## Evaluating the secondary

The secondary's evaluation is its own topic. A few things worth knowing:

**Never use raw accuracy.** The meta-label distribution is typically imbalanced (more failures than successes, often heavily). A classifier that always predicts 0 has high accuracy on such data but zero utility. Precision-recall curves, F1 on the positive class, and ROC-AUC all handle imbalance better than accuracy.

**Precision-recall on the minority class.** You care about the cases the secondary says "take." Precision = what fraction of "take" predictions were actually profitable. Recall = what fraction of actually-profitable signals did we identify. These are the operational metrics.

**Calibration matters.** If you're using soft sizing (probability → size), the probabilities need to be calibrated. A classifier that says "70% confident" should be right 70% of the time. Uncalibrated classifiers produce brittle soft sizing. Gradient boosting is generally reasonably calibrated; if not, post-hoc calibration (Platt scaling, isotonic regression) is the fix.

**Final evaluation is Sharpe lift.** The secondary's value is how much it improves the full strategy's Sharpe vs using the primary alone. Compute both, report both, report the ratio.

## The sizing function

The secondary outputs a probability $P(\text{take}) \in [0, 1]$. Converting that to a position size is the final step — and more consequential than people expect.

Several valid shapes:

- **Hard threshold**: `size = 1 if p >= threshold else 0`. Simplest, most interpretable, throws away the magnitude of the probability.
- **Thresholded soft**: `size = p if p >= threshold else 0`. Keeps gradient information, but amplifies calibration errors.
- **Linear ramp**: `size = clip((p - p_lo) / (p_hi - p_lo), 0, 1)`. Smooth, tolerant to small calibration bias, filters out very low probabilities.
- **Kelly-style**: `size = clip(2p - 1, 0, 1)`. Theoretically optimal under log-utility with accurate probabilities, punishing if miscalibrated.

The capstone strategy uses a linear ramp from 0.45 to 0.65 (per the lesson-by-lesson design). Stability sweep showed the choice is robust — lift is stable across neighboring ramps and seeds. The choice is not arbitrary but it's not unique either.

## Why direction + size beats monolithic

Historical perspective. Before meta-labeling, the standard approach was: train one model to predict return (regression) or direction (classification), scale position by confidence. This worked poorly. A few reasons:

- **Loss functions conflate direction and magnitude.** A model minimizing MSE on returns is optimizing a combination of hit rate and realized magnitude. Pushing on one hurts the other. Direction-only losses don't have this problem.
- **Imbalance.** Direction labels are noisy; magnitude labels are noisier. Training on both simultaneously concentrates the signal into the noise-heavy regression target.
- **Calibration.** Multi-task outputs are hard to calibrate jointly.

Meta-labeling decouples these. The primary has one loss (classification accuracy on triple-barrier +1 / -1). The secondary has a different loss (classification accuracy on the binarized meta-label). Each is trained to do its own job well. The decomposition produces a better whole than either task alone.

## Practical checklist

Before deploying a meta-labeling strategy, audit:

- [ ] Primary emits clean directional signals with sufficient density (hundreds per year).
- [ ] Triple-barrier labels generated with reasonable pt_mult/sl_mult/vertical_bars.
- [ ] Meta-label binarization applied (`afml.labeling.meta_label`).
- [ ] Secondary features are strictly available at entry time (no forward-looking).
- [ ] Inner purged-k-fold for hyperparameter selection (no leakage).
- [ ] Outer walk-forward with label-horizon embargo between train and test folds.
- [ ] Stability sweep over hyperparameters and seeds before trusting any single Sharpe number.
- [ ] DSR computed to discount for multiple-testing bias (pending harness implementation).
- [ ] Sizing function chosen with awareness of its calibration sensitivity.

The capstone strategy passes all except the DSR check — the one hanging thread is the NotImplementedError stub in `harness.metrics`.

## What you can now reason about

- Why the primary-secondary decomposition often improves Sharpe more than improving the primary — conditional hit rates live in feature space the primary can't access.
- Why the secondary's training label is binary (`did the primary's bet work?`), not directional — the direction is already set.
- Why soft sizing amplifies calibration errors — uncalibrated probabilities translate directly into inappropriately-aggressive (or timid) position sizes.

## Implemented at

- `trading/packages/afml/src/afml/meta.py:25` — `MetaLabeler(model, threshold=0.5)`. Wraps any sklearn-compatible binary classifier. The `size(X)` method returns $P(\text{take}) \cdot \mathbb{1}[P \ge \text{threshold}]$ by default (thresholded soft); custom sizing is easy to substitute.
- `trading/packages/afml/src/afml/labeling.py:126` — `meta_label(triple_barrier_out, sides)` binarizes the triple-barrier output.
- `trading/strategies/meta_rsi2.py` — the capstone implementation:
  - Primary: RSI(2) via `rsi2_primary`.
  - Features: 6-column matrix with side, vol percentile, trailing return, trailing abs-return, day-of-week, primary trailing hit rate.
  - Secondary: sklearn `GradientBoostingClassifier(n_estimators=200, max_depth=3)`.
  - Sizer: linear ramp `probability_to_size(p, p_lo=0.45, p_hi=0.65)`.
  - Walk-forward via `harness.backtest.WalkForward` with a label-horizon embargo.
- `trading/scripts/sweep_meta_rsi2.py` — hyperparameter × seed stability probe (25 cells; 25/25 beat the primary in the paper's most recent run).

---

**Next:** [Microstructure and order flow →](../flows/microstructure.md)
