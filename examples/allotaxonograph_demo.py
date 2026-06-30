"""Allotaxonograph demo: rank-turbulence divergence and the rank-rank map.

Run with:  uv run python examples/allotaxonograph_demo.py
Writes allotaxonograph.png to the current directory.
"""

from keyflux import RankedList, allotaxonograph, rtd
from keyflux.datasets import load_demo_pair


def main() -> None:
    """Compare the bundled climate and finance corpora and save the figure."""
    focus, reference = load_demo_pair()
    climate = RankedList.from_counts(focus, label="climate")
    finance = RankedList.from_counts(reference, label="finance")

    result = rtd(climate, finance, alpha=1.0 / 3.0)
    print(f"Rank-turbulence divergence (alpha=1/3): {result.divergence:.3f}")
    print("Top contributors:")
    for contribution in result.contributions[:5]:
        leans = "climate" if contribution.direction == "system1" else "finance"
        print(f"  {contribution.type:<12} {contribution.contribution:.3f}  ({leans})")

    fig = allotaxonograph(climate, finance, alpha=1.0 / 3.0)
    fig.savefig("allotaxonograph.png", dpi=120)
    print("\nSaved allotaxonograph.png")


if __name__ == "__main__":
    main()
