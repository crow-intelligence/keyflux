# Two views of one comparison

A keyword/lockword table and an allotaxonograph are two views of the **same
thing**. This is the unifying idea behind keyflux:

- **Lockwords are the diagonal.** Types at comparable rank in both corpora sit on
  the equality line of the rank-rank histogram — the stable centre.
- **Keywords are the off-diagonal high-divergence contributors.** Types that
  moved sit away from the diagonal and dominate the rank-turbulence-divergence
  contribution list.

The categorical (corpus-linguistics) view and the continuous (RTD) view describe
one comparison from two angles.

## Set up one comparison

```python
from keyflux import Keyness, RankedList, rtd, allotaxonograph
from keyflux.datasets import load_demo_pair

focus, reference = load_demo_pair()

# Categorical view: keywords and lockwords
k = Keyness(focus, reference, min_focus_freq=1, min_reference_freq=1)
keywords = {r.type for r in k.keywords()}
lockwords = {r.type for r in k.lockwords()}

# Continuous view: rank-turbulence divergence over the same counts
r1 = RankedList.from_counts(focus, label="climate")
r2 = RankedList.from_counts(reference, label="finance")
result = rtd(r1, r2, alpha=1/3)
```

## Lockwords sit near the diagonal

Lockwords have near-equal ranks in both lists, so their rank-rank points cluster
on the centre line and they contribute almost nothing to the divergence:

```python
contribution = {c.type: c.contribution for c in result.contributions}
sorted(lockwords, key=lambda t: contribution.get(t, 0.0))[:3]
# the lowest-contribution types are lockwords — they barely moved
```

## Keywords are the off-diagonal contributors

The top divergence contributors are exactly the keywords — the types whose ranks
diverge between the two corpora:

```python
top_contributors = {c.type for c in result.contributions[:8]}
top_contributors & keywords        # substantial overlap
top_contributors & lockwords       # empty — lockwords don't drive the shift
```

## See both at once

The allotaxonograph shows both views in one figure: the diagonal of the left
panel is the lockword zone, and the bars of the right panel are the keyword
contributions.

```python
fig = allotaxonograph(r1, r2, alpha=1/3, labels=("climate", "finance"))
fig.savefig("two_views.png")
```

Reading the picture: function words such as *the*, *of*, and *and* sit at the top
centre (shallow depth, on the diagonal) — the lockwords. *climate*, *carbon*, and
*market*, *stock* fan out to the left and right edges — the positive and negative
keywords — and they are the bars that dominate the contribution panel.
