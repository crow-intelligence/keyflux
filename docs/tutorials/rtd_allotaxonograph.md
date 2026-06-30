# Rank-turbulence divergence and the allotaxonograph

The usual summary of "did the vocabulary shift?" is Jaccard overlap on the
top-N keywords — one opaque number that discards rank, discards everything below
the cutoff, and cannot say *which* words drove the change. Rank-turbulence
divergence (RTD; Dodds et al. 2020) replaces it with a rank-sensitive number plus
a per-type accounting, and the allotaxonograph turns that into a picture.

## Ranked lists

RTD compares two `RankedList`s. Build them from counts (the classic frequency
ranking) or from a `Keyness` object (rank by a corpus side):

```python
from keyflux import RankedList
from keyflux.datasets import load_demo_pair

focus, reference = load_demo_pair()
r1 = RankedList.from_counts(focus, label="climate")
r2 = RankedList.from_counts(reference, label="finance")
```

Tied counts share an average rank. When two lists are aligned for comparison, a
type present in one list but absent from the other is placed at a **tied-last**
rank — the average of the unused tail positions — so exclusives are handled
consistently everywhere.

## Compute the divergence

```python
from keyflux import rtd

result = rtd(r1, r2, alpha=1/3)
result.divergence            # scalar in [0, 1]; 0 = identical, 1 = disjoint
```

The per-type term is
`delta(tau) = |r1**-alpha - r2**-alpha|**(1/(alpha+1))`, summed and normalised by
the divergence of the maximally disjoint pair so the total lands in `[0, 1]`.

### Tuning `alpha`

- **Small `alpha`** (toward 0) emphasises churn among rare, low-rank types.
- **Large `alpha`** emphasises shifts among common, high-rank types.
- **`alpha = 0`** uses the exact logarithmic limit
  (`delta ∝ |ln r1 - ln r2|`), so there is never a division by zero.
- The default **`1/3`** is the Dodds et al. recommendation for text.

## Which words drove the shift

```python
for c in result.contributions[:5]:
    leans = "climate" if c.direction == "system1" else "finance"
    print(c.type, round(c.contribution, 3), leans)
# climate 0.036 climate
# market  0.036 finance
# carbon  0.030 climate
# ...
```

`contributions` is sorted by contribution descending, and the contributions sum
to `divergence` — so each row is a literal share of the total shift, tagged with
the system it leans toward.

## The allotaxonograph

```python
from keyflux import allotaxonograph

fig = allotaxonograph(r1, r2, alpha=1/3, labels=("climate", "finance"))
fig.savefig("allotaxonograph.png", dpi=120)
```

The figure has two panels:

- **Left — the rank-rank histogram.** A 2D histogram of the two log-ranks,
  rotated so the equality diagonal is vertical. Types on the centre line sit at
  comparable rank in both corpora (the lockword zone); types off-centre have
  moved; exclusives land on the outer edges.
- **Right — the contribution balance.** The top contributors as bars leaning
  left or right toward whichever corpus each is more characteristic of — the
  "which words drove the shift" panel.

`allotaxonograph` returns a matplotlib `Figure` and never calls `show()`, so it
renders inline in Jupyter and saves cleanly from a script. Both panels are driven
by the same `rtd` call, so they can never disagree.

## Properties worth knowing

- `rtd(x, x).divergence == 0` — a list never diverges from itself.
- `rtd(a, b) == rtd(b, a)` — symmetric.
- `0 <= divergence <= 1` for every input and every `alpha`.
