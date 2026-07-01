# Troubleshooting

## `ValueError: Both corpora must be non-empty to compute keyness`

`Keyness` needs both Counters to have at least one token. Check that your
tokenisation produced counts, and that the focus and reference corpora are not
swapped with an empty placeholder.

## My keyword list is empty

The most common cause is the minimum-frequency cutoff. On small corpora the
defaults (`min_focus_freq=5`, `min_reference_freq=5`) can exclude everything.
Lower them:

```python
Keyness(focus, reference, min_focus_freq=1, min_reference_freq=1)
```

A type enters the scored table only when it clears the minimum in at least one
corpus, so raising the cutoffs is also how you exclude under-evidenced
absent words.

## Too many keywords

On large corpora the log-likelihood flags far too many types as significant —
this is expected (Brezina 2018). Rank by effect size and take the top N:

```python
k.keywords(top=50)        # significance-filtered, sorted by |log ratio|
```

## My lockword list is empty

Lockwords must be frequent in **both** corpora (`min_freq_both`, default 5) and
near parity (`max_abs_log_ratio`, default 0.5). On small corpora, lower
`min_freq_both`:

```python
k.lockwords(min_freq_both=2)
```

## Simple Maths does not match a textbook value

keyflux computes Simple Maths from true relative frequencies per million words
(formula 3.6 in Brezina). Some worked examples plug in absolute frequencies
directly, which is only valid when both corpora are about a million tokens. For
the `war` example, keyflux returns 1.94 (correct per-million) where a textbook may
print 1.96 (absolute-frequency shortcut).

## `rtd` returns 0 for two different corpora

`rtd(x, x)` is 0 by definition. If two genuinely different lists return 0, check
that you did not build both `RankedList`s from the same Counter.

## The allotaxonograph window does not appear

`allotaxonograph` never calls `show()` — it returns a `Figure`. In a script, save
it (`fig.savefig(...)`); in Jupyter, make it the last expression in a cell so the
inline backend renders it.

## Figures fail to render on a headless server

keyflux builds figures with matplotlib's `Figure` API and does not require an
interactive backend, so it works headless out of the box. If you also import
`matplotlib.pyplot` elsewhere, set a non-interactive backend first:

```python
import matplotlib
matplotlib.use("Agg")
```

## Real linguistic tokenisation

keyflux ships only a simple word-character tokeniser, deliberately — it is about
keyness and rank comparison, not tokenisation. For lemmatisation, multi-word
handling, or non-English text, pre-tokenise (for example with `kenon.Tokenizer`)
and pass the resulting `Counter` to `Keyness` and `RankedList.from_counts`.
