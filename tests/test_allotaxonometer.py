"""Tests for keyflux.viz.allotaxonometer (the diamond allotaxonograph).

Headless by construction (Figure API, no pyplot).
"""

from matplotlib.colors import LogNorm
from matplotlib.figure import Figure

from keyflux.datasets import load_demo_pair, load_jkbren_example
from keyflux.ranking.rankedlist import RankedList
from keyflux.viz.allotaxonometer import allotaxonometer


class TestAllotaxonometer:
    """The diamond figure contract."""

    def test_returns_figure_with_three_axes(self) -> None:
        r1, r2 = load_jkbren_example()
        fig = allotaxonometer(r1, r2, alpha=1.0)
        assert isinstance(fig, Figure)
        assert len(fig.axes) == 3  # diamond, colorbar, wordshift

    def test_alpha_and_divergence_annotated(self) -> None:
        r1, r2 = load_jkbren_example()
        fig = allotaxonometer(r1, r2, alpha=0.3)
        title = fig._suptitle.get_text()
        assert "0.3" in title
        assert "divergence" in title

    def test_labels_from_arguments(self) -> None:
        r1, r2 = load_jkbren_example()
        fig = allotaxonometer(r1, r2, labels=("2019", "2024"))
        texts = " ".join(t.get_text() for ax in fig.axes for t in ax.texts)
        texts += " " + fig.axes[2].get_xlabel()
        assert "2019" in texts and "2024" in texts

    def test_falls_back_to_list_labels(self) -> None:
        focus, reference = load_demo_pair()
        c = RankedList.from_counts(focus, label="climate")
        f = RankedList.from_counts(reference, label="finance")
        fig = allotaxonometer(c, f)
        texts = " ".join(t.get_text() for ax in fig.axes for t in ax.texts)
        assert "climate" in texts and "finance" in texts

    def test_inputs_not_mutated(self) -> None:
        r1, r2 = load_jkbren_example()
        counts1, counts2 = dict(r1.counts), dict(r2.counts)
        allotaxonometer(r1, r2)
        assert dict(r1.counts) == counts1
        assert dict(r2.counts) == counts2

    def test_colorbar_uses_lognorm(self) -> None:
        r1, r2 = load_jkbren_example()
        fig = allotaxonometer(r1, r2)
        mesh = fig.axes[0].collections[0]
        assert isinstance(mesh.norm, LogNorm)

    def test_top_limits_bars(self) -> None:
        focus, reference = load_demo_pair()
        fig = allotaxonometer(
            RankedList.from_counts(focus), RankedList.from_counts(reference), top=3
        )
        # wordshift is the third axis; barh adds one patch per bar.
        assert len(fig.axes[2].patches) <= 3

    def test_handles_disjoint_inputs(self) -> None:
        r1 = RankedList.from_counts({"a": 5, "b": 3, "c": 1}, label="L")
        r2 = RankedList.from_counts({"x": 5, "y": 3, "z": 1}, label="R")
        fig = allotaxonometer(r1, r2, alpha=1.0 / 3.0)
        assert len(fig.axes) == 3

    def test_single_shared_type(self) -> None:
        # All ranks equal 1 -> extent floors to one decade; must not crash.
        fig = allotaxonometer(
            RankedList.from_counts({"a": 1}), RankedList.from_counts({"a": 1})
        )
        assert isinstance(fig, Figure)

    def test_alpha_zero_contours(self) -> None:
        r1, r2 = load_jkbren_example()
        fig = allotaxonometer(r1, r2, alpha=0.0)
        # the diamond axis should carry contour collections and the mesh
        assert len(fig.axes[0].collections) >= 1

    def test_renders_headless(self) -> None:
        r1, r2 = load_jkbren_example()
        fig = allotaxonometer(r1, r2)
        fig.canvas.draw()  # would raise if a backend/display were required
