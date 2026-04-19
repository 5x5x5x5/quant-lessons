---
title: "The labeling problem"
prereqs: "Returns, compounding, log-returns; Random walks and the null model"
arrives_at: "why financial ML can't use iid-time-series labels, and what the alternative looks like"
code_ref: "—"
---

# The labeling problem

> **Status:** Draft pending.

**Scope:** Supervised ML needs labels. The naive approach — "label each day with sign(return)" — fails in multiple directions: labels are noisy near zero, don't encode magnitude, don't correspond to a tradable decision, and create autocorrelated samples that naive CV can't handle. A "fixed horizon return" label ignores the fact that actual traders use stop-losses and profit-takes with a time cap. This is the motivation for **triple-barrier labels** in the next lesson.

**You'll be able to reason about:**

- Why "predict tomorrow's close" is the wrong framing — there's no decision behind the label.
- How trader intuition (target + stop + time cap) translates into labels that respect path dependence.
- Why label overlap forces **sample weighting** (sequential bootstrap) and **CV purging**, covered in earlier lessons and in the `afml.bootstrap` / `afml.cv` modules.

**Implemented at:** — (the motivation; the fix lives in the next lesson's code.)

---

**Next:** [Triple-barrier labeling →](triple-barrier.md)
