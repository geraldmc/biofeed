from datetime import datetime, timedelta
from typing import Dict, Any, Optional

CACHE_DURATION = 3600  # Default cache duration in seconds (1 hour)
_CACHE: Dict[str, Any] = {}
_CACHE_TIMESTAMPS: Dict[str, datetime] = {}

def get_from_cache(url: str, max_age: Optional[int] = CACHE_DURATION) -> Optional[Any]:
    """Get an item from cache if it exists and is not too old."""
    if url in _CACHE and url in _CACHE_TIMESTAMPS:
        age = (datetime.now() - _CACHE_TIMESTAMPS[url]).total_seconds()
        if age <= max_age:
            return _CACHE[url]
    return None

def store_in_cache(url: str, data: Any) -> None:
    """Store an item in the cache."""
    _CACHE[url] = data
    _CACHE_TIMESTAMPS[url] = datetime.now()

def clear_cache() -> None:
    """Clear the entire cache."""
    _CACHE.clear()
    _CACHE_TIMESTAMPS.clear()