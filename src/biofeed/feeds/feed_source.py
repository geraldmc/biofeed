from typing import List, Optional, Any
from datetime import datetime

import fastfeedparser
import requests

from biofeed.feeds.article import Article
from biofeed.feeds.feed_parser import FeedParser
from biofeed.feeds.cache import get_from_cache, store_in_cache, CACHE_DURATION

class FeedSource:
    """Generic feed source that works with multiple formats."""
    
    def __init__(self, name: str, url: str, category: str = "general", cache_duration: int = CACHE_DURATION):
      self.name = name
      self.url = url
      self.category = category
      self.cache_duration = cache_duration
      self._last_fetched = None
    
    def fetch(self, force_refresh: bool = False) -> Any:
      """Fetch the feed content from source or cache."""
      if not force_refresh:
          cached_data = get_from_cache(self.url, self.cache_duration)
          if cached_data:
              self._last_fetched = _CACHE_TIMESTAMPS[self.url]
              return cached_data
      
      try:
          data = fastfeedparser.parse(self.url)
          store_in_cache(self.url, data)
          self._last_fetched = datetime.now()
          return data
      except Exception as e:
          try:
              response = requests.get(self.url)
              response.raise_for_status()
              data = response.json()
              store_in_cache(self.url, data)
              self._last_fetched = datetime.now()
              return data
          except Exception as json_error:
              raise ValueError(f"Failed to parse feed at {self.url}: {str(e)}, {str(json_error)}")
    
    def get_articles(self, force_refresh: bool = False) -> List[Article]:
      """Get list of articles in standardized format."""
      feed_data = self.fetch(force_refresh)
      return FeedParser.parse_feed(feed_data)
    
    def get_article(self, article_id: str) -> Article:
      """Get a single article by ID."""
      articles = self.get_articles()
      try:
          index = int(article_id)
          if 0 <= index < len(articles):
              return articles[index]
          raise ValueError(f"Article ID {article_id} out of range")
      except ValueError:
          for article in articles:
              if article.id == article_id:
                  return article
          raise ValueError(f"Article with ID {article_id} not found")
    
    def get_last_fetched(self) -> Optional[datetime]:
      """Get the timestamp of when this feed was last fetched."""
      return self._last_fetched