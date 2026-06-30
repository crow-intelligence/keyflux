# keyflux — changes summary

What each phase delivers, and the human-decision points that need a maintainer's
sign-off. Each phase is a feature branch with its own commit; none are merged.

## Per-phase PRs

### Phase 0 — `scaffold`
Project skeleton mirroring the sibling package `kenon`: `uv_build` backend, ruff
(line 88, Google docstrings), `ty`, pytest with `--doctest-modules`,
mkdocs-material, Makefile, MIT licence. Subpackage layout
(`keyness/ranking/divergence/viz/io/datasets`). `papers/` is gitignored. `make
ci` is green on the empty-but-importable package.

### Phase 1 — `keyness`
Pure-function measures (`log_likelihood`, `log_ratio`, `simple_maths`,
`percent_diff`, `chi_square`, `significance_band`) validated against Brezina
Ch. 3's worked `war` example (LL = 140.87, log ratio = 1.20). `Keyness` derives
positive/negative keywords and lockwords with explicit min-frequency cutoffs and
a machine-readable `ReproRecord`. `classify` categorises rows; `io.corpus` builds
Counters; `datasets` ships a tiny demo pair. Swap symmetry, significance
thresholds, and absent-word exclusion are tested.

### Phase 2 — `rtd`
`RankedList` ranks types by frequency with average ties; `aligned()` ranks over
the combined domain so exclusives land at a tied-last average rank (the single
owner of tied-last logic). `rtd` implements Dodds et al. (2020) with the
`1/(alpha+1)` element exponent, `N1 + N2/2` normalisation, and an explicit
`alpha -> 0` logarithmic limit. Reproduces the jkbren reference value
`0.45924793111057804` at `alpha=1.0` to 1e-12. Property tests cover identity,
`[0,1]` bounds, symmetry, and totality. Pure numpy — no scipy.

### Phase 3 — `viz`
`allotaxonograph` returns a matplotlib `Figure` (Figure API directly — no
pyplot, no `show()`) with a diamond rank-rank histogram and a contribution
balance panel, both driven by one `rtd` call. Renders headless, saves via
`savefig`, leaves inputs unmutated. Two runnable example scripts.

### Phase 4 — `quality`
Comprehensive docs (mkdocs strict): quickstart, a keyword/lockword tutorial, an
RTD + allotaxonograph tutorial, the "lockwords = diagonal, keywords =
off-diagonal" side-by-side example, troubleshooting, and an autodoc API
reference. ReadTheDocs config, CI + publish workflows, mutation-testing scope,
and this pre-mortem. Property tests on `rtd` and the measures.

## Human-decision points

These are exposed as parameters with sensible defaults and recorded in the
`ReproRecord` where applicable. They change results and deserve a maintainer's
explicit choice.

| Decision | Default | Where | Notes |
|---|---|---|---|
| Subpackage vs flat layout | subpackages | repo layout | kenon is flat; keyflux's surface is larger |
| Zero-cell floor | `0.5` | `measures.ZERO_CELL_FLOOR` | Hardie/CQPweb convention; sets every exclusive's effect size |
| Simple Maths `k` | `100` | `measures.SMP_DEFAULT_K` | Kilgarriff default; also a frequency filter |
| Min-frequency cutoffs | focus 5, reference 5 | `Keyness(...)` | symmetric so swap-symmetry holds; lower for small corpora |
| Lockword thresholds | `max_ll=3.84`, `max_abs_log_ratio=0.5`, `min_freq_both=5` | `Keyness.lockwords` | not significant, near parity, frequent in both |
| Tied-last rank | averaged tail | `RankedList.aligned` | required to reproduce the jkbren value |
| Default `alpha` | `1/3` | `rtd`, `allotaxonograph` | Dodds et al. text default |
| `log_likelihood` sign | unsigned magnitude | `measures.log_likelihood` | direction stored separately from relative frequencies |
| matplotlib dependency | core | `pyproject.toml` | the public API returns a Figure |

## Validation status

- `make ci` (ruff format + ruff check + `ty` + pytest `--doctest-modules`) green
  on Python 3.12.
- Keyness measures reproduce the `papers/` worked numbers; focus/reference swap
  flips keyword polarity and preserves lockwords.
- `rtd(jkbren, alpha=1.0).divergence == 0.45924793111057804` to 1e-12.
- `mkdocs build --strict` builds with no dead autodoc or snippet targets.
- Quickstart pipeline (text -> Keyness -> RankedList -> rtd -> allotaxonograph)
  runs end to end and saves a figure headless.
