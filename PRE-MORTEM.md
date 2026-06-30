# keyflux — pre-mortem

A fragility map of the numerical core: *assume a future incident has happened —
what most likely caused it?* This is a design-review artifact, not a bug list.
Each entry names a failure mode, how it would surface, and a direction. Nothing
here is a confirmed defect; items marked **[needs human decision]** would change
public behaviour and are deliberately **not** changed in this pass.

Scope: read-through of `src/keyflux/` (keyness measures, `Keyness`, `RankedList`,
`rtd`, `allotaxonograph`). The code is in good shape — Google docstrings with
explicit `Contract:` sections, no bare `except`, clean `ty`/`ruff`, and the two
risky numbers (LL = 140.87, RTD = 0.45924793111057804) are pinned by regression
tests. The fragilities below are mostly *semantic* and *operational*.

---

## High-impact fragilities

### 1. The zero-cell floor is a silent modelling choice  *(most important)*
`log_ratio` and `percent_diff` replace a zero count with `floor=0.5` so
exclusives stay finite. The chosen floor directly sets the effect size of every
exclusive (a word in one corpus, absent from the other), and exclusives are
often the most interesting keywords. A different floor reorders the top of the
keyword list. **[needs human decision]** — the default (0.5, the Hardie/CQPweb
convention) is exposed as a parameter and recorded in `ReproRecord.floor`, but
users should know it is a knob, not a fact.

### 2. Simple Maths uses true per-million RF, not absolute frequencies
`simple_maths` follows Brezina's formula 3.6 (relative frequency per million).
Worked textbook examples sometimes plug in absolute frequencies, which agrees
only when both corpora are ~1M tokens. On corpora of very different sizes the two
conventions diverge. Documented in the measure's docstring and in
Troubleshooting; surfaces as "the number doesn't match my textbook."

### 3. RTD normalisation assumes the reference disjoint configuration
`rtd` normalises by the divergence of the maximally disjoint pair, computed
analytically from `N1`, `N2` (the *present* element counts) via the
`N1 + N2/2` reference ranks. `N1`/`N2` are `len(list.counts)` — the number of
positive-count types. If a caller hand-builds a `RankedList` whose `counts`
includes zero entries, `N` is inflated and the normaliser shifts. `from_counts`
never does this, but the dataclass is constructable directly.

### 4. `alpha` continuity across the log-limit branch
`rtd` switches to the closed-form logarithmic limit when `alpha < 1e-10`. The
limit is mathematically exact, and a regression test checks `alpha=0` against
`alpha=1e-7` to ~1e-4. Very small but non-zero `alpha` (e.g. `1e-11`) takes the
log branch; values like `1e-8` take the general branch where `(alpha+1)/alpha`
is large but finite. No NaNs occur in tested ranges, but extreme `alpha` is worth
a property sweep if the public surface ever exposes it without bounds.

---

## Medium fragilities

### 5. Tied counts and rank stability
`average_ranks` sorts by count descending; Python's sort is stable, so the
*order* of equal-count types is input-insertion order, but their *ranks* are all
the tie-group average, so the rank vector is deterministic. Relabelling does not
change any rank. Safe, but the determinism rests on assigning the average (not
the first/last) rank — a mutation here would pass coarse tests and is covered by
the exact-value `test_tied_pair_averaged`.

### 6. `chi_square` guards the impossible-count case but not non-negativity drift
`chi_square` raises when `a > n_focus` (a type cannot exceed the corpus size) but
otherwise trusts inputs. Property tests pin non-negativity. It is documented as
teaching-only; if it were ever used for selection, its rare-event overestimation
(the very thing the package moves beyond) would bite.

### 7. Allotaxonograph readability on tiny vocabularies
The diamond histogram bins log-ranks; on a handful of types the bins are sparse
and the "diamond" reads as scattered cells. This is cosmetic and expected for toy
inputs; real keyword lists fill it in. Not a correctness issue.

---

## What is solid

- The log-likelihood, log ratio, Simple Maths, and %DIFF reproduce Brezina's
  worked `war` numbers to the printed precision.
- RTD reproduces the jkbren reference value to 1e-12 and satisfies identity,
  `[0, 1]` bounds, symmetry, and totality under property tests.
- Tied-last ranking lives in exactly one place (`RankedList.aligned`), so the
  metric and the figure cannot disagree.
- No bare excepts; all corpus-empty / negative-alpha / impossible-count cases
  raise explicit `ValueError`s with messages.
