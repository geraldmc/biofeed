"""Entry point for the BioFeed CLI."""

import sys
import typer
from biofeed.cli.commands import main

if __name__ == "__main__":
    sys.exit(main())