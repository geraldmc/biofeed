"""Cache system for feed data."""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from biofeed.utils.config import DEFAULT_CONFIG

# Default cache duration from config or fallback to 1 hour (3600 seconds)
CACHE_DURATION = DEFAULT_CONFIG.get("cache_duration", 3600)

class FeedCache:
    """Cache system for feed data."""
    
    def __init__(self):
      """Initialize an empty cache."""
      self._cache: Dict[str, Any] = {}
      self._timestamps: Dict[str, datetime] = {}
    
    def get(self, key: str, max_age: Optional[int] = None) -> Optional[Any]:
      """Get an item from cache if it exists and is not too old.
      
      Args:
          key: Cache key (usually the feed URL)
          max_age: Maximum age in seconds (defaults to CACHE_DURATION)
              
      Returns:
          Cached data or None if not found or expired
      """
      if max_age is None:
          max_age = CACHE_DURATION
          
      if key in self._cache and key in self._timestamps:
          age = (datetime.now() - self._timestamps[key]).total_seconds()
          if age <= max_age:
              return self._cache[key]
      return None
    
    def set(self, key: str, data: Any) -> None:
      """Store an item in the cache.
      
      Args:
          key: Cache key (usually the feed URL)
          data: Data to store
      """
      self._cache[key] = data
      self._timestamps[key] = datetime.now()
    
    def clear(self) -> None:
      """Clear the entire cache."""
      self._cache.clear()
      self._timestamps.clear()
    
    def get_timestamp(self, key: str) -> Optional[datetime]:
      """Get the timestamp when an item was cached.
      
      Args:
          key: Cache key
          
      Returns:
          Timestamp or None if key not found
      """
      return self._timestamps.get(key)
    
    def get_age(self, key: str) -> Optional[float]:
      """Get the age of a cached item in seconds.
      
      Args:
          key: Cache key
          
      Returns:
          Age in seconds or None if key not found
      """
      if key in self._timestamps:
          return (datetime.now() - self._timestamps[key]).total_seconds()
      return None
    
    def is_expired(self, key: str, max_age: Optional[int] = None) -> bool:
      """Check if a cached item is expired.
      
      Args:
          key: Cache key
          max_age: Maximum age in seconds (defaults to CACHE_DURATION)
          
      Returns:
          True if expired or not found, False otherwise
      """
      if max_age is None:
          max_age = CACHE_DURATION
          
      age = self.get_age(key)
      if age is None:
          return True
      return age > max_age

# Global cache instance
cache = FeedCache()

# Legacy functions for backward compatibility
def get_from_cache(url: str, max_age: Optional[int] = None) -> Optional[Any]:
  """Get an item from cache if it exists and is not too old."""
  return cache.get(url, max_age)

def store_in_cache(url: str, data: Any) -> None:
  """Store an item in the cache."""
  cache.set(url, data)

def clear_cache() -> None:
  """Clear the entire cache."""
  cache.clear()