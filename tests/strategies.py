"""Shared Hypothesis strategies for keyflux tests."""

from __future__ import annotations

import string
from collections import Counter
from typing import TYPE_CHECKING

from hypothesis import strategies as st

if TYPE_CHECKING:
    from keyflux.ranking.rankedlist import RankedList

word = st.text(alphabet=string.ascii_lowercase, min_size=1, max_size=12)
"""A lowercase alphabetic word type (1-12 chars)."""

alpha_value = st.floats(min_value=0.0, max_value=3.0, allow_nan=False)
"""A rank-turbulence-divergence tuning parameter alpha in [0, 3] (0 = log limit)."""


@st.composite
def freq_counter(draw: st.DrawFn) -> Counter[str]:
    """A non-empty frequency Counter with positive integer counts."""
    items = draw(
        st.dictionaries(
            keys=word,
            values=st.integers(min_value=1, max_value=10_000),
            min_size=1,
            max_size=60,
        )
    )
    return Counter(items)


@st.composite
def corpus_pair(draw: st.DrawFn) -> tuple[Counter[str], Counter[str]]:
    """A (focus, reference) pair of frequency Counters sharing some vocabulary."""
    focus = draw(freq_counter())
    reference = draw(freq_counter())
    return focus, reference


@st.composite
def ranked_list(draw: st.DrawFn) -> RankedList:
    """A RankedList built from a non-empty frequency Counter."""
    from keyflux.ranking.rankedlist import RankedList as _RankedList

    return _RankedList.from_counts(draw(freq_counter()))


@st.composite
def ranked_pair(draw: st.DrawFn) -> tuple[RankedList, RankedList]:
    """A pair of RankedLists with possibly overlapping, possibly disjoint vocab."""
    return draw(ranked_list()), draw(ranked_list())
