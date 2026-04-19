---
title: "The labeling problem"
prereqs: "Returns, compounding, log-returns; Random walks and the null model"
arrives_at: "why financial ML can't use iid-time-series labels, and what the alternative looks like"
code_ref: "—"
---

# The labeling problem

Supervised ML requires labels. What label should be assigned to observations in a financial time series?

The textbook answer — predict tomorrow's return or predict its sign — fails in specific ways once applied. This lesson explains why naive labeling strategies fall short and introduces the labeling framework AFML uses. It sets up the triple-barrier method in the next lesson.

## The naive approach: fixed-horizon returns

Given a daily return series $r_t$, assign each day a binary label: $y_t = 1$ if $r_{t+1} > 0$, else $y_t = 0$. Train a classifier to predict $y_t$ from features available at $t$.

This is the "predict tomorrow's close" framing common in introductory tutorials. Several problems follow.

### The label does not correspond to a decision

A trader's decision is not "will tomorrow close up?" It is: if this position is taken now, should it be closed at a profit target, a stop, or after a time period? The decision depends on the *path* between entry and exit, not only on the terminal price.

Fixed-horizon labels ignore path dependence. A label of $y = 1$ on a day with a 0.3% close-to-close gain is treated identically to $y = 1$ on a day with a 5% intraday peak that reverses before close. The two scenarios produce materially different trading outcomes, but the fixed-horizon label collapses them into a single class.

### Magnitude is discarded

Reducing a continuous return to $\pm 1$ discards information. A strategy trading on the signal does not treat a 0.01% move and a 5% move equivalently: sizing and expected profit differ. Binary labels eliminate this distinction.

### Labels are noisy near zero

In flat markets, small returns flip sign randomly. A day with $r_t = +0.001\%$ receives label 1; a day with $r_t = -0.001\%$ receives label 0. These represent the same market condition, yet the classifier treats them as opposites. The model learns to produce confident predictions on days with no real signal.

### The iid assumption fails

Scikit-learn's default cross-validation shuffles the dataset. For time series, this produces the k-fold leakage covered in [the walk-forward lesson](../backtest/walk-forward.md). Fixed-horizon labeling does not create additional leakage but does nothing to prevent the standard temporal leakage from shuffled k-fold.

## A partial improvement: continuous return labels

One variation addresses the magnitude problem: use the continuous return $y_t = r_{t+1}$ as a regression target instead of a binary label. The improvement is partial:

- Regression on raw returns has very low signal-to-noise ratio — most of the variance in $r_{t+1}$ is noise. A regressor with $R^2 = 0.02$ on daily returns may be genuinely useful, but standard ML evaluation frameworks will treat it as essentially random.
- Path dependence remains unaddressed: the target is still a single terminal point.
- Regression introduces other issues. MSE loss weights outlier days disproportionately, producing models that are sensitive to tails in potentially undesirable ways.

## The AFML reframe: label events, not bars

The key conceptual change: rather than predicting the return at every bar, predict the outcome of specific events where a trading decision would actually be made.

An event is a moment at which a primary signal fires — an RSI cross, a volatility spike, a news release, a calendar trigger. At each event, the labeling question becomes: given the primary signal at time $t$, what would the outcome have been had the trade been taken?

The outcome is determined by a specific exit rule. The canonical choice is the **triple barrier**, which defines three exit conditions:

- **Upper barrier** (profit-take): a move of $+\text{pt\_mult} \times \sigma$ above entry.
- **Lower barrier** (stop-loss): a move of $-\text{sl\_mult} \times \sigma$ below entry.
- **Vertical barrier** (time stop): a fixed maximum holding period.

The first barrier hit determines the label: upper hit yields $+1$, lower hit yields $-1$, vertical hit yields $\text{sign}(r_\text{final})$ ($+1$ if the position was net positive at the time stop, $-1$ otherwise).

This is the labeling system used in the trading project. [The next lesson](triple-barrier.md) develops the mechanics.

## How triple-barrier addresses the naive failure modes

### Labels correspond to decisions

A triple-barrier label answers the question: was taking the trade correct? The profit-take and stop-loss levels are actions the strategy could have executed in practice. The time barrier reflects the maximum holding period constraint.

### Path dependence is preserved

The label depends on the entire path between entry and exit, not only the terminal return. A +5% peak that reverses to −1% is labeled differently (likely stop-loss hit at some point) than a path that rises slowly to +1% (likely profit-take or vertical hit with positive return).

### Vol scaling makes labels comparable across regimes

Barriers are specified in units of rolling volatility. A 2σ move in 2017 and a 2σ move in 2020 receive the same label, even though their dollar magnitudes may differ by 5× or more. The classifier sees comparable targets across different volatility regimes.

### Events are sparse

A typical strategy produces hundreds to thousands of events per year rather than thousands of bars. This density is appropriate: enough data for training, but each observation is not dominated by noise.

## New problems introduced by triple-barrier

### Label overlap

When events occur close together in time, their label horizons overlap. An event at $t$ has a label depending on prices through $t + 5$. An event at $t + 2$ has a label depending on prices through $t + 7$. The two labels overlap by three days, so the labels are not iid — they share underlying price realizations.

This breaks naive cross-validation. [Purging](../backtest/purging-embargo.md) is the correction, covered in Part 6.

### Sample non-uniqueness

Overlapping labels share causal observations — the same price move contributes to multiple event labels. Treating the labels as iid in training over-weights the overlapping regions. Sample weighting by uniqueness corrects for this. AFML's sequential bootstrap (implemented in `packages/afml/src/afml/bootstrap.py`) is the standard tool.

### Meta-labels for primary-secondary decomposition

A triple-barrier label describes whether a trade would have been profitable. The operational question is whether to take the trade. Meta-labeling separates the two: a primary model emits direction, a secondary model predicts whether the primary's direction would have been profitable. The secondary's training target is the binarized meta-label ("did the primary bet succeed?"). [The meta-labeling lesson](meta-labeling.md) covers the construction.

## Features for the model

Labeling is half the problem; feature selection is the other half. Several points matter:

- **Stationarity.** Raw price is non-stationary. Features should be stationary or approximately so: returns, log-returns, fractionally-differentiated prices, z-scored features.
- **Fractional differentiation.** AFML's fracdiff recipe preserves memory (the level information that classical differencing destroys) while achieving stationarity. `packages/afml/src/afml/fracdiff.py` implements this.
- **Information available at $t$, not $t + 1$.** Any feature used to predict an event at $t$ must be computable from data available at $t$. Features that inadvertently reference $t + 1$ data produce forward-looking leakage.
- **Features for the secondary.** Meta-labeling features may include regime tags (from the GEX pipeline), trailing hit rates of the primary, vol regime, time-of-day, and day-of-week — variables that describe when the primary signal works and when it fails.

## Summary

The reader can now reason about:

- Why "predict tomorrow's close" is an inappropriate framing for a tradeable ML model: it ignores decision structure, path dependence, and has near-zero signal-to-noise.
- Why labeling events rather than bars aligns ML with the trading decisions that matter.
- The new problems introduced by triple-barrier labeling (label overlap, sample non-uniqueness) and why the rest of the AFML toolkit (purging, sequential bootstrap, meta-labeling) addresses them.

## Implemented at

The labeling problem is the motivation. The fixes live in the AFML package:

- `trading/packages/afml/src/afml/labeling.py` — `apply_triple_barrier`, `meta_label`, `rolling_vol`. The labeling machinery itself, covered in [the next lesson](triple-barrier.md).
- `trading/packages/afml/src/afml/cv.py` — `PurgedKFold`, covered in [the purging lesson](../backtest/purging-embargo.md).
- `trading/packages/afml/src/afml/bootstrap.py` — `sequential_bootstrap`, `average_uniqueness` for the sample-weighting problem introduced by overlapping labels.
- `trading/packages/afml/src/afml/fracdiff.py` — `get_weights_ffd`, `frac_diff_ffd` for stationarity-preserving feature construction.
- `trading/packages/afml/src/afml/meta.py` — `MetaLabeler` scaffold.

Every one of these exists because the naive labeling approach doesn't work. The collection is what AFML proposes in its place.

---

**Next:** [Triple-barrier labeling →](triple-barrier.md)
