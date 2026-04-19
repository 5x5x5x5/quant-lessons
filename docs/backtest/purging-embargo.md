---
title: "Purging, embargo, and label horizons"
prereqs: "Walk-forward vs k-fold"
arrives_at: "leak-free CV on overlapping labels — the AFML ch.7 fix"
code_ref: "trading/packages/afml/src/afml/cv.py — PurgedKFold"
---

# Purging, embargo, and label horizons

Walk-forward ensures test data follows training data in wall-clock time. This is necessary but not sufficient. A more subtle form of leakage occurs within a single fold and silently inflates k-fold results on overlapping labels.

This lesson covers the López de Prado AFML ch. 7 corrections: purging and embargo.

## The problem: label horizons

Consider a triple-barrier label. A signal at time $t$ receives a label based on what happens between $t$ and $t + 5$ (or until the first barrier is hit). The label at $t$ is therefore a function of prices up to $t + 5$.

Now consider k-fold cross-validation. Suppose the test fold contains observation $t_\text{test}$ and the train fold contains observation $t_\text{train}$ with $t_\text{train} < t_\text{test} < t_\text{train} + 5$. The training observation's label (not its features, but its label) was computed using prices through $t_\text{train} + 5$, which includes the test observation's window.

The model trains on this label. The training label encodes information from the test period. Even with walk-forward's temporal ordering, if $t_\text{train}$ precedes $t_\text{test}$ by less than the label horizon, the training label reaches forward into the test fold.

The result: the model performs better on the test fold than it would in live trading. The Sharpe is inflated. The bias is systematic — every training observation near the train-test boundary leaks. Naive k-fold on triple-barrier labels typically overstates Sharpe by 10-30% in standard setups.

## Purging

The AFML correction: drop training observations whose label horizons overlap the test fold.

For each observation $i$, define the label horizon $t_1[i]$ — the time at which its label is realized. In triple-barrier labeling, this corresponds to `exit_idx`, which may be the upper barrier hit, the lower barrier hit, or the vertical barrier. An observation $i$ in the train fold is purged if:

$$
[i, t_1[i]] \cap [\text{test fold boundaries}] \neq \emptyset.
$$

Any train observation whose label horizon overlaps the test fold is dropped. This removes the leakage channel.

Purging reduces training data by an amount that depends on the label horizon and fold size. For a vertical barrier of 5 and fold sizes of 50, approximately 10% of train observations are purged. For very long label horizons, the purge becomes aggressive; for typical settings, the cost is modest.

## Embargo

Purging addresses overlap on the "before" side of the test fold. The "after" side involves a subtler form of leakage: serial correlation.

Even when no label horizon crosses the test-fold boundary, consecutive observations in a time series tend to be correlated — prices, volumes, implied volatilities all show some degree of autocorrelation. A training observation at $t = t_\text{test,end} + 1$, immediately after the test fold, correlates with test observations through short-horizon serial dependence. Training on such observations weakly exposes the model to information about the test period via neighboring data.

The correction is to embargo a buffer of samples after the test fold, excluding them from training.

Embargo size is typically a small percentage of total samples — 1% to 2% is standard for liquid markets. On 5,000 daily observations, a 1% embargo removes 50 samples after each test fold.

The embargo applies whether or not labels themselves overlap. It addresses serial-correlation leakage rather than label-horizon leakage and operates independently of purging.

## Combined procedure

The full AFML purged-k-fold with embargo:

1. Partition samples into $k$ equal-size contiguous folds (without shuffling).
2. For each test fold:
   a. Drop training observations whose label horizon $t_1[i]$ overlaps the test fold's time window (purging).
   b. Drop training observations within a small buffer after the test fold (embargo).
   c. Train on what remains.
   d. Evaluate on the test fold.
3. Aggregate results.

Contiguous, non-shuffled test folds preserve time order within each fold, which is required for purging to be meaningful. Shuffled folds would require purging around every sample's neighborhood rather than fold boundaries, defeating the construction.

## Purged k-fold versus walk-forward

Purged k-fold is a model-selection tool: hyperparameter tuning, feature selection, threshold calibration. It provides an out-of-sample estimate of model performance that does not leak through label horizons or serial correlation.

Walk-forward is a final-evaluation tool: how would this strategy have performed as it rolled forward through time? Walk-forward's folds are strictly ordered; purged k-fold's folds are contiguous but not necessarily ordered (fold 3 may precede fold 2 chronologically under some definitions).

The two solve related but distinct problems. The AFML protocol uses:

- **Inner loop (purged k-fold)** for hyperparameter selection on held-out purged folds within each walk-forward training window.
- **Outer loop (walk-forward)** for evaluating the selected model on strictly-future test windows.

This is the pattern encoded in the trading project: `harness.backtest.WalkForward` for the outer loop, `afml.cv.PurgedKFold` for the inner.

## Embargo as a percentage

A design choice: the embargo in `PurgedKFold` is specified as a fraction of sample size (`embargo_pct=0.01`) rather than as an absolute count.

A percentage scales cleanly across dataset sizes. A 1% embargo drops 10 samples on 1,000 observations and 1,000 samples on 100,000 observations. This corresponds to the intuition that the serial correlation being buffered is roughly constant in calendar time, so absolute embargo should scale with sample rate.

An absolute embargo is appropriate when the autocorrelation length of a specific asset is known with high confidence. The percentage default is a reasonable general-purpose choice.

## Cost of correctness

Purging has the following costs:

- **Reduced training data.** For barrier labels with horizon 5 and fold sizes of 50, purging removes approximately 10% of train samples. For horizons of 50 and fold sizes of 100, the reduction approaches 50%. Long horizons combined with small folds produce aggressive purges.
- **Less stable early folds.** Purging disproportionately affects observations near fold boundaries. Early folds with small training sets can experience high purge rates.
- **Increased computational cost.** The purge mask is computed per fold; the cost is small but nonzero.

These costs are worth paying. A k-fold Sharpe that overstates by 20% is less useful than a purged-k-fold Sharpe on smaller training data. The relevant question is not "can I afford the purge" but "can I afford the bias from skipping it."

## Summary

The reader can now reason about:

- Why naive k-fold on triple-barrier labels systematically overstates Sharpe: training labels computed from future prices leak across fold boundaries.
- The distinction between purging (drops train samples whose label horizons overlap the test fold) and embargo (drops train samples in a buffer after the test fold to prevent serial-correlation leakage).
- Why purged k-fold does not replace walk-forward: they solve different leakage problems and combine into a nested CV protocol.

## Implemented at

`trading/packages/afml/src/afml/cv.py:18` — `PurgedKFold(n_splits, t1, embargo_pct=0.01)` extends `sklearn.model_selection.BaseCrossValidator`. The `split()` method, lines 39-75:

```python
train_mask = np.ones(n, dtype=bool)
train_mask[test_idx] = False
overlap = (indices <= test_end) & (self.t1 >= test_start)
train_mask &= ~overlap
if embargo > 0:
    embargo_mask = (indices > test_end) & (indices <= test_end + embargo)
    train_mask &= ~embargo_mask
yield indices[train_mask], test_idx
```

— the overlap line is the purge, the embargo block is the serial-correlation buffer. Because it subclasses `BaseCrossValidator`, it drops into any sklearn `GridSearchCV` or `cross_val_score` call: `cv=PurgedKFold(n_splits=5, t1=t1, embargo_pct=0.01)`.

---

**Next:** [Deflated Sharpe →](deflated-sharpe.md)
