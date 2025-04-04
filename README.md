# BioFeed

A Python package and command-line tool for browsing and reading the latest bioinformatics articles from various feeds.

## Features

- Browse recent articles from multiple bioinformatics sources
- Support for RSS, Atom, and JSON feed formats
- Manage multiple feed sources (add, remove, list)
- Search articles by keyword
- Read article details including title, publication date, authors, and abstract
- Simple and intuitive command-line interface
- Importable Python API for use in your own projects

## Installation

### Using pip (recommended)

```bash
pip install biofeed
```

### From source

```bash
# Clone the repository
git clone https://github.com/geraldmc/biofeed.git
cd biofeed

# Install the package
pip install -e .
```

## Dependencies

The project requires the following dependencies:

- Python 3.9+
- fastfeedparser
- requests
- beautifulsoup4
- dateparser

## Command-Line Usage

BioFeed provides several commands for managing feeds and reading articles.

### Managing Feeds

```bash
# List available feeds
biofeed feeds --list

# Add a new feed
biofeed feeds --add "Feed Name" "https://feed-url.com/feed.xml"

# Add a feed with a specific category
biofeed feeds --add "Feed Name" "https://feed-url.com/feed.xml" --category "genetics"

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

# List articles with summaries
biofeed list --summary

# Read a specific article by ID
biofeed read 0
```

### Examples

```bash
# Start by listing available feeds
biofeed feeds --list

# Select a feed (e.g., Nature Bioinformatics)
biofeed feeds --select nature_bioinformatics

# List the 5 most recent articles
biofeed list --count 5

# Read the first article
biofeed read 0
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
biofeed/
├── src/
│   └── biofeed/
│       ├── __init__.py
│       ├── cli/
│       │   ├── __init__.py
│       │   ├── __main__.py
│       │   └── commands.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── controller.py
│       │   └── formatter.py
│       ├── feeds/
│       │   ├── __init__.py
│       │   ├── article.py
│       │   ├── cache.py
│       │   ├── feed_parser.py
│       │   ├── feed_source.py
│       │   └── registry.py
│       └── utils/
│           ├── __init__.py
│           └── config.py
├── tests/
├── pyproject.toml
├── setup.py
├── requirements.txt
└── README.md
```

## Default Feeds

BioFeed comes pre-configured with several bioinformatics feeds:

- Nature Bioinformatics (Atom)
- BMC Bioinformatics (RSS)
- Oxford Bioinformatics (RSS)
- PLOS Computational Biology (RSS)
- bioRxiv Bioinformatics (RSS)

You can add your own feeds using the `feeds --add` command or the Python API.

## Configuration

BioFeed stores configuration in:

`~/.config/biofeed/` (Linux/macOS)
`%APPDATA%\biofeed\` (Windows)

## Contributing

Contributions are welcome! Here's how you can contribute:

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add some amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Future Enhancements

- Web interface
- Advanced article filtering
- Favorite/bookmark articles
- Export articles to different formats (PDF, Markdown)
- Integration with reference managers