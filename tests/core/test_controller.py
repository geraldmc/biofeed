import pytest
from unittest.mock import MagicMock, patch

from biofeed.core.controller import ReaderController
from biofeed.feeds.registry import FeedRegistry
from biofeed.feeds.feed_source import FeedSource
from biofeed.feeds.article import Article

@pytest.fixture
def mock_registry():
  registry = MagicMock(spec=FeedRegistry)
  # Set up test feed
  test_feed = MagicMock(spec=FeedSource)
  test_feed.name = "Test Feed"
  
  registry.feeds = {"test_feed": test_feed}
  registry.list_feeds.return_value = [
      {"id": "test_feed", "name": "Test Feed", "category": "test"}
  ]
  registry.get_feed.return_value = test_feed
  return registry

@pytest.fixture
def mock_article():
  return Article(
    id="test-article-1",
    title="Test Article",
    link="https://example.com/article",
    published="2025-05-07T12:00:00Z",
    author="Test Author",
    summary="This is a test article summary."
  )

# Basic initialization test
@patch("biofeed.core.controller.load_config")
def test_controller_initialization(mock_load_config):
  # In the _initialize() method of ReaderController, the controller tries to load 
  # the last used feed from settings. To test, we ensure that there is no last feed.
  mock_load_config.return_value = {"last_feed": None}
  with patch("biofeed.core.controller.FeedRegistry") as MockRegistry:
    mock_registry = MockRegistry.return_value
    mock_registry.list_feeds.return_value = [
        {"id": "first_feed", "name": "First Feed", "category": "test"}
    ]
    
    controller = ReaderController()
    
    # Should try to get the first feed if no last feed is saved
    mock_registry.get_feed.assert_called_once_with("first_feed")

# Test get_available_feeds method
@patch.object(ReaderController, '_initialize')
def test_get_available_feeds(mock_init, mock_registry):
  controller = ReaderController(registry=mock_registry)
  
  feeds = controller.get_available_feeds()
  
  mock_registry.list_feeds.assert_called_once()
  assert feeds == mock_registry.list_feeds.return_value

# Test select_feed method
@patch.object(ReaderController, '_initialize')
def test_select_feed(mock_init, mock_registry):
  controller = ReaderController(registry=mock_registry)
  controller.active_feed = None  # Ensure clean state
  
  result = controller.select_feed("test_feed")
  
  mock_registry.get_feed.assert_called_once_with("test_feed")
  assert controller.active_feed == mock_registry.get_feed.return_value
  assert result == mock_registry.get_feed.return_value

# Test get_active_feed method
@patch.object(ReaderController, '_initialize')
def test_get_active_feed(mock_init, mock_registry):
    controller = ReaderController(registry=mock_registry)
    test_feed = mock_registry.get_feed.return_value
    controller.active_feed = test_feed
    
    result = controller.get_active_feed()
    
    assert result == test_feed

# Test add_feed method
@patch.object(ReaderController, '_initialize')
@patch.object(ReaderController, '_create_feed_id')
def test_add_feed(mock_create_id, mock_init, mock_registry):
  controller = ReaderController(registry=mock_registry)
  mock_create_id.return_value = "new_feed_id"
  
  feed_id = controller.add_feed("New Feed", "https://example.com/feed", "test")
  
  mock_registry.add_feed.assert_called_once_with(
      "new_feed_id", "New Feed", "https://example.com/feed", category="test"
  )
  assert feed_id == "new_feed_id"

  # Test get_article method
@patch.object(ReaderController, '_initialize')
def test_get_article(mock_init, mock_registry, mock_article):
  controller = ReaderController(registry=mock_registry)
  test_feed = mock_registry.get_feed.return_value
  controller.active_feed = test_feed
  
  test_feed.get_article.return_value = mock_article
  
  article = controller.get_article("test-article-1")
  
  test_feed.get_article.assert_called_once_with("test-article-1")
  assert article == mock_article

# Test get_recent_articles method
@patch.object(ReaderController, '_initialize')
def test_get_recent_articles(mock_init, mock_registry):
  controller = ReaderController(registry=mock_registry)
  test_feed = mock_registry.get_feed.return_value
  controller.active_feed = test_feed
  
  # Mock article results
  test_articles = [MagicMock(spec=Article) for _ in range(5)]
  test_feed.get_articles.return_value = test_articles
  
  # Test default count
  articles = controller.get_recent_articles()
  test_feed.get_articles.assert_called_once_with(force_refresh=False)
  assert articles == test_articles[:10]  # Default count is 10
  
  # Reset mock and test with custom count
  test_feed.get_articles.reset_mock()
  articles = controller.get_recent_articles(count=3)
  test_feed.get_articles.assert_called_once_with(force_refresh=False)
  assert articles == test_articles[:3]
  
  # Test with force_refresh
  test_feed.get_articles.reset_mock()
  articles = controller.get_recent_articles(force_refresh=True)
  test_feed.get_articles.assert_called_once_with(force_refresh=True)