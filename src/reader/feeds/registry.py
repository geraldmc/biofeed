# src/reader/feeds/registry.py
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Union

from reader.feeds.base import FeedSource
from reader.feeds.atom import AtomFeedSource
from reader.feeds.rss import RSSFeedSource

class FeedRegistry:
    """Manages registration and retrieval of feed sources."""
    
    def __init__(self, config_file: Optional[Path] = None):
        if config_file is None:
            # Default config location
            config_dir = Path.home() / ".config" / "biofeed"
            config_dir.mkdir(parents=True, exist_ok=True)
            self.config_file = config_dir / "feeds.json"
        else:
            self.config_file = config_file
        
        self.feeds: Dict[str, FeedSource] = {}
        self._load_feeds()
    
    def _load_feeds(self) -> None:
        """Load feeds from config file."""
        if not self.config_file.exists():
            self._initialize_default_feeds()
            return
        
        try:
            with open(self.config_file, "r") as f:
                feed_data = json.load(f)
            
            for feed_id, feed_info in feed_data.items():
                self._create_feed_source(
                    feed_id, 
                    feed_info["name"], 
                    feed_info["url"], 
                    feed_info["type"],
                    feed_info.get("category", "general")
                )
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading feeds: {e}")
            self._initialize_default_feeds()
    
    def _initialize_default_feeds(self) -> None:
        """Create default feeds configuration."""
        self.add_feed(
            "nature_bioinformatics",
            "Nature Bioinformatics", 
            "https://www.nature.com/subjects/bioinformatics.atom",
            "atom",
            "bioinformatics"
        )
        self._save_feeds()
    
    def _save_feeds(self) -> None:
        """Save feeds to config file."""
        feed_data = {}
        for feed_id, feed in self.feeds.items():
            feed_data[feed_id] = {
                "name": feed.name,
                "url": feed.url,
                "type": "atom" if isinstance(feed, AtomFeedSource) else "rss",
                "category": feed.category
            }
        
        with open(self.config_file, "w") as f:
            json.dump(feed_data, f, indent=2)
    
    def _create_feed_source(self, feed_id: str, name: str, url: str, 
                           feed_type: str, category: str) -> FeedSource:
        """Create appropriate feed source based on type."""
        if feed_type.lower() == "atom":
            self.feeds[feed_id] = AtomFeedSource(name, url, category)
        elif feed_type.lower() == "rss":
            self.feeds[feed_id] = RSSFeedSource(name, url, category)
        else:
            raise ValueError(f"Unsupported feed type: {feed_type}")
        return self.feeds[feed_id]
    
    def add_feed(self, feed_id: str, name: str, url: str, 
                feed_type: Optional[str] = None, category: str = "general") -> FeedSource:
        """Add a new feed source."""
        # Auto-detect feed type if not specified
        if feed_type is None:
            feed_type = self._detect_feed_type(url)
        
        feed = self._create_feed_source(feed_id, name, url, feed_type, category)
        self._save_feeds()
        return feed
    
    def _detect_feed_type(self, url: str) -> str:
        """Detect feed type by examining its content."""
        import fastfeedparser
        try:
            feed_data = fastfeedparser.parse(url)
            # Look for Atom namespace
            if hasattr(feed_data, 'namespaces') and 'http://www.w3.org/2005/Atom' in feed_data.namespaces.values():
                return "atom"
            # Check for RSS version
            elif hasattr(feed_data, 'version') and feed_data.version.startswith('rss'):
                return "rss"
            else:
                # Default to RSS if unsure
                return "rss"
        except Exception:
            # Default to RSS if detection fails
            return "rss"
    
    def remove_feed(self, feed_id: str) -> None:
        """Remove a feed source."""
        if feed_id in self.feeds:
            del self.feeds[feed_id]
            self._save_feeds()
    
    def get_feed(self, feed_id: str) -> FeedSource:
        """Get a feed source by ID."""
        if feed_id not in self.feeds:
            raise ValueError(f"Feed with ID {feed_id} not found")
        return self.feeds[feed_id]
    
    def list_feeds(self) -> List[Dict[str, str]]:
        """List all available feeds."""
        return [
            {"id": feed_id, "name": feed.name, "category": feed.category}
            for feed_id, feed in self.feeds.items()
        ]
    
    def get_feeds_by_category(self, category: str) -> List[FeedSource]:
        """Get all feeds in a specific category."""
        return [
            feed for feed in self.feeds.values() 
            if feed.category.lower() == category.lower()
        ]