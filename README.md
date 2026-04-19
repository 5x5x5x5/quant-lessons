# quant-lessons

A curriculum from first principles to the primitives behind the [trading](https://github.com/5x5x5x5/trading) project. Each lesson arrives at something concrete — a metric, an instrument, or a specific piece of code you can open and run.

**Site:** https://5x5x5x5.github.io/quant-lessons/

## Local development

```bash
uv sync
uv run mkdocs serve  # live reload at localhost:8000
```

## Deploy

Pushes to `main` trigger `.github/workflows/deploy.yml`, which runs `mkdocs gh-deploy --force` and publishes to the `gh-pages` branch.

## Structure

Lessons are organized into 8 parts. The intended reading order is the nav order. Each lesson's frontmatter declares its prerequisites and what it *arrives at* — the concrete thing you can reason about by the end.
