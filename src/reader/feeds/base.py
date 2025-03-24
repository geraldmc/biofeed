# src/reader/feeds/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

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

class FeedSource(ABC):
    """Abstract base class for all feed sources."""
    def __init__(self, name: str, url: str, category: str = "general"):
        self.name = name
        self.url = url
        self.category = category
        self._cache = None
        self._last_updated = None
    
    @abstractmethod
    def fetch(self, force_refresh: bool = False) -> None:
        """Fetch the feed content."""
        pass
    
    @abstractmethod
    def get_articles(self) -> List[Article]:
        """Return list of articles in standardized format."""
        pass
    
    @abstractmethod
    def get_article(self, article_id: str) -> Article:
        """Get a single article by ID."""
        pass