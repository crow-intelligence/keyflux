"""Tiny bundled corpora and fixtures for docs and tests.

The data lives inline as Python dicts so it is always importable in doctests
with no package-data or ``importlib.resources`` machinery.
"""

from __future__ import annotations

from collections import Counter

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
