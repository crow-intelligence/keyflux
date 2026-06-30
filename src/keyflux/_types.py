"""Shared type aliases for the keyflux package."""

from collections import Counter
from typing import Literal, TypeAlias

Token: TypeAlias = str
"""A surface or lemmatised word type."""

Count: TypeAlias = int
"""A raw frequency count for a single type."""

FreqTable: TypeAlias = Counter[str]
"""Type-to-count mapping for one corpus (focus or reference)."""

Rank: TypeAlias = float
"""A 1-based rank; float because tied and tied-last ranks are averaged."""

MeasureName: TypeAlias = Literal[
    "log_likelihood",
    "log_ratio",
    "simple_maths",
    "percent_diff",
    "chi_square",
]
"""Identifier selecting a keyness scoring function."""

Significance: TypeAlias = Literal["ns", "p05", "p01", "p001", "p0001"]
"""Significance band from a log-likelihood / chi-square statistic (1 d.f.)."""

Direction: TypeAlias = Literal["positive", "negative", "neutral"]
"""Keyness polarity: over-represented, under-represented, or neither in focus."""
