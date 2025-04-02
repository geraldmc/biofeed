"""Controller for coordinating feed selection and article retrieval."""

from typing import Dict, List, Optional
import re

from biofeed.feeds.registry import FeedRegistry
from biofeed.feeds.feed_source import FeedSource
from biofeed.feeds.article import Article
from biofeed.utils.config import load_config, save_config

class ReaderController:
    """Coordinates feed selection and article retrieval."""
    
    def __init__(self, registry: Optional[FeedRegistry] = None):
        """Initialize the reader controller.
        
        Args:
            registry: Optional FeedRegistry instance to use.
                If None, a new FeedRegistry is created.
        """
        self.registry = registry or FeedRegistry()
        self.active_feed: Optional[FeedSource] = None
        self._initialize()
    
    def _initialize(self) -> None:
        """Set up initial state."""
        # Try to load the last used feed from settings
        settings = load_config("settings.json", default={"last_feed": None})
        last_feed = settings.get("last_feed")
        
        if last_feed:
            try:
                self.active_feed = self.registry.get_feed(last_feed)
                return
            except ValueError:
                pass  # Feed not found, continue with fallback
        
        # Fallback: use the first available feed
        feeds = self.registry.list_feeds()
        if feeds:
            self.active_feed = self.registry.get_feed(feeds[0]["id"])
    
    def _save_last_feed(self) -> None:
        """Save the active feed to settings."""
        if self.active_feed:
            settings = load_config("settings.json", default={})
            settings["last_feed"] = next(
                (feed_id for feed_id, feed in self.registry.feeds.items() 
                 if feed is self.active_feed),
                None
            )
            save_config("settings.json", settings)
    
    def get_available_feeds(self) -> List[Dict[str, str]]:
        """Get list of all available feeds.
        
        Returns:
            List of dictionaries containing feed information
        """
        return self.registry.list_feeds()
    
    def select_feed(self, feed_id: str) -> FeedSource:
        """Select a feed as the active feed.
        
        Args:
            feed_id: ID of the feed to select
            
        Returns:
            The selected FeedSource object
            
        Raises:
            ValueError: If the feed ID is not found
        """
        self.active_feed = self.registry.get_feed(feed_id)
        self._save_last_feed()
        return self.active_feed
    
    def get_active_feed(self) -> Optional[FeedSource]:
        """Get the currently active feed.
        
        Returns:
            The active FeedSource object or None if no feed is selected
        """
        return self.active_feed
    
    def add_feed(self, name: str, url: str, category: str = "general") -> str:
        """Add a new feed and return its ID.
        
        Args:
            name: Display name for the feed
            url: URL of the feed
            category: Category of the feed (default: "general")
            
        Returns:
            The ID of the newly created feed
        """
        # Create a unique ID from the name
        feed_id = self._create_feed_id(name)
        
        # Add the feed to the registry
        self.registry.add_feed(feed_id, name, url, category=category)
        return feed_id
    
    def _create_feed_id(self, name: str) -> str:
        """Create a unique feed ID from a name.
        
        Args:
            name: Display name for the feed
            
        Returns:
            A unique feed ID
        """
        # Convert to lowercase, replace spaces with underscores
        feed_id = re.sub(r'[^a-z0-9_]', '', name.lower().replace(' ', '_'))
        
        # Handle duplicate IDs
        existing_ids = {feed["id"] for feed in self.registry.list_feeds()}
        if feed_id in existing_ids:
            counter = 1
            while f"{feed_id}_{counter}" in existing_ids:
                counter += 1
            feed_id = f"{feed_id}_{counter}"
        
        return feed_id
    
    def remove_feed(self, feed_id: str) -> None:
        """Remove a feed.
        
        Args:
            feed_id: ID of the feed to remove
        """
        # Check if the active feed is being removed
        if self.active_feed and feed_id in self.registry.feeds and self.registry.feeds[feed_id] is self.active_feed:
            self.active_feed = None
            
        self.registry.remove_feed(feed_id)
    
    def get_recent_articles(self, count: int = 10, force_refresh: bool = False) -> List[Article]:
        """Get the most recent articles from the active feed.
        
        Args:
            count: Maximum number of articles to retrieve
            force_refresh: Whether to force a refresh of the feed data
            
        Returns:
            List of Article objects
            
        Raises:
            ValueError: If no active feed is selected
        """
        if not self.active_feed:
            raise ValueError("No active feed selected")
        
        articles = self.active_feed.get_articles(force_refresh=force_refresh)
        return articles[:min(count, len(articles))]
    
    def get_article(self, article_id: str) -> Article:
        """Get a specific article by ID.
        
        Args:
            article_id: ID of the article to retrieve
            
        Returns:
            The requested Article object
            
        Raises:
            ValueError: If no active feed is selected or if the article is not found
        """
        if not self.active_feed:
            raise ValueError("No active feed selected")
        
        return self.active_feed.get_article(article_id)
    
    def search_articles(self, query: str, count: int = 10) -> List[Article]:
        """Search for articles matching a query.
        
        Args:
            query: Search query
            count: Maximum number of articles to return
            
        Returns:
            List of Article objects matching the query
            
        Raises:
            ValueError: If no active feed is selected
        """
        if not self.active_feed:
            raise ValueError("No active feed selected")
        
        articles = self.active_feed.get_articles()
        
        # Simple search implementation - can be improved later
        query = query.lower()
        results = []
        
        for article in articles:
            if (query in article.title.lower() or 
                (article.summary and query in article.summary.lower()) or
                (article.content and query in article.content.lower())):
                results.append(article)
                if len(results) >= count:
                    break
        
        return results