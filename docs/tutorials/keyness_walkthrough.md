# Keywords and lockwords

This tutorial walks through a focus-versus-reference keyness comparison: how
keywords and lockwords are defined, how to read the measures, and how to keep a
result reproducible. It uses the bundled demo corpora (a small climate-discourse
focus corpus and a finance-discourse reference corpus).

## The keyword procedure

A **keyword** is a type used markedly more (positive) or less (negative) in a
focus corpus *C* than in a reference corpus *R*. A **lockword** is a type used
with *comparable* frequency in both — the stable vocabulary the two corpora
share. keyflux follows the corpus-linguistic convention (Brezina 2018, Ch. 3):

1. **Significance** comes from the log-likelihood (Dunning 1993). keyflux flags
   it against the chi-square critical values at 1 d.f.: 3.84 (p<0.05), 6.63
   (p<0.01), 10.83 (p<0.001), 15.13 (p<0.0001).
2. **Sorting** uses an effect size — the log ratio — because in large corpora
   the log-likelihood flags far too many keywords to rank usefully.

## Build a comparison

```python
from keyflux import Keyness
from keyflux.datasets import load_demo_pair

focus, reference = load_demo_pair()
k = Keyness(focus, reference, measure="log_likelihood",
            min_focus_freq=1, min_reference_freq=1, reference_id="finance")
```

## Read the keywords

```python
keywords = k.keywords(top=20)

for row in keywords.positive(5):
    print(row.type, round(row.effect_size, 2), row.significance)
# climate    6.37  p0001
# carbon     5.79  p0001
# emissions  5.23  p0001
```

`positive()` is sorted by effect size (largest first); `negative()` lists the
reference-leaning keywords (most negative first). Each `KeynessRow` carries the
counts, per-million relative frequencies, the chosen measure's `score`, the
`effect_size` (always the log ratio), the `significance` band, the raw
`statistic` (log-likelihood), and the `direction`.

## Read the lockwords

```python
for row in k.lockwords(max_abs_log_ratio=0.5, min_freq_both=5):
    print(row.type)
# the
# of
# and
# to
# global
# policy
```

Lockwords must be (i) **not** significant, (ii) near parity (small absolute log
ratio), and (iii) frequent in **both** corpora — they are stable, frequent words,
not rare noise. They are disjoint from keywords by construction.

## Choosing a measure

`measure=` sets each row's `score`. The effect size and significance are always
the log ratio and the log-likelihood, so keyword ranking is measure-independent;
`measure` only changes the headline number you read.

| measure | what it reports |
|---|---|
| `log_likelihood` | Dunning's G2 (significance, also the score) |
| `log_ratio` | log2 relative-frequency ratio (the effect size) |
| `simple_maths` | Kilgarriff's `(rpm_C + k) / (rpm_R + k)`, `k` filters low frequencies |
| `percent_diff` | Gabrielatos & Marchi's `%DIFF` |
| `chi_square` | for contrast only — it overestimates rare-event significance |

## Absent words and cutoffs

A word frequent in one corpus and absent from the other is the recurring hard
case: *absence of evidence is not evidence of absence*. keyflux does not promote
under-evidenced absent words to keywords — a type enters the scored table only
when it meets the minimum frequency in at least one corpus
(`min_focus_freq`, `min_reference_freq`). Raise these cutoffs to demand more
evidence.

## Reproducibility

Three parameters govern any keyness result — the reference corpus, the
minimum-frequency cutoffs, and the measure. keyflux emits them (plus corpus
totals and version) with every result:

```python
keywords.repro.to_dict()
```

## Symmetry

Swapping focus and reference (with equal cutoffs) flips positive and negative
keywords and leaves the lockwords unchanged — a useful sanity check:

```python
forward = Keyness(focus, reference, min_focus_freq=1, min_reference_freq=1)
backward = Keyness(reference, focus, min_focus_freq=1, min_reference_freq=1)
{r.type for r in forward.keywords().positive()} == \
    {r.type for r in backward.keywords().negative()}   # True
```
