"""Tests for keyflux.datasets."""

from collections import Counter

from keyflux.datasets import load_demo_pair
from keyflux.keyness.keyness import Keyness


class TestDemoPair:
    """The bundled demo corpus pair."""

    def test_returns_two_counters(self) -> None:
        focus, reference = load_demo_pair()
        assert isinstance(focus, Counter)
        assert isinstance(reference, Counter)

    def test_independent_copies(self) -> None:
        focus1, _ = load_demo_pair()
        focus2, _ = load_demo_pair()
        focus1["climate"] += 1000
        assert focus2["climate"] == 42

    def test_runs_through_keyness(self) -> None:
        focus, reference = load_demo_pair()
        k = Keyness(focus, reference, min_focus_freq=1, min_reference_freq=1)
        assert "climate" in {r.type for r in k.keywords().positive()}
        assert "the" in {r.type for r in k.lockwords()}
