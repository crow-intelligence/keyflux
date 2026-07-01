<p align="center">
  <img src="https://raw.githubusercontent.com/crow-intelligence/keyflux/main/imgs/logo.png" alt="keyflux logo" width="440">
</p>

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

## Roadmap

Planned for the next iteration. The robustness items are analysed in detail in
[`PRE-MORTEM.md`](PRE-MORTEM.md), and the open modelling choices are listed in
[`CHANGES_SUMMARY.md`](CHANGES_SUMMARY.md).

**Robustness / API decisions**

- [ ] Revisit the zero-cell floor default (0.5): it sets the effect size of every exclusive keyword and reorders the top of the list.
- [ ] Decide whether `min_focus_freq` / `min_reference_freq` should default asymmetrically (keep focus-exclusive keywords while demanding more reference evidence).
- [ ] Add Cohen's *d* (dispersion-aware effect size) once the corpus input can carry sub-corpus structure.

**Proposed features**

- [ ] `RankedList.from_keyness(..., by="score")` — rank by keyness score, not just frequency, so "compare the distinctive-word lists over time" is a one-liner.
- [ ] Optional self-contained interactive HTML+JS allotaxonograph export (an alpha slider), gated behind an extra so the core stays pure Python.

**Maintenance**

- [ ] Publish to PyPI and wire up ReadTheDocs.

## Made by

keyflux is made by [Crow Intelligence](https://crowintelligence.org/).

## License

MIT
