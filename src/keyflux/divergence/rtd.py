r"""Rank-turbulence divergence (Dodds et al. 2020, arXiv:2002.09770).

Rank-turbulence divergence (RTD) compares two ranked lists by how far each type
moves between them, with a tunable parameter ``alpha``. Small ``alpha`` surfaces
churn among rare, low-rank types; large ``alpha`` surfaces shifts among common,
high-rank types. The per-type divergence is

    delta(tau; alpha) = | r1 ** -alpha - r2 ** -alpha | ** (1 / (alpha + 1))

and the total is normalised to [0, 1] by the divergence of the maximally
disjoint pair, so RTD(x, x) = 0 and disjoint lists approach 1. As ``alpha -> 0``
the per-type term degenerates to the logarithmic form ``| ln r1 - ln r2 |``,
which is used directly to avoid dividing by zero.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from keyflux.ranking.rankedlist import RankedList

ShiftDirection = Literal["system1", "system2", "shared"]
"""Which system a type is more characteristic of (lower rank = more typical)."""

_ALPHA_ZERO_TOL = 1e-10


@dataclass(frozen=True, slots=True)
class Contribution:
    """One type's contribution to the total divergence.

    Attributes:
        type: The type.
        delta: The raw per-type divergence term (before normalisation).
        contribution: This type's additive share of ``divergence`` (the shares
            sum to the total divergence).
        rank1: The type's rank in the first list (tied-last if absent).
        rank2: The type's rank in the second list (tied-last if absent).
        direction: Which list the type leans toward (lower rank wins).
    """

    type: str
    delta: float
    contribution: float
    rank1: float
    rank2: float
    direction: ShiftDirection


@dataclass(frozen=True, slots=True)
class RTDResult:
    """The result of a rank-turbulence divergence computation.

    Attributes:
        divergence: The normalised divergence in [0, 1].
        raw: The un-normalised weighted sum (matches the jkbren reference at
            ``alpha=1.0`` when ``normalize=False``).
        alpha: The tuning parameter used.
        contributions: Per-type contributions, sorted by contribution descending.
        labels: The two list labels.
    """

    divergence: float
    raw: float
    alpha: float
    contributions: tuple[Contribution, ...]
    labels: tuple[str, str]


def _direction(rank1: float, rank2: float) -> ShiftDirection:
    if rank1 < rank2:
        return "system1"
    if rank2 < rank1:
        return "system2"
    return "shared"


def _elements_general(
    ranks1: list[float],
    ranks2: list[float],
    n1: int,
    n2: int,
    alpha: float,
) -> tuple[list[float], float]:
    """Per-type terms and normalisation for alpha > 0."""
    exp = 1.0 / (alpha + 1.0)
    ref1 = (n1 + 0.5 * n2) ** (-alpha)
    ref2 = (n2 + 0.5 * n1) ** (-alpha)
    deltas: list[float] = []
    norm = 0.0
    for r1, r2 in zip(ranks1, ranks2, strict=True):
        a1 = r1**-alpha
        a2 = r2**-alpha
        deltas.append(abs(a1 - a2) ** exp)
        norm += abs(a1 - ref1) ** exp + abs(ref2 - a2) ** exp
    return deltas, norm


def _elements_log_limit(
    ranks1: list[float],
    ranks2: list[float],
    n1: int,
    n2: int,
) -> tuple[list[float], float]:
    """Per-type terms and normalisation for the alpha -> 0 logarithmic limit."""
    ref1 = math.log(n1 + 0.5 * n2)
    ref2 = math.log(n2 + 0.5 * n1)
    deltas: list[float] = []
    norm = 0.0
    for r1, r2 in zip(ranks1, ranks2, strict=True):
        l1 = math.log(r1)
        l2 = math.log(r2)
        deltas.append(abs(l1 - l2))
        norm += abs(l1 - ref1) + abs(ref2 - l2)
    return deltas, norm


def rtd(
    list1: RankedList,
    list2: RankedList,
    *,
    alpha: float = 1.0 / 3.0,
    normalize: bool = True,
) -> RTDResult:
    """Compute the rank-turbulence divergence between two ranked lists.

    Args:
        list1: The first ranked list.
        list2: The second ranked list.
        alpha: Tuning parameter (``>= 0``). Small values surface rare, low-rank
            churn; large values surface common-word shifts. ``alpha == 0`` uses
            the logarithmic limit. The default ``1/3`` is the Dodds et al.
            recommendation for text.
        normalize: If True, return ``divergence`` scaled to [0, 1]; the ``raw``
            field always holds the un-normalised sum.

    Returns:
        An :class:`RTDResult` with the scalar divergence and the sorted per-type
        contributions, each tagged with its shift direction.

    Raises:
        ValueError: If ``alpha`` is negative, or either list is empty.

    Contract:
        - ``rtd(x, x).divergence == 0`` (a list never diverges from itself).
        - ``0 <= divergence <= 1`` for every input and every ``alpha``.
        - Symmetric: ``rtd(a, b).divergence == rtd(b, a).divergence``.
        - The per-type contributions sum to ``divergence``.
        - Exclusives (present in one list only) are placed at a tied-last rank.

    Examples:
        >>> from keyflux.ranking.rankedlist import RankedList
        >>> r1 = RankedList.from_counts({"a": 20, "e": 14, "c": 8, "b": 7,
        ...                              "f": 4, "g": 2, "d": 1})
        >>> r2 = RankedList.from_counts({"b": 24, "a": 16, "e": 5, "d": 4,
        ...                              "c": 3, "f": 2, "g": 1})
        >>> round(rtd(r1, r2, alpha=1.0).divergence, 6)
        0.459248
        >>> rtd(r1, r1, alpha=1.0).divergence
        0.0
    """
    if alpha < 0:
        msg = f"alpha must be non-negative, got {alpha}."
        raise ValueError(msg)
    if not len(list1) or not len(list2):
        msg = "Both ranked lists must be non-empty."
        raise ValueError(msg)

    types, ranks1, ranks2 = list1.aligned(list2)
    n1 = len(list1)
    n2 = len(list2)

    if alpha < _ALPHA_ZERO_TOL:
        deltas, norm = _elements_log_limit(ranks1, ranks2, n1, n2)
        prefactor = 1.0
    else:
        deltas, norm = _elements_general(ranks1, ranks2, n1, n2, alpha)
        prefactor = (alpha + 1.0) / alpha

    raw = prefactor * math.fsum(deltas)
    normalizer = prefactor * norm
    divergence = raw / normalizer if normalize and normalizer > 0 else raw
    if normalize and normalizer <= 0:
        divergence = 0.0

    share_denom = normalizer if normalize and normalizer > 0 else 1.0
    contributions = tuple(
        sorted(
            (
                Contribution(
                    type=t,
                    delta=d,
                    contribution=prefactor * d / share_denom,
                    rank1=r1,
                    rank2=r2,
                    direction=_direction(r1, r2),
                )
                for t, d, r1, r2 in zip(types, deltas, ranks1, ranks2, strict=True)
            ),
            key=lambda c: c.contribution,
            reverse=True,
        )
    )
    return RTDResult(
        divergence=divergence,
        raw=raw,
        alpha=alpha,
        contributions=contributions,
        labels=(list1.label, list2.label),
    )
