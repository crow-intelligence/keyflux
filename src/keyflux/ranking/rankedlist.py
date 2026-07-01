"""Ranked lists with tied-average ranks and tied-last handling for exclusives.

A ``RankedList`` maps each type to a 1-based rank (rank 1 = most frequent).
Types that tie on count share the average of the ranks they span. When two
ranked lists are aligned for comparison, a type present in one list but absent
from the other is placed at a tied-last rank — the average of the unused tail
positions — exactly as in the allotaxonometry reference (Dodds et al. 2020).
This is the bridge type consumed by both :func:`keyflux.divergence.rtd.rtd` and
:func:`keyflux.viz.allotaxonograph.allotaxonograph`.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from keyflux.keyness.keyness import Keyness


def average_ranks(counts: Mapping[str, float]) -> dict[str, float]:
    """Rank types by descending count, averaging ties (fractional ranking).

    Args:
        counts: Mapping of type to count. The highest count gets rank 1.

    Returns:
        A dict mapping each type to its 1-based rank; tied counts share the
        average of the ranks they would occupy.

    Contract:
        - The highest count maps to the smallest rank.
        - A group of ``g`` tied types occupying ranks ``i..i+g-1`` each receive
          their average, ``i + (g - 1) / 2``.
        - The ranks sum to ``n (n + 1) / 2`` for ``n`` types (rank-sum identity).

    Examples:
        >>> average_ranks({"a": 5, "b": 5, "c": 1})
        {'a': 1.5, 'b': 1.5, 'c': 3.0}
    """
    ordered = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    ranks: dict[str, float] = {}
    i = 0
    n = len(ordered)
    while i < n:
        j = i
        while j < n and ordered[j][1] == ordered[i][1]:
            j += 1
        # Types ordered[i:j] tie; they occupy 1-based ranks (i+1)..j.
        average = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[ordered[k][0]] = average
        i = j
    return ranks


@dataclass(frozen=True, slots=True)
class RankedList:
    """A type-to-rank mapping derived from counts or scores.

    Attributes:
        ranks: Type-to-rank mapping within this list's own domain (average ties).
        counts: The values the ranks were derived from — frequency counts
            (:meth:`from_counts`) or arbitrary scores (:meth:`from_scores`).
            Used by :meth:`aligned` to place a type absent from the other list at
            a tied-last rank, so scores should be non-negative "prominence"
            values for that comparison semantics to hold.
        total: Sum of the values.
        label: An optional label (e.g. a time period) for plots and results.
    """

    ranks: Mapping[str, float]
    counts: Mapping[str, float]
    total: float
    label: str = field(default="")

    @classmethod
    def from_counts(cls, counts: Mapping[str, int], *, label: str = "") -> RankedList:
        """Build a ranked list by ranking types on descending frequency.

        Args:
            counts: Mapping of type to (positive) count.
            label: Optional label for the list.

        Returns:
            A ``RankedList`` whose ranks average tied counts.

        Raises:
            ValueError: If ``counts`` is empty.

        Examples:
            >>> r = RankedList.from_counts({"the": 100, "cat": 100, "sat": 5})
            >>> r.ranks["sat"]
            3.0
            >>> r.ranks["the"]
            1.5
        """
        if not counts:
            msg = "Cannot build a RankedList from empty counts."
            raise ValueError(msg)
        plain = dict(counts)
        return cls(
            ranks=average_ranks(plain),
            counts=plain,
            total=sum(plain.values()),
            label=label,
        )

    @classmethod
    def from_scores(cls, scores: Mapping[str, float], *, label: str = "") -> RankedList:
        """Build a ranked list by ranking types on descending score.

        Ranks by any numeric metric — keyness score, log ratio, salience — so a
        keyword ranking (or any other) can be compared like a frequency ranking.

        Args:
            scores: Mapping of type to score. The highest score gets rank 1.
                Scores are treated as prominence: when two lists are aligned, a
                type absent from one gets score 0 there (tied-last), so
                non-negative scores keep that behaviour intuitive.
            label: Optional label for the list.

        Returns:
            A ``RankedList`` whose ranks average tied scores.

        Raises:
            ValueError: If ``scores`` is empty.

        Examples:
            >>> r = RankedList.from_scores({"climate": 6.4, "carbon": 5.8, "the": 0.1})
            >>> r.ranks["climate"], r.ranks["the"]
            (1.0, 3.0)
        """
        if not scores:
            msg = "Cannot build a RankedList from empty scores."
            raise ValueError(msg)
        plain = dict(scores)
        return cls(
            ranks=average_ranks(plain),
            counts=plain,
            total=sum(plain.values()),
            label=label,
        )

    @classmethod
    def from_keyness(
        cls, keyness: Keyness, *, side: str = "focus", label: str = ""
    ) -> RankedList:
        """Build a ranked list from one side of a :class:`Keyness` object.

        Args:
            keyness: A Keyness comparison.
            side: ``"focus"`` or ``"reference"`` — which corpus to rank.
            label: Optional label; defaults to the side name.

        Returns:
            A ``RankedList`` over the chosen corpus's counts.

        Raises:
            ValueError: If ``side`` is not "focus" or "reference".

        Examples:
            >>> from collections import Counter
            >>> from keyflux.keyness.keyness import Keyness
            >>> k = Keyness(Counter({"a": 30, "b": 10}), Counter({"a": 5, "b": 9}),
            ...             min_focus_freq=1, min_reference_freq=1)
            >>> RankedList.from_keyness(k).ranks["a"]
            1.0
        """
        if side == "focus":
            counts: Mapping[str, int] = keyness.focus
        elif side == "reference":
            counts = keyness.reference
        else:
            msg = f"side must be 'focus' or 'reference', got {side!r}."
            raise ValueError(msg)
        return cls.from_counts(counts, label=label or side)

    def types(self) -> set[str]:
        """Return the set of types in this list.

        Examples:
            >>> sorted(RankedList.from_counts({"a": 2, "b": 1}).types())
            ['a', 'b']
        """
        return set(self.ranks)

    def rank_of(self, type_: str, *, last_rank: float | None = None) -> float:
        """Return the rank of a type, or a fallback for an absent type.

        Args:
            type_: The type to look up.
            last_rank: Rank to return when ``type_`` is absent; if None, the
                next rank past the last (``len(ranks) + 1``) is used.

        Returns:
            The type's rank, or the fallback for an absent type.

        Examples:
            >>> r = RankedList.from_counts({"a": 2, "b": 1})
            >>> r.rank_of("a")
            1.0
            >>> r.rank_of("z", last_rank=99.0)
            99.0
        """
        if type_ in self.ranks:
            return self.ranks[type_]
        return last_rank if last_rank is not None else float(len(self.ranks) + 1)

    def aligned(self, other: RankedList) -> tuple[list[str], list[float], list[float]]:
        """Align two lists over their combined domain with tied-last exclusives.

        Both lists are re-ranked over the union of their types. A type absent
        from a list is given count 0 there, so all of that list's exclusives tie
        at the bottom and receive the average of the unused tail ranks. This is
        the single place vocabulary union and tied-last ranking happen, so the
        divergence metric and the allotaxonograph always agree.

        Args:
            other: The list to align against.

        Returns:
            ``(types, ranks_self, ranks_other)`` — the union types and each
            list's combined-domain rank for every type, index-aligned.

        Contract:
            - ``types`` is the sorted union of both lists' types.
            - A type present in only one list gets a tied-last (averaged)
              rank in the other.
            - Present types keep the rank they have within their own list.

        Examples:
            >>> r1 = RankedList.from_counts({"a": 10, "b": 5})
            >>> r2 = RankedList.from_counts({"b": 8, "c": 2})
            >>> types, s, o = r1.aligned(r2)
            >>> types
            ['a', 'b', 'c']
            >>> s[types.index("c")] == o[types.index("a")]  # both tied-last (3.0)
            True
        """
        union = sorted(self.types() | other.types())
        vec_self = {t: self.counts.get(t, 0) for t in union}
        vec_other = {t: other.counts.get(t, 0) for t in union}
        ranks_self = average_ranks(vec_self)
        ranks_other = average_ranks(vec_other)
        return (
            union,
            [ranks_self[t] for t in union],
            [ranks_other[t] for t in union],
        )

    def __len__(self) -> int:
        return len(self.ranks)
