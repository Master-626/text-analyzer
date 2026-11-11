"""Count words, characters, and lines in plain text."""

from __future__ import annotations

import os
import string
from collections import Counter
from typing import NamedTuple

# Characters removed from both ends of a token before it is ranked.
# Internal hyphens and apostrophes are kept ("well-known", "don't").
_EDGE_PUNCTUATION = string.punctuation + "_“”‘’«»‹›「」『』…—–"


class TextStats(NamedTuple):
    """Whitespace word count, Unicode characters, and lines."""

    words: int
    characters: int
    lines: int


def load_text(path: str | os.PathLike[str]) -> str:
    """Read a text file as UTF-8.

    A leading UTF-8 BOM is removed so it is not counted as a character or
    glued onto the first word. Newlines are normalized to ``\\n``.
    ``UnicodeDecodeError`` is raised when the bytes are not valid UTF-8.
    """
    with open(path, encoding="utf-8-sig") as handle:
        return handle.read()


def analyze_text(text: str) -> TextStats:
    """Count words, characters, and lines.

    Words are whitespace-separated (``str.split``). Characters are Unicode
    code points. Lines follow ``str.splitlines``: a blank line in the middle
    counts, and a trailing newline does not add an extra line.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    return TextStats(
        words=len(text.split()),
        characters=len(text),
        lines=len(text.splitlines()),
    )


def top_words(text: str, limit: int) -> list[tuple[str, int]]:
    """Return the most common words, most frequent first.

    Matching is case-insensitive (``str.casefold``). Punctuation is stripped
    from the edges of each whitespace-separated token, and tokens that are
    empty afterward are dropped. Ties are broken alphabetically. ``limit``
    of 0 returns an empty list. This ranking does not change ``analyze_text``
    word counts, which still include punctuation-only tokens.
    """
    if isinstance(limit, bool) or not isinstance(limit, int):
        raise TypeError("limit must be an int")
    if limit < 0:
        raise ValueError("limit must be non-negative")
    if limit == 0:
        return []

    counts: Counter[str] = Counter()
    for raw in text.split():
        token = raw.strip(_EDGE_PUNCTUATION).casefold()
        if token:
            counts[token] += 1
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return ranked[:limit]
