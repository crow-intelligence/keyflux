"""Tests for keyflux.keyness.keyness (Keyness, KeywordTable, ReproRecord)."""

from collections import Counter

import pytest

from keyflux.datasets import load_demo_pair
from keyflux.keyness.keyness import Keyness


class TestKeywords:
    """Keyword extraction, ordering, and direction."""

    def test_positive_keyword_detected(self, tiny_focus, tiny_reference) -> None:
        k = Keyness(tiny_focus, tiny_reference, min_focus_freq=1, min_reference_freq=1)
        positive = {r.type for r in k.keywords().positive()}
        assert "climate" in positive

    def test_negative_keyword_detected(self, tiny_focus, tiny_reference) -> None:
        k = Keyness(tiny_focus, tiny_reference, min_focus_freq=1, min_reference_freq=1)
        negative = {r.type for r in k.keywords().negative()}
        assert "market" in negative

    def test_keywords_sorted_by_abs_effect_size(self) -> None:
        focus = Counter({"climate": 300, "carbon": 80, "the": 800})
        reference = Counter({"climate": 30, "carbon": 60, "the": 790})
        k = Keyness(focus, reference)
        rows = list(k.keywords())
        sizes = [abs(r.effect_size) for r in rows]
        assert sizes == sorted(sizes, reverse=True)

    def test_top_limits_count(self) -> None:
        focus, reference = load_demo_pair()
        k = Keyness(focus, reference, min_focus_freq=1, min_reference_freq=1)
        assert len(k.keywords(top=2)) == 2

    def test_all_keywords_are_significant(self) -> None:
        focus, reference = load_demo_pair()
        k = Keyness(focus, reference, min_focus_freq=1, min_reference_freq=1)
        for row in k.keywords():
            assert row.significance != "ns"
            assert row.direction != "neutral"


class TestLockwords:
    """Lockwords are stable, frequent, near-parity types present in both corpora."""

    def test_function_word_is_lockword(self) -> None:
        focus, reference = load_demo_pair()
        k = Keyness(focus, reference, min_focus_freq=1, min_reference_freq=1)
        lock = {r.type for r in k.lockwords()}
        assert "the" in lock

    def test_lockwords_require_presence_in_both(self) -> None:
        focus = Counter({"solo": 100, "the": 500})
        reference = Counter({"the": 500})
        k = Keyness(focus, reference, min_focus_freq=1, min_reference_freq=1)
        assert "solo" not in {r.type for r in k.lockwords()}

    def test_keywords_and_lockwords_disjoint(self) -> None:
        focus, reference = load_demo_pair()
        k = Keyness(focus, reference, min_focus_freq=1, min_reference_freq=1)
        kw = {r.type for r in k.keywords()}
        lw = {r.type for r in k.lockwords()}
        assert kw.isdisjoint(lw)


class TestLockwordThresholds:
    """Pin the lockword default thresholds against boundary mutations."""

    def _corpus(self) -> tuple[Counter[str], Counter[str]]:
        # "the": near parity, frequent -> lockword.
        # "mid": |log ratio| == 1.0 (twice as frequent), not significant.
        # "rare": parity but only 3 in each (below min_freq_both=5).
        focus = Counter({"the": 5000, "mid": 10, "rare": 3})
        reference = Counter({"the": 5000, "mid": 5, "rare": 3})
        return focus, reference

    def test_log_ratio_ceiling_excludes_mid(self) -> None:
        # |log ratio| of "mid" is 1.0, above the default 0.5 ceiling.
        focus, reference = self._corpus()
        k = Keyness(focus, reference, min_focus_freq=1, min_reference_freq=1)
        lock = {r.type for r in k.lockwords()}
        assert "the" in lock
        assert "mid" not in lock

    def test_raising_ceiling_admits_mid(self) -> None:
        focus, reference = self._corpus()
        k = Keyness(focus, reference, min_focus_freq=1, min_reference_freq=1)
        assert "mid" in {r.type for r in k.lockwords(max_abs_log_ratio=1.5)}

    def test_min_freq_both_excludes_rare(self) -> None:
        focus, reference = self._corpus()
        k = Keyness(focus, reference, min_focus_freq=1, min_reference_freq=1)
        # "rare" is at parity but only 3 in each, below the default min_freq_both=5.
        assert "rare" not in {r.type for r in k.lockwords()}
        assert "rare" in {r.type for r in k.lockwords(min_freq_both=2)}


class TestSwapSymmetry:
    """Swapping focus and reference flips keyword polarity, preserves lockwords."""

    def test_positive_and_negative_swap(self) -> None:
        focus, reference = load_demo_pair()
        forward = Keyness(focus, reference, min_focus_freq=1, min_reference_freq=1)
        backward = Keyness(reference, focus, min_focus_freq=1, min_reference_freq=1)
        fwd_pos = {r.type for r in forward.keywords().positive()}
        bwd_neg = {r.type for r in backward.keywords().negative()}
        assert fwd_pos == bwd_neg

    def test_lockwords_unchanged_by_swap(self) -> None:
        focus, reference = load_demo_pair()
        forward = Keyness(focus, reference, min_focus_freq=1, min_reference_freq=1)
        backward = Keyness(reference, focus, min_focus_freq=1, min_reference_freq=1)
        assert {r.type for r in forward.lockwords()} == {
            r.type for r in backward.lockwords()
        }


class TestMinFrequencyCutoffs:
    """Cutoffs exclude under-evidenced absent words from the scored table."""

    def test_absent_word_excluded(self) -> None:
        # "rincewind": absent in focus, only 3 in reference, both cutoffs at 5.
        focus = Counter({"common": 100})
        reference = Counter({"common": 90, "rincewind": 3})
        k = Keyness(focus, reference, min_focus_freq=5, min_reference_freq=5)
        assert "rincewind" not in {r.type for r in k.table()}

    def test_focus_exclusive_keyword_kept(self) -> None:
        # "defense": 120 in focus, only 1 in reference -> still a positive keyword.
        focus = Counter({"defense": 120, "the": 500})
        reference = Counter({"defense": 1, "the": 500})
        k = Keyness(focus, reference, min_focus_freq=5, min_reference_freq=5)
        assert "defense" in {r.type for r in k.keywords().positive()}


class TestReproRecord:
    """The reproducibility record captures the governing parameters."""

    def test_to_dict_complete(self) -> None:
        focus, reference = load_demo_pair()
        k = Keyness(focus, reference, measure="log_ratio", reference_id="demo-R")
        record = k.keywords(top=10).repro.to_dict()
        assert record["reference_id"] == "demo-R"
        assert record["measure"] == "log_ratio"
        assert record["top_n"] == 10
        assert record["focus_total"] == sum(focus.values())
        assert "keyflux_version" in record

    def test_unbounded_top_is_none(self) -> None:
        focus, reference = load_demo_pair()
        k = Keyness(focus, reference)
        assert k.keywords().repro.top_n is None


class TestValidation:
    """Constructor and measure validation."""

    def test_unknown_measure_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown measure"):
            Keyness(Counter({"a": 1}), Counter({"a": 1}), measure="bogus")  # type: ignore[arg-type]

    def test_empty_corpus_raises(self) -> None:
        with pytest.raises(ValueError, match="non-empty"):
            Keyness(Counter(), Counter({"a": 1}))
