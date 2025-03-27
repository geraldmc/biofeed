# src/reader/controller.py
from typing import Dict, List, Optional
from reader.feeds.registry import FeedRegistry
from reader.feeds.feed_source import FeedSource
from reader.feeds.article import Article

class ReaderController:
    """Coordinates feed selection and article retrieval."""
    
    def __init__(self):
        self.registry = FeedRegistry()
        self.active_feed: Optional[FeedSource] = None
        self._initialize()
    
    def _initialize(self):
        """Set up initial state."""
        # Try to load the last used feed, or use the first available
        feeds = self.registry.list_feeds()
        if feeds:
            self.active_feed = self.registry.get_feed(feeds[0]["id"])
    
    def get_available_feeds(self) -> List[Dict[str, str]]:
        """Get list of all available feeds."""
        return self.registry.list_feeds()
    
    def select_feed(self, feed_id: str) -> FeedSource:
        """Select a feed as the active feed."""
        self.active_feed = self.registry.get_feed(feed_id)
        return self.active_feed
    
    def get_active_feed(self) -> Optional[FeedSource]:
        """Get the currently active feed."""
        return self.active_feed
    
    def add_feed(self, name: str, url: str, category: str = "general") -> str:
        """Add a new feed and return its ID."""
        # Create a unique ID from the name
        feed_id = name.lower().replace(" ", "_")
        # Handle duplicate IDs
        existing_ids = {feed["id"] for feed in self.registry.list_feeds()}
        if feed_id in existing_ids:
            counter = 1
            while f"{feed_id}_{counter}" in existing_ids:
                counter += 1
            feed_id = f"{feed_id}_{counter}"
        
        self.registry.add_feed(feed_id, name, url, category=category)
        return feed_id
    
    def remove_feed(self, feed_id: str) -> None:
        """Remove a feed."""
        if self.active_feed and self.active_feed.name == feed_id:
            self.active_feed = None
        self.registry.remove_feed(feed_id)

      # Additional methods for ReaderController class
    def get_recent_articles(self, count: int = 10) -> List[Article]:
        """Get the most recent articles from the active feed."""
        if not self.active_feed:
            raise ValueError("No active feed selected")
        
        articles = self.active_feed.get_articles()
        return articles[:min(count, len(articles))]

    def get_article(self, article_id: str) -> Article:
        """Get a specific article by ID."""
        if not self.active_feed:
            raise ValueError("No active feed selected")
        
        return self.active_feed.get_article(article_id)