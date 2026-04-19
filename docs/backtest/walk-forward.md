---
title: "Walk-forward vs k-fold"
prereqs: "Sharpe, Sortino, max drawdown"
arrives_at: "time-respecting cross-validation — train on past, test on future, advance the anchor"
code_ref: "trading/packages/harness/src/harness/backtest.py"
---

# Walk-forward vs k-fold

Any backtest answers a counterfactual: "If I had deployed this strategy at time $t$, knowing only what was available then, how would it have performed?" The protocol for answering that question is cross-validation. But the standard CV machinery from machine learning — random k-fold — quietly fails on time series. Walk-forward is the fix.

## Why naive k-fold is wrong

Standard k-fold cross-validation shuffles the dataset, splits into $k$ folds, trains on $k-1$ folds, tests on the held-out one. This procedure assumes the data points are **iid** — independently and identically distributed. For iid data, the fold you test on is a fair sample of the same distribution that produced the training data.

Financial time series are *not* iid, and k-fold fails in two ways:

1. **Temporal leakage.** In shuffled k-fold, your training fold contains data from *after* your test fold (in wall-clock time). A model trained on that sees the future. Its realized test performance reflects knowledge that wouldn't have been available at prediction time.

2. **Regime mixing.** Real markets alternate regimes (low vol, high vol, trending, mean-reverting). If your test fold randomly samples from all regimes and your training fold does too, the model learns a regime-average rather than a live-trading-regime response. The test statistic overstates how robust the model will be in a specific regime you actually encounter.

These aren't minor effects. A k-fold Sharpe on a trading strategy can be double the live-trading Sharpe on the same signal — entirely because of temporal leakage masquerading as out-of-sample evidence.

## Walk-forward: the right shape

Walk-forward respects time order. At each step:

1. Train on data from the start through time $t$ (or from $t - \text{window}$ through $t$ if using a fixed-length train window).
2. Test on data from $t$ to $t + h$ (horizon).
3. Advance $t$ by a stride and repeat.

Pictorially, with an expanding train window and horizon $h = 3$, stride $s = 3$:

```
fold 1: TRAIN [ 0 ... 9 ]        TEST [ 10, 11, 12 ]
fold 2: TRAIN [ 0 ... 12 ]       TEST [ 13, 14, 15 ]
fold 3: TRAIN [ 0 ... 15 ]       TEST [ 16, 17, 18 ]
fold 4: TRAIN [ 0 ... 18 ]       TEST [ 19, 20, 21 ]
...
```

Every test fold is **strictly after** its training fold in wall-clock time. No temporal leakage. Every test observation answers "what would this model have said about this period, given only what was available before it?"

## Expanding vs sliding train windows

Two common variations:

- **Expanding**: train window grows with each step, always using everything up to $t$. More data over time (generally favors more stable estimates), but old regimes have increasing weight as a fraction of training data.
- **Sliding** (or "rolling"): train window has fixed length $W$, so training data is always $[t - W, t]$. Adaptive to regime changes — old data ages out — but uses less data at any given time.

Which is right? It depends. For a strategy whose edge is stationary across regimes, expanding wins — more data is usually better. For a strategy whose edge is regime-dependent, sliding wins — forgetting the old regime lets the model adapt. In doubt, run both and report both.

The harness's `WalkForwardConfig` has a boolean `expanding` field (defaults True). Flipping to False gives the sliding variant with train length set to `initial_train`.

## Stride and overlap

The **stride** controls how much the anchor advances between folds. Equal to test horizon ($s = h$) produces non-overlapping test folds — simplest, most defensible. Less than horizon ($s < h$) produces overlapping test folds, each making use of a new piece of data plus some already-seen data. Greater than horizon ($s > h$) leaves gaps.

For most backtests, use $s = h$. Overlapping test folds look like more data but don't give you independent observations — you're re-measuring the same thing with small perturbations. Non-overlapping is cleaner.

## Walk-forward as the outer loop

Walk-forward is the **outer** evaluation loop. Inside each fold, you may still need cross-validation for model selection — which hyperparameters, which features, which thresholds. That inner CV is a separate design choice, and it has its own leakage hazards ([next lesson on purging](purging-embargo.md)).

A clean protocol:

1. Walk-forward defines the outer train/test splits.
2. Inside each outer train set, use purged k-fold to select hyperparameters on held-out purged-k-folds.
3. Retrain on the full outer train set using the selected hyperparameters.
4. Evaluate on the outer test fold.
5. Advance the walk-forward anchor.

Violating this structure — using the outer test fold to pick hyperparameters, for example — is subtle look-ahead that won't survive into live trading.

## What walk-forward does not prevent

A realistic view of what walk-forward still leaves on the table:

- **Label-horizon leakage.** If a training label at time $t$ depends on prices through $t + 5$, that label can overlap with the test fold even when $t$ itself is in the train set. Purging ([next lesson](purging-embargo.md)) is the fix.
- **Data-snooping bias.** Walk-forward evaluates *one* strategy. If you tried 100 strategies and picked this one, the test performance is biased upward by the selection. Walk-forward doesn't know how many strategies you tried. [Deflated Sharpe](deflated-sharpe.md) is the downstream correction.
- **Future information baked into features.** Using a feature whose computation reaches into the future (forward-looking corporate action adjustments, some index methodology data) leaks regardless of your CV. Audit features against "what did I know at $t$?"
- **Survivorship bias.** Running a backtest on today's index constituents (rather than the constituents at each historical date) silently excludes companies that went bust. Walk-forward on today's list looks better than it should.

Walk-forward is necessary but not sufficient. It catches the easiest-to-miss leakage (temporal) but not the subtler kinds.

## The expanding-train failure mode

One more subtlety worth naming. Expanding-train walk-forward means early folds train on tiny datasets. Fold 1 might have 252 observations; by fold 20, there are 1,512. Early-fold model quality is genuinely worse, not because the strategy doesn't work, but because the estimator is noisy on small samples.

This biases the cumulative out-of-sample Sharpe downward in the early folds. The bias unwinds as the train set grows, which means realized backtest performance improves over time even if the underlying edge is stationary. Don't mistake this for "the edge is getting stronger" — it's the estimator getting less noisy.

The `initial_train` parameter sets the size of the first training window, and should be large enough that the model has reasonable out-of-sample behavior from fold 1. For daily bars, 252 (one year) is a typical minimum; 504 is more conservative.

## What you can now reason about

- Why random k-fold cross-validation produces optimistic Sharpes on time series — the shuffling gives training data access to the future.
- The distinction between expanding and sliding train windows, and when each is right (stationary edge vs regime-dependent edge).
- Why walk-forward is necessary but not sufficient — it catches temporal leakage but not survivorship bias, data snooping, or forward-looking features.

## Implemented at

`trading/packages/harness/src/harness/backtest.py`:

- Line 22: `WalkForwardConfig(initial_train, test_horizon, stride, expanding=True)`.
- Line 40: `WalkForward.split(n_samples)` — generator that yields `(train_idx, test_idx)` pairs.

The module docstring notes explicitly: `WalkForward does NOT execute the strategy — it yields index pairs. The caller trains, predicts, and computes PnL per window`. This separation is deliberate; it keeps the harness agnostic to model type, feature construction, and cost modeling.

---

**Next:** [Purging, embargo, and label horizons →](purging-embargo.md)
