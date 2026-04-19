---
title: "The options contract"
prereqs: "Random walks and the null model"
arrives_at: "a right, not an obligation, with a payoff diagram you can draw on paper"
code_ref: "—"
---

# The options contract

Before the Greeks, before Black-Scholes, there is the contract itself. An option is a simple legal object that, once you see clearly, makes the rest of this curriculum almost inevitable.

## The definition

An **option** is a contract that gives its *holder* the right — but not the obligation — to buy or sell a specific asset at a specific price by a specific date.

Four pieces. Memorize them.

| Term | Meaning |
|------|---------|
| **Underlying** | The asset the contract references (a stock, ETF, index, commodity). |
| **Strike** $K$ | The agreed transaction price. |
| **Expiry** $T$ | The date the right lapses. |
| **Premium** | The price the buyer pays the seller upfront for the contract itself. |

Two flavors:

- A **call option** gives the right to *buy* the underlying at $K$.
- A **put option** gives the right to *sell* the underlying at $K$.

And two sides of every contract: the **holder** (who paid the premium and owns the right) and the **writer** or **seller** (who received the premium and carries the obligation). The asymmetry is the whole game. The holder can walk away; the writer cannot.

## "Right, not obligation" is load-bearing

This single phrase is why options have the properties they do. A holder who owns the right to buy at $K = \$100$ will:

- Exercise if the underlying is above $\$100$ at expiry (buy at $\$100$, sell at market, pocket the spread).
- **Not exercise** if the underlying is below $\$100$ (no point buying at $\$100$ what you can buy cheaper in the open market).

The holder's worst case at expiry is "I don't exercise and I lose the premium I already paid." The holder's loss is capped at the premium. The writer, having sold the right, faces the mirror: their best case is "the holder doesn't exercise, and I keep the premium." Their potential loss — if the holder exercises — is not capped.

This asymmetry means **options always have non-negative value**: the right to do something valuable plus the right to walk away is worth at least zero. A contract with zero expected value (deep OTM, near expiry) might trade for a few cents, but it won't trade negative. You cannot pay someone to take a right off your hands.

## Payoff at expiry

At the moment of expiry, all the complications (time value, implied vol, hedging) evaporate. The payoff is purely mechanical.

**Long call** on an underlying trading at $S_T$, struck at $K$:

$$
\text{Payoff}_\text{call} = \max(S_T - K, 0).
$$

If $S_T > K$, you exercise; profit is $S_T - K$. If $S_T \le K$, you don't; profit is zero. Subtract the premium you paid to get your net P&L.

**Long put:**

$$
\text{Payoff}_\text{put} = \max(K - S_T, 0).
$$

Symmetric: if $S_T < K$, you exercise; profit is $K - S_T$. Otherwise zero.

**Short call** (you wrote it):

$$
\text{Payoff}_\text{short call} = -\max(S_T - K, 0).
$$

Unbounded loss if the underlying runs up. This is why naked short calls are considered among the most dangerous positions in standard options trading.

**Short put:**

$$
\text{Payoff}_\text{short put} = -\max(K - S_T, 0).
$$

Loss capped at $K$ (a stock can go to zero but not negative), but the loss can be large. Selling puts is equivalent to agreeing to buy the stock at $K$ regardless of how far it has fallen.

If you draw these on paper — payoff on the y-axis, $S_T$ on the x-axis — the shapes are the iconic "hockey sticks" that appear in every options textbook. They are worth drawing by hand once. The geometry of more complex positions (spreads, straddles, butterflies) is sums and differences of these four shapes.

## Intrinsic value and time value

At any moment *before* expiry, an option trades at some premium $P$. That premium decomposes into two parts:

$$
P = \underbrace{\max(S_t - K, 0)}_{\text{intrinsic}} + \underbrace{P - \text{intrinsic}}_{\text{time value}} \qquad \text{(for a call).}
$$

**Intrinsic value** is what you'd get by exercising immediately (ignoring the option premium you paid). If the call is ITM, intrinsic value is positive; if OTM or ATM, it's zero.

**Time value** is everything else. It reflects the possibility that between now and expiry, the underlying might move favorably — that remaining optionality has positive expected value. Time value is largest for ATM options (where the next move matters most) and decays to zero at expiry, fastest in the final days. That decay is **theta**, covered in Part 3.

A call that is $10$% ITM with a month to expiry might trade at a premium of $\$11$ when its intrinsic value is $\$10$: $\$10$ intrinsic plus $\$1$ time value. Let the same position sit until expiry day, and the time value collapses to zero. If the underlying hasn't moved, the option trades for $\$10$ — pure intrinsic.

## Moneyness and leverage

"Moneyness" describes where the strike sits relative to the underlying:

- **ITM** (in the money): a call with $S > K$ or a put with $S < K$. Intrinsic value is positive.
- **ATM** (at the money): $S \approx K$. Maximum time value, maximum gamma (Part 3).
- **OTM** (out of the money): a call with $S < K$ or a put with $S > K$. Intrinsic value is zero; all premium is time value.

OTM options are cheap because their payoff requires a move. A $\$2$ OTM call on a $\$100$ stock needs a nearly 10% move to be ITM by expiry. If that move happens, the option might 10x. If it doesn't, you lose the $\$2$ in full. **OTM options have high leverage and a high probability of total loss.** This asymmetry is what attracts speculators and what makes naked-short OTM options profitable *on average* and punishing *occasionally* — the variance-risk-premium story covered in [Part 4](../vol-surface/implied-vol.md).

## American vs European, cash vs physical

Two mechanical features vary across option markets:

- **American options** can be exercised any time before expiry. Single-name U.S. equity options (AAPL, TSLA) are American.
- **European options** can only be exercised at expiry. Cash-settled index options (SPX) are European.

Why it matters: European options are easier to price (Black-Scholes gives a closed form). American options add the complexity of an optimal-exercise decision — when should you exercise early? For most calls on non-dividend-paying stocks, the answer is "never" — you give up time value by exercising early and gain nothing. For puts and for calls on dividend-paying stocks, early exercise is sometimes optimal. The distinction appears as a pricing premium (American ≥ European of the same strike/expiry) that's often small in practice.

**Settlement** is whether you actually receive or deliver the underlying (physical) or just exchange cash for the economic value (cash). Single-name equity options are physical; you get or deliver shares on exercise. Index options are cash-settled; nobody delivers 500 baskets of S&P stocks. For pricing and hedging, this is usually a footnote, but it becomes real around ex-dividend dates and corporate actions.

## What this sets up

Everything in this curriculum about options pricing reduces to one question: given what we know about the underlying (its price, volatility, the time left, the risk-free rate), what is a fair premium for this specific payoff? The payoffs above are all the model has to produce at expiry. The rest of Part 2 is about finding a price today that is consistent with them.

- [Payoffs and put-call parity](payoffs-and-parity.md) — the no-arbitrage equation linking calls, puts, stock, and cash. Fully model-free.
- [Black-Scholes as a bridge](black-scholes.md) — a closed-form premium under the GBM assumption from Part 1.

## What you can now reason about

- Why every option has a non-negative premium: the right to do something plus the right to walk away is worth at least zero.
- Why deeper-OTM options are cheaper in absolute terms but have higher leverage to the moves that matter — and why the same feature makes them likely to expire worthless.
- The distinction between intrinsic and time value, and why time value is concentrated near ATM and collapses fastest near expiry (foreshadowing theta).

## Implemented at

The trading project does not price options from scratch — it consumes quoted premiums and uses them to compute Greeks via `trading/packages/gex/src/gex/greeks.py`. The contract mechanics above are what those quotes represent. Future lessons will trace a quoted premium → implied vol → Greeks → dealer positioning, the full pipeline that the GEX package implements.

---

**Next:** [Payoffs and put-call parity →](payoffs-and-parity.md)
