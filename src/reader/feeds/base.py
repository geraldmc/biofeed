# src/reader/feeds/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union
import datetime

@dataclass
class Article:
    """Standardized article representation regardless of source format."""
    id: str
    title: str
    link: str
    published: str
    updated: Optional[str] = None
    author: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    categories: List[str] = None

    def __post_init__(self):
        if self.categories is None:
            self.categories = []

class FeedParser:
    """Parser for feed formats that converts to standardized Article objects."""
    
    @staticmethod
    def parse_feed(feed_data: Any) -> List[Article]:
        """Parse feed data into a list of standardized Article objects."""
        articles = []
        
        # Determine the type of feed by examining its structure
        if hasattr(feed_data, 'entries'):
            # This is likely a feedparser/fastfeedparser result (RSS or Atom)
            for index, entry in enumerate(feed_data.entries):
                # Extract author information
                author = FeedParser._extract_author(entry)
                
                # Extract publication date
                published = FeedParser._extract_date(entry, ['published', 'pubDate', 'updated'])
                
                # Extract updated date
                updated = FeedParser._extract_date(entry, ['updated', 'modified'])
                
                # Extract summary
                summary = FeedParser._extract_text(entry, ['summary', 'description'])
                
                # Extract content
                content = FeedParser._extract_content(entry)
                
                # Extract categories/tags
                categories = FeedParser._extract_categories(entry)
                
                articles.append(Article(
                    id=str(index),
                    title=getattr(entry, 'title', 'No Title'),
                    link=FeedParser._extract_link(entry),
                    published=published,
                    updated=updated,
                    author=author,
                    summary=summary,
                    content=content,
                    categories=categories
                ))
        elif isinstance(feed_data, dict) and 'items' in feed_data:
            # This is likely a JSON feed format
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

class FeedSource:
    """Generic feed source that works with multiple formats."""
    
    def __init__(self, name: str, url: str, category: str = "general"):
        self.name = name
        self.url = url
        self.category = category
        self._cache = None
        self._last_updated = None
        self._cache_duration = 3600  # Cache for 1 hour by default
    
    def fetch(self, force_refresh: bool = False) -> None:
        """Fetch the feed content."""
        # Only fetch if cache is empty or refresh is forced or cache has expired
        if (self._cache is None or force_refresh or
            (self._last_updated and 
             (datetime.datetime.now() - self._last_updated).seconds > self._cache_duration)):
            import fastfeedparser
            try:
                # Try to parse as RSS/Atom
                self._cache = fastfeedparser.parse(self.url)
            except Exception as e:
                # If parsing fails, try to fetch as JSON
                try:
                    import requests
                    response = requests.get(self.url)
                    self._cache = response.json()
                except Exception as json_error:
                    # Both parsing methods failed
                    raise ValueError(f"Failed to parse feed at {self.url}: {e}, {json_error}")
            
            self._last_updated = datetime.datetime.now()
    
    def get_articles(self) -> List[Article]:
        """Get list of articles in standardized format."""
        self.fetch()
        return FeedParser.parse_feed(self._cache)
    
    def get_article(self, article_id: str) -> Article:
        """Get a single article by ID."""
        articles = self.get_articles()
        try:
            index = int(article_id)
            if 0 <= index < len(articles):
                return articles[index]
            raise ValueError(f"Article ID {article_id} out of range")
        except ValueError:
            # If not an integer index, try matching by ID string
            for article in articles:
                if article.id == article_id:
                    return article
            raise ValueError(f"Article with ID {article_id} not found")