# Text Analyzer

## 概要

`textan` 是一个轻量的命令行文本分析工具。它统计 UTF-8 文本文件的词数、字符数和行数，并可用 `--top` 列出出现最多的词。程序固定按 UTF-8 读取文件，并自动忽略文件开头的 BOM。安装、用法、选项和测试见下方英文说明。

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/Master-626/text-analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/Master-626/text-analyzer/actions/workflows/ci.yml)

## Purpose

Text Analyzer reports basic statistics for a plain-text file: how many words, characters, and lines it contains. Pass `--top` when you also want the words that appear most often. It is a small command-line tool for notes, drafts, and other UTF-8 text.

## Installation

Python 3.8 or newer is required.

```bash
git clone https://github.com/Master-626/text-analyzer.git
cd text-analyzer
pip install .
```

The install adds a `textan` command. If that script directory is not on your `PATH`, run the module instead:

```bash
python -m text_analyzer --help
```

To work on the code, install the development extra (pytest and Ruff):

```bash
pip install -e ".[dev]"
```

Runtime dependencies are [Click](https://click.palletsprojects.com/) and [Rich](https://rich.readthedocs.io/).

## Usage

```bash
printf 'Hello, hello!\nWorld.\n' > notes.txt

textan stats notes.txt
textan stats notes.txt --top 5
textan --version
```

That sample file has 3 words, 21 characters, and 2 lines. `--top 5` ranks `hello` (2) ahead of `world` (1). The same commands work as `python -m text_analyzer stats notes.txt`.

`stats` prints a table. On a terminal that supports color, the metric names and values are colored. `--top` adds a second table. With no words to rank, it prints `No words found.`

## Options

### `textan`

| Option | Description |
| --- | --- |
| `--help` | Show help and exit. |
| `--version` | Show the version and exit. |

Commands: `stats`.

### `textan stats FILE`

| Option | Description |
| --- | --- |
| `FILE` | Path to a UTF-8 text file. The path must exist, must be a file, and must be readable. |
| `--top N` | Also show the N most frequent words. Default: `0`, which skips the ranking. `N` must be an integer greater than or equal to 0. |

`--top` can be placed before or after the file path.

## How counts work

- **Words** are whitespace-separated tokens, the same as `str.split()`. Punctuation attached to a token stays part of that token, and a token made only of punctuation still counts as one word.
- **Characters** are Unicode code points after Python's universal-newline translation, so both `\r\n` and a lone `\r` become a single `\n`. A leading UTF-8 BOM is not counted.
- **Lines** follow `str.splitlines()`. A blank line in the middle of the file counts. A newline at the end of the file does not add another empty line.
- **`--top`** compares words case-insensitively (`str.casefold()`). It strips punctuation from the edges of each token, including underscores and common quotation marks, then drops tokens that are empty after stripping. Equal counts are ordered alphabetically. The ranking does not change the Words total.

Files must be UTF-8. The same file is read the same way regardless of the locale. Bytes that are not valid UTF-8 produce an error message and a non-zero exit status.

## Running tests

```bash
pip install -e ".[dev]"
ruff check .
ruff format --check .
pytest
```

GitHub Actions runs Ruff and runs pytest on Python 3.8 through 3.14.

## License

Released under the MIT License. See [LICENSE](LICENSE).
