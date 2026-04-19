---
title: "The labeling problem"
prereqs: "Returns, compounding, log-returns; Random walks and the null model"
arrives_at: "why financial ML can't use iid-time-series labels, and what the alternative looks like"
code_ref: "—"
---

# The labeling problem

ML needs labels. What label should you give a financial time series?

The textbook answer, "predict tomorrow's return" or "predict the sign of tomorrow's return," is wrong in ways that become obvious once you've tried it. This lesson is about why the naive labeling strategies fail, and what kind of labels the AFML framework uses instead. It sets up the triple-barrier method in the next lesson.

## The naive attempt: fixed-horizon returns

Take a daily return series $r_t$. Assign each day a binary label: $y_t = 1$ if $r_{t+1} > 0$, else $0$. Train a classifier to predict $y_t$ from features available at $t$.

This is the "predict tomorrow's close" framing that populates tutorial blog posts. Multiple problems:

### The label has no decision behind it

A trader's decision isn't "do I think tomorrow closes up?" It's "if I buy this now, should I take profit at some target, cut at some stop, or hold for some time?" The decision involves a **path** — what happens between now and exit — not just a terminal price.

The fixed-horizon label ignores paths. A label of $y = 1$ on a day with a 0.3% close-to-close gain is the same as a label of $y = 1$ on a day with a 5% peak intraday that gives back most of the gain before close. These are wildly different trading experiences, but the fixed-horizon label collapses them.

### The magnitude is discarded

Reducing a continuous return to $\pm 1$ throws away information. A strategy that trades on the signal doesn't care equally about a 0.01% move and a 5% move — sizing and expected profit differ. The binarized label erases that.

### Labels are noisy near zero

When the underlying is flat, small returns flip sign randomly. A day with $r_t = +0.001\%$ gets labeled 1; a day with $r_t = -0.001\%$ gets labeled 0. These are essentially the same market condition, but the classifier sees them as opposite. The classifier learns to be confident on days with no real signal, which is the opposite of what you want.

### iid assumption fails

Sklearn's default CV shuffles the dataset. For time series, this produces the k-fold leakage covered in [the walk-forward lesson](../backtest/walk-forward.md). Fixed-horizon labeling doesn't create *extra* leakage, but it does nothing to prevent the standard time-series leakage from k-fold.

## The slightly less naive attempt: continuous return labels

Fix the magnitude problem: use the continuous return $y_t = r_{t+1}$ as a regression target instead of a binary label. Better?

Partially. You now preserve magnitude and don't have the near-zero flip. But:

- Regression on raw returns has very low SNR — most of the variance in $r_{t+1}$ is noise. A regressor that achieves R² of 0.02 on daily returns might be genuinely useful, but most ML evaluation frameworks will report it as "essentially random."
- The path-dependence problem remains. You're still predicting a single point (tomorrow's close), not a tradeable signal.
- Regression introduces new issues: the loss function (MSE) weighs a small number of outlier days disproportionately, and the resulting model tends to be sensitive to tails in ways you may not want.

## The AFML insight: label events, not bars

The key reframe. Don't try to predict the return of every bar. Predict the outcome of **specific events** where a trading decision would actually be made.

An event is a moment where a primary signal fires — an RSI cross, a volatility spike, a news release, a calendar trigger. At each event, the labeling question becomes: "Given the primary signal at time $t$, what would have happened if we'd taken the trade?"

"What would have happened" is answered by a specific exit rule. The canonical choice: **triple-barrier**. Three barriers define when the trade ends:

- **Upper barrier** (profit-take): a move of $+\text{pt\_mult} \times \sigma$ above entry.
- **Lower barrier** (stop-loss): a move of $-\text{sl\_mult} \times \sigma$ below entry.
- **Vertical barrier** (time stop): a fixed maximum holding period.

Whichever barrier hits first determines the label. Upper hit: label $+1$. Lower hit: label $-1$. Vertical hit: label = $\text{sign}(r_\text{final})$, which is $+1$ if the position was net-up on the day the time stop triggered, $-1$ if net-down.

This is the labeling system the trading project uses. [The next lesson](triple-barrier.md) develops the mechanics.

## Why triple-barrier fixes the problems

Running down the failure modes of naive labels:

### Labels correspond to decisions

A triple-barrier label answers "was it correct to take the trade?" in terms that map to actual trading actions. The profit-take and stop-loss levels are things the strategy could have done in practice. The time barrier reflects the hold-period constraint.

### Path dependence is respected

The label depends on the entire path between entry and exit, not just the terminal return. A +5% peak that reverses to −1% gets labeled differently (likely stop-loss hit at some point) than a path that rises slowly to +1% (likely profit-take or vertical hit with positive return).

### Vol scaling makes labels comparable

Barriers are specified in units of rolling volatility. A 2σ move in 2017 and a 2σ move in 2020 are labeled the same way, even though their dollar magnitudes differ by 5× or more. The classifier sees comparable targets across regimes.

### Events are sparse

A typical strategy has hundreds to thousands of events per year, not thousands of bars. This is the right density — enough data to train on, not so much that each "observation" is dominated by noise.

## The new problems triple-barrier introduces

Every fix creates new problems. The ones triple-barrier brings:

### Label overlap

If events are close together in time, their label horizons overlap. An event at $t$ has a label depending on prices through $t + 5$. An event at $t + 2$ has a label depending on prices through $t + 7$. The two overlap by three days. Labels are not iid — they share underlying price realizations.

This breaks naive cross-validation. [Purging](../backtest/purging-embargo.md) is the fix, covered earlier in Part 6.

### Sample non-uniqueness

Overlapping labels share "causal" observations — the same price move can label multiple events. Treating them as iid in training over-weights those overlapping regions. **Sample weighting by uniqueness** — how "unique" each label's information is — corrects for this. AFML's sequential bootstrap (implemented in `packages/afml/src/afml/bootstrap.py`) is the standard machinery.

### Meta-labels for primary-vs-secondary decomposition

A triple-barrier label describes whether a trade would have worked. But the real operational question is whether to *take* the trade at all. Meta-labeling splits this: a primary model emits direction, a secondary model predicts whether the primary's direction would have been profitable. Training data for the secondary uses the binarized meta-label ("did the primary bet work?"). [The meta-labeling lesson](meta-labeling.md) covers this.

## What features should the model use?

The labeling question is half the problem. The feature question — what predictors the model trains on — is the other half. A few things worth keeping in mind:

- **Stationarity.** Raw price is non-stationary. Features should be stationary or approximately so. Returns, log-returns, fractionally-differentiated prices, z-scored features.
- **Fractional differentiation.** AFML's fracdiff recipe: preserves memory (the level information of price that classical differencing destroys) while achieving stationarity. `packages/afml/src/afml/fracdiff.py` implements this.
- **Information at $t$, not $t + 1$.** Strictly: any feature used to predict an event at $t$ must be computable from data available at $t$. A feature that accidentally references $t + 1$ data is the classic "forward-looking" leak.
- **Features for the secondary.** Meta-labeling features can include regime tags (from the GEX pipeline), trailing hit rates of the primary, vol regime, time-of-day, day-of-week — things that describe when the primary works vs fails.

## What you can now reason about

- Why "predict tomorrow's close" is not the right framing for an actually-tradeable ML model — it ignores decision structure, path dependence, and gives near-zero signal-to-noise.
- Why labeling events rather than bars aligns ML with the trading decisions that actually matter.
- The new problems triple-barrier introduces (label overlap, sample non-uniqueness) and why the rest of the AFML toolkit (purging, sequential bootstrap, meta-labeling) exists to address them.

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
