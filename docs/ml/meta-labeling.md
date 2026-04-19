---
title: "Meta-labeling"
prereqs: "Triple-barrier labeling"
arrives_at: "direction vs sizing decomposition — and the capstone strategy's reason to exist"
code_ref: "trading/packages/afml/src/afml/meta.py — MetaLabeler; trading/strategies/meta_rsi2.py"
---

# Meta-labeling

Meta-labeling is an underused technique in financial ML. It decomposes the trading decision into two questions, trains separate models for each, and uses the second to filter the first.

## The two-question decomposition

**Question 1 (primary):** What direction? Long, short, or flat.

**Question 2 (secondary):** Should we take this signal, and at what size? A probability multiplied by a sizing map.

Every trading strategy answers both questions, usually implicitly. Meta-labeling makes them explicit: the primary model emits direction only, and the secondary model decides whether the primary's direction is worth acting on.

The rationale for separating the two questions: they are answered using different information. Direction is often determined by simple rules (RSI thresholds, MA crosses, mechanical calendar events). Sizing requires conditional reasoning — given a primary signal, what is the probability that this specific signal succeeds? Training a single model to perform both tasks well is typically harder than training two specialized models.

## Why a mediocre primary combined with a capable secondary can outperform

A concrete illustration: suppose the primary (RSI(2) on SPY) has a 46% hit rate across all signals — below coin-flip and not tradeable in isolation.

Now build a secondary classifier trained to predict, given features at signal time (volatility regime, trailing performance, time of day, and so on), whether the primary's signal will hit the profit-take barrier. Apply the secondary as a filter: take only signals where $P(\text{take}) > 0.55$. The filtered signals have a 56% hit rate.

The primary is unchanged. The same features are available. Sharpe improves from 0.73 to 2.72 in the stability sweep. The secondary did not identify a better direction signal; it identified a better way to use the existing signal.

This pattern recurs in practice. The underlying reason is that conditional hit rates are often substantially higher than marginal hit rates. Most primary signals succeed in some conditions and fail in others. A secondary that identifies the favorable conditions concentrates exposure in high-probability signals.

## The secondary's label

The secondary trains on the binarized version of the triple-barrier direction labels, not on the labels themselves:

$$
\text{meta}_i = \begin{cases} 1 & \text{if label}_i = +1 \text{ (primary's bet was profitable)} \\ 0 & \text{otherwise} \end{cases}
$$

This binarization is produced by `meta_label` in `afml.labeling`. The secondary is a binary classifier answering whether the primary's bet succeeded, not what direction to bet. Direction is already determined by the primary.

The side information is encoded in the triple-barrier label. A profitable short has label $+1$ (via the side adjustment in the previous lesson), so `meta = 1`. A losing long has a label other than $+1$, so `meta = 0`. The meta-label is direction-neutral in its semantics: it distinguishes successful from unsuccessful trades.

## Features for the secondary

Useful features discriminate between conditions where the primary succeeds and those where it fails. Effective feature families include:

- **Regime tags.** The `long_gamma` / `short_gamma` / `vol_inverted` regime from the GEX classifier is a strong conditional feature, as primaries often behave differently across regimes.
- **Trailing primary performance.** The primary's hit rate over the last 20 signals is informative: a primary in a losing streak is more likely to produce another losing signal.
- **Entry conditions.** Volatility regime at entry (percentile of current vol versus trailing 252 days), recent trend, recent volatility of volatility.
- **Calendar features.** Time-of-day, day-of-week, proximity to macro events. Mechanical flows around the close, mid-day doldrums, and post-FOMC dynamics each show characteristic patterns.
- **Price-path features.** Short-window trailing return, recent absolute move size, distance from rolling high.

The capstone strategy uses a small feature set (6 columns) to demonstrate the pattern rather than optimize. Production meta-labelers typically use 20-50 features.

A structural warning: secondary features must be computable at primary-signal time. A feature that looks beyond the primary signal introduces leakage regardless of its source. The primary's trailing hit rate must use labels from strictly prior signals (shift by one), not inclusive.

## Classifier choice

AFML recommends starting with simple models. Gradient boosting (XGBoost, LightGBM, scikit-learn's `GradientBoostingClassifier`) performs well for several reasons:

- Non-linear, handling regime interactions naturally.
- Robust to feature scale, requiring no preprocessing.
- Tolerant of noisy features via regularization through tree depth and learning rate.
- Fast to train, suitable for walk-forward retraining.

Neural networks (small MLPs) are viable alternatives but typically do not outperform boosted trees on financial tabular data with limited samples. A JAX MLP may be educational but rarely improves Sharpe meaningfully.

The most important hyperparameters control regularization aggressiveness (`max_depth`, `learning_rate`, `n_estimators`). Financial data is noisy; under-regularized models memorize noise and produce brittle predictions. Conservative defaults — small tree depth (3), moderate number of trees (200), lower learning rate (0.05-0.1) — are appropriate starting points.

## Evaluating the secondary

Secondary evaluation has its own considerations:

**Avoid raw accuracy.** The meta-label distribution is typically imbalanced (more failures than successes). A classifier that always predicts 0 has high accuracy on such data but no utility. Precision-recall curves, F1 on the positive class, and ROC-AUC handle imbalance better.

**Precision and recall on the minority class.** The cases of interest are those where the secondary predicts "take." Precision is the fraction of "take" predictions that were actually profitable; recall is the fraction of profitable signals that were identified. These are the operational metrics.

**Calibration.** When soft sizing maps probability to position size, the probabilities must be well-calibrated. A classifier that reports 70% confidence should be correct 70% of the time. Uncalibrated classifiers produce brittle soft sizing. Gradient boosting is generally reasonably calibrated; when not, post-hoc calibration (Platt scaling, isotonic regression) is the correction.

**Final evaluation via Sharpe lift.** The secondary's value is quantified by the improvement in the full strategy's Sharpe relative to the primary alone. Both Sharpes should be computed and reported.

## The sizing function

The secondary outputs a probability $P(\text{take}) \in [0, 1]$. Mapping this probability to a position size is more consequential than it may appear.

Several valid shapes:

- **Hard threshold**: `size = 1 if p >= threshold else 0`. Simplest and most interpretable, but discards probability magnitude.
- **Thresholded soft**: `size = p if p >= threshold else 0`. Retains gradient information but amplifies calibration errors.
- **Linear ramp**: `size = clip((p - p_lo) / (p_hi - p_lo), 0, 1)`. Smooth and tolerant to small calibration biases; filters out very low probabilities.
- **Kelly-style**: `size = clip(2p - 1, 0, 1)`. Theoretically optimal under log-utility with accurate probabilities; penalizes miscalibration.

The capstone strategy uses a linear ramp from 0.45 to 0.65. The stability sweep demonstrated robustness: lift remains stable across neighboring ramps and seeds. The choice is not unique but is not arbitrary either.

## Why direction + size beats a monolithic approach

Before meta-labeling, the standard approach was to train one model to predict return (regression) or direction (classification) and scale position size by model confidence. This approach typically underperformed the two-model decomposition for several reasons:

- **Loss functions conflate direction and magnitude.** A model minimizing MSE on returns optimizes a combination of hit rate and realized magnitude. Improvements in one can harm the other. Direction-only losses avoid this issue.
- **Label imbalance.** Direction labels are noisy; magnitude labels are noisier. Training on both simultaneously directs signal into the noise-heavy regression target.
- **Calibration.** Multi-task outputs are difficult to calibrate jointly.

Meta-labeling decouples these concerns. The primary has a single loss (classification on triple-barrier ±1). The secondary has a different loss (classification on the binarized meta-label). Each is trained for its own task. The decomposition produces a stronger overall system than either task alone would yield.

## Pre-deployment checklist

Before deploying a meta-labeling strategy, verify:

- [ ] The primary emits clean directional signals with sufficient density (hundreds per year).
- [ ] Triple-barrier labels are generated with reasonable `pt_mult`, `sl_mult`, and `vertical_bars`.
- [ ] Meta-label binarization is applied (`afml.labeling.meta_label`).
- [ ] Secondary features are strictly available at entry time (no forward-looking leakage).
- [ ] Inner purged k-fold is used for hyperparameter selection.
- [ ] Outer walk-forward uses a label-horizon embargo between train and test folds.
- [ ] A stability sweep over hyperparameters and seeds is performed before trusting any single Sharpe number.
- [ ] DSR is computed to discount for multiple-testing bias (pending harness implementation).
- [ ] The sizing function is chosen with awareness of its calibration sensitivity.

The capstone strategy passes all items except the DSR check, which is pending the `NotImplementedError` stub in `harness.metrics`.

## Summary

The reader can now reason about:

- Why the primary-secondary decomposition often improves Sharpe more than improvements to the primary alone: conditional hit rates live in feature space the primary cannot access.
- Why the secondary's training label is binary (did the primary's bet succeed?) rather than directional: the direction is already determined.
- Why soft sizing amplifies calibration errors: uncalibrated probabilities translate directly into inappropriately aggressive or timid position sizes.

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
