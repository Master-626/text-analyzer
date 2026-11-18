"""Core counting, UTF-8 loading, and word-frequency behavior."""

import pytest

from text_analyzer import TextStats, analyze_text, load_text, top_words


def test_analyze_basic_sentence():
    stats = analyze_text("one two\nthree\n")
    assert stats == TextStats(words=3, characters=14, lines=2)


def test_analyze_empty_string():
    assert analyze_text("") == TextStats(words=0, characters=0, lines=0)


def test_analyze_whitespace_is_not_words():
    assert analyze_text("   \n\n  \t\n") == TextStats(words=0, characters=9, lines=3)


def test_analyze_collapses_repeated_whitespace():
    assert analyze_text("a  b\t\nc") == TextStats(words=3, characters=7, lines=2)


def test_analyze_trailing_newline_does_not_add_a_line():
    assert analyze_text("hello") == TextStats(words=1, characters=5, lines=1)
    assert analyze_text("hello\n") == TextStats(words=1, characters=6, lines=1)
    assert analyze_text("hello\nworld\n") == TextStats(words=2, characters=12, lines=2)


def test_analyze_internal_blank_line_counts():
    assert analyze_text("a\n\nb\n") == TextStats(words=2, characters=5, lines=3)


def test_analyze_counts_punctuation_only_tokens_as_words():
    assert analyze_text("Hello, hello! ...") == TextStats(
        words=3, characters=17, lines=1
    )


def test_analyze_counts_unicode_code_points_not_bytes():
    stats = analyze_text("你好 世界\n")
    assert stats == TextStats(words=2, characters=6, lines=1)


def test_analyze_rejects_non_strings():
    with pytest.raises(TypeError):
        analyze_text(None)
    with pytest.raises(TypeError):
        analyze_text(b"abc")


def test_load_text_reads_plain_utf8(tmp_path):
    path = tmp_path / "plain.txt"
    path.write_bytes(b"hello\n")
    assert load_text(path) == "hello\n"


def test_load_text_strips_leading_bom(tmp_path):
    path = tmp_path / "bom.txt"
    path.write_bytes(b"\xef\xbb\xbfhello world")
    text = load_text(path)
    assert text == "hello world"
    assert "\ufeff" not in text
    assert analyze_text(text) == TextStats(words=2, characters=11, lines=1)


def test_load_text_bom_only_file_is_empty(tmp_path):
    path = tmp_path / "only-bom.txt"
    path.write_bytes(b"\xef\xbb\xbf")
    assert load_text(path) == ""
    assert analyze_text(load_text(path)) == TextStats(0, 0, 0)


def test_load_text_normalizes_crlf(tmp_path):
    path = tmp_path / "crlf.txt"
    path.write_bytes(b"hello\r\nworld\r\n")
    text = load_text(path)
    assert text == "hello\nworld\n"
    assert analyze_text(text) == TextStats(words=2, characters=12, lines=2)


def test_load_text_chinese_utf8(tmp_path):
    path = tmp_path / "zh.txt"
    path.write_bytes("你好\n".encode())
    text = load_text(path)
    assert text == "你好\n"
    assert analyze_text(text) == TextStats(words=1, characters=3, lines=1)


def test_load_text_rejects_invalid_utf8(tmp_path):
    path = tmp_path / "bad.txt"
    path.write_bytes(b"hello\xffworld")
    with pytest.raises(UnicodeDecodeError):
        load_text(path)


def test_load_text_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_text(tmp_path / "missing.txt")


def test_load_text_directory(tmp_path):
    with pytest.raises(IsADirectoryError):
        load_text(tmp_path)


def test_top_words_merges_case_and_edge_punctuation():
    text = "Hello, hello! HELLO."
    assert analyze_text(text).words == 3
    assert top_words(text, 5) == [("hello", 3)]


def test_top_words_casefold_merges_eszett():
    assert top_words("Straße strasse STRASSE", 5) == [("strasse", 3)]


def test_top_words_keeps_internal_apostrophe_and_strips_quotes():
    assert top_words("Don't don't 'Don't'", 5) == [("don't", 3)]
    assert top_words("“Hello” hello", 5) == [("hello", 2)]


def test_top_words_keeps_internal_hyphen_and_sorts_ties_alphabetically():
    text = "bb aa well-known aa bb"
    assert top_words(text, 10) == [("aa", 2), ("bb", 2), ("well-known", 1)]


def test_top_words_ignores_punctuation_only_tokens():
    text = "hi ... hi ___"
    assert analyze_text(text).words == 4
    assert top_words(text, 10) == [("hi", 2)]


def test_top_words_respects_limit_and_zero():
    assert top_words("c b a a b", 2) == [("a", 2), ("b", 2)]
    assert top_words("a a", 0) == []
    assert top_words("", 5) == []
    assert top_words("   \n", 5) == []


def test_top_words_rejects_bad_limits():
    with pytest.raises(ValueError):
        top_words("a", -1)
    with pytest.raises(TypeError):
        top_words("a", 1.5)
    with pytest.raises(TypeError):
        top_words("a", True)
