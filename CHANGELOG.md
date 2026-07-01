# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-07-01

### Added

- `allotaxonometer` — the full Dodds (2020) diamond allotaxonograph: a
  rotated-square rank-rank histogram (log color scale) with iso-divergence
  contours, log-rank edge axes, exclusive edge strips, and a wordshift + balance
  panel. Complements the existing two-panel `allotaxonograph`, which is unchanged.
- `RankedList.from_scores` — rank types by any numeric score (keyness score, log
  ratio, …), so keyword rankings, "frequent words vs keywords", and other
  non-frequency comparisons are first-class inputs to `rtd`/`allotaxonometer`.
- Presidential-speech gallery: diamond figures and a frequency-vs-keyness diamond;
  README research note on comparing many rankings.

## [0.1.2] - 2026-07-01

### Fixed

- `keyflux.__version__` is now read from the installed package metadata
  (`importlib.metadata`) instead of a hardcoded string, so it always matches the
  release (0.1.1's `__version__` incorrectly reported `0.1.0`). This also fixes
  the version recorded in `ReproRecord`.

## [0.1.1] - 2026-07-01

### Added

- Presidential-speech allotaxonograph gallery: `examples/presidential_speeches.py`
  (+ executed notebook and saved figures under `examples/gallery/`) comparing
  U.S. presidential speech vocabulary across eras, with a matching docs page.
- PNG logo (`imgs/logo.png`) so the README logo renders on PyPI.

## [0.1.0] - 2026-06-30

### Added

- Project scaffold: packaging (`uv_build`), tooling (ruff, ty, pytest with
  `--doctest-modules`), docs (mkdocs-material), and CI.
- **Keyness**: `Keyness` with positive/negative keywords, lockwords, and a
  `ReproRecord`; pure-function measures (`log_likelihood`, `log_ratio`,
  `simple_maths`, `percent_diff`, `chi_square`, `significance_band`) validated
  against Brezina Ch. 3; `classify` helpers; `io.corpus` Counter builders.
- **Ranking + divergence**: `RankedList` (average ties, tied-last exclusives via
  `aligned`) and `rtd` (rank-turbulence divergence with the `alpha -> 0` log
  limit), reproducing the jkbren reference value at `alpha=1.0`.
- **Visualization**: `allotaxonograph` — a two-panel matplotlib figure (diamond
  rank-rank histogram + contribution balance), returning a `Figure`, no JS runtime.
- **Datasets**: bundled demo corpus pair and the jkbren regression fixture.
- Documentation (quickstart, tutorials, troubleshooting, API reference) and
  runnable example scripts.
