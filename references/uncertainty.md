# Uncertainty — when a difference is yours to claim

This skill already refuses to invent a number. This file is the other half: it refuses to
**assert a difference the data cannot carry.**

A report that says "direct 13.5% vs brokered 86.5%" is stating an arithmetic fact. A report that
says "the direct share is rising" is making a claim about a population from a sample of it, and a
claim needs an interval. Most reports slide from the first sentence to the second without noticing.

---

## The rule

> **A comparison shipped without a denominator and an interval is a claim you did not earn.**

Concretely, three things must be on the page before a difference is described as real:

1. **The denominator.** 13.5% *of what*, counted how, over what window.
2. **An interval**, or an explicit statement that one could not be computed and why.
3. **The reference** the difference is measured against — the pooled value, the previous period,
   zero. A difference is always *from something*.

If you cannot supply all three, describe the magnitude and stop. "Direct sales are 324 of 2,453
transactions (13.2%)" is always safe. "Direct sales are rising" needs the rest.

---

## What to compute, cheapest first

### A share of a count → **Wilson interval**

The shell ships it. Use it whenever a report quotes a percentage of a countable base.

```js
var w = R.wilson(324, 2453);        // k successes, n trials, z defaults to 1.96 (95%)
// -> { p: 0.1321, lo: 0.1193, hi: 0.1461, n: 2453, k: 324 }
```

Why Wilson and not `p ± 1.96·√(p(1−p)/n)`: the textbook interval collapses to zero width as `p`
approaches 0 or 1 and can run past the ends of the scale. A share of 8 out of 2,453 gets an
honest interval from Wilson and a nonsense one from the normal approximation. Three lines, no
simulation, no library.

**n is the number of independent observations, not the number of rows you happen to have.** If one
buyer made forty of the trades, n is not forty.

### A median, a mean, a ratio of sums → **bootstrap, at build time**

There is no closed form worth trusting for a median of a skewed distribution. Resample with
replacement, recompute the statistic, take the 2.5th and 97.5th percentiles.

```python
import random, statistics as st
def boot_ci(values, stat=st.median, iters=2000, seed=0):
    rnd = random.Random(seed)                  # seed it: a report must rebuild identically
    n = len(values)
    dist = sorted(stat([values[rnd.randrange(n)] for _ in range(n)]) for _ in range(iters))
    return dist[int(.025*iters)], dist[int(.975*iters)]
```

**Do this in the query or the build script, not in the browser.** Embed `lo` and `hi` beside the
point value. A report is a document; it should not be running two thousand resamples on the
reader's phone, and the raw values usually do not belong in the file anyway.

### Spread that outliers cannot move → **MAD**

When a report says "typical", quote the median with the **median absolute deviation**, not the
standard deviation. One sale ten times the median moves a standard deviation and leaves a MAD alone.

```
MAD = median(|xᵢ − median(x)|)          robust σ ≈ 1.4826 × MAD
```

### A trend → say the slope, or say nothing

A line going up is not a trend claim. If you want one, fit it and report the slope **with its
interval and its unit** ("+1.4 transactions/month, 95% CI +0.6 … +2.2"). If the series has fewer
than about a dozen points, or the last period is still filling up, do not fit at all — annotate and
move on.

---

## Drawing it: `VIZ.interval`

```js
VIZ.interval(canvas, {
  rows: fn, label:'k', value:'p', lo:'lo', hi:'hi',
  ref: 13.2, refLabel: 'pooled',        // the line a band either clears or does not
  format: v => v.toFixed(1) + '%'
});
```

The factory encodes exactly one judgement and nothing more: **a band that covers `ref` is drawn
muted.** It is not distinguishable from the reference, and the tooltip says so in words. A band
entirely on one side takes the direction colour — and the value is printed either way, so the
direction is never carried by colour alone.

What it deliberately does **not** do: p-values, significance stars, or any "✓ significant" badge.
An interval shows the reader the size of what is not known. A star hides it behind a threshold
somebody else chose.

## Drawing it: `VIZ.concentration`

The other half of "advanced" is usually not inference at all — it is that **a handful of things
account for almost everything**, and a report says so in prose while the chart shows a ranking.

```js
VIZ.concentration(canvas, { rows: fn, value:'v', label:'k', marks:[10,20,50] });
```

Entities sorted largest first; the curve is cumulative share of the total against cumulative share
of the entities, with a dashed diagonal for "even split". The called-out marks read as the sentence
you were going to write anyway: *the top 10% hold 51%*.

**Gini is not computed, on purpose.** One number for a whole shape invites comparison between
populations of different sizes and different tail behaviour, and the comparison is rarely valid.
The top-k share is bounded, interpretable, and says what it means.

---

## Do not

- **A significance star, a p-value, or the word "significant."** Show the interval.
- **An interval on a convenience sample described as if it were a sample.** Billing rows are a
  census of the billing account, not a sample of anything; a Wilson interval on them is theatre.
  When the data *is* the whole population, say so and drop the interval entirely.
- **Comparing two intervals by eye and concluding.** Overlapping intervals do not imply no
  difference. Non-overlap does imply one. Say only what the picture supports.
- **An interval whose method is not in the methodology.** Which statistic, which method, how many
  resamples, what seed.
- **Bootstrapping in the browser.** Build time, seeded, embedded.
