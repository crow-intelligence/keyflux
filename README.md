# keyflux

Corpus keyness, rank-turbulence divergence, and allotaxonographs — in pure Python.

keyflux owns the whole comparison arc that diachronic and comparative discourse
analysis usually splits across tools and languages. It derives **keywords** and
**lockwords** from a focus-versus-reference comparison using proper corpus-linguistic
measures (log-likelihood for significance, log ratio for effect size — not just
chi-square), compares the resulting ranked lists with **rank-turbulence divergence
(RTD)**, and renders the **allotaxonograph**: the rank-rank map plus the ranked list
of which exact words drove the shift. No JavaScript runtime — figures are matplotlib.

It replaces the usual "Jaccard overlap on the top-N keywords" summary — one opaque
number that throws away rank, everything below the cutoff, and any account of *which*
words moved — with a transparent, pip-installable pipeline.

## Installation

```bash
uv add keyflux
```

## Quickstart

```python
from collections import Counter

from keyflux import Keyness, RankedList, rtd, allotaxonograph

# 1. Keyness: focus vs reference
focus = Counter({"climate": 30, "carbon": 12, "the": 80, "policy": 9})
reference = Counter({"climate": 3, "carbon": 1, "the": 78, "market": 15})
k = Keyness(focus, reference, measure="log_likelihood")
keywords = k.keywords(top=20)
lockwords = k.lockwords()

# 2. Rank-turbulence divergence between two ranked lists
r1 = RankedList.from_counts(focus, label="2019")
r2 = RankedList.from_counts(reference, label="2024")
result = rtd(r1, r2, alpha=1 / 3)
print(result.divergence)

# 3. Allotaxonograph (returns a matplotlib Figure)
fig = allotaxonograph(r1, r2, alpha=1 / 3, labels=("2019", "2024"))
fig.savefig("allotaxonograph.png")
```

## Features

- **Keyness measures**: log-likelihood (Dunning), log ratio, Simple Maths, %DIFF, and
  chi-square (for contrast) — significance flagged against the chi-square thresholds
- **Keywords and lockwords**: positive / negative keywords plus the stable lockword zone
- **Rank-turbulence divergence**: tunable, rank-sensitive corpus comparison with
  per-type contributions and an explicit alpha-to-zero log limit
- **Allotaxonograph**: publication-quality two-panel matplotlib figure, no JS runtime
- **Reproducibility records**: every keyness result emits its reference, cutoffs, and measure

## Documentation

Full documentation — quickstart, the keyness and allotaxonograph tutorials,
troubleshooting, and the complete API reference — is at
[keyflux.readthedocs.io](https://keyflux.readthedocs.io). The sources live in `docs/`.

## Made by

keyflux is made by [Crow Intelligence](https://crowintelligence.org/).

## License

MIT
