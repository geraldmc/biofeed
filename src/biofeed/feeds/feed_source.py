"""Feed source implementation for retrieving feed content."""

from datetime import datetime
from typing import List, Optional, Any
import logging

import fastfeedparser
import requests

from biofeed.feeds.article import Article
from biofeed.feeds.feed_parser import FeedParser
from biofeed.feeds.cache import FeedCache, CACHE_DURATION, cache

# Set up logging
logger = logging.getLogger(__name__)

class FeedSource:
    """Generic feed source that works with multiple formats."""
    
    def __init__(
        self, 
        name: str, 
        url: str, 
        category: str = "general", 
        cache_duration: int = CACHE_DURATION
    ):
        """Initialize a feed source.
        
        Args:
            name: Display name for the feed
            url: URL of the feed
            category: Category of the feed (default: "general")
            cache_duration: Cache duration in seconds (default: CACHE_DURATION)
        """
        self.name = name
        self.url = url
        self.category = category
        self.cache_duration = cache_duration
        self._last_fetched: Optional[datetime] = None
        self._cache = cache  # Use the global cache instance
    
    def fetch(self, force_refresh: bool = False) -> Any:
        """Fetch the feed content from source or cache.
        
        Args: force_refresh: Whether to force a refresh of the feed data
        Returns: The feed data in its raw format
        Raises: ValueError: If the feed cannot be fetched or parsed
        """
        if not force_refresh:
            cached_data = self._cache.get(self.url, self.cache_duration)
            if cached_data:
                # Use the cache's method to get the timestamp
                self._last_fetched = self._cache.get_timestamp(self.url)
                return cached_data
        
        logger.info(f"Fetching feed from {self.url}")
        
        # Try parsing with fastfeedparser first (handles RSS/Atom feeds)
        try:
            data = fastfeedparser.parse(self.url)
            self._cache.set(self.url, data)
            self._last_fetched = datetime.now()  # Update the timestamp
            return data
        except Exception as e:
            logger.warning(f"Failed to parse feed with fastfeedparser: {e}")
            
            # Try as JSON
            try:
                response = requests.get(self.url, timeout=10)
                response.raise_for_status()
                data = response.json()
                self._cache.set(self.url, data)
                self._last_fetched = datetime.now()  # Update the timestamp
                return data
            except Exception as json_error:
                logger.error(f"Failed to parse feed as JSON: {json_error}")
                raise ValueError(
                    f"Failed to parse feed at {self.url}. "
                    f"Tried RSS/Atom and JSON formats but both failed."
                )
    
    def get_articles(self, force_refresh: bool = False) -> List[Article]:
        """Get list of articles in standardized format.
        
        Args: force_refresh: Whether to force a refresh of the feed data
        Returns: List of Article objects
        """
        feed_data = self.fetch(force_refresh)
        return FeedParser.parse_feed(feed_data)
    
    def get_article(self, article_id: str) -> Article:
        """Get a single article by ID.
        
        Args: article_id: ID of the article to retrieve
        Returns: The requested Article object
            
        Raises: ValueError: If the article is not found
        """
        articles = self.get_articles()
        
        # Try to interpret as index first
        try:
            index = int(article_id)
            if 0 <= index < len(articles):
                return articles[index]
            raise ValueError(f"Article ID {article_id} out of range")
        except ValueError:
            # Try as string ID
            for article in articles:
                if article.id == article_id:
                    return article
            raise ValueError(f"Article with ID {article_id} not found")
    
    def get_last_fetched(self) -> Optional[datetime]:
        """Get the timestamp of when this feed was last fetched.
        
        Returns: The timestamp when the feed was last fetched or None if never fetched
        """
        return self._last_fetched
    
    def __str__(self) -> str:
        """String representation of the feed source.
        
        Returns: String representation
        """
        return f"{self.name} ({self.category})"
    
    def __repr__(self) -> str:
        """Representation of the feed source.
                """
        return f"FeedSource(name='{self.name}', url='{self.url}', category='{self.category}')"