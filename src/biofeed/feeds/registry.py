"""Feed registry for managing feed sources."""

from pathlib import Path
from typing import Dict, List, Optional

from biofeed.feeds.feed_source import FeedSource
from biofeed.utils.config import load_config, save_config, DEFAULT_CONFIG

class FeedRegistry:
    """Manages registration and retrieval of feed sources."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize the feed registry.
        
        Args:
            config_file: Optional path to a custom configuration file.
                If None, the default configuration location is used.
        """
        self.config_file = config_file or "feeds.json"
        self.feeds: Dict[str, FeedSource] = {}
        self._load_feeds()
    
    def _load_feeds(self) -> None:
        """Load feeds from config file."""
        feed_data = load_config(
            self.config_file, 
            default=DEFAULT_CONFIG.get("default_feeds", {})
        )
        
        for feed_id, feed_info in feed_data.items():
            self.feeds[feed_id] = FeedSource(
                feed_info["name"], 
                feed_info["url"], 
                feed_info.get("category", "general")
            )
    
    def _save_feeds(self) -> None:
        """Save feeds to config file."""
        feed_data = {}
        for feed_id, feed in self.feeds.items():
            feed_data[feed_id] = {
                "name": feed.name,
                "url": feed.url,
                "category": feed.category
            }
        
        save_config(self.config_file, feed_data)
    
    def add_feed(self, feed_id: str, name: str, url: str, category: str = "general") -> FeedSource:
        """Add a new feed source.
        
        Args:
            feed_id: Unique identifier for the feed
            name: Display name for the feed
            url: URL of the feed
            category: Category of the feed (default: "general")
            
        Returns:
            The newly created FeedSource object
        """
        self.feeds[feed_id] = FeedSource(name, url, category)
        self._save_feeds()
        return self.feeds[feed_id]
    
    def remove_feed(self, feed_id: str) -> None:
        """Remove a feed source.
        
        Args:
            feed_id: ID of the feed to remove
        """
        if feed_id in self.feeds:
            del self.feeds[feed_id]
            self._save_feeds()
    
    def get_feed(self, feed_id: str) -> FeedSource:
        """Get a feed source by ID.
        
        Args:
            feed_id: ID of the feed to retrieve
            
        Returns:
            The requested FeedSource object
            
        Raises:
            ValueError: If the feed ID is not found
        """
        if feed_id not in self.feeds:
            raise ValueError(f"Feed with ID {feed_id} not found")
        return self.feeds[feed_id]
    
    def list_feeds(self) -> List[Dict[str, str]]:
        """List all available feeds.
        
        Returns:
            List of dictionaries containing feed information
        """
        return [
            {"id": feed_id, "name": feed.name, "category": feed.category}
            for feed_id, feed in self.feeds.items()
        ]
    
    def get_feeds_by_category(self, category: str) -> List[FeedSource]:
        """Get all feeds in a specific category.
        
        Args:
            category: Category name to filter by
            
        Returns:
            List of FeedSource objects in the specified category
        """
        return [
            feed for feed in self.feeds.values() 
            if feed.category.lower() == category.lower()
        ]