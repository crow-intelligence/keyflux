# Keyness quickstart

Derive keywords and lockwords from two raw texts and print the reproducibility
record.

## What it shows

1. Counting two texts with `counts_from_text`
2. Positive and negative keywords, ranked by effect size
3. Lockwords — the stable shared vocabulary
4. The reproducibility record for the run

## Run it

```bash
python examples/keyness_quickstart.py
```

```text
Positive keywords (more typical of the climate text):
  climate      log-ratio=+2.50  p05

Negative keywords (more typical of the finance text):
  market       log-ratio=-2.67  p05

Lockwords (stable across both texts):
  the
  and

Reproducibility record:
  reference_id: finance-text
  measure: log_likelihood
  min_focus_freq: 1
  min_reference_freq: 1
  focus_total: 35
  reference_total: 33
  top_n: 10
  floor: 0.5
  smp_k: 100.0
  keyflux_version: 0.1.0
```

## Source

```python title="examples/keyness_quickstart.py"
--8<-- "examples/keyness_quickstart.py"
```
