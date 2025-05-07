# BioFeed

A command-line tool for browsing and reading the latest bioinformatics articles from various RSS, Atom, and JSON feeds.

## Overview

BioFeed helps bioinformatics researchers stay up-to-date with the latest publications by providing a simple command-line interface to browse, manage, and read articles from multiple sources. It standardizes articles from different feed formats into a consistent representation, making it easy to consume content from diverse publishers.

## Features

- Simple and intuitive command-line interface
- Browse recent articles from multiple bioinformatics sources
- Support for RSS, Atom, and JSON feed formats
- Manage multiple feed sources (add, remove, list)
- Select active feed to browse
- Read article details including title, publication date, authors, and abstract
- Caching system to reduce network requests and improve performance
- Standardized article representation regardless of source format

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/geraldmc/biofeed.git
cd biofeed

# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

### Using pip

```bash
# Install directly from GitHub
pip install git+https://github.com/geraldmc/biofeed.git

# Or once published to PyPI
pip install biofeed
```

## Dependencies

The project requires the following dependencies:

- Python 3.9+
- fastfeedparser (for RSS and Atom parsing)
- requests (for HTTP requests)
- beautifulsoup4 (for HTML parsing)
- dateparser (for handling various date formats)

See `requirements.txt` or `pyproject.toml` for a complete list.

## Usage

BioFeed provides several commands for managing feeds and reading articles.

### Managing Feeds

```bash
# List available feeds
biofeed feeds --list

# Add a new feed
biofeed feeds --add "Feed Name" "https://feed-url.com/feed.xml"

# Remove a feed
biofeed feeds --remove feed_id

# Select a feed to browse
biofeed feeds --select feed_id
```

### Reading Articles

```bash
# List recent articles from the active feed
biofeed list

# List a specific number of articles
biofeed list --count 20

# List articles from a specific feed
biofeed list --feed feed_id

# Read a specific article by ID
biofeed read 0
```

### Example Session

```bash
# Start by listing available feeds
$ biofeed feeds --list

Available feeds:
biorxiv		bioRxiv Bioinformatics
bmc		BMC Bioinformatics
oxford		Oxford Bioinformatics
nature		Nature Bioinformatics
plos		PLOS Computational Biology

# Select a feed (e.g., bioRxiv - the preprint server for biology)
$ biofeed feeds --select biorxiv

Selected feed 'biorxiv'

# List the 5 most recent articles
$ biofeed list --count 5

Articles from bioRxiv Bioinformatics:
  0. mimicDetector: a pipeline for protein motif mimicry detection in host-pathogen systems (2025-05-05)
  1. PyCycleBio: modelling non-sinusoidal-oscillator systems in temporal biology (2025-05-05)
  2. Limits of deep-learning-based RNA prediction methods (2025-05-05)
  3. Athlytics: A Computational Framework for Longitudinal Analysis of Exercise Physiology Metrics from Wearable Sensor Data (2025-05-05)
  4. Quantification of single cell-type-specific alternative transcript initiation (2025-05-04)

# Read an article
$ biofeed read 0

================================================================================
TITLE: mimicDetector: a pipeline for protein motif mimicry detection in host-pathogen systems
DATE: 2025-05-05
AUTHORS:  Rich, K. D., Wasmuth, J. D.
URL:
https://www.biorxiv.org/content/10.1101/2025.05.02.651971v1?rss=1


ABSTRACT:
Motivation: Molecular mimicry is a widespread strategy used by pathogens to
evade the host immune system and manipulate other host cellular processes.
Detecting these events--where pathogen proteins resemble host molecules--is
challenging due to limitations in the sensitivity, specificity, and scalability
of current bioinformatics tools. The challenges are pronounced when identifying
subtle similarities in short protein fragments. 
...
...
https://github.com/Kayleerich/mimicDetector/, implemented in Python, and
compatible with Unix-based systems.
================================================================================
```

## Python API Usage

BioFeed can also be used as a Python library in your own projects:

```python
import biofeed

# Get available feeds
feeds = biofeed.get_available_feeds()
print(feeds)

# Get articles from a specific feed
articles = biofeed.get_articles(feed_id='nature_bioinformatics', count=5)
for article in articles:
    print(f"{article.title} ({article.published})")

# Add a new feed
feed_id = biofeed.add_feed("My Feed", "https://example.com/feed.xml", "custom")
```

For more advanced usage:

```python
from biofeed import ReaderController, FeedRegistry, FeedSource

# Create a controller
controller = ReaderController()

# Select a feed
controller.select_feed('nature_bioinformatics')

# Get recent articles
articles = controller.get_recent_articles(count=10)

# Search for articles
results = controller.search_articles("CRISPR")
```

## Project Structure

```
biofeed
├── README.md
├── pyproject.toml
├── src
│   ├── biofeed
│   │   ├── cli
│   │   │   └── commands.py
│   │   ├── core
│   │   │   ├── controller.py
│   │   │   └── formatter.py
│   │   ├── feeds
│   │   │   ├── article.py
│   │   │   ├── cache.py
│   │   │   ├── feed_parser.py
│   │   │   ├── feed_source.py
│   │   │   └── registry.py
│   │   └── utils
│   │       └── config.py
├── tests
│   ├── cli
│   │   └── test_cli.py
│   ├── core
│   │   ├── test_controller.py
│   │   └── test_formatter.py
│   ├── feeds
│   │   ├── fixtures
│   │   │   ├── biorxiv_20250413.xml
│   │   │   ├── bmc_20250413.xml
│   │   │   ├── feeds.json
│   │   │   ├── nature_20250319.xml
│   │   │   ├── oxford_20250413.xml
│   │   │   └── plos_20250413.xml
│   │   ├── test_entries.py
│   │   ├── test_feeds.py
│   │   └── test_single_feed.py
│   │   └── test_registry.py
│   └── utils
│       └── test_utils.py
└── uv.lock
```

## Default Feeds

BioFeed comes pre-configured with several bioinformatics feeds:

- bioRxiv Bioinformatics (RSS)
- BMC Bioinformatics (RSS)
- Oxford Bioinformatics (RSS)
- Nature Bioinformatics (Atom)
- PLOS Computational Biology (RSS)

You can add your own feeds using the `feeds --add` command.

## Configuration

BioFeed stores feed configuration in:

`~/.config/biofeed/feeds.json`

This file is created automatically when you first run the application.

## Testing

The project uses pytest for testing. To run the tests:

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run the tests
pytest

# Run with coverage
pytest --cov=reader
```

See the Testing section below for more information on writing tests for BioFeed.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Future Enhancements

- Article search functionality
- Export articles to different formats (PDF, Markdown)
- Filter articles by category/tag
- Integration with reference management systems
- Full-text article retrieval where available
- Notification system for new articles