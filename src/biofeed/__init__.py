"""BioFeed - A package for browsing bioinformatics articles from feeds.

This package provides tools to fetch, parse, and display articles from
various bioinformatics feeds (RSS, Atom, JSON).
"""

__version__ = "0.1.0"

# Core components
from biofeed.core.controller import ReaderController
from biofeed.feeds.article import Article
from biofeed.feeds.feed_source import FeedSource
from biofeed.feeds.registry import FeedRegistry

# Convenience functions
def get_controller():
    """Get a pre-configured ReaderController instance."""
    return ReaderController()

def get_available_feeds():
    """Get a list of all available feeds."""
    controller = get_controller()
    return controller.get_available_feeds()

def get_articles(feed_id=None, count=10):
    """Get articles from a specific feed or the default feed."""
    controller = get_controller()
    if feed_id:
        controller.select_feed(feed_id)
    return controller.get_recent_articles(count=count)

def add_feed(name, url, category="general"):
    """Add a new feed and return its ID."""
    controller = get_controller()
    return controller.add_feed(name, url, category)