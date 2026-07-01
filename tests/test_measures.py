"""Tests for keyflux.keyness.measures.

The headline numbers are validated against Brezina, *Statistics in Corpus
Linguistics* (2018), Ch. 3, the worked ``war`` example in AmE06 vs BE06
(AmE06 = 1,017,879 tokens; BE06 = 1,007,532 tokens).
"""

import math

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from keyflux.keyness.measures import (
    CHI2_CRITICAL,
    chi_square,
    expected_counts,
    log_likelihood,
    log_ratio,
    percent_diff,
    significance_band,
    simple_maths,
)

# Brezina's worked example: war in AmE06 (focus) vs BE06 (reference).
WAR = (620, 267, 1_017_879, 1_007_532)


class TestExpectedCounts:
    """Expected counts redistribute the observed total by corpus size."""

    def test_brezina_war(self) -> None:
        e_c, e_r = expected_counts(*WAR)
        assert e_c == pytest.approx(445.77, abs=0.01)
        assert e_r == pytest.approx(441.23, abs=0.01)

    def test_sum_equals_observed_total(self) -> None:
        a, b = 30, 12
        e_c, e_r = expected_counts(a, b, 5000, 8000)
        assert e_c + e_r == pytest.approx(a + b)

    def test_empty_corpora_raise(self) -> None:
        with pytest.raises(ValueError, match="empty"):
            expected_counts(0, 0, 0, 0)


class TestLogLikelihood:
    """Dunning's G2, validated against Brezina's worked value of 140.87."""

    def test_brezina_war(self) -> None:
        assert log_likelihood(*WAR) == pytest.approx(140.87, abs=0.01)

    def test_hand_checked_2x2(self) -> None:
        # a=10, b=2, N_C=N_R=1000 -> E_C=E_R=6.0
        # 2*(10*ln(10/6) + 2*ln(2/6)) = 2*(5.1083 - 2.1972) = 5.8221
        assert log_likelihood(10, 2, 1000, 1000) == pytest.approx(5.8221, abs=1e-4)

    def test_zero_when_rates_equal(self) -> None:
        assert log_likelihood(10, 10, 1000, 1000) == pytest.approx(0.0)

    def test_both_absent_is_zero(self) -> None:
        assert log_likelihood(0, 0, 1000, 1000) == 0.0

    def test_exclusive_is_finite(self) -> None:
        assert math.isfinite(log_likelihood(50, 0, 1000, 1000))


class TestLogRatio:
    """Log ratio effect size (Hardie 2014)."""

    def test_brezina_war(self) -> None:
        # RF_C/RF_R = 609.11 / 265.00 = 2.30 -> log2(2.30) = 1.20
        assert log_ratio(*WAR) == pytest.approx(1.20, abs=0.01)

    def test_hand_checked(self) -> None:
        # log2((10/1000)/(2/1000)) = log2(5) = 2.3219
        assert log_ratio(10, 2, 1000, 1000) == pytest.approx(2.3219, abs=1e-4)

    def test_sign_flips_on_swap(self) -> None:
        lr = log_ratio(10, 2, 1000, 1000)
        assert log_ratio(2, 10, 1000, 1000) == pytest.approx(-lr)

    def test_zero_cell_uses_floor(self) -> None:
        # b=0 -> floored to 0.5; result must be finite and large-positive.
        value = log_ratio(50, 0, 1000, 1000, floor=0.5)
        assert math.isfinite(value)
        assert value == pytest.approx(math.log2((50 / 1000) / (0.5 / 1000)))


class TestSimpleMaths:
    """Simple Maths parameter (Kilgarriff 2009), k=100 by default."""

    def test_brezina_war_with_rf(self) -> None:
        # Using true per-million RF (609.11, 265.00): (609.11+100)/(265.00+100).
        # Brezina's text shows 1.96 by plugging in the absolute frequencies
        # 620/267 directly (valid only because both corpora are ~1M tokens).
        assert simple_maths(*WAR) == pytest.approx(1.94, abs=0.01)

    def test_equal_rates_is_one(self) -> None:
        assert simple_maths(5, 5, 1000, 1000) == pytest.approx(1.0)

    def test_always_finite_for_exclusive(self) -> None:
        assert math.isfinite(simple_maths(50, 0, 1000, 1000))


class TestPercentDiff:
    """%DIFF (Gabrielatos & Marchi 2012)."""

    def test_brezina_war(self) -> None:
        # (609.11 - 265.00) / 265.00 * 100 = 129.85
        assert percent_diff(*WAR) == pytest.approx(129.85, abs=0.05)

    def test_zero_when_equal(self) -> None:
        assert percent_diff(10, 10, 1000, 1000) == pytest.approx(0.0)


class TestChiSquare:
    """Pearson chi-square, for contrast only."""

    def test_hand_checked_war(self) -> None:
        assert chi_square(*WAR) == pytest.approx(136.96, abs=0.05)

    def test_zero_when_equal(self) -> None:
        assert chi_square(10, 10, 1000, 1000) == pytest.approx(0.0)

    def test_rejects_impossible_count(self) -> None:
        with pytest.raises(ValueError, match="more often"):
            chi_square(2000, 1, 1000, 1000)


class TestSignificanceBand:
    """Bands match the chi-square critical values at 1 d.f."""

    def test_brezina_war_is_strongest(self) -> None:
        assert significance_band(log_likelihood(*WAR)) == "p0001"

    @pytest.mark.parametrize(
        ("value", "band"),
        [
            (3.83, "ns"),
            (3.84, "p05"),
            (6.62, "p05"),
            (6.63, "p01"),
            (10.83, "p001"),
            (15.13, "p0001"),
            (1000.0, "p0001"),
        ],
    )
    def test_thresholds(self, value: float, band: str) -> None:
        assert significance_band(value) == band


class TestMeasureProperties:
    """Property-based contracts for the measures."""

    @settings(max_examples=200)
    @given(
        st.integers(min_value=0, max_value=10_000),
        st.integers(min_value=0, max_value=10_000),
        st.integers(min_value=1, max_value=1_000_000),
        st.integers(min_value=1, max_value=1_000_000),
    )
    def test_log_likelihood_non_negative(
        self, a: int, b: int, n_focus: int, n_reference: int
    ) -> None:
        assert log_likelihood(a, b, n_focus, n_reference) >= -1e-9

    @settings(max_examples=200)
    @given(
        st.integers(min_value=0, max_value=900),
        st.integers(min_value=0, max_value=900),
    )
    def test_chi_square_non_negative(self, a: int, b: int) -> None:
        assert chi_square(a, b, 1000, 1000) >= -1e-9

    @settings(max_examples=200)
    @given(
        st.floats(min_value=0.0, max_value=1000.0, allow_nan=False),
        st.floats(min_value=0.0, max_value=1000.0, allow_nan=False),
    )
    def test_significance_band_monotone(self, x: float, y: float) -> None:
        lo, hi = sorted((x, y))
        order = ("ns", "p05", "p01", "p001", "p0001")
        assert order.index(significance_band(lo)) <= order.index(significance_band(hi))

    @settings(max_examples=200)
    @given(
        st.integers(min_value=1, max_value=10_000),
        st.integers(min_value=1, max_value=10_000),
        st.integers(min_value=1, max_value=1_000_000),
        st.integers(min_value=1, max_value=1_000_000),
    )
    def test_log_ratio_antisymmetric(
        self, a: int, b: int, n_focus: int, n_reference: int
    ) -> None:
        forward = log_ratio(a, b, n_focus, n_reference)
        backward = log_ratio(b, a, n_reference, n_focus)
        assert forward == pytest.approx(-backward)

    def test_critical_values_are_canonical(self) -> None:
        assert CHI2_CRITICAL == {
            "p05": 3.84,
            "p01": 6.63,
            "p001": 10.83,
            "p0001": 15.13,
        }


class TestDefaultArguments:
    """Pin the documented default parameters (floor=0.5, k=100)."""

    def test_log_ratio_default_floor_is_half(self) -> None:
        # The default floor must be 0.5: an exclusive's value is pinned by it.
        assert log_ratio(50, 0, 1000, 1000) == log_ratio(50, 0, 1000, 1000, floor=0.5)
        assert log_ratio(50, 0, 1000, 1000) != log_ratio(50, 0, 1000, 1000, floor=1.0)

    def test_percent_diff_default_floor_is_half(self) -> None:
        assert percent_diff(0, 50, 1000, 1000) == percent_diff(
            0, 50, 1000, 1000, floor=0.5
        )
        assert percent_diff(0, 50, 1000, 1000) != percent_diff(
            0, 50, 1000, 1000, floor=1.0
        )

    def test_simple_maths_default_k_is_hundred(self) -> None:
        assert simple_maths(620, 267, 1_017_879, 1_007_532) == simple_maths(
            620, 267, 1_017_879, 1_007_532, k=100.0
        )
        assert simple_maths(620, 267, 1_017_879, 1_007_532) != simple_maths(
            620, 267, 1_017_879, 1_007_532, k=10.0
        )
