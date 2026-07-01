"""Tiny bundled corpora and fixtures for docs and tests.

The data lives inline as Python dicts so it is always importable in doctests
with no package-data or ``importlib.resources`` machinery.
"""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from keyflux.ranking.rankedlist import RankedList

# The jkbren/rank-turbulence-divergence reference example. Both systems rank the
# same seven elements; rtd at alpha=1.0 is 0.45924793111057804.
_JKBREN_FOCUS: dict[str, int] = {
    "a": 20,
    "e": 14,
    "c": 8,
    "b": 7,
    "f": 4,
    "g": 2,
    "d": 1,
}
_JKBREN_REFERENCE: dict[str, int] = {
    "b": 24,
    "a": 16,
    "e": 5,
    "d": 4,
    "c": 3,
    "f": 2,
    "g": 1,
}

_DEMO_FOCUS: dict[str, int] = {
    "climate": 42,
    "carbon": 28,
    "emissions": 19,
    "warming": 14,
    "policy": 11,
    "the": 320,
    "of": 180,
    "and": 165,
    "to": 150,
    "energy": 22,
    "renewable": 9,
    "global": 17,
}
_DEMO_REFERENCE: dict[str, int] = {
    "market": 40,
    "stock": 26,
    "trade": 21,
    "profit": 13,
    "policy": 12,
    "the": 318,
    "of": 176,
    "and": 170,
    "to": 148,
    "energy": 8,
    "shares": 15,
    "global": 16,
}


def load_demo_pair() -> tuple[Counter[str], Counter[str]]:
    """Return the bundled (focus, reference) demo corpus pair.

    A tiny climate-discourse focus corpus versus a finance-discourse reference
    corpus, with shared function words and a couple of lockword-like overlaps.

    Returns:
        ``(focus, reference)`` frequency Counters.

    Examples:
        >>> focus, reference = load_demo_pair()
        >>> focus["climate"], reference["market"]
        (42, 40)
    """
    return Counter(_DEMO_FOCUS), Counter(_DEMO_REFERENCE)


def load_jkbren_example() -> tuple[RankedList, RankedList]:
    """Return the jkbren rank-turbulence-divergence regression pair.

    Two ranked lists over the same seven elements. Their rank-turbulence
    divergence at ``alpha=1.0`` is ``0.45924793111057804`` — the regression
    anchor from the reference implementation.

    Returns:
        ``(list1, list2)`` as :class:`keyflux.ranking.rankedlist.RankedList`.

    Examples:
        >>> from keyflux.divergence import rtd
        >>> r1, r2 = load_jkbren_example()
        >>> round(rtd(r1, r2, alpha=1.0).divergence, 6)
        0.459248
    """
    from keyflux.ranking.rankedlist import RankedList

    return (
        RankedList.from_counts(_JKBREN_FOCUS, label="system 1"),
        RankedList.from_counts(_JKBREN_REFERENCE, label="system 2"),
    )
