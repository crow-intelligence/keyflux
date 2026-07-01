"""Tests for keyflux.viz.allotaxonograph.

The Figure API is used directly (no pyplot), so these tests are headless by
construction and need no display backend.
"""

from matplotlib.figure import Figure

from keyflux.datasets import load_demo_pair, load_jkbren_example
from keyflux.ranking.rankedlist import RankedList
from keyflux.viz.allotaxonograph import allotaxonograph


class TestAllotaxonograph:
    """The two-panel figure contract."""

    def test_returns_figure_with_two_axes(self) -> None:
        r1, r2 = load_jkbren_example()
        fig = allotaxonograph(r1, r2, alpha=1.0)
        assert isinstance(fig, Figure)
        assert len(fig.axes) == 2

    def test_alpha_is_annotated(self) -> None:
        r1, r2 = load_jkbren_example()
        fig = allotaxonograph(r1, r2, alpha=0.3)
        assert fig._suptitle is not None
        assert "0.3" in fig._suptitle.get_text()

    def test_labels_from_arguments(self) -> None:
        r1, r2 = load_jkbren_example()
        fig = allotaxonograph(r1, r2, labels=("2019", "2024"))
        text = " ".join(t.get_text() for ax in fig.axes for t in [ax.xaxis.label])
        assert "2019" in text and "2024" in text

    def test_falls_back_to_list_labels(self) -> None:
        focus, reference = load_demo_pair()
        c = RankedList.from_counts(focus, label="climate")
        f = RankedList.from_counts(reference, label="finance")
        fig = allotaxonograph(c, f)
        text = " ".join(t.get_text() for ax in fig.axes for t in [ax.xaxis.label])
        assert "climate" in text and "finance" in text

    def test_inputs_not_mutated(self) -> None:
        r1, r2 = load_jkbren_example()
        counts1 = dict(r1.counts)
        counts2 = dict(r2.counts)
        allotaxonograph(r1, r2)
        assert dict(r1.counts) == counts1
        assert dict(r2.counts) == counts2

    def test_handles_exclusives(self) -> None:
        # Disjoint vocabularies — every type is an exclusive on an outer edge.
        r1 = RankedList.from_counts({"a": 5, "b": 3, "c": 1}, label="L")
        r2 = RankedList.from_counts({"x": 5, "y": 3, "z": 1}, label="R")
        fig = allotaxonograph(r1, r2, alpha=1.0 / 3.0)
        assert len(fig.axes) == 2
