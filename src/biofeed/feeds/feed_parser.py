from typing import Any, List, Dict
from biofeed.feeds.article import Article

class FeedParser:
    """Parser for feed formats that converts to standardized Article objects."""
    
    @staticmethod
    def parse_feed(feed_data: Any) -> List[Article]:
      """Parse feed data into a list of standardized Article objects."""
      if hasattr(feed_data, 'entries'):
          return FeedParser._parse_rss_feed(feed_data)
      elif isinstance(feed_data, dict) and 'items' in feed_data:
          return FeedParser._parse_json_feed(feed_data)
      return []

    @staticmethod
    def _parse_rss_feed(feed_data: Any) -> List[Article]:
      articles = []
      for index, entry in enumerate(feed_data.entries):
          articles.append(Article(
            id=str(index),
            title=getattr(entry, 'title', 'No Title'),
            link=FeedParser._extract_link(entry),
            published=FeedParser._extract_date(entry, ['published', 'pubDate', 'updated']),
            updated=FeedParser._extract_date(entry, ['updated', 'modified']),
            author=FeedParser._extract_author(entry),
            summary=FeedParser._extract_text(entry, ['summary', 'description']),
            content=FeedParser._extract_content(entry),
            categories=FeedParser._extract_categories(entry)
          ))
      return articles

    @staticmethod
    def _parse_json_feed(feed_data: Dict) -> List[Article]:
      articles = []
      for index, item in enumerate(feed_data['items']):
          articles.append(Article(
            id=str(index),
            title=item.get('title', 'No Title'),
            link=item.get('url', item.get('link', '')),
            published=item.get('date_published', ''),
            updated=item.get('date_modified', ''),
            author=FeedParser._extract_json_author(item),
            summary=item.get('summary', ''),
            content=item.get('content_text', item.get('content_html', '')),
            categories=item.get('tags', [])
          ))
      return articles

    # Helper methods: (_extract_author, _extract_json_author, _extract_date, 
    # _extract_text, _extract_content, _extract_categories, _extract_link)

    @staticmethod
    def _extract_author(entry: Any) -> str:
      """Extract author information from an entry."""
      author = getattr(entry, 'author', None)
      
      # Handle complex author structures
      if isinstance(author, dict) and 'name' in author:
          return author['name']
      elif hasattr(entry, 'authors') and entry.authors:
          if isinstance(entry.authors[0], dict) and 'name' in entry.authors[0]:
              return entry.authors[0]['name']
          return str(entry.authors[0])
      
      return author or 'Unknown'
    
    @staticmethod
    def _extract_json_author(item: Dict) -> str:
      """Extract author information from a JSON feed item."""
      author = item.get('author')
      if isinstance(author, dict):
          return author.get('name', 'Unknown')
      elif isinstance(author, list) and author:
          if isinstance(author[0], dict):
              return author[0].get('name', 'Unknown')
          return str(author[0])
      
      return author or 'Unknown'
    
    @staticmethod
    def _extract_date(entry: Any, possible_fields: List[str]) -> str:
      """Extract date from an entry, trying multiple possible field names."""
      for field in possible_fields:
          if hasattr(entry, field):
              return getattr(entry, field)
      return ''
    
    @staticmethod
    def _extract_text(entry: Any, possible_fields: List[str]) -> str:
      """Extract text content from an entry, trying multiple possible field names."""
      for field in possible_fields:
          if hasattr(entry, field):
              value = getattr(entry, field)
              if value:
                  # Handle possible dict format
                  if isinstance(value, dict) and 'value' in value:
                      return value['value']
                  return value
      return ''
    
    @staticmethod
    def _extract_content(entry: Any) -> str:
      """Extract the content from an entry, handling various formats."""
      content = getattr(entry, 'content', None)
      
      # Handle feedparser content list format
      if isinstance(content, list) and content:
          if isinstance(content[0], dict) and 'value' in content[0]:
              return content[0]['value']
          return str(content[0])
      
      # Try other possible content fields
      return FeedParser._extract_text(entry, ['content', 'content_encoded', 'description'])
    
    @staticmethod
    def _extract_categories(entry: Any) -> List[str]:
      """Extract categories/tags from an entry."""
      # Try tags attribute (common in feedparser)
      tags = getattr(entry, 'tags', None)
      if tags:
          # Handle different tag formats
          categories = []
          for tag in tags:
              if isinstance(tag, dict) and 'term' in tag:
                  categories.append(tag['term'])
              elif isinstance(tag, str):
                  categories.append(tag)
              else:
                  # Try to convert tag object to string
                  categories.append(str(tag))
          return categories
      
      # Try categories attribute
      categories = getattr(entry, 'categories', [])
      if categories:
          return [c if isinstance(c, str) else str(c) for c in categories]
      
      return []
    
    @staticmethod
    def _extract_link(entry: Any) -> str:
      """Extract the link from an entry, handling various formats."""
      # Simple link attribute
      if hasattr(entry, 'link') and entry.link:
          return entry.link
      
      # Links list attribute (common in Atom)
      links = getattr(entry, 'links', [])
      if links:
          # Try to find the first link with rel='alternate' or just the first link
          for link in links:
              if isinstance(link, dict):
                  # Prefer alternate links
                  if link.get('rel') == 'alternate':
                      return link.get('href', '')
          
          # If no alternate link found, use the first one
          if links and isinstance(links[0], dict) and 'href' in links[0]:
              return links[0]['href']
      
      return ''
