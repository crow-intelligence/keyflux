# Allotaxonograph demo

Compute the rank-turbulence divergence between the bundled climate and finance
corpora, list the top contributors, and save the allotaxonograph.

## What it shows

1. Building two `RankedList`s from the demo corpus pair
2. The rank-turbulence divergence and its top per-type contributions
3. Saving the two-panel allotaxonograph to a PNG

## Run it

```bash
python examples/allotaxonograph_demo.py
```

```text
Rank-turbulence divergence (alpha=1/3): 0.267
Top contributors:
  climate      0.036  (climate)
  market       0.036  (finance)
  carbon       0.030  (climate)
  stock        0.030  (finance)
  trade        0.026  (finance)

Saved allotaxonograph.png
```

## Source

```python title="examples/allotaxonograph_demo.py"
--8<-- "examples/allotaxonograph_demo.py"
```
