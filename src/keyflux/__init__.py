"""Keyflux — keyness, rank-turbulence divergence, and allotaxonographs."""

from importlib.metadata import PackageNotFoundError, version

from keyflux.divergence import Contribution, RTDResult, rtd
from keyflux.io.corpus import counts_from_text, counts_from_tokens, load_counts
from keyflux.keyness import (
    Keyness,
    KeynessRow,
    KeywordTable,
    ReproRecord,
)
from keyflux.ranking import RankedList
from keyflux.viz import allotaxonograph, allotaxonometer

try:
    __version__ = version("keyflux")
except PackageNotFoundError:  # pragma: no cover - only when running uninstalled
    __version__ = "0.0.0+unknown"

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
    "allotaxonometer",
    "counts_from_tokens",
    "counts_from_text",
    "load_counts",
    "__version__",
]
