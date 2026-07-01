"""Keyword and lockword categorisation (Baker 2011; Brezina Ch. 3).

Each compared type is one of three categories:

- **Positive keyword (+):** significantly more frequent in the focus corpus.
- **Negative keyword (-):** significantly more frequent in the reference corpus.
- **Lockword (0):** comparable relative frequency in both corpora.

This module owns the categorisation boundary (direction and band thresholds);
the numeric zero-cell flooring lives in :mod:`keyflux.keyness.measures`.
"""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Literal

from keyflux._types import Direction, Significance

if TYPE_CHECKING:
    from collections.abc import Sequence

    from keyflux.keyness.keyness import KeynessRow

Category = Literal["keyword+", "keyword-", "lockword", "other"]
"""The bucket a type falls into under :func:`classify_row`."""

_BAND_ORDER: tuple[Significance, ...] = ("ns", "p05", "p01", "p001", "p0001")
"""Significance bands from weakest to strongest, for threshold comparison."""


def is_significant(
    significance: Significance, min_significance: Significance = "p05"
) -> bool:
    """Whether a significance band reaches at least ``min_significance``.

    Args:
        significance: The band to test.
        min_significance: The weakest band that still counts as significant.

    Returns:
        True if ``significance`` is at least as strong as ``min_significance``.

    Contract:
        - ``"ns"`` is never significant for any ``min_significance`` above it.
        - Monotone in the band ordering ns < p05 < p01 < p001 < p0001.

    Examples:
        >>> is_significant("p001")
        True
        >>> is_significant("ns")
        False
        >>> is_significant("p05", min_significance="p01")
        False
    """
    return _BAND_ORDER.index(significance) >= _BAND_ORDER.index(min_significance)


def classify_direction(focus_rf: float, reference_rf: float) -> Direction:
    """Decide keyness polarity from relative frequencies.

    Args:
        focus_rf: Relative frequency of the type in the focus corpus.
        reference_rf: Relative frequency of the type in the reference corpus.

    Returns:
        ``"positive"`` if more frequent in the focus corpus, ``"negative"`` if
        more frequent in the reference corpus, ``"neutral"`` if exactly equal.

    Contract:
        - Swapping the two arguments swaps ``"positive"`` and ``"negative"`` and
          leaves ``"neutral"`` unchanged.

    Examples:
        >>> classify_direction(0.003, 0.001)
        'positive'
        >>> classify_direction(0.001, 0.003)
        'negative'
        >>> classify_direction(0.002, 0.002)
        'neutral'
    """
    if focus_rf > reference_rf:
        return "positive"
    if focus_rf < reference_rf:
        return "negative"
    return "neutral"


def classify_row(
    row: KeynessRow,
    *,
    min_significance: Significance = "p05",
    lockword_max_abs_log_ratio: float = 0.5,
) -> Category:
    """Bucket a keyness row into keyword(+/-), lockword, or other.

    Args:
        row: A scored keyness row.
        min_significance: The weakest band that counts as a keyword.
        lockword_max_abs_log_ratio: A non-significant type is a lockword only if
            its absolute log ratio is at or below this (relative frequencies near
            parity).

    Returns:
        ``"keyword+"``, ``"keyword-"``, ``"lockword"``, or ``"other"`` (a
        non-significant type whose frequencies are too far apart to be stable).

    Contract:
        - Significant rows are keywords; their sign follows ``row.direction``.
        - A non-significant row is a lockword when its effect size is small,
          otherwise ``"other"``.
        - Frequency cutoffs (minimum evidence in both corpora) are applied by
          :meth:`keyflux.keyness.keyness.Keyness.lockwords`, not here.

    Examples:
        >>> from keyflux.keyness.keyness import KeynessRow
        >>> kw = KeynessRow("war", 620, 267, 609.1, 265.0, 140.87, 1.2,
        ...                  "p0001", 140.87, "positive")
        >>> classify_row(kw)
        'keyword+'
        >>> lock = KeynessRow("the", 59901, 58960, 58848.8, 58519.2, 1.5, 0.01,
        ...                   "ns", 1.5, "positive")
        >>> classify_row(lock)
        'lockword'
    """
    if is_significant(row.significance, min_significance):
        return "keyword+" if row.direction == "positive" else "keyword-"
    if abs(row.effect_size) <= lockword_max_abs_log_ratio:
        return "lockword"
    return "other"


def partition(
    rows: Sequence[KeynessRow],
    *,
    min_significance: Significance = "p05",
    lockword_max_abs_log_ratio: float = 0.5,
) -> dict[Category, list[KeynessRow]]:
    """Group rows by :func:`classify_row` category.

    Args:
        rows: Scored keyness rows.
        min_significance: The weakest band that counts as a keyword.
        lockword_max_abs_log_ratio: Lockword effect-size ceiling.

    Returns:
        A dict mapping each category to its rows. Every input row appears in
        exactly one bucket; absent categories map to an empty list.

    Contract:
        - The buckets partition the input: disjoint and exhaustive.
        - All four category keys are always present.

    Examples:
        >>> from keyflux.keyness.keyness import KeynessRow
        >>> rows = [
        ...     KeynessRow("war", 620, 267, 609.1, 265.0, 140.87, 1.2,
        ...                "p0001", 140.87, "positive"),
        ...     KeynessRow("the", 59901, 58960, 58848.8, 58519.2, 1.5, 0.01,
        ...                "ns", 1.5, "positive"),
        ... ]
        >>> buckets = partition(rows)
        >>> len(buckets["keyword+"]), len(buckets["lockword"])
        (1, 1)
    """
    buckets: dict[Category, list[KeynessRow]] = defaultdict(list)
    for row in rows:
        category = classify_row(
            row,
            min_significance=min_significance,
            lockword_max_abs_log_ratio=lockword_max_abs_log_ratio,
        )
        buckets[category].append(row)
    for key in ("keyword+", "keyword-", "lockword", "other"):
        buckets.setdefault(key, [])
    return dict(buckets)
