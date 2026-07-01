# Mutation testing summary

Tool: [`mutmut`](https://github.com/boxed/mutmut) 3.x (dev-only; not run in CI).
Run with `KEYFLUX_MUTATION=1 uv run mutmut run` (the env var loads a Hypothesis
profile in `tests/conftest.py` that suppresses the `differing_executors` health
check and disables the example database during parallel mutation runs).

## Scope

Mutation is scoped to the **math-heavy core** and its fast tests (see
`[tool.mutmut]` in `pyproject.toml`):

- mutated: `keyness/measures.py`, `keyness/keyness.py`, `ranking/rankedlist.py`,
  `divergence/rtd.py`
- test selection: `test_measures.py`, `test_keyness.py`, `test_rankedlist.py`,
  `test_rtd.py`

`classify.py`, `io/corpus.py`, `datasets/`, and `viz/allotaxonograph.py` are
**not** mutated — categorisation and plotting are validated by ordinary unit
tests, not per-mutant. This is a deliberate cap, not full coverage.

## Score

| metric | value |
|--------|------:|
| total mutants | 638 |
| killed | 467 |
| killed by timeout | 3 |
| **survived** | **168** |
| **mutation score** | **~74%** (470 / 638) |

The validated numeric kernels are killed: every mutation that changes the
formulas producing the pinned regression numbers (log-likelihood = 140.87, log
ratio = 1.20, RTD = 0.45924793111057804) is caught by the exact-value and
regression tests.

## What survives, and why

Inspecting the survivors, they fall into three benign classes:

1. **Error-message string mutations** — e.g. changing the text or case of
   `"Cannot compute expected counts: both corpora are empty."`. No test asserts
   exact message text, so these survive. Behaviourally equivalent.
2. **Validation-guard boundary mutations** — e.g. `n_focus <= 0 or
   n_reference <= 0` mutated to `and`, or `< 0`. These guard against
   non-positive corpus totals; the public API (`Keyness`, `RankedList`) never
   produces such inputs, so the mutants are unreachable through normal use.
3. **Default-argument and tie-boundary variants** — e.g. `a > 0` vs `a > 1` in
   the `x ln x -> 0` guard, which only differs at a count of exactly 1. The
   `TestDefaultArguments` / `TestLockwordThresholds` / `TestDefaults` classes
   were added this pass to pin the *documented* defaults (floor 0.5, k 100,
   alpha 1/3, lockword thresholds), killing the default-swap mutants that
   matter to results.

## Gaps closed this pass

Tests added specifically to kill surviving mutants:

- **Default parameters** (`test_measures.py::TestDefaultArguments`,
  `test_rtd.py::TestDefaults`): pin `log_ratio`/`percent_diff` `floor=0.5`,
  `simple_maths` `k=100`, `rtd` `alpha=1/3` and `normalize=True` by asserting the
  no-argument call equals the explicit-default call and differs from a
  neighbouring value.
- **Lockword thresholds** (`test_keyness.py::TestLockwordThresholds`): a crafted
  corpus pins the `max_abs_log_ratio=0.5` ceiling (a `|log ratio| == 1.0` type is
  excluded by default, admitted when the ceiling is raised) and the
  `min_freq_both=5` floor (a parity type with frequency 3 is excluded).

The remaining survivors are the message-string and unreachable-guard classes
above, which are not worth chasing — killing them would mean asserting exact
error text or constructing inputs the type system and constructors forbid.
