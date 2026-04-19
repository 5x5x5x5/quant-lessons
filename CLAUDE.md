# quant-lessons — curriculum companion to the trading project

MkDocs Material site deployed to GitHub Pages. Every lesson should arrive at
something concrete: a metric, an instrument, or a specific piece of code in
the sibling [trading](https://github.com/5x5x5x5/trading) project.

## Layout

    docs/
      index.md              Landing
      measurable/           Part 1: returns, vol, random walks
      options/              Part 2: contracts, payoffs, Black-Scholes
      greeks/               Part 3: delta, gamma, theta/vega/rho
      vol-surface/          Part 4: IV, term structure, skew
      regime/               Part 5: MMs, dealer gamma, gamma flip
      backtest/             Part 6: metrics, walk-forward, purging, DSR
      ml/                   Part 7: labeling problem, triple-barrier, meta-label
      flows/                Part 8: microstructure, events, cross-asset
      javascripts/mathjax.js  MathJax config for KaTeX-style math
    mkdocs.yml              nav, theme, extensions
    .github/workflows/deploy.yml  auto-deploy on push to main

## Lesson shape

Every lesson file should:

1. Open with one-sentence intuition, not formalism.
2. Build the concept via examples before equations.
3. Use math with `$...$` or `$$...$$` (rendered by MathJax via `pymdownx.arithmatex`).
4. Close with a section **Implemented at** pointing to the trading-repo
   file path + line (e.g. `trading/packages/afml/src/afml/labeling.py:52`).
5. End with a **Next:** link to the next lesson in reading order.

Stubs use the same skeleton with a "draft pending" note so the site still
builds and navigates.

## Commands

- `uv sync` — install mkdocs-material locally
- `uv run mkdocs serve` — live preview at localhost:8000
- `uv run mkdocs build` — static output in `site/` (gitignored)
- `git push origin main` — triggers GitHub Actions deploy

## Voice

Informed reader who knows calculus and basic probability but hasn't seen
options or financial math. No measure theory. No hand-waving. If a
statement needs "it can be shown", either show it or cut it.
