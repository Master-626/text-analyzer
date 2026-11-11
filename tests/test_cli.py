"""CLI behavior: unchanged counts, clean failures, and ``--top``."""

import os
import re
import subprocess
import sys

import pytest
from click.testing import CliRunner

from text_analyzer import __version__
from text_analyzer.cli import main

runner = CliRunner()


def metric_value(output, label):
    match = re.search(rf"{re.escape(label)}\s+(?:[│|]\s+)?(\d+)", output)
    assert match, f"{label} not found in:\n{output}"
    return int(match.group(1))


def write_text(path, text):
    path.write_bytes(text.encode("utf-8"))


def assert_clean_failure(result, fragment, exit_code):
    assert result.exit_code == exit_code
    assert fragment in result.output
    assert "Traceback" not in result.output


def test_stats_reports_words_characters_and_lines(tmp_path):
    path = tmp_path / "notes.txt"
    write_text(path, "one two\nthree\n")
    result = runner.invoke(main, ["stats", str(path)])
    assert result.exit_code == 0
    assert result.exception is None
    assert metric_value(result.output, "Words") == 3
    assert metric_value(result.output, "Characters") == 14
    assert metric_value(result.output, "Lines") == 2
    assert "Text Statistics" in result.output
    assert "Top Words" not in result.output


def test_stats_empty_file(tmp_path):
    path = tmp_path / "empty.txt"
    write_text(path, "")
    result = runner.invoke(main, ["stats", str(path)])
    assert result.exit_code == 0
    assert metric_value(result.output, "Words") == 0
    assert metric_value(result.output, "Characters") == 0
    assert metric_value(result.output, "Lines") == 0


def test_stats_accepts_paths_with_spaces(tmp_path):
    path = tmp_path / "my notes.txt"
    write_text(path, "hello\n")
    result = runner.invoke(main, ["stats", str(path)])
    assert result.exit_code == 0
    assert metric_value(result.output, "Words") == 1


def test_stats_strips_bom_from_the_character_count(tmp_path):
    path = tmp_path / "bom.txt"
    path.write_bytes(b"\xef\xbb\xbfhello world")
    result = runner.invoke(main, ["stats", str(path)])
    assert result.exit_code == 0
    assert metric_value(result.output, "Words") == 2
    assert metric_value(result.output, "Characters") == 11
    assert metric_value(result.output, "Lines") == 1


def test_missing_file_is_a_clean_error(tmp_path):
    result = runner.invoke(main, ["stats", str(tmp_path / "missing.txt")])
    assert_clean_failure(result, "does not exist", exit_code=2)


def test_directory_is_a_clean_error(tmp_path):
    result = runner.invoke(main, ["stats", str(tmp_path)])
    assert_clean_failure(result, "is a directory", exit_code=2)


def test_unreadable_file_is_a_clean_error(tmp_path):
    path = tmp_path / "secret.txt"
    write_text(path, "secret")
    path.chmod(0o000)
    if os.access(path, os.R_OK):
        path.chmod(0o644)
        pytest.skip("process can read files even when mode bits deny it")
    try:
        result = runner.invoke(main, ["stats", str(path)])
    finally:
        path.chmod(0o644)
    assert_clean_failure(result, "not readable", exit_code=2)


def test_invalid_utf8_is_a_clean_error(tmp_path):
    path = tmp_path / "bad.txt"
    path.write_bytes(b"caf\xff")
    result = runner.invoke(main, ["stats", str(path)])
    assert_clean_failure(result, "UTF-8", exit_code=1)


def test_oserror_while_reading_is_a_clean_error(tmp_path, monkeypatch):
    path = tmp_path / "ok.txt"
    write_text(path, "hi\n")

    def boom(_path):
        raise OSError(5, "Input/output error")

    monkeypatch.setattr("text_analyzer.cli.load_text", boom)
    result = runner.invoke(main, ["stats", str(path)])
    assert_clean_failure(result, "Input/output error", exit_code=1)


def test_top_lists_frequent_words_without_changing_the_word_count(tmp_path):
    path = tmp_path / "words.txt"
    write_text(path, "Apple banana apple! banana apple\n")
    result = runner.invoke(main, ["stats", str(path), "--top", "2"])
    assert result.exit_code == 0
    assert metric_value(result.output, "Words") == 5
    assert "Top Words" in result.output
    assert "apple" in result.output
    assert "banana" in result.output
    apple = result.output.index("apple")
    banana = result.output.index("banana")
    assert apple < banana


def test_top_option_may_precede_the_path(tmp_path):
    path = tmp_path / "words.txt"
    write_text(path, "one one two\n")
    result = runner.invoke(main, ["stats", "--top", "1", str(path)])
    assert result.exit_code == 0
    assert "one" in result.output
    assert metric_value(result.output, "Words") == 3


def test_top_zero_matches_the_default_and_omits_the_ranking(tmp_path):
    path = tmp_path / "words.txt"
    write_text(path, "one one\n")
    default = runner.invoke(main, ["stats", str(path)])
    explicit = runner.invoke(main, ["stats", str(path), "--top", "0"])
    assert default.exit_code == 0
    assert explicit.exit_code == 0
    assert default.output == explicit.output
    assert "Top Words" not in default.output


def test_top_on_a_file_with_no_words(tmp_path):
    path = tmp_path / "blank.txt"
    write_text(path, " ... \n")
    result = runner.invoke(main, ["stats", str(path), "--top", "3"])
    assert result.exit_code == 0
    assert metric_value(result.output, "Words") == 1
    assert "No words found." in result.output


def test_top_prints_tokens_that_look_like_rich_markup(tmp_path):
    path = tmp_path / "markup.txt"
    write_text(path, "[bold]Hi[/bold] hi\n")
    result = runner.invoke(main, ["stats", str(path), "--top", "5"])
    assert result.exit_code == 0
    assert "bold]hi[/bold" in result.output


def test_negative_top_is_rejected(tmp_path):
    path = tmp_path / "words.txt"
    write_text(path, "hello\n")
    result = runner.invoke(main, ["stats", str(path), "--top", "-1"])
    assert_clean_failure(result, "range", exit_code=2)


def test_help_describes_stats_without_claiming_readability():
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "stats" in result.output
    assert "readability" not in result.output.lower()


def test_stats_help_documents_top():
    result = runner.invoke(main, ["stats", "--help"])
    assert result.exit_code == 0
    assert "--top" in result.output
    assert "FILE" in result.output
    assert "default: 0" in result.output


def test_version_matches_package():
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_module_entrypoint_prints_stats(tmp_path):
    path = tmp_path / "notes.txt"
    write_text(path, "hi\n")
    completed = subprocess.run(
        [sys.executable, "-m", "text_analyzer", "stats", str(path)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert "Words" in completed.stdout
    assert metric_value(completed.stdout, "Words") == 1


def test_utf8_file_survives_ascii_locale(tmp_path):
    """Regression: open() without an encoding follows the locale.

    With UTF-8 mode disabled and ``LC_ALL=C``, a valid UTF-8 file used to
    raise UnicodeDecodeError before any statistics were printed.
    """
    path = tmp_path / "zh.txt"
    path.write_bytes("你好\n".encode())
    env = os.environ.copy()
    env["LC_ALL"] = "C"
    env["LANG"] = "C"
    env["PYTHONUTF8"] = "0"
    completed = subprocess.run(
        [sys.executable, "-m", "text_analyzer", "stats", str(path)],
        check=False,
        capture_output=True,
        env=env,
    )
    stdout = completed.stdout.decode("utf-8", "replace")
    stderr = completed.stderr.decode("utf-8", "replace")
    assert completed.returncode == 0, stderr
    assert "UnicodeDecodeError" not in stderr
    assert metric_value(stdout, "Words") == 1
    assert metric_value(stdout, "Characters") == 3
    assert metric_value(stdout, "Lines") == 1
