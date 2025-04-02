from dataclasses import dataclass, field
from typing import List, Optional

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
  categories: List[str] = field(default_factory=list)

  def __post_init__(self):
      if self.categories is None:
          self.categories = []