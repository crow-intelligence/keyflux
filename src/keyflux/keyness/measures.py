"""Keyness association measures as pure functions.

Each measure compares one word type across a focus corpus C and a reference
corpus R. The four observed quantities are the type's frequency in each corpus
(``a`` in C, ``b`` in R) and the corpus token totals (``n_focus``,
``n_reference``). This is the keyword contingency of Brezina, *Statistics in
Corpus Linguistics* (2018), Ch. 3, and Dunning (1993) for the log-likelihood.

The log-likelihood (Dunning's G2) is the significance backbone; an effect-size
measure (log ratio, Simple Maths, %DIFF) is used to rank keywords. Brezina's
caution applies: in large corpora the log-likelihood flags far too many
keywords, so it is for significance only and the sorting key should be an
effect size.
"""

from __future__ import annotations

import math

from keyflux._types import Significance

CHI2_CRITICAL: dict[Significance, float] = {
    "p05": 3.84,
    "p01": 6.63,
    "p001": 10.83,
    "p0001": 15.13,
}
"""Chi-square critical values at 1 d.f. for the log-likelihood significance bands."""

ZERO_CELL_FLOOR: float = 0.5
"""Count substituted for a zero cell in log ratio / %DIFF so exclusives stay finite."""

SMP_DEFAULT_K: float = 100.0
"""Default Simple Maths constant ``k`` (Kilgarriff 2009); also a frequency filter."""

_PER_MILLION = 1_000_000.0


def expected_counts(
    a: int, b: int, n_focus: int, n_reference: int
) -> tuple[float, float]:
    """Expected focus and reference counts under the shared-rate null hypothesis.

    Args:
        a: Frequency of the type in the focus corpus C.
        b: Frequency of the type in the reference corpus R.
        n_focus: Token total of the focus corpus C.
        n_reference: Token total of the reference corpus R.

    Returns:
        ``(E_C, E_R)`` — the counts expected if the type occurred at the same
        rate in both corpora. ``E_C + E_R == a + b``.

    Raises:
        ValueError: If ``n_focus + n_reference`` is zero (no tokens at all).

    Contract:
        - ``E_C + E_R`` equals ``a + b`` (the expected counts redistribute the
          observed total by corpus size).
        - Both returned values are non-negative.

    Examples:
        >>> e_c, e_r = expected_counts(620, 267, 1_017_879, 1_007_532)
        >>> round(e_c, 2), round(e_r, 2)
        (445.77, 441.23)
    """
    total = n_focus + n_reference
    if total == 0:
        msg = "Cannot compute expected counts: both corpora are empty."
        raise ValueError(msg)
    shared = (a + b) / total
    return n_focus * shared, n_reference * shared


def log_likelihood(a: int, b: int, n_focus: int, n_reference: int) -> float:
    """Dunning's log-likelihood ratio (G2) for one type — the significance score.

    Uses the two-cell keyword short form (Brezina eq. 3.4): the statistic is the
    unsigned magnitude only. Direction (whether the type is over- or
    under-represented in the focus corpus) is decided separately from relative
    frequencies; see :func:`keyflux.keyness.classify.classify_direction`.

    Args:
        a: Frequency of the type in the focus corpus C.
        b: Frequency of the type in the reference corpus R.
        n_focus: Token total of the focus corpus C.
        n_reference: Token total of the reference corpus R.

    Returns:
        The log-likelihood statistic, always ``>= 0``. Compare it against
        :data:`CHI2_CRITICAL` (1 d.f.) to flag significance.

    Raises:
        ValueError: If ``n_focus + n_reference`` is zero.

    Contract:
        - The result is non-negative (it is zero only when the relative
          frequencies in C and R are identical).
        - A zero-frequency cell contributes nothing (the ``x ln x -> 0`` limit),
          so the statistic is finite for exclusives.
        - Handles rare events far better than :func:`chi_square` (Dunning 1993).

    Examples:
        >>> round(log_likelihood(620, 267, 1_017_879, 1_007_532), 2)
        140.87
        >>> log_likelihood(0, 0, 1000, 1000)
        0.0
    """
    e_c, e_r = expected_counts(a, b, n_focus, n_reference)
    term_c = a * math.log(a / e_c) if a > 0 else 0.0
    term_r = b * math.log(b / e_r) if b > 0 else 0.0
    return 2.0 * (term_c + term_r)


def log_ratio(
    a: int,
    b: int,
    n_focus: int,
    n_reference: int,
    floor: float = ZERO_CELL_FLOOR,
) -> float:
    """Log ratio (Hardie 2014) — the signed effect size, in log2 units.

    The base-2 logarithm of the relative-frequency ratio between C and R. A
    value of ``+1`` means the type is twice as frequent (per token) in the focus
    corpus; ``-1`` means twice as frequent in the reference corpus. Brezina's
    convention is to filter by log-likelihood significance first, then sort
    keywords by log ratio.

    Args:
        a: Frequency of the type in the focus corpus C.
        b: Frequency of the type in the reference corpus R.
        n_focus: Token total of the focus corpus C.
        n_reference: Token total of the reference corpus R.
        floor: Count substituted for a zero cell so exclusives stay finite
            rather than diverging to +/- infinity.

    Returns:
        ``log2((a' / n_focus) / (b' / n_reference))``, where a zero ``a`` or
        ``b`` is replaced by ``floor``.

    Raises:
        ValueError: If either corpus total is non-positive.

    Contract:
        - Sign convention: positive when the type leans to the focus corpus,
          negative when it leans to the reference corpus.
        - Swapping (a, n_focus) with (b, n_reference) negates the result.
        - Finite for exclusives (one of a, b zero) thanks to ``floor``.

    Examples:
        >>> round(log_ratio(620, 267, 1_017_879, 1_007_532), 2)
        1.2
        >>> round(log_ratio(10, 2, 1000, 1000), 2)
        2.32
    """
    if n_focus <= 0 or n_reference <= 0:
        msg = "Corpus totals must be positive to compute a log ratio."
        raise ValueError(msg)
    rf_c = (a if a > 0 else floor) / n_focus
    rf_r = (b if b > 0 else floor) / n_reference
    return math.log2(rf_c / rf_r)


def simple_maths(
    a: int,
    b: int,
    n_focus: int,
    n_reference: int,
    k: float = SMP_DEFAULT_K,
) -> float:
    """Simple Maths parameter (Kilgarriff 2009) — ratio with a built-in filter.

    Compares relative frequencies per million words after adding a constant
    ``k`` to each, which both avoids division by zero and doubles as a
    frequency filter: larger ``k`` suppresses low-frequency words.

    Args:
        a: Frequency of the type in the focus corpus C.
        b: Frequency of the type in the reference corpus R.
        n_focus: Token total of the focus corpus C.
        n_reference: Token total of the reference corpus R.
        k: Smoothing constant / frequency filter, typically 1, 10, 100, or 1000.

    Returns:
        ``(rpm_C + k) / (rpm_R + k)``, where ``rpm`` is relative frequency per
        million words.

    Raises:
        ValueError: If either corpus total is non-positive.

    Contract:
        - Always positive and finite (``k > 0`` removes the zero-denominator
          case), so exclusives need no special handling.
        - A value of 1.0 means equal smoothed rates in the two corpora.

    Examples:
        >>> round(simple_maths(620, 267, 1_017_879, 1_007_532), 2)
        1.94
        >>> simple_maths(5, 5, 1000, 1000)
        1.0
    """
    if n_focus <= 0 or n_reference <= 0:
        msg = "Corpus totals must be positive to compute Simple Maths."
        raise ValueError(msg)
    rpm_c = a / n_focus * _PER_MILLION
    rpm_r = b / n_reference * _PER_MILLION
    return (rpm_c + k) / (rpm_r + k)


def percent_diff(
    a: int,
    b: int,
    n_focus: int,
    n_reference: int,
    floor: float = ZERO_CELL_FLOOR,
) -> float:
    """%DIFF (Gabrielatos & Marchi 2012) — percentage change in relative frequency.

    Args:
        a: Frequency of the type in the focus corpus C.
        b: Frequency of the type in the reference corpus R.
        n_focus: Token total of the focus corpus C.
        n_reference: Token total of the reference corpus R.
        floor: Count substituted for a zero cell so the reference rate is never
            exactly zero (which would make the percentage undefined).

    Returns:
        ``100 * (rf_C - rf_R) / rf_R``: 0 means identical rates, +100 means the
        focus rate is double the reference rate.

    Raises:
        ValueError: If either corpus total is non-positive.

    Contract:
        - Positive when the type leans to the focus corpus, negative otherwise.
        - The reference rate is floored, so the result is always finite.

    Examples:
        >>> round(percent_diff(620, 267, 1_017_879, 1_007_532), 2)
        129.85
        >>> percent_diff(10, 10, 1000, 1000)
        0.0
    """
    if n_focus <= 0 or n_reference <= 0:
        msg = "Corpus totals must be positive to compute %DIFF."
        raise ValueError(msg)
    rf_c = (a if a > 0 else floor) / n_focus
    rf_r = (b if b > 0 else floor) / n_reference
    return (rf_c - rf_r) / rf_r * 100.0


def chi_square(a: int, b: int, n_focus: int, n_reference: int) -> float:
    """Pearson chi-square (1 d.f.) on the 2x2 keyword contingency table.

    Included for contrast and teaching only. As Dunning (1993) shows, chi-square
    overestimates the significance of rare events; this is exactly the failure
    that :func:`log_likelihood` is preferred to avoid. Prefer the log-likelihood
    for significance in real analyses.

    Args:
        a: Frequency of the type in the focus corpus C.
        b: Frequency of the type in the reference corpus R.
        n_focus: Token total of the focus corpus C.
        n_reference: Token total of the reference corpus R.

    Returns:
        The chi-square statistic, always ``>= 0``.

    Raises:
        ValueError: If ``n_focus + n_reference`` is zero, or if ``a > n_focus``
            or ``b > n_reference`` (a type cannot occur more often than there
            are tokens).

    Contract:
        - The result is non-negative.
        - Computed over the full 2x2 table (word present / absent x corpus), so
          it uses the "other tokens" cells that the log-likelihood short form
          omits.

    Examples:
        >>> round(chi_square(620, 267, 1_017_879, 1_007_532), 2)
        136.96
        >>> chi_square(10, 10, 1000, 1000)
        0.0
    """
    total = n_focus + n_reference
    if total == 0:
        msg = "Cannot compute chi-square: both corpora are empty."
        raise ValueError(msg)
    if a > n_focus or b > n_reference:
        msg = "A type cannot occur more often than the corpus has tokens."
        raise ValueError(msg)
    row_word = a + b
    row_other = total - row_word
    observed = ((a, n_focus - a), (b, n_reference - b))
    expected = (
        (n_focus * row_word / total, n_focus * row_other / total),
        (n_reference * row_word / total, n_reference * row_other / total),
    )
    stat = 0.0
    for i in range(2):
        for j in range(2):
            e = expected[i][j]
            if e > 0:
                stat += (observed[i][j] - e) ** 2 / e
    return stat


def significance_band(statistic: float) -> Significance:
    """Map a log-likelihood / chi-square statistic to its significance band.

    Args:
        statistic: A log-likelihood or chi-square value (1 d.f.).

    Returns:
        One of ``"ns"`` (not significant at p<0.05), ``"p05"``, ``"p01"``,
        ``"p001"``, or ``"p0001"`` — the strongest band whose critical value the
        statistic reaches.

    Contract:
        - Monotone: a larger statistic never maps to a weaker band.
        - Thresholds are the chi-square critical values at 1 d.f.: 3.84, 6.63,
          10.83, 15.13.

    Examples:
        >>> significance_band(140.87)
        'p0001'
        >>> significance_band(3.83)
        'ns'
        >>> significance_band(6.63)
        'p01'
    """
    if statistic >= CHI2_CRITICAL["p0001"]:
        return "p0001"
    if statistic >= CHI2_CRITICAL["p001"]:
        return "p001"
    if statistic >= CHI2_CRITICAL["p01"]:
        return "p01"
    if statistic >= CHI2_CRITICAL["p05"]:
        return "p05"
    return "ns"
