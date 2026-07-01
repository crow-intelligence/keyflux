r"""The diamond allotaxonograph (Dodds et al. 2020) — the full allotaxonometer.

This is the canonical rank-rank "diamond" chart: a rotated-square 2D histogram of
the two log-ranks, coloured on a logarithmic scale, overlaid with iso-divergence
contours, paired with a wordshift list of the top rank-turbulence-divergence
contributors. It complements :func:`keyflux.viz.allotaxonograph.allotaxonograph`
(the simpler two-panel view), which is left unchanged.

The equality line ``r1 == r2`` runs vertically down the centre; the top types
(rank 1) sit at the top corner and rare/exclusive types spread to the bottom
edges. Types leaning to the first system fall on the left, the second on the
right. The figure works on any two :class:`~keyflux.ranking.rankedlist.RankedList`
objects — frequency, keyness score (via ``RankedList.from_scores``), or any other
ranking — so it can compare keywords, frequent words, lockwords, and more.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from matplotlib.colors import LogNorm
from matplotlib.figure import Figure

from keyflux.divergence.rtd import rtd

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.collections import QuadMesh

    from keyflux.divergence.rtd import RTDResult
    from keyflux.ranking.rankedlist import RankedList

_ROOT2 = np.sqrt(2.0)
_SYSTEM1_COLOR = "#1f77b4"
_SYSTEM2_COLOR = "#d62728"
_ALPHA_ZERO_TOL = 1e-10


def _rotate(log1: np.ndarray, log2: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Rotate (log rank1, log rank2) 45° so r1==r2 is vertical, (1,1) at the top."""
    u = (log1 - log2) / _ROOT2
    v = -(log1 + log2) / _ROOT2
    return u, v


def _diamond_histogram(
    ax: Axes,
    x: np.ndarray,
    y: np.ndarray,
    extent: float,
    *,
    bins: int,
    cmap: str,
) -> QuadMesh:
    """Draw the rotated-square 2D log-rank histogram; return the mesh."""
    edges = np.linspace(0.0, extent, bins + 1)
    hist, _, _ = np.histogram2d(x, y, bins=[edges, edges])
    xg, yg = np.meshgrid(edges, edges, indexing="ij")
    ug, vg = _rotate(xg, yg)
    masked = np.ma.masked_where(hist == 0, hist)
    norm = LogNorm(vmin=1, vmax=max(float(np.max(hist)), 2.0))
    return ax.pcolormesh(ug, vg, masked, cmap=cmap, norm=norm, shading="flat")


def _iso_divergence_contours(
    ax: Axes,
    extent: float,
    *,
    alpha: float,
    n_contours: int,
    color: str,
) -> None:
    """Overlay curves of constant per-type divergence delta(tau; alpha)."""
    grid = np.linspace(0.0, extent, 400)
    gx, gy = np.meshgrid(grid, grid, indexing="ij")
    r1 = 10.0**gx
    r2 = 10.0**gy
    if alpha < _ALPHA_ZERO_TOL:
        d = np.abs(np.log(r1) - np.log(r2))
    else:
        d = np.abs(r1**-alpha - r2**-alpha) ** (1.0 / (alpha + 1.0))
    ug, vg = _rotate(gx, gy)
    dmax = float(np.max(d))
    if dmax <= 0.0:
        return
    levels = np.linspace(0.0, dmax, n_contours + 2)[1:-1]
    ax.contour(ug, vg, d, levels=levels, colors=color, linewidths=0.7, alpha=0.9)


def _diamond_axes(ax: Axes, extent: float, labels: tuple[str, str]) -> None:
    """Draw the square boundary, equality line, log-rank edge ticks, and edge labels."""
    corners = np.array([[0.0, 0.0], [extent, 0.0], [extent, extent], [0.0, extent]])
    bu, bv = _rotate(corners[:, 0], corners[:, 1])
    ax.plot(np.append(bu, bu[0]), np.append(bv, bv[0]), color="0.4", linewidth=1.0)
    ax.axvline(0.0, color="0.6", linewidth=0.8, linestyle="--")

    for k in range(int(extent) + 1):
        ur, vr = _rotate(np.array(float(k)), np.array(0.0))  # right edge: r1 axis
        ul, vl = _rotate(np.array(0.0), np.array(float(k)))  # left edge:  r2 axis
        ax.text(
            float(ur),
            float(vr),
            f"$10^{{{k}}}$",
            ha="left",
            va="center",
            fontsize=7,
            color="0.3",
        )
        ax.text(
            float(ul),
            float(vl),
            f"$10^{{{k}}}$",
            ha="right",
            va="center",
            fontsize=7,
            color="0.3",
        )
    mid = extent / (2.0 * _ROOT2)
    ax.text(
        mid,
        -mid,
        f"rank in {labels[0]}",
        rotation=-45,
        ha="center",
        va="bottom",
        fontsize=9,
    )
    ax.text(
        -mid,
        -mid,
        f"rank in {labels[1]}",
        rotation=45,
        ha="center",
        va="bottom",
        fontsize=9,
    )

    lim = extent / _ROOT2
    ax.set_xlim(-lim * 1.08, lim * 1.08)
    ax.set_ylim(-extent * _ROOT2 * 1.08, extent * 0.12 + 0.05)
    ax.set_aspect("equal")
    ax.axis("off")


def _wordshift_panel(
    ax: Axes, result: RTDResult, labels: tuple[str, str], *, top: int
) -> tuple[float, float]:
    """Draw the top-N contributor bars per system; return each system's share."""
    contributions = result.contributions[:top]
    types = [c.type for c in contributions]
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
    ax.set_yticklabels(types, fontsize=8)
    ax.invert_yaxis()
    ax.axvline(0.0, color="0.4", linewidth=1.0)
    ax.set_xlabel(f"← {labels[0]}     contribution     {labels[1]} →", fontsize=9)
    share1 = sum(
        c.contribution for c in result.contributions if c.direction == "system1"
    )
    share2 = sum(
        c.contribution for c in result.contributions if c.direction == "system2"
    )
    return share1, share2


def _annotations(
    fig: Figure,
    ax: Axes,
    result: RTDResult,
    labels: tuple[str, str],
    *,
    alpha: float,
    n_types: int,
    n_shared: int,
    n_excl1: int,
    n_excl2: int,
) -> None:
    """Add the suptitle and the type/exclusive count block."""
    fig.suptitle(
        f"Allotaxonometer  (α = {alpha:g},  divergence = {result.divergence:.3f})",
        fontsize=13,
    )
    ax.text(
        0.01,
        0.99,
        f"types: {n_types}\n"
        f"shared: {n_shared}\n"
        f"{labels[0]}-only: {n_excl1}\n"
        f"{labels[1]}-only: {n_excl2}",
        transform=ax.transAxes,
        va="top",
        ha="left",
        fontsize=8,
        color="0.25",
    )


def allotaxonometer(
    list1: RankedList,
    list2: RankedList,
    *,
    alpha: float = 1.0 / 3.0,
    labels: tuple[str, str] | None = None,
    top: int = 25,
    bins: int = 36,
    n_contours: int = 8,
    figsize: tuple[float, float] = (13.0, 7.0),
    cmap: str = "inferno",
    contour_color: str = "0.75",
) -> Figure:
    """Draw the diamond allotaxonograph (Dodds et al. 2020) of two ranked lists.

    Args:
        list1: The first ranked list (its types lean to the left half).
        list2: The second ranked list (its types lean to the right half).
        alpha: Rank-turbulence-divergence tuning parameter; ``0`` uses the
            logarithmic limit. Sets the iso-divergence contours and the wordshift.
        labels: ``(label1, label2)``; falls back to each list's own label, then to
            generic names.
        top: Number of top contributors in the wordshift panel.
        bins: Number of bins per axis in the rank-rank histogram.
        n_contours: Number of iso-divergence contour lines.
        figsize: Figure size in inches.
        cmap: Colormap for the histogram (read under a logarithmic norm).
        contour_color: Colour of the iso-divergence contours.

    Returns:
        A :class:`matplotlib.figure.Figure` with three axes (diamond, colorbar,
        wordshift). The function never calls ``show()``.

    Raises:
        ValueError: If either list is empty (propagated from :func:`rtd`).

    Contract:
        - Returns a Figure with exactly three axes.
        - Inputs are never mutated.
        - The histogram, contours, and wordshift all derive from the same aligned
          ranks and ``rtd`` call, so they cannot disagree.
        - Exclusive types (present in one list only) sit at a tied-last rank on the
          outer edges.

    Examples:
        >>> from keyflux.datasets import load_jkbren_example
        >>> r1, r2 = load_jkbren_example()
        >>> fig = allotaxonometer(r1, r2, alpha=1.0, labels=("A", "B"))
        >>> type(fig).__name__
        'Figure'
        >>> len(fig.axes)
        3
    """
    if labels is None:
        labels = (list1.label or "system 1", list2.label or "system 2")

    result = rtd(list1, list2, alpha=alpha)
    types, ranks1, ranks2 = list1.aligned(list2)
    x = np.log10(np.asarray(ranks1))
    y = np.log10(np.asarray(ranks2))
    extent = max(float(np.ceil(max(np.max(x), np.max(y)))), 1.0)

    t1, t2 = list1.types(), list2.types()
    n_shared = len(t1 & t2)

    fig = Figure(figsize=figsize)
    gs = fig.add_gridspec(nrows=1, ncols=3, width_ratios=[6.0, 0.25, 3.5], wspace=0.4)
    ax_diamond = fig.add_subplot(gs[0, 0])
    ax_cbar = fig.add_subplot(gs[0, 1])
    ax_shift = fig.add_subplot(gs[0, 2])

    mesh = _diamond_histogram(ax_diamond, x, y, extent, bins=bins, cmap=cmap)
    _iso_divergence_contours(
        ax_diamond, extent, alpha=alpha, n_contours=n_contours, color=contour_color
    )
    _diamond_axes(ax_diamond, extent, labels)
    cbar = fig.colorbar(mesh, cax=ax_cbar)
    cbar.set_label("types per cell", fontsize=9)

    share1, share2 = _wordshift_panel(ax_shift, result, labels, top=top)
    total = share1 + share2
    if total > 0:
        ax_shift.set_title(
            f"balance: {labels[0]} {share1 / total:.0%}  |  "
            f"{labels[1]} {share2 / total:.0%}",
            fontsize=9,
        )
    _annotations(
        fig,
        ax_diamond,
        result,
        labels,
        alpha=alpha,
        n_types=len(types),
        n_shared=n_shared,
        n_excl1=len(t1 - t2),
        n_excl2=len(t2 - t1),
    )
    fig.subplots_adjust(top=0.9)
    return fig
