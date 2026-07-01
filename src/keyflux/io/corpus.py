"""Build frequency Counters from tokens, text, or count files.

keyflux is about keyness and rank comparison, not tokenisation. These helpers
cover the simple cases; for real linguistic tokenisation, pre-tokenise (for
example with ``kenon.Tokenizer``) and pass the resulting Counter directly.
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Iterable
from pathlib import Path

_WORD_RE = re.compile(r"\w+", re.UNICODE)


def counts_from_tokens(
    tokens: Iterable[str], *, lowercase: bool = True
) -> Counter[str]:
    """Build a frequency Counter from a token iterable.

    Args:
        tokens: Already-tokenised word types.
        lowercase: If True, lowercase each token before counting.

    Returns:
        A Counter mapping each type to its frequency.

    Examples:
        >>> counts_from_tokens(["The", "cat", "the", "CAT"])
        Counter({'the': 2, 'cat': 2})
    """
    if lowercase:
        return Counter(t.lower() for t in tokens)
    return Counter(tokens)


def counts_from_text(text: str, *, lowercase: bool = True) -> Counter[str]:
    """Tokenise a string on word characters, then count.

    Uses a simple word-character regular expression — adequate for demos and
    tests, not a substitute for linguistic tokenisation.

    Args:
        text: Raw text to tokenise and count.
        lowercase: If True, lowercase before counting.

    Returns:
        A Counter mapping each type to its frequency.

    Examples:
        >>> counts_from_text("The cat sat. The dog ran.")["the"]
        2
    """
    tokens = _WORD_RE.findall(text.lower() if lowercase else text)
    return Counter(tokens)


def load_counts(path: str | Path) -> Counter[str]:
    """Read a count file into a Counter.

    Each non-empty line is either ``type<TAB>count`` or a bare ``type`` (counted
    as one occurrence per line).

    Args:
        path: Path to the count file.

    Returns:
        A Counter built from the file.

    Raises:
        FileNotFoundError: If ``path`` does not exist.
        ValueError: If a count field is present but not an integer.

    Examples:
        >>> import tempfile, pathlib
        >>> p = pathlib.Path(tempfile.mkdtemp()) / "counts.tsv"
        >>> rows = ["climate" + chr(9) + "30", "carbon" + chr(9) + "12"]
        >>> _ = p.write_text(chr(10).join(rows))
        >>> load_counts(p)
        Counter({'climate': 30, 'carbon': 12})
    """
    counts: Counter[str] = Counter()
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) == 1:
            counts[parts[0]] += 1
        else:
            word, raw = parts[0], parts[1]
            try:
                counts[word] += int(raw)
            except ValueError as exc:
                msg = f"Non-integer count {raw!r} for type {word!r}."
                raise ValueError(msg) from exc
    return counts
