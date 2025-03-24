# src/reader/feeds/rss.py
import datetime
from typing import List
import fastfeedparser

from reader.feeds.base import FeedSource, Article

class RSSFeedSource(FeedSource):
  """Handler for RSS feeds."""
  
  def fetch(self, force_refresh: bool = False) -> None:
      """Fetch and parse the Atom feed."""
      # Only fetch if cache is empty or refresh is forced
      if self._cache is None or force_refresh or (
          self._last_updated and 
          (datetime.datetime.now() - self._last_updated).seconds > 3600
      ):
          self._cache = fastfeedparser.parse(self.url)
          self._last_updated = datetime.datetime.now()
  
  def get_articles(self) -> List[Article]:
      """Convert RSS entries to standardized Article objects."""
      self.fetch()
      articles = []
      
      for index, entry in enumerate(self._cache.entries):
          # Extract author name
          author = getattr(entry, 'author', None)
          # Some feeds have a complex author structure
          if isinstance(author, dict) and 'name' in author:
              author = author['name']
          
          articles.append(Article(
              id=str(index),  # Use index as ID for simplicity
              title=entry.title,
              link=entry.link,
              published=getattr(entry, 'published', getattr(entry, 'updated', '')),
              updated=getattr(entry, 'updated', None),
              author=author,
              summary=getattr(entry, 'summary', None),
              content=getattr(entry, 'content', None),
              categories=[tag.term for tag in getattr(entry, 'tags', [])]
          ))
      
      return articles
  
  def get_article(self, article_id: str) -> Article:
      """Get article by ID (index)."""
      articles = self.get_articles()
      try:
          return articles[int(article_id)]
      except (IndexError, ValueError):
          raise ValueError(f"Article with ID {article_id} not found")