"""Generate matplotlib figures for the quant-lessons curriculum.

All output goes to docs/assets/figures/ as PNGs. Script is deterministic
(fixed seeds) so regeneration produces identical output.

Run: uv run python scripts/generate_figures.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm

FIG_DIR = Path(__file__).resolve().parents[1] / "docs" / "assets" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams.update(
    {
        "figure.dpi": 120,
        "savefig.dpi": 150,
        "savefig.bbox": "tight",
        "axes.grid": True,
        "grid.alpha": 0.3,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "font.size": 11,
    }
)

INDIGO = "#3F51B5"
PINK = "#E91E63"
GREEN = "#4CAF50"
ORANGE = "#FF9800"
PURPLE = "#9C27B0"
GRAY = "#666666"


def save(fig: plt.Figure, name: str) -> None:
    path = FIG_DIR / f"{name}.png"
    fig.savefig(path)
    plt.close(fig)
    print(f"wrote {path.relative_to(FIG_DIR.parents[2])}")


# ---------- options ---------------------------------------------------------


def payoffs_atomic() -> None:
    fig, axes = plt.subplots(2, 2, figsize=(10, 7))
    S = np.linspace(80, 120, 400)
    K = 100
    c = p = 3.0

    configs = [
        ("Long call", np.maximum(S - K, 0) - c, INDIGO, "upper left"),
        ("Long put", np.maximum(K - S, 0) - p, INDIGO, "upper right"),
        ("Short call", c - np.maximum(S - K, 0), PINK, "lower left"),
        ("Short put", p - np.maximum(K - S, 0), PINK, "lower right"),
    ]
    for ax, (title, payoff, color, loc) in zip(axes.flat, configs, strict=True):
        ax.plot(S, payoff, color=color, linewidth=2)
        ax.axhline(0, color="black", linewidth=0.5)
        ax.axvline(K, color=GRAY, linestyle="--", linewidth=0.7, label=f"strike K={K}")
        ax.fill_between(S, 0, payoff, where=(payoff > 0), alpha=0.15, color=GREEN)
        ax.fill_between(S, 0, payoff, where=(payoff < 0), alpha=0.15, color=PINK)
        ax.set_title(title)
        ax.set_xlabel("$S_T$")
        ax.set_ylabel("payoff at expiry")
        ax.legend(loc=loc, fontsize=9)
    fig.suptitle("The four atomic option payoffs (net of premium)", fontsize=13, y=1.02)
    fig.tight_layout()
    save(fig, "payoffs_atomic")


def payoffs_composite() -> None:
    fig, axes = plt.subplots(2, 2, figsize=(10, 7))
    S = np.linspace(80, 120, 400)

    # Bull call spread: long K1=95, short K2=105
    K1, K2 = 95, 105
    bull = np.maximum(S - K1, 0) - np.maximum(S - K2, 0) - 4.0

    # Long straddle
    Kstr = 100
    straddle = np.abs(S - Kstr) - 6.0

    # Long strangle
    strangle = np.maximum(K1 - S, 0) + np.maximum(S - K2, 0) - 4.0

    # Risk reversal: long K2 call, short K1 put
    risk_rev = np.maximum(S - K2, 0) - np.maximum(K1 - S, 0) - 0.0

    plots = [
        (axes[0, 0], bull, f"Bull call spread (long {K1}C, short {K2}C)", (K1, K2)),
        (axes[0, 1], straddle, f"Long straddle (long {Kstr}C + long {Kstr}P)", (Kstr,)),
        (axes[1, 0], strangle, f"Long strangle (long {K1}P + long {K2}C)", (K1, K2)),
        (axes[1, 1], risk_rev, f"Risk reversal (long {K2}C, short {K1}P)", (K1, K2)),
    ]
    for ax, payoff, title, strikes in plots:
        ax.plot(S, payoff, color=INDIGO, linewidth=2)
        ax.axhline(0, color="black", linewidth=0.5)
        for k in strikes:
            ax.axvline(k, color=GRAY, linestyle="--", linewidth=0.7)
        ax.fill_between(S, 0, payoff, where=(payoff > 0), alpha=0.15, color=GREEN)
        ax.fill_between(S, 0, payoff, where=(payoff < 0), alpha=0.15, color=PINK)
        ax.set_title(title, fontsize=11)
        ax.set_xlabel("$S_T$")
        ax.set_ylabel("payoff at expiry")
    fig.suptitle("Composite option payoffs (net of premium)", fontsize=13, y=1.02)
    fig.tight_layout()
    save(fig, "payoffs_composite")


# ---------- greeks ----------------------------------------------------------


def _bs_d1(S, K, r, sigma, T):
    return (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))


def _bs_delta_call(S, K, r, sigma, T):
    return norm.cdf(_bs_d1(S, K, r, sigma, T))


def _bs_gamma(S, K, r, sigma, T):
    d1 = _bs_d1(S, K, r, sigma, T)
    return norm.pdf(d1) / (S * sigma * np.sqrt(T))


def _tenor_plot(compute, ylabel, title, fname, legend_loc):
    fig, ax = plt.subplots(figsize=(9, 5))
    S = np.linspace(70, 130, 400)
    K, r, sigma = 100, 0.04, 0.20
    tenors = [
        ("7 days", 7 / 365),
        ("30 days", 30 / 365),
        ("90 days", 90 / 365),
        ("1 year", 1.0),
    ]
    colors = [PINK, ORANGE, GREEN, INDIGO]
    for (label, T), color in zip(tenors, colors, strict=True):
        ax.plot(S, compute(S, K, r, sigma, T), color=color, linewidth=2, label=label)
    ax.axvline(K, color=GRAY, linestyle="--", linewidth=0.7, label=f"strike K={K}")
    ax.set_xlabel("spot $S$")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(loc=legend_loc)
    save(fig, fname)


def delta_curves() -> None:
    _tenor_plot(
        _bs_delta_call,
        r"call $\Delta$",
        r"Call delta vs spot at different tenors ($\sigma=20\%$, $r=4\%$)",
        "delta_curves",
        "lower right",
    )


def gamma_curves() -> None:
    _tenor_plot(
        _bs_gamma,
        r"$\Gamma$ (per share per dollar of spot)",
        r"Gamma vs spot at different tenors ($\sigma=20\%$, $r=4\%$)",
        "gamma_curves",
        "upper right",
    )


# ---------- vol surface -----------------------------------------------------


def term_structure() -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    tenors_days = np.array([7, 14, 30, 60, 90, 120, 180, 270, 365])
    contango = np.array([14.0, 14.5, 15.5, 16.5, 17.2, 17.7, 18.3, 18.8, 19.2])
    backwardation = np.array([42.0, 38.0, 32.0, 28.0, 26.0, 25.0, 24.0, 23.5, 23.0])
    ax.plot(
        tenors_days,
        contango,
        color=INDIGO,
        linewidth=2,
        marker="o",
        label="Contango (quiet market)",
    )
    ax.plot(
        tenors_days,
        backwardation,
        color=PINK,
        linewidth=2,
        marker="s",
        label="Backwardation (crisis)",
    )
    ax.set_xlabel("days to expiry")
    ax.set_ylabel("implied vol (%)")
    ax.set_title("Term structure of IV: contango vs backwardation")
    ax.legend()
    ax.set_xscale("log")
    ax.set_xticks(tenors_days)
    ax.set_xticklabels(tenors_days)
    save(fig, "term_structure")


def skew_and_smile() -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    moneyness = np.linspace(0.85, 1.15, 200)
    equity_skew = 0.25 - 0.30 * (moneyness - 1.0) + 0.15 * (moneyness - 1.0) ** 2
    single_smile = 0.30 + 2.0 * (moneyness - 1.0) ** 2
    ax.plot(
        moneyness,
        equity_skew * 100,
        color=INDIGO,
        linewidth=2,
        label="Equity index (skew)",
    )
    ax.plot(
        moneyness,
        single_smile * 100,
        color=PINK,
        linewidth=2,
        label="Single name (smile)",
    )
    ax.axvline(1.0, color=GRAY, linestyle="--", linewidth=0.7, label="ATM")
    ax.set_xlabel("moneyness $K/S$")
    ax.set_ylabel("implied vol (%)")
    ax.set_title("IV across strikes: equity-index skew vs single-name smile")
    ax.legend()
    save(fig, "skew_and_smile")


# ---------- GEX -------------------------------------------------------------


def _synthetic_gex_profile():
    """Deterministic synthetic SPX-like per-strike GEX distribution."""
    spot = 5200
    strikes = np.arange(4800, 5600, 25, dtype=float)
    rng = np.random.default_rng(42)
    gex = np.zeros_like(strikes)
    gex += 3.5 * np.exp(-(((strikes - 5000) / 80.0) ** 2))  # put-heavy below spot
    gex -= 4.5 * np.exp(-(((strikes - 5300) / 80.0) ** 2))  # call-heavy above spot
    gex += rng.normal(0, 0.15, size=len(strikes))
    return spot, strikes, gex


def gex_per_strike() -> None:
    spot, strikes, gex = _synthetic_gex_profile()
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = [INDIGO if g >= 0 else PINK for g in gex]
    ax.bar(strikes, gex, width=20, color=colors, alpha=0.85)
    ax.axhline(0, color="black", linewidth=0.7)
    ax.axvline(spot, color=GRAY, linestyle="--", linewidth=1.2, label=f"spot = {spot}")
    ax.set_xlabel("strike")
    ax.set_ylabel("per-strike GEX ($B per 1% move)")
    ax.set_title("Per-strike GEX profile — typical SPX snapshot shape")
    ax.legend(loc="upper right")
    from matplotlib.patches import Patch

    legend_elems = [
        Patch(facecolor=INDIGO, alpha=0.85, label="positive (dealer long gamma)"),
        Patch(facecolor=PINK, alpha=0.85, label="negative (dealer short gamma)"),
    ]
    ax.legend(
        handles=[*legend_elems, *ax.get_legend().legend_handles],
        loc="upper right",
        fontsize=9,
    )
    save(fig, "gex_per_strike")


def gex_cumulative_flip() -> None:
    spot, strikes, gex = _synthetic_gex_profile()
    cumsum = np.cumsum(gex)

    signs = np.sign(cumsum)
    diffs = np.diff(signs)
    crossings = np.where(diffs != 0)[0]
    if len(crossings) > 0:
        i = crossings[-1]
        c0, c1 = cumsum[i], cumsum[i + 1]
        t = -c0 / (c1 - c0)
        flip = strikes[i] + t * (strikes[i + 1] - strikes[i])
    else:
        flip = None

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(strikes, cumsum, color=INDIGO, linewidth=2)
    ax.fill_between(
        strikes,
        0,
        cumsum,
        where=(cumsum > 0),
        alpha=0.15,
        color=GREEN,
        label="cumulative > 0",
    )
    ax.fill_between(
        strikes,
        0,
        cumsum,
        where=(cumsum < 0),
        alpha=0.15,
        color=PINK,
        label="cumulative < 0",
    )
    ax.axhline(0, color="black", linewidth=0.7)
    ax.axvline(spot, color=GRAY, linestyle="--", linewidth=1.2, label=f"spot = {spot}")
    if flip is not None:
        ax.axvline(
            flip, color=ORANGE, linestyle="-", linewidth=1.8, label=f"flip ≈ {flip:.0f}"
        )
    ax.set_xlabel("strike")
    ax.set_ylabel("cumulative GEX ($B per 1% move)")
    ax.set_title("Cumulative GEX and the gamma-flip strike")
    ax.legend(loc="upper right", fontsize=9)
    save(fig, "gex_cumulative_flip")


# ---------- triple-barrier --------------------------------------------------


def triple_barrier() -> None:
    fig, ax = plt.subplots(figsize=(10, 5.5))
    rng = np.random.default_rng(7)
    p0 = 100.0
    sigma = 1.5
    pt = p0 + 2 * sigma
    sl = p0 - 2 * sigma
    vb = 15

    # Three paths
    path_pt = np.insert(p0 + np.cumsum(rng.normal(0.4, 1.1, 20)), 0, p0)
    path_sl = np.insert(p0 + np.cumsum(rng.normal(-0.4, 1.1, 20)), 0, p0)
    path_v = np.insert(p0 + np.cumsum(rng.normal(0.05, 0.7, 20)), 0, p0)

    # Clip each path at the first barrier hit
    def clip(path):
        for i in range(1, len(path)):
            if i > vb or path[i] >= pt or path[i] <= sl:
                return path[: i + 1], i
        return path, len(path) - 1

    p1, e1 = clip(path_pt)
    p2, e2 = clip(path_sl)
    p3, e3 = clip(path_v)

    # Shade regions
    xs = np.arange(0, vb + 5)
    ax.axhspan(pt, pt + 5, color=GREEN, alpha=0.08)
    ax.axhspan(sl - 5, sl, color=PINK, alpha=0.08)
    ax.axhline(
        pt, color=GREEN, linestyle="--", linewidth=1.3, label=f"PT = p₀ + 2σ = {pt:.1f}"
    )
    ax.axhline(
        sl, color=PINK, linestyle="--", linewidth=1.3, label=f"SL = p₀ - 2σ = {sl:.1f}"
    )
    ax.axvline(
        vb, color=GRAY, linestyle="--", linewidth=1.3, label=f"vertical = {vb} bars"
    )
    ax.axhline(p0, color="black", linewidth=0.5)

    ax.plot(
        range(len(p1)),
        p1,
        color=INDIGO,
        linewidth=1.8,
        label="Path A: label = +1 (PT hit)",
    )
    ax.plot(e1, p1[-1], "o", color=GREEN, markersize=9, zorder=5)

    ax.plot(
        range(len(p2)),
        p2,
        color=ORANGE,
        linewidth=1.8,
        label="Path B: label = −1 (SL hit)",
    )
    ax.plot(e2, p2[-1], "o", color=PINK, markersize=9, zorder=5)

    label_v = "+1" if p3[-1] > p0 else "−1"
    ax.plot(
        range(len(p3)),
        p3,
        color=PURPLE,
        linewidth=1.8,
        label=f"Path C: label = {label_v} (vertical)",
    )
    ax.plot(e3, p3[-1], "o", color=PURPLE, markersize=9, zorder=5)

    ax.set_xlabel("bars from entry")
    ax.set_ylabel("price")
    ax.set_title(f"Triple-barrier labeling — three example paths (entry at {p0:.0f})")
    ax.legend(loc="lower left", fontsize=9)
    ax.set_xlim(-0.5, vb + 4)
    save(fig, "triple_barrier")


# ---------- walk-forward ----------------------------------------------------


def walk_forward_folds() -> None:
    fig, axes = plt.subplots(2, 1, figsize=(10, 5.5), sharex=True)
    n_samples = 30
    initial_train = 10
    test_horizon = 3
    stride = 3

    def draw(ax, expanding):
        anchor = initial_train
        fold_num = 1
        while anchor + test_horizon <= n_samples:
            if expanding:
                train_start = 0
            else:
                train_start = max(0, anchor - initial_train)
            train_end = anchor
            test_start, test_end = anchor, anchor + test_horizon
            y = -fold_num
            ax.barh(
                y,
                train_end - train_start,
                left=train_start,
                height=0.6,
                color=INDIGO,
                alpha=0.75,
                label="train" if fold_num == 1 else None,
            )
            ax.barh(
                y,
                test_end - test_start,
                left=test_start,
                height=0.6,
                color=PINK,
                alpha=0.85,
                label="test" if fold_num == 1 else None,
            )
            ax.text(
                -0.4,
                y,
                f"fold {fold_num}",
                ha="right",
                va="center",
                fontsize=9,
                color=GRAY,
            )
            anchor += stride
            fold_num += 1
        ax.set_yticks([])
        ax.set_xlim(-4, n_samples + 1)
        ax.grid(axis="x", alpha=0.3)
        ax.grid(axis="y", visible=False)

    axes[0].set_title("Expanding train window")
    draw(axes[0], expanding=True)
    axes[0].legend(loc="lower right")

    axes[1].set_title("Sliding (fixed-length) train window")
    draw(axes[1], expanding=False)
    axes[1].set_xlabel("bar index →")

    save(fig, "walk_forward_folds")


if __name__ == "__main__":
    payoffs_atomic()
    payoffs_composite()
    delta_curves()
    gamma_curves()
    term_structure()
    skew_and_smile()
    gex_per_strike()
    gex_cumulative_flip()
    triple_barrier()
    walk_forward_folds()
    print(f"\nAll figures in {FIG_DIR}")
