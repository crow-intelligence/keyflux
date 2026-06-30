# Quickstart

From a clean install to an allotaxonograph in one sitting. Every snippet is
runnable as-is.

## Installation

```bash
uv add keyflux
```

keyflux is pure Python — it renders figures with matplotlib and needs no
JavaScript runtime. Its only dependencies are `numpy` and `matplotlib`.

## 1. Count two corpora

keyflux compares two frequency tables (`collections.Counter`). You can build
them from raw text with the bundled helpers, or pass your own counts (for real
linguistic tokenisation, pre-tokenise — for example with `kenon.Tokenizer` — and
pass the resulting `Counter`).

```python
from keyflux import counts_from_text

focus = counts_from_text("the climate report warns that carbon emissions rise")
reference = counts_from_text("the market rallied as the stock index climbed")
```

## 2. Keyness: keywords and lockwords

```python
from keyflux import Keyness

k = Keyness(focus, reference, measure="log_likelihood",
            min_focus_freq=1, min_reference_freq=1)

keywords = k.keywords(top=20)
keywords.positive(10)   # over-represented in the focus corpus
keywords.negative(10)   # over-represented in the reference corpus
k.lockwords()           # comparable frequency in both (the stable zone)
```

The log-likelihood decides significance (against the chi-square thresholds
3.84 / 6.63 / 10.83 / 15.13); the log ratio is the effect size used to rank
keywords. Every result carries a reproducibility record:

```python
keywords.repro.to_dict()
# {'reference_id': 'reference', 'measure': 'log_likelihood',
#  'min_focus_freq': 1, ...}
```

## 3. Rank-turbulence divergence

```python
from keyflux import RankedList, rtd

r1 = RankedList.from_counts(focus, label="2019")
r2 = RankedList.from_counts(reference, label="2024")

result = rtd(r1, r2, alpha=1/3)
result.divergence        # scalar in [0, 1]
result.contributions[:5] # which types drove the shift, and which way
```

`alpha` tunes what you see: small `alpha` surfaces churn among rare, low-rank
words; large `alpha` surfaces shifts among common words. The default `1/3` is the
Dodds et al. recommendation for text. At `alpha=0` keyflux uses the logarithmic
limit, so there is no division by zero.

## 4. Allotaxonograph

```python
from keyflux import allotaxonograph

fig = allotaxonograph(r1, r2, alpha=1/3, labels=("2019", "2024"))
fig.savefig("allotaxonograph.png")   # or display inline in Jupyter
```

`allotaxonograph` returns a matplotlib `Figure` and never calls `show()`, so it
displays inline in a notebook and saves cleanly from a script.

## Next steps

- [Keyword and lockword tutorial](tutorials/keyness_walkthrough.md)
- [RTD and allotaxonograph tutorial](tutorials/rtd_allotaxonograph.md)
- [Two views of one comparison](tutorials/two_views.md) — lockwords = diagonal,
  keywords = off-diagonal
