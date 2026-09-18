"""CLI interface."""
import click
from rich.console import Console
from rich.table import Table

console = Console()

@click.group()
@click.version_option(version="0.1.0")
def main():
    """Text Analyzer - Analyze text files with statistics and readability scores."""
    pass

@main.command()
@click.argument("file")
def stats(file):
    """Show text statistics."""
    with open(file, "r") as f:
        text = f.read()
    
    words = len(text.split())
    chars = len(text)
    lines = len(text.splitlines())
    
    table = Table(title="Text Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Words", str(words))
    table.add_row("Characters", str(chars))
    table.add_row("Lines", str(lines))
    console.print(table)

if __name__ == "__main__":
    main()
