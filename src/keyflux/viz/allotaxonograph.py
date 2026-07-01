"""Allotaxonograph: a two-panel matplotlib rank-rank map (no JavaScript runtime).

The left panel is the diamond rank-rank histogram — a 2D histogram of the two
log-ranks rotated so the equality diagonal is vertical. Types on the centre line
are stable (the lockword zone); types off-centre have moved; exclusives sit on
the outer edges. The right panel is the contribution-balance list: the top
rank-turbulence-divergence contributors as bars leaning toward whichever system
each is more characteristic of. Both panels are driven by the same
:func:`keyflux.divergence.rtd.rtd` call, so they cannot disagree.

The single public function returns a :class:`matplotlib.figure.Figure` and never
calls ``show()``, so it renders inline in Jupyter and saves cleanly with
``fig.savefig(...)``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from matplotlib.figure import Figure

from keyflux.divergence.rtd import rtd

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from keyflux.divergence.rtd import RTDResult
    from keyflux.ranking.rankedlist import RankedList

_SYSTEM1_COLOR = "#1f77b4"
_SYSTEM2_COLOR = "#d62728"


def _diamond_histogram(
    ax: Axes,
    ranks1: list[float],
    ranks2: list[float],
    labels: tuple[str, str],
    *,
    bins: int,
    cmap: str,
) -> None:
    """Draw the rotated-square (diamond) rank-rank 2D histogram."""
    log1 = np.log10(np.asarray(ranks1))
    log2 = np.log10(np.asarray(ranks2))
    # Rotate 45 degrees: departure from the diagonal vs. mean log-rank depth.
    departure = log2 - log1
    depth = log1 + log2
    spread = float(np.abs(departure).max()) if len(departure) else 1.0
    spread = max(spread, 1e-6)

    ax.hist2d(
        departure,
        depth,
        bins=bins,
        range=[[-spread * 1.1, spread * 1.1], [0.0, max(float(depth.max()), 1e-6)]],
        cmap=cmap,
        cmin=1,
    )
    ax.axvline(0.0, color="0.4", linewidth=1.0, linestyle="--")
    ax.set_xlabel(f"← typical of {labels[0]}     typical of {labels[1]} →")
    ax.set_ylabel("rank depth  (log r1 + log r2)")
    ax.set_title("rank-rank histogram")
    ax.invert_yaxis()


def _balance_bars(
    ax: Axes,
    result: RTDResult,
    labels: tuple[str, str],
    *,
    top: int,
) -> None:
    """Draw the top divergence contributors as left/right balance bars."""
    contributions = result.contributions[:top]
    types = [c.type for c in contributions]
    # Sign the bar by direction: system1 leans left (negative), system2 right.
    values = [
        -c.contribution if c.direction == "system1" else c.contribution
        for c in contributions
    ]
    colors = [
        _SYSTEM1_COLOR if c.direction == "system1" else _SYSTEM2_COLOR
        for c in contributions
    ]
    y = np.arange(len(types))
    ax.barh(y, values, color=colors)
    ax.set_yticks(y)
    ax.set_yticklabels(types)
    ax.invert_yaxis()
    ax.axvline(0.0, color="0.4", linewidth=1.0)
    ax.set_xlabel(f"← {labels[0]}     contribution     {labels[1]} →")
    ax.set_title("top contributors")


def allotaxonograph(
    list1: RankedList,
    list2: RankedList,
    *,
    alpha: float = 1.0 / 3.0,
    labels: tuple[str, str] | None = None,
    top: int = 30,
    bins: int = 24,
    figsize: tuple[float, float] = (12.0, 6.0),
    cmap: str = "viridis",
) -> Figure:
    """Draw a two-panel allotaxonograph of two ranked lists.

    Args:
        list1: The first ranked list.
        list2: The second ranked list.
        alpha: Rank-turbulence-divergence tuning parameter; annotated on the
            figure and used for the contribution panel.
        labels: ``(label1, label2)`` for the two systems; falls back to each
            list's own label, then to generic names.
        top: Number of top contributors to show in the right panel.
        bins: Number of bins per axis in the rank-rank histogram.
        figsize: Figure size in inches.
        cmap: Matplotlib colormap name for the histogram.

    Returns:
        A :class:`matplotlib.figure.Figure` with two axes. The function never
        calls ``show()``, so it displays inline in Jupyter and saves with
        ``fig.savefig(...)``.

    Raises:
        ValueError: If either list is empty (propagated from :func:`rtd`).

    Contract:
        - Returns a Figure with exactly two axes.
        - Inputs are never mutated.
        - The histogram and the contribution bars come from the same ``rtd``
          call, so the two panels are always consistent.

    Examples:
        >>> from keyflux.datasets import load_jkbren_example
        >>> r1, r2 = load_jkbren_example()
        >>> fig = allotaxonograph(r1, r2, alpha=1.0, labels=("A", "B"))
        >>> type(fig).__name__
        'Figure'
        >>> len(fig.axes)
        2
    """
    if labels is None:
        labels = (list1.label or "system 1", list2.label or "system 2")

    result = rtd(list1, list2, alpha=alpha)
    _types, ranks1, ranks2 = list1.aligned(list2)

    fig = Figure(figsize=figsize)
    ax_hist, ax_bars = fig.subplots(1, 2)
    _diamond_histogram(ax_hist, ranks1, ranks2, labels, bins=bins, cmap=cmap)
    _balance_bars(ax_bars, result, labels, top=top)
    fig.suptitle(
        f"Allotaxonograph  (alpha = {alpha:g},  divergence = {result.divergence:.3f})"
    )
    fig.tight_layout()
    return fig
