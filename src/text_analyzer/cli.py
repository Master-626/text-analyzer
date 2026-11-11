"""Command-line interface for Text Analyzer."""

import click
from rich.console import Console
from rich.table import Table
from rich.text import Text

from text_analyzer import __version__
from text_analyzer.analyze import analyze_text, load_text, top_words

console = Console()


@click.group()
@click.version_option(version=__version__)
def main():
    """Text Analyzer: word, character, and line counts for UTF-8 text files."""


@main.command()
@click.argument("file", type=click.Path(exists=True, dir_okay=False, readable=True))
@click.option(
    "--top",
    default=0,
    show_default=True,
    metavar="N",
    type=click.IntRange(min=0),
    help="Show the N most frequent words. 0 skips the ranking.",
)
def stats(file, top):
    """Show text statistics."""
    try:
        text = load_text(file)
    except UnicodeDecodeError as exc:
        raise click.ClickException(f"Could not read {file!r} as UTF-8 text.") from exc
    except OSError as exc:
        detail = exc.strerror or str(exc)
        raise click.ClickException(f"Could not read {file!r}: {detail}") from exc

    result = analyze_text(text)
    table = Table(title="Text Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Words", str(result.words))
    table.add_row("Characters", str(result.characters))
    table.add_row("Lines", str(result.lines))
    console.print(table)

    if top:
        _print_top_words(text, top)


def _print_top_words(text, limit):
    rows = top_words(text, limit)
    if not rows:
        console.print("No words found.")
        return
    # Short title so Rich does not wrap it inside a narrow table.
    table = Table(title="Top Words")
    table.add_column("Word", style="cyan")
    table.add_column("Count", style="green")
    for word, count in rows:
        # User text can look like Rich markup, for example "[bold]".
        table.add_row(Text(word), str(count))
    console.print(table)


if __name__ == "__main__":
    main()
