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
- **Rank-turbulence divergence**: tunable, rank-sensitive comparison of *any* two
  rankings (frequency, keyness score, …) with per-type contributions and an
  explicit alpha-to-zero log limit
- **Allotaxonographs**: a two-panel view (`allotaxonograph`) and the full Dodds
  (2020) **diamond** (`allotaxonometer`) — rank-rank histogram, iso-divergence
  contours, wordshift — publication-quality matplotlib, no JS runtime
- **Reproducibility records**: every keyness result emits its reference, cutoffs, and measure

## Documentation

Full documentation — quickstart, the keyness and allotaxonograph tutorials,
troubleshooting, and the complete API reference — is at
[keyflux.readthedocs.io](https://keyflux.readthedocs.io). The sources live in `docs/`.

## Research direction: comparing many rankings

Rank-turbulence divergence and the allotaxonograph are **pairwise** — they compare
two rankings at a time. This is true of the whole allotaxonometry line, including
the 2025 tooling suite ([arXiv:2506.21808](https://arxiv.org/abs/2506.21808)). But
the questions we care about are often *many*-way: how does presidential vocabulary
drift across **all eleven** eras at once? Which of a dozen speaker groups is the
outlier? Comparing many rankings simultaneously is an open problem we intend to
research and, eventually, support.

The nearest existing framework is **rank aggregation** — finding a consensus
ranking that best agrees with a set of input rankings. The classic formulation is
the **Kemeny median** (minimise total pairwise disagreement), which is NP-hard,
with squared-distance and set-wise / k-wise generalisations
([Kemeny aggregation](https://arxiv.org/abs/1402.5259);
[squared Kemeny](https://arxiv.org/html/2404.08474v1);
[set-wise Kemeny](https://www.sciencedirect.com/science/article/abs/pii/S030439752100414X)).
Candidate directions for keyflux: a **pairwise RTD matrix** (all-pairs divergence
+ clustering/MDS of systems), **consensus-vs-each** allotaxonographs (compare every
ranking against an aggregate), and **time-series flipbooks** of successive
allotaxonographs. If you work on this, we'd love to hear from you.

## Roadmap

Planned for the next iteration. The robustness items are analysed in detail in
[`PRE-MORTEM.md`](PRE-MORTEM.md), and the open modelling choices are listed in
[`CHANGES_SUMMARY.md`](CHANGES_SUMMARY.md).

**Robustness / API decisions**

- [ ] Revisit the zero-cell floor default (0.5): it sets the effect size of every exclusive keyword and reorders the top of the list.
- [ ] Decide whether `min_focus_freq` / `min_reference_freq` should default asymmetrically (keep focus-exclusive keywords while demanding more reference evidence).
- [ ] Add Cohen's *d* (dispersion-aware effect size) once the corpus input can carry sub-corpus structure.

**Proposed features**

- [x] Rank by any score, not just frequency (`RankedList.from_scores`) — compare keyword rankings, keyness scores, or any metric.
- [ ] Comparing many rankings at once — see [Research direction](#research-direction-comparing-many-rankings) above.
- [ ] Optional self-contained interactive HTML+JS allotaxonograph export (an alpha slider), gated behind an extra so the core stays pure Python.

**Maintenance**

- [x] Publish to PyPI and wire up ReadTheDocs.

## Made by

keyflux is made by [Crow Intelligence](https://crowintelligence.org/).

## License

MIT
