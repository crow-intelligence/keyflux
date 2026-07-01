"""Tests for keyflux.ranking.rankedlist."""

from collections import Counter

import pytest
from hypothesis import given, settings

from keyflux.keyness.keyness import Keyness
from keyflux.ranking.rankedlist import RankedList, average_ranks
from tests.strategies import freq_counter, ranked_list


class TestAverageRanks:
    """Fractional (average) ranking by descending count."""

    def test_no_ties(self) -> None:
        assert average_ranks({"a": 3, "b": 2, "c": 1}) == {"a": 1.0, "b": 2.0, "c": 3.0}

    def test_tied_pair_averaged(self) -> None:
        # a and b tie for ranks 1,2 -> 1.5 each; c gets rank 3.
        assert average_ranks({"a": 5, "b": 5, "c": 1}) == {
            "a": 1.5,
            "b": 1.5,
            "c": 3.0,
        }

    def test_all_tied(self) -> None:
        ranks = average_ranks({"a": 2, "b": 2, "c": 2})
        assert set(ranks.values()) == {2.0}

    @settings(max_examples=100)
    @given(freq_counter())
    def test_rank_sum_identity(self, counts: Counter[str]) -> None:
        ranks = average_ranks(counts)
        n = len(counts)
        assert sum(ranks.values()) == pytest.approx(n * (n + 1) / 2)


class TestFromCounts:
    """Building a RankedList from counts."""

    def test_basic_ranks(self) -> None:
        r = RankedList.from_counts({"the": 100, "cat": 5})
        assert r.ranks == {"the": 1.0, "cat": 2.0}
        assert r.total == 105

    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError, match="empty"):
            RankedList.from_counts({})


class TestFromKeyness:
    """RankedList.from_keyness mirrors from_counts on the chosen side."""

    def test_focus_matches_from_counts(self) -> None:
        focus = Counter({"a": 30, "b": 10, "c": 4})
        reference = Counter({"a": 5, "b": 9})
        k = Keyness(focus, reference, min_focus_freq=1, min_reference_freq=1)
        from_keyness = RankedList.from_keyness(k, side="focus")
        from_counts = RankedList.from_counts(focus)
        assert from_keyness.ranks == from_counts.ranks

    def test_invalid_side_raises(self) -> None:
        k = Keyness(Counter({"a": 5}), Counter({"a": 3}), min_reference_freq=1)
        with pytest.raises(ValueError, match="focus.*reference"):
            RankedList.from_keyness(k, side="bogus")


class TestFromScores:
    """Ranking by an arbitrary numeric score."""

    def test_ranks_by_descending_score(self) -> None:
        r = RankedList.from_scores({"climate": 6.4, "carbon": 5.8, "the": 0.1})
        assert r.ranks == {"climate": 1.0, "carbon": 2.0, "the": 3.0}

    def test_tied_scores_average(self) -> None:
        r = RankedList.from_scores({"a": 2.0, "b": 2.0, "c": 1.0})
        assert r.ranks["a"] == 1.5
        assert r.ranks["b"] == 1.5
        assert r.ranks["c"] == 3.0

    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError, match="empty"):
            RankedList.from_scores({})

    def test_matches_from_counts_ordering(self) -> None:
        # from_scores on integer-like scores reproduces from_counts ranks.
        counts = {"a": 30, "b": 10, "c": 4}
        assert (
            RankedList.from_scores(counts).ranks == RankedList.from_counts(counts).ranks
        )


class TestAligned:
    """Combined-domain alignment with tied-last ranks for exclusives."""

    def test_union_is_sorted(self) -> None:
        r1 = RankedList.from_counts({"b": 2, "a": 1})
        r2 = RankedList.from_counts({"c": 3})
        types, _, _ = r1.aligned(r2)
        assert types == ["a", "b", "c"]

    def test_single_exclusive_gets_last_rank(self) -> None:
        # r1 has {a,b}; c is exclusive to r2 -> in r1, c ties last at rank 3.
        r1 = RankedList.from_counts({"a": 10, "b": 5})
        r2 = RankedList.from_counts({"b": 8, "c": 2})
        types, ranks1, ranks2 = r1.aligned(r2)
        assert ranks1[types.index("c")] == 3.0

    def test_multiple_exclusives_averaged(self) -> None:
        # r2 has two types absent from r1 (c, d); they share ranks 3,4 -> 3.5.
        r1 = RankedList.from_counts({"a": 10, "b": 5})
        r2 = RankedList.from_counts({"c": 8, "d": 2})
        types, ranks1, _ = r1.aligned(r2)
        assert ranks1[types.index("c")] == 3.5
        assert ranks1[types.index("d")] == 3.5

    def test_present_types_keep_their_rank(self) -> None:
        r1 = RankedList.from_counts({"a": 10, "b": 5, "z": 1})
        r2 = RankedList.from_counts({"a": 1})
        types, ranks1, _ = r1.aligned(r2)
        assert ranks1[types.index("a")] == 1.0


class TestRankOf:
    """rank_of lookup and fallback."""

    def test_present(self) -> None:
        assert RankedList.from_counts({"a": 2, "b": 1}).rank_of("a") == 1.0

    def test_absent_default(self) -> None:
        assert RankedList.from_counts({"a": 2}).rank_of("z") == 2.0

    def test_absent_custom(self) -> None:
        assert RankedList.from_counts({"a": 2}).rank_of("z", last_rank=50.0) == 50.0


class TestRankedListProperties:
    """Property-based contracts."""

    @settings(max_examples=100)
    @given(ranked_list())
    def test_ranks_in_valid_window(self, r: RankedList) -> None:
        n = len(r)
        for rank in r.ranks.values():
            assert 1.0 <= rank <= n
