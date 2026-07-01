"""Focus-versus-reference keyness: keywords, lockwords, and a repro record.

``Keyness`` scores every type in the combined vocabulary of two frequency
Counters, using the log-likelihood for significance and the log ratio as the
effect size used to rank keywords (Brezina Ch. 3). It exposes positive and
negative keywords, the stable lockword zone, and a machine-readable
reproducibility record of the parameters that produced the result.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterator
from dataclasses import asdict, dataclass

import keyflux
from keyflux._types import Direction, MeasureName, Significance
from keyflux.keyness import measures
from keyflux.keyness.classify import classify_direction, is_significant

_VALID_MEASURES: frozenset[MeasureName] = frozenset(
    ("log_likelihood", "log_ratio", "simple_maths", "percent_diff", "chi_square")
)


@dataclass(frozen=True, slots=True)
class KeynessRow:
    """One type's keyness statistics.

    Attributes:
        type: The word type.
        focus_count: Raw frequency in the focus corpus C.
        reference_count: Raw frequency in the reference corpus R.
        focus_rf: Relative frequency in C, per million tokens.
        reference_rf: Relative frequency in R, per million tokens.
        score: Value of the chosen keyness ``measure`` (the sortable headline).
        effect_size: Log ratio (log2), always computed regardless of ``measure``.
        significance: Band from the log-likelihood: ns / p05 / p01 / p001 / p0001.
        statistic: The log-likelihood magnitude behind ``significance``.
        direction: positive / negative / neutral, from the relative frequencies.
    """

    type: str
    focus_count: int
    reference_count: int
    focus_rf: float
    reference_rf: float
    score: float
    effect_size: float
    significance: Significance
    statistic: float
    direction: Direction


@dataclass(frozen=True, slots=True)
class ReproRecord:
    """Reproducibility record for one keyness run.

    Captures the three parameters that govern any keyness result — reference
    corpus, minimum-frequency cutoffs, and the statistical measure — plus the
    corpus totals and the keyflux version, so an analysis can be reproduced.

    Attributes:
        reference_id: A label identifying the reference corpus.
        measure: The keyness measure used for ``score``.
        min_focus_freq: Minimum focus-corpus frequency to enter the table.
        min_reference_freq: Minimum reference-corpus frequency to enter the table.
        focus_total: Token total of the focus corpus.
        reference_total: Token total of the reference corpus.
        top_n: The ``top`` cap applied to a keyword list, or None if unbounded.
        floor: Zero-cell floor used by log ratio / %DIFF.
        smp_k: Simple Maths constant ``k``.
        keyflux_version: Version of keyflux that produced the result.
    """

    reference_id: str
    measure: MeasureName
    min_focus_freq: int
    min_reference_freq: int
    focus_total: int
    reference_total: int
    top_n: int | None
    floor: float
    smp_k: float
    keyflux_version: str

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serialisable dict of the record.

        Returns:
            A plain dict with one key per field.

        Examples:
            >>> rec = ReproRecord("BE06", "log_likelihood", 5, 5, 1000, 1000,
            ...                    None, 0.5, 100.0, "0.1.0")
            >>> rec.to_dict()["measure"]
            'log_likelihood'
        """
        return asdict(self)


@dataclass(frozen=True, slots=True)
class KeywordTable:
    """A significance-filtered, effect-size-sorted set of keywords.

    Attributes:
        rows: The keyword rows, sorted by absolute effect size (descending).
        repro: The reproducibility record for the run that produced them.
    """

    rows: tuple[KeynessRow, ...]
    repro: ReproRecord

    def positive(self, n: int | None = None) -> list[KeynessRow]:
        """Positive keywords (over-represented in the focus corpus).

        Args:
            n: Maximum number to return; None returns all.

        Returns:
            Positive-direction rows sorted by effect size, largest first.

        Examples:
            >>> from collections import Counter
            >>> k = Keyness(Counter({"a": 30, "x": 5}), Counter({"a": 2, "x": 6}))
            >>> [r.type for r in k.keywords().positive()]
            ['a']
        """
        rows = [r for r in self.rows if r.direction == "positive"]
        rows.sort(key=lambda r: r.effect_size, reverse=True)
        return rows[:n] if n is not None else rows

    def negative(self, n: int | None = None) -> list[KeynessRow]:
        """Negative keywords (over-represented in the reference corpus).

        Args:
            n: Maximum number to return; None returns all.

        Returns:
            Negative-direction rows sorted by effect size, most negative first.

        Examples:
            >>> from collections import Counter
            >>> k = Keyness(Counter({"a": 30, "x": 5}), Counter({"a": 2, "x": 6}))
            >>> [r.type for r in k.keywords().negative()]
            ['x']
        """
        rows = [r for r in self.rows if r.direction == "negative"]
        rows.sort(key=lambda r: r.effect_size)
        return rows[:n] if n is not None else rows

    def __iter__(self) -> Iterator[KeynessRow]:
        return iter(self.rows)

    def __len__(self) -> int:
        return len(self.rows)


class Keyness:
    """Compare a focus corpus against a reference corpus to derive keyness.

    Scores the combined vocabulary of two frequency Counters once, eagerly. The
    log-likelihood drives significance; the log ratio is the effect size used to
    rank keywords. A type enters the scored table when it meets the minimum
    frequency in at least one corpus, which keeps focus-exclusive keywords while
    discarding under-evidenced absent words.

    Args:
        focus: Frequency Counter for the focus corpus C (corpus of interest).
        reference: Frequency Counter for the reference corpus R.
        measure: Keyness measure used for each row's ``score``.
        min_focus_freq: Minimum focus-corpus frequency to enter the table.
        min_reference_freq: Minimum reference-corpus frequency to enter the table.
        reference_id: A label for the reference corpus, stored in the repro record.
        floor: Zero-cell floor for log ratio / %DIFF.
        smp_k: Simple Maths constant ``k``.

    Contract:
        - A type is scored iff ``focus_count >= min_focus_freq`` OR
          ``reference_count >= min_reference_freq`` (evidence in either corpus).
        - Significance always comes from the log-likelihood, even when ``measure``
          is something else; ``effect_size`` is always the log ratio.
        - Swapping ``focus`` and ``reference`` (with equal cutoffs) flips each
          row's direction and negates its effect size, turning positive keywords
          into negative ones and leaving lockwords unchanged.

    Examples:
        >>> from collections import Counter
        >>> focus = Counter({"climate": 300, "the": 800, "policy": 90})
        >>> reference = Counter({"climate": 30, "the": 780, "policy": 88})
        >>> k = Keyness(focus, reference, measure="log_likelihood")
        >>> kw = k.keywords(top=10)
        >>> [r.type for r in kw.positive()]
        ['climate']
    """

    def __init__(
        self,
        focus: Counter[str],
        reference: Counter[str],
        measure: MeasureName = "log_likelihood",
        *,
        min_focus_freq: int = 5,
        min_reference_freq: int = 5,
        reference_id: str = "reference",
        floor: float = measures.ZERO_CELL_FLOOR,
        smp_k: float = measures.SMP_DEFAULT_K,
    ) -> None:
        if measure not in _VALID_MEASURES:
            choices = sorted(_VALID_MEASURES)
            msg = f"Unknown measure {measure!r}; choose one of {choices}."
            raise ValueError(msg)
        self.focus = focus
        self.reference = reference
        self.measure: MeasureName = measure
        self.min_focus_freq = min_focus_freq
        self.min_reference_freq = min_reference_freq
        self.reference_id = reference_id
        self.floor = floor
        self.smp_k = smp_k
        self.focus_total = sum(focus.values())
        self.reference_total = sum(reference.values())
        self._rows = self._build_rows()

    def _repro(self, top_n: int | None) -> ReproRecord:
        return ReproRecord(
            reference_id=self.reference_id,
            measure=self.measure,
            min_focus_freq=self.min_focus_freq,
            min_reference_freq=self.min_reference_freq,
            focus_total=self.focus_total,
            reference_total=self.reference_total,
            top_n=top_n,
            floor=self.floor,
            smp_k=self.smp_k,
            keyflux_version=keyflux.__version__,
        )

    def _score(self, a: int, b: int) -> float:
        n_focus, n_reference = self.focus_total, self.reference_total
        if self.measure == "log_ratio":
            return measures.log_ratio(a, b, n_focus, n_reference, self.floor)
        if self.measure == "percent_diff":
            return measures.percent_diff(a, b, n_focus, n_reference, self.floor)
        if self.measure == "simple_maths":
            return measures.simple_maths(a, b, n_focus, n_reference, self.smp_k)
        if self.measure == "chi_square":
            return measures.chi_square(a, b, n_focus, n_reference)
        return measures.log_likelihood(a, b, n_focus, n_reference)

    def _build_rows(self) -> tuple[KeynessRow, ...]:
        if self.focus_total == 0 or self.reference_total == 0:
            msg = "Both corpora must be non-empty to compute keyness."
            raise ValueError(msg)
        rows: list[KeynessRow] = []
        for word in self.focus.keys() | self.reference.keys():
            a = self.focus.get(word, 0)
            b = self.reference.get(word, 0)
            if a < self.min_focus_freq and b < self.min_reference_freq:
                continue
            focus_rf = a / self.focus_total * 1_000_000.0
            reference_rf = b / self.reference_total * 1_000_000.0
            statistic = measures.log_likelihood(
                a, b, self.focus_total, self.reference_total
            )
            rows.append(
                KeynessRow(
                    type=word,
                    focus_count=a,
                    reference_count=b,
                    focus_rf=focus_rf,
                    reference_rf=reference_rf,
                    score=self._score(a, b),
                    effect_size=measures.log_ratio(
                        a, b, self.focus_total, self.reference_total, self.floor
                    ),
                    significance=measures.significance_band(statistic),
                    statistic=statistic,
                    direction=classify_direction(focus_rf, reference_rf),
                )
            )
        rows.sort(key=lambda r: abs(r.effect_size), reverse=True)
        return tuple(rows)

    def table(self) -> list[KeynessRow]:
        """Return the full per-type table, sorted by absolute effect size.

        Returns:
            Every scored row (one per type clearing the minimum frequency).

        Examples:
            >>> from collections import Counter
            >>> k = Keyness(Counter({"a": 30}), Counter({"a": 5, "b": 20}),
            ...             min_focus_freq=1, min_reference_freq=1)
            >>> len(k.table())
            2
        """
        return list(self._rows)

    def keywords(self, top: int | None = None) -> KeywordTable:
        """Return significance-filtered keywords, sorted by absolute effect size.

        Args:
            top: Maximum number of keywords (positive and negative combined) to
                keep; None keeps all significant keywords.

        Returns:
            A :class:`KeywordTable` of the significant, directional rows.

        Contract:
            - Only rows significant at p<0.05 (log-likelihood) and with a
              non-neutral direction are included.
            - Rows are ordered by absolute effect size, descending.

        Examples:
            >>> from collections import Counter
            >>> focus = Counter({"climate": 30, "the": 80})
            >>> reference = Counter({"climate": 2, "the": 78})
            >>> k = Keyness(focus, reference)
            >>> [r.type for r in k.keywords(top=5)]
            ['climate']
        """
        rows = [
            r
            for r in self._rows
            if r.direction != "neutral" and is_significant(r.significance)
        ]
        if top is not None:
            rows = rows[:top]
        return KeywordTable(rows=tuple(rows), repro=self._repro(top))

    def lockwords(
        self,
        *,
        max_ll: float = measures.CHI2_CRITICAL["p05"],
        max_abs_log_ratio: float = 0.5,
        min_freq_both: int = 5,
    ) -> list[KeynessRow]:
        """Return lockwords: stable types with comparable frequency in both corpora.

        Args:
            max_ll: Lockwords must have a log-likelihood below this (not
                significant at p<0.05 by default).
            max_abs_log_ratio: Lockwords must have an absolute log ratio at or
                below this (relative frequencies near parity).
            min_freq_both: Lockwords must occur at least this many times in BOTH
                corpora (they are stable, frequent words — not rare noise).

        Returns:
            Lockword rows, most frequent first.

        Contract:
            - Lockwords are disjoint from keywords: the log-likelihood ceiling is
              the same threshold that defines significance.
            - Requires evidence in both corpora, so exclusives are never lockwords.

        Examples:
            >>> from collections import Counter
            >>> focus = Counter({"the": 800, "climate": 30})
            >>> reference = Counter({"the": 790, "climate": 2})
            >>> k = Keyness(focus, reference)
            >>> [r.type for r in k.lockwords()]
            ['the']
        """
        rows = [
            r
            for r in self._rows
            if r.statistic < max_ll
            and abs(r.effect_size) <= max_abs_log_ratio
            and r.focus_count >= min_freq_both
            and r.reference_count >= min_freq_both
        ]
        rows.sort(key=lambda r: r.focus_count + r.reference_count, reverse=True)
        return rows
