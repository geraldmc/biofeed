"""Tests for the FeedSource and FeedParser classes."""
import pathlib
import pytest
from unittest.mock import patch, MagicMock

from biofeed.feeds.feed_source import FeedSource
from biofeed.feeds.feed_parser import FeedParser
from biofeed.feeds.article import Article

# Get fixtures directory
CWD = pathlib.Path(__file__).resolve().parent
FIXTURES = f"{CWD}/fixtures"

@pytest.fixture
def feed_files():
    """Return paths to all feed fixture files."""
    return [
        f"{FIXTURES}/nature_20250319.xml",
        f"{FIXTURES}/oxford_20250413.xml", 
        f"{FIXTURES}/biorxiv_20250413.xml",
        f"{FIXTURES}/plos_20250413.xml",
        f"{FIXTURES}/bmc_20250413.xml"
    ]

@pytest.fixture
def feed_formats():
  """Return a list of feed format names corresponding to the fixture files."""
  return ["atom", "rss", "rdf", "atom", "rss"]

# FeedParser Tests

@pytest.mark.parametrize("feed_file", [
  "nature_20250319.xml", 
  "oxford_20250413.xml", 
  "biorxiv_20250413.xml",
  "plos_20250413.xml",
  "bmc_20250413.xml"
])
def test_feed_parser_parse_feed(feed_file):
  """Test that FeedParser.parse_feed correctly parses different feed formats."""
  with open(f"{FIXTURES}/{feed_file}") as f:
    import fastfeedparser
    feed_data = fastfeedparser.parse(f.read())
    
    articles = FeedParser.parse_feed(feed_data)
    
    # Basic validation of parsing results
    assert isinstance(articles, list)
    assert len(articles) > 0
    assert all(isinstance(article, Article) for article in articles)
    
    # Check essential fields
    for article in articles:
        assert article.id
        assert article.title
        assert article.link
        assert article.published

def test_feed_parser_extract_authors():
  """Test extraction of author information from different formats."""
  test_cases = [
    # Dictionary author
    {"entry": MagicMock(author={"name": "Jane Curtain"}), "expected": "Jane Curtain"},
    
    # List of authors
    {"entry": MagicMock(authors=[{"name": "Alice in Chains"}]), "expected": "Alice in Chains"},
    
    # Multiple authors (should return first)
    {"entry": MagicMock(authors=[MagicMock(__str__=lambda self: "Bob Dylan")]), 
      "expected": "Bob Dylan"},
    
    # No author
    {"entry": MagicMock(spec=[]), "expected": "Unknown"}
  ]
  
  for case in test_cases:
    result = FeedParser._extract_author(case["entry"])
    assert result == case["expected"]

def test_feed_parser_extract_date():
  """Test extraction of dates from entries."""
  entry = MagicMock(published="2025-05-07", updated="2025-05-08")
  
  published = FeedParser._extract_date(entry, ["published", "pubDate"])
  updated = FeedParser._extract_date(entry, ["updated", "modified"])
  
  assert published == "2025-05-07"
  assert updated == "2025-05-08"

def test_feed_parser_extract_link():
  """Test extraction of links from different feed formats."""
  # Simple link
  entry1 = MagicMock(link="https://example.com/article1")
  
  # Atom-style links list
  entry2 = MagicMock(link=None)
  entry2.links = [
    {"rel": "alternate", "href": "https://example.com/article2"},
    {"rel": "related", "href": "https://example.com/related"}
  ]
  # No preferred link type
  entry3 = MagicMock(link=None)
  entry3.links = [
    {"rel": "related", "href": "https://example.com/article3"}
  ]
  assert FeedParser._extract_link(entry1) == "https://example.com/article1"
  assert FeedParser._extract_link(entry2) == "https://example.com/article2"
  assert FeedParser._extract_link(entry3) == "https://example.com/article3"

# FeedSource Tests

def test_feed_source_init():
    """Test FeedSource initialization."""
    feed = FeedSource("Test Feed", "https://example.com/feed.xml", "test")
    
    assert feed.name == "Test Feed"
    assert feed.url == "https://example.com/feed.xml"
    assert feed.category == "test"
    assert feed._last_fetched is None

@patch("biofeed.feeds.feed_source.fastfeedparser")
@patch("biofeed.feeds.feed_source.FeedParser")
def test_feed_source_get_articles(mock_parser, mock_fastfeedparser):
    """Test getting articles from a feed."""
    # Set up mocks
    mock_feed_data = MagicMock()
    mock_fastfeedparser.parse.return_value = mock_feed_data
    
    mock_articles = [MagicMock(spec=Article) for _ in range(3)]
    mock_parser.parse_feed.return_value = mock_articles
    
    # Create feed and get articles
    feed = FeedSource("Test Feed", "https://example.com/feed.xml")
    articles = feed.get_articles()

    # Verify results
    mock_fastfeedparser.parse.assert_called_once_with("https://example.com/feed.xml")
    mock_parser.parse_feed.assert_called_once_with(mock_feed_data)
    assert articles == mock_articles

@patch("biofeed.feeds.feed_source.FeedParser")
@patch.object(FeedSource, "fetch")
def test_feed_source_get_article_by_id(mock_fetch, mock_parser):
    """Test getting a specific article by ID."""
    mock_articles = [
        Article(id="0", title="Article 1", link="https://example.com/1", published="2025-05-01"),
        Article(id="1", title="Article 2", link="https://example.com/2", published="2025-05-02"),
        Article(id="test-id", title="Article 3", link="https://example.com/3", published="2025-05-03")
    ]
    mock_fetch.return_value = MagicMock()
    mock_parser.parse_feed.return_value = mock_articles
    
    feed = FeedSource("Test Feed", "https://example.com/feed.xml")
    
    # Test getting by numeric ID
    article = feed.get_article("0")
    assert article.title == "Article 1"
    
    # Test getting by string ID
    article = feed.get_article("test-id")
    assert article.title == "Article 3"
    
    # Test ID not found
    with pytest.raises(ValueError):
        feed.get_article("nonexistent")
