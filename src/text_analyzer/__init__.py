"""Text statistics for the command line and for other Python programs."""

__version__ = "0.1.0"

from text_analyzer.analyze import TextStats, analyze_text, load_text, top_words

__all__ = [
    "TextStats",
    "__version__",
    "analyze_text",
    "load_text",
    "top_words",
]
