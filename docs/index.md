# keyflux

Corpus keyness, rank-turbulence divergence, and allotaxonographs — in pure Python.

keyflux compares two corpora end to end: it derives **keywords** and **lockwords**
with proper corpus-linguistic measures (log-likelihood for significance, log ratio
for effect size), compares the resulting ranked lists with **rank-turbulence
divergence (RTD)**, and draws the **allotaxonograph** — the rank-rank map paired with
the ranked list of which exact words drove the shift. No JavaScript runtime: figures
render with matplotlib.

## Core concepts

- **Keyness**: focus-vs-reference keywords (positive / negative) and lockwords (stable)
- **Rank-turbulence divergence**: a rank-sensitive, tunable comparison of two ranked lists
- **Allotaxonograph**: the diamond rank-rank histogram plus a contribution-balance list

## Quick links

- [Quickstart](quickstart.md) — clean install to allotaxonograph
- [API Reference](api/measures.md) — every public function and its contract

---

Made by [Crow Intelligence](https://crowintelligence.org/)
