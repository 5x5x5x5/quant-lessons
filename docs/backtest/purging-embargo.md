---
title: "Purging, embargo, and label horizons"
prereqs: "Walk-forward vs k-fold"
arrives_at: "leak-free CV on overlapping labels — the AFML ch.7 fix"
code_ref: "trading/packages/afml/src/afml/cv.py — PurgedKFold"
---

# Purging, embargo, and label horizons

Walk-forward keeps the test data in the future of the training data in wall-clock time. That's necessary but not sufficient. A more subtle leak happens inside a single fold, and it's the one that makes k-fold on overlapping labels silently lie to you.

This lesson is the López de Prado AFML ch. 7 fix: purging and embargo.

## The problem: label horizons

Consider a triple-barrier label. You take a signal at time $t$ and assign a label based on what happens between $t$ and $t + 5$ (or whenever the first barrier hits). The label at $t$ is a function of prices up to $t + 5$.

Now do k-fold CV. Suppose the test fold contains observation $t_\text{test}$, and the train fold contains observation $t_\text{train}$ with $t_\text{train} < t_\text{test} < t_\text{train} + 5$. The training observation's *label* — not its features, but its label — was computed using prices through $t_\text{train} + 5$, which includes the entire test observation's window.

The model trains on this training label. The training label encodes information from the test period. Even with walk-forward's temporal ordering, when $t_\text{train}$ precedes $t_\text{test}$ by less than the label horizon, the training label reaches forward into the test fold.

Result: the model performs better on the test fold than it would in live trading. The Sharpe is inflated. The bias is systematic — every training observation near the train-test boundary leaks. Naive k-fold on triple-barrier labels over-reports Sharpe by roughly 10-30% in typical setups.

## Purging

The AFML fix: **drop training observations whose label horizons overlap the test fold**.

Define for each observation $i$ its label horizon $t_1[i]$ — the time at which its label is realized (in triple-barrier, this is the `exit_idx`, which can be the upper barrier hit, the lower barrier hit, or the vertical barrier). An observation $i$ in the train fold is *purged* if:

$$
[i, t_1[i]] \cap [\text{test fold boundaries}] \neq \emptyset.
$$

In other words, if the train observation's label horizon overlaps the test fold at all, drop it. This removes the leakage channel.

Purging costs training data — how much depends on the label horizon and the fold sizes. For vertical-barrier = 5 and fold sizes of 50, roughly 10% of train observations get purged. For very long label horizons, purging becomes aggressive enough to matter. Mostly, it's cheap.

## Embargo

Purging fixes the overlap on the "before" side of the test fold. The "after" side has a similar but subtler leak: serial correlation.

Even if no label horizon crosses the test fold boundary, consecutive observations in a time series tend to be correlated — prices, volumes, implied vols, everything has some degree of autocorrelation. A training observation at $t = t_\text{test,end} + 1$, immediately after the test fold, is correlated with the test observations through short-horizon serial correlation. Training on it causes the model to (weakly) learn about the test period from a neighbor.

The fix: **embargo a buffer of samples after the test fold, excluding them from the training set**.

The embargo size is typically a small percentage of total samples — 1% to 2% works for most liquid markets. On 5,000 daily observations, a 1% embargo removes 50 samples right after each test fold.

The embargo exists whether or not the labels themselves overlap. It's a separate machinery from purging, handling serial-correlation leak rather than label-horizon leak.

## The combined procedure

The full AFML purged-k-fold with embargo:

1. Partition samples into $k$ equal-size contiguous folds (do **not** shuffle).
2. For each test fold:
   a. Drop training observations whose label horizon $t_1[i]$ overlaps the test fold's time window. (Purging.)
   b. Drop training observations within a small buffer after the test fold. (Embargo.)
   c. Train on what remains.
   d. Evaluate on the test fold.
3. Aggregate.

Contiguous test folds (not shuffled) preserve time order within each fold, which makes purging meaningful. Shuffled folds would defeat the purpose — the purge would need to apply around every sample's neighborhood instead of just the fold boundaries.

## Why this doesn't replace walk-forward

Purged-k-fold is for **model selection**: hyperparameter tuning, feature selection, threshold calibration. It gives you an out-of-sample estimate of model performance that doesn't leak through label horizons or serial correlation.

Walk-forward is for **final evaluation**: "how would this strategy have performed as I rolled it forward through time?" Walk-forward's folds are strictly ordered; purged k-fold's are contiguous but not necessarily ordered (fold 3 can be earlier than fold 2 if you define folds chronologically).

The two solve related but distinct problems. In the AFML protocol:

- **Inner loop (purged k-fold):** select hyperparameters on held-out purged folds inside each walk-forward training window.
- **Outer loop (walk-forward):** evaluate selected model on strictly-future test windows.

This is the pattern encoded in the trading project: `harness.backtest.WalkForward` for outer, `afml.cv.PurgedKFold` for inner.

## Embargo as a percentage: why not absolute?

One design choice worth naming. The embargo in `PurgedKFold` is specified as a percentage of sample size (`embargo_pct=0.01`), not as an absolute number of samples.

Percentage scales cleanly across different dataset sizes. A 1% embargo on 1,000 samples drops 10 samples; on 100,000 samples, it drops 1,000. This matches intuition — the serial correlation you're buffering against is probably roughly constant in calendar time, so as your sample rate grows, so should your absolute embargo.

An absolute embargo might make sense if you have strong priors about the autocorrelation length of your specific asset. The percentage default is a reasonable compromise.

## The cost of correctness

An honest accounting of what purging costs you:

- **Reduced training data.** For barrier labels with horizon 5 and fold sizes 50, purging drops ~10% of train samples. For horizons 50 and fold sizes 100, it drops ~50%. Long horizons + small folds = punishing purge.
- **Potentially unstable early folds.** Purging hits the earliest and latest train samples hardest (boundary effects). Early folds with small train sizes can have high purge rates.
- **Increased computational cost.** The purge mask is computed per-fold, not once — cheap, but not free.

These costs are worth paying. A k-fold Sharpe that's 20% too high is worse than a purged-k-fold Sharpe on less data. The question is never "can I afford the purge," it's "can I afford the bias if I skip it."

## What you can now reason about

- Why naive k-fold on triple-barrier labels systematically over-reports Sharpe — training labels encoded from future-prices leak through the fold boundaries.
- The distinction between purging (drops train samples whose label horizons overlap the test fold) and embargo (drops train samples in a buffer after the test fold to block serial-correlation leak).
- Why this isn't a replacement for walk-forward — they solve different leakage problems and work together in a nested CV protocol.

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
