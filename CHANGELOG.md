# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
