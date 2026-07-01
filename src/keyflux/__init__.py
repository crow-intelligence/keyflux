"""Keyflux — keyness, rank-turbulence divergence, and allotaxonographs."""

__version__ = "0.1.0"

from keyflux.divergence import Contribution, RTDResult, rtd
from keyflux.io.corpus import counts_from_text, counts_from_tokens, load_counts
from keyflux.keyness import (
    Keyness,
    KeynessRow,
    KeywordTable,
    ReproRecord,
)
from keyflux.ranking import RankedList
from keyflux.viz import allotaxonograph

__all__ = [
    "Keyness",
    "KeynessRow",
    "KeywordTable",
    "ReproRecord",
    "RankedList",
    "rtd",
    "RTDResult",
    "Contribution",
    "allotaxonograph",
    "counts_from_tokens",
    "counts_from_text",
    "load_counts",
    "__version__",
]
