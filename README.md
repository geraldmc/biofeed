# BioFeed

A command-line tool for browsing and reading the latest bioinformatics articles from various feeds.

## Features

- Browse recent articles from multiple bioinformatics sources
- Support for both RSS and Atom feed formats. JSON feed support coming...
- Manage multiple feed sources (add, remove, list)
- Select active feed to browse
- Read article details including title, publication date, authors, and abstract
- Simple and intuitive command-line interface

## Installation

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

## Dependencies

The project requires the following dependencies:

- Python 3.9+
- fastfeedparser
- requests
- beautifulsoup4
- dateparser

See `requirements.txt` for a complete list. A `pyproject.toml` file is also provided. 

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

## Project Structure

```
biofeed/
├── src/
│   └── reader/
│       ├── __init__.py
│       ├── __main__.py        # Command-line interface
│       ├── controller.py      # Application controller
│       ├── formatter.py       # Article formatting
│       ├── feeds/
│           ├── __init__.py
│           ├── article.py     # Article data class
│           ├── cache.py       # Feed caching
│           ├── feed_parser.py # Feed parsing logic
│           ├── feed_source.py # Feed source management
│           ├── feeds.json     # Default feeds configuration
│           └── registry.py    # Feed registry
├── tests/                     # Test files
├── requirements.txt           # Project dependencies
├── pyproject.toml             # toml file
└── README.md                  # This file
```

## Default Feeds

BioFeed comes pre-configured with several bioinformatics feeds:

- Nature Bioinformatics (Atom)
- Nature Genetics (Atom)
- Nature Methods (Atom)
- Nature Reviews Cancer (Atom)
- Oxford Bioinformatics (RSS)

You can add your own feeds using the `feeds --add` command.

## Configuration

BioFeed stores feed configuration in:

`~/.config/biofeed/feeds.json`

This file is created automatically when you first run the application.

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
- Article search functionality
- Favorite/bookmark articles
- Export articles to different formats (PDF, Markdown)
- Filter articles by category/tag