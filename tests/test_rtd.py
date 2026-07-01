"""Tests for keyflux.divergence.rtd.

The headline regression is the jkbren/rank-turbulence-divergence reference
value 0.45924793111057804 at alpha=1.0.
"""

import math

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from keyflux.datasets import load_jkbren_example
from keyflux.divergence.rtd import rtd
from keyflux.ranking.rankedlist import RankedList
from tests.strategies import alpha_value, ranked_list, ranked_pair

JKBREN_TARGET = 0.45924793111057804


class TestRegression:
    """Reproduce the jkbren reference value exactly."""

    def test_jkbren_alpha_one(self) -> None:
        r1, r2 = load_jkbren_example()
        assert rtd(r1, r2, alpha=1.0).divergence == pytest.approx(
            JKBREN_TARGET, abs=1e-12
        )

    def test_raw_unnormalised_is_stable(self) -> None:
        r1, r2 = load_jkbren_example()
        result = rtd(r1, r2, alpha=1.0, normalize=False)
        assert result.raw == pytest.approx(6.0214664, abs=1e-6)


class TestCoreProperties:
    """Identity, bounds, symmetry, and the alpha->0 limit."""

    def test_self_divergence_is_zero(self) -> None:
        r1, _ = load_jkbren_example()
        assert rtd(r1, r1, alpha=1.0).divergence == 0.0

    def test_alpha_zero_uses_log_limit(self) -> None:
        r1, r2 = load_jkbren_example()
        limit = rtd(r1, r2, alpha=0.0).divergence
        near = rtd(r1, r2, alpha=1e-7).divergence
        assert limit == pytest.approx(near, abs=1e-4)
        assert math.isfinite(limit)

    def test_contributions_sum_to_divergence(self) -> None:
        r1, r2 = load_jkbren_example()
        result = rtd(r1, r2, alpha=1.0 / 3.0)
        assert math.fsum(c.contribution for c in result.contributions) == pytest.approx(
            result.divergence
        )

    def test_contributions_sorted_descending(self) -> None:
        r1, r2 = load_jkbren_example()
        contribs = [c.contribution for c in rtd(r1, r2).contributions]
        assert contribs == sorted(contribs, reverse=True)

    def test_disjoint_lists_are_finite(self) -> None:
        r1 = RankedList.from_counts({"a": 3, "b": 2, "c": 1})
        r2 = RankedList.from_counts({"x": 3, "y": 2, "z": 1})
        div = rtd(r1, r2, alpha=1.0 / 3.0).divergence
        assert 0.0 <= div <= 1.0


class TestDefaults:
    """Pin the documented default parameters."""

    def test_default_alpha_is_one_third(self) -> None:
        r1, r2 = load_jkbren_example()
        assert rtd(r1, r2).divergence == rtd(r1, r2, alpha=1.0 / 3.0).divergence
        assert rtd(r1, r2).divergence != rtd(r1, r2, alpha=1.0).divergence

    def test_normalize_default_is_true(self) -> None:
        r1, r2 = load_jkbren_example()
        assert (
            rtd(r1, r2, alpha=1.0).divergence
            == rtd(r1, r2, alpha=1.0, normalize=True).divergence
        )
        # With normalize off, divergence falls back to the raw (un-normalised) sum.
        assert rtd(r1, r2, alpha=1.0, normalize=False).divergence > 1.0


class TestValidation:
    """Input validation."""

    def test_negative_alpha_raises(self) -> None:
        r1, r2 = load_jkbren_example()
        with pytest.raises(ValueError, match="non-negative"):
            rtd(r1, r2, alpha=-0.5)


class TestRTDProperties:
    """Property-based contracts over random ranked lists."""

    @settings(max_examples=150, deadline=None)
    @given(ranked_pair(), alpha_value)
    def test_bounded_unit_interval(self, pair, alpha: float) -> None:
        r1, r2 = pair
        div = rtd(r1, r2, alpha=alpha).divergence
        assert -1e-9 <= div <= 1.0 + 1e-9

    @settings(max_examples=150, deadline=None)
    @given(ranked_pair(), alpha_value)
    def test_symmetry(self, pair, alpha: float) -> None:
        r1, r2 = pair
        forward = rtd(r1, r2, alpha=alpha).divergence
        backward = rtd(r2, r1, alpha=alpha).divergence
        assert forward == pytest.approx(backward, abs=1e-9)

    @settings(max_examples=100, deadline=None)
    @given(ranked_list(), alpha_value)
    def test_identity_is_zero(self, r, alpha: float) -> None:
        assert rtd(r, r, alpha=alpha).divergence == pytest.approx(0.0, abs=1e-9)

    @settings(max_examples=150, deadline=None)
    @given(ranked_pair(), st.floats(min_value=0.0, max_value=3.0, allow_nan=False))
    def test_never_raises(self, pair, alpha: float) -> None:
        r1, r2 = pair
        rtd(r1, r2, alpha=alpha)
