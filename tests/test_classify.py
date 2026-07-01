"""Tests for keyflux.keyness.classify."""

from keyflux.keyness.classify import (
    classify_direction,
    classify_row,
    is_significant,
    partition,
)
from keyflux.keyness.keyness import KeynessRow


def _row(name: str, ll: float, lr: float, sig: str, direction: str) -> KeynessRow:
    return KeynessRow(name, 1, 1, 1.0, 1.0, ll, lr, sig, ll, direction)  # type: ignore[arg-type]


class TestIsSignificant:
    """Significance-band threshold comparison."""

    def test_ns_never_significant(self) -> None:
        assert not is_significant("ns")

    def test_default_threshold(self) -> None:
        assert is_significant("p05")
        assert is_significant("p0001")

    def test_custom_threshold(self) -> None:
        assert not is_significant("p05", min_significance="p01")
        assert is_significant("p001", min_significance="p01")


class TestClassifyDirection:
    """Polarity from relative frequencies."""

    def test_positive(self) -> None:
        assert classify_direction(0.003, 0.001) == "positive"

    def test_negative(self) -> None:
        assert classify_direction(0.001, 0.003) == "negative"

    def test_neutral(self) -> None:
        assert classify_direction(0.002, 0.002) == "neutral"

    def test_swap_flips(self) -> None:
        assert classify_direction(0.001, 0.003) == "negative"
        assert classify_direction(0.003, 0.001) == "positive"


class TestClassifyRow:
    """Bucketing a row into keyword(+/-), lockword, or other."""

    def test_positive_keyword(self) -> None:
        assert classify_row(_row("w", 140.0, 1.2, "p0001", "positive")) == "keyword+"

    def test_negative_keyword(self) -> None:
        assert classify_row(_row("w", 140.0, -1.2, "p0001", "negative")) == "keyword-"

    def test_lockword(self) -> None:
        assert classify_row(_row("the", 1.5, 0.01, "ns", "positive")) == "lockword"

    def test_other_when_unstable_and_insignificant(self) -> None:
        assert classify_row(_row("w", 2.0, 3.0, "ns", "positive")) == "other"


class TestPartition:
    """Grouping rows by category."""

    def test_disjoint_and_exhaustive(self) -> None:
        rows = [
            _row("kw+", 140.0, 1.2, "p0001", "positive"),
            _row("kw-", 140.0, -1.2, "p0001", "negative"),
            _row("lock", 1.5, 0.01, "ns", "positive"),
            _row("other", 2.0, 3.0, "ns", "positive"),
        ]
        buckets = partition(rows)
        total = sum(len(v) for v in buckets.values())
        assert total == len(rows)
        assert set(buckets) == {"keyword+", "keyword-", "lockword", "other"}

    def test_all_keys_present_even_when_empty(self) -> None:
        buckets = partition([])
        assert set(buckets) == {"keyword+", "keyword-", "lockword", "other"}
        assert all(v == [] for v in buckets.values())
