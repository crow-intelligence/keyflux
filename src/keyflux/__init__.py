"""Keyflux — keyness, rank-turbulence divergence, and allotaxonographs."""

__version__ = "0.1.0"

from keyflux.io.corpus import counts_from_text, counts_from_tokens, load_counts
from keyflux.keyness import (
    Keyness,
    KeynessRow,
    KeywordTable,
    ReproRecord,
)

__all__ = [
    "Keyness",
    "KeynessRow",
    "KeywordTable",
    "ReproRecord",
    "counts_from_tokens",
    "counts_from_text",
    "load_counts",
    "__version__",
]
