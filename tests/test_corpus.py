"""Tests for keyflux.io.corpus."""

from collections import Counter

import pytest

from keyflux.io.corpus import counts_from_text, counts_from_tokens, load_counts


class TestCountsFromTokens:
    """Counting an already-tokenised iterable."""

    def test_lowercases_by_default(self) -> None:
        assert counts_from_tokens(["The", "the", "CAT"]) == Counter(
            {"the": 2, "cat": 1}
        )

    def test_preserves_case_when_disabled(self) -> None:
        assert counts_from_tokens(["The", "the"], lowercase=False) == Counter(
            {"The": 1, "the": 1}
        )


class TestCountsFromText:
    """Tokenising and counting a raw string."""

    def test_basic_tokenisation(self) -> None:
        counts = counts_from_text("The cat sat. The dog ran.")
        assert counts["the"] == 2
        assert counts["cat"] == 1

    def test_strips_punctuation(self) -> None:
        assert "." not in counts_from_text("a, b. c!")


class TestLoadCounts:
    """Reading a count file into a Counter."""

    def test_tab_separated(self, tmp_path) -> None:
        p = tmp_path / "counts.tsv"
        p.write_text("climate\t30\ncarbon\t12\n")
        assert load_counts(p) == Counter({"climate": 30, "carbon": 12})

    def test_one_token_per_line(self, tmp_path) -> None:
        p = tmp_path / "tokens.txt"
        p.write_text("a\nb\na\n")
        assert load_counts(p) == Counter({"a": 2, "b": 1})

    def test_non_integer_count_raises(self, tmp_path) -> None:
        p = tmp_path / "bad.tsv"
        p.write_text("climate\tlots\n")
        with pytest.raises(ValueError, match="Non-integer"):
            load_counts(p)

    def test_missing_file_raises(self, tmp_path) -> None:
        with pytest.raises(FileNotFoundError):
            load_counts(tmp_path / "nope.tsv")
