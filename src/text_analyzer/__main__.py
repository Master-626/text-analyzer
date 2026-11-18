"""Allow ``python -m text_analyzer`` when the ``textan`` script is not on PATH."""

from text_analyzer.cli import main

if __name__ == "__main__":
    main()
