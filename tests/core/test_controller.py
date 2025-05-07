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

# Specific test for initialization
def test_controller_initialization():
    with patch("biofeed.core.controller.load_config") as mock_load_config:
        # Test with no last feed
        mock_load_config.return_value = {"last_feed": None}
        with patch("biofeed.core.controller.FeedRegistry") as MockRegistry:
            mock_registry = MockRegistry.return_value
            mock_registry.list_feeds.return_value = [
                {"id": "first_feed", "name": "First Feed", "category": "test"}
            ]
            
            controller = ReaderController()
            
            # Should try to get the first feed
            mock_registry.get_feed.assert_called_once_with("first_feed")

# Tests for specific methods with initialization bypassed
@patch.object(ReaderController, '_initialize')
def test_select_feed(mock_init, mock_registry):
    controller = ReaderController(registry=mock_registry)
    controller.active_feed = None  # Ensure clean state
    
    controller.select_feed("test_feed")
    
    mock_registry.get_feed.assert_called_once_with("test_feed")
    assert controller.active_feed == mock_registry.get_feed.return_value