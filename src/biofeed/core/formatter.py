# src/reader/formatter.py
from typing import List
from datetime import datetime
import textwrap
from biofeed.feeds.article import Article

class ArticleFormatter:
    """Formats articles for display in terminal."""
    
    @staticmethod
    def format_date(date_str: str) -> str:
      """Format date string to a consistent format."""
      try:
          # Try different date formats
          for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
              try:
                  dt = datetime.strptime(date_str[:19], fmt)  # Only use first 19 chars to avoid timezone issues
                  return dt.strftime("%Y-%m-%d")
              except ValueError:
                  continue
      except Exception:
          # If all parsing fails, return the original string
          return date_str[:10] if len(date_str) >= 10 else date_str
    
    @staticmethod
    def format_article_list(articles: List[Article], include_summary: bool = False) -> str:
      """Format a list of articles for display."""
      if not articles:
          return "No articles found."
      
      result = []
      for i, article in enumerate(articles):
          # Format the date
          date = ArticleFormatter.format_date(article.published)
          
          # Create the line
          line = f"{i:>3}. {article.title} ({date})"
          result.append(line)
          
          # Add summary if requested
          if include_summary and article.summary:
              summary = textwrap.fill(
                  article.summary, 
                  width=80, 
                  initial_indent="     ", 
                  subsequent_indent="     "
              )
              result.append(summary)
              result.append("")
      
      return "\n".join(result)
    
    @staticmethod
    def format_article_detail(article: Article) -> str:
      """Format an article for detailed display."""
      # Format the date
      date = ArticleFormatter.format_date(article.published)
      
      # Format authors
      authors = article.author or "Unknown"
      
      # Format summary/content
      content = article.content or article.summary or "No content available."
      if isinstance(content, list):  # Some feeds provide content as a list of dictionaries
          content = " ".join(item.get("value", "") for item in content)
      
      # Create the formatted output
      lines = [
          f"\n{'=' * 80}",
          f"TITLE: [grey]{article.title}",
          f"DATE: {date}",
          f"AUTHORS: {authors}",
          f"URL: {article.link}",
          f"\nABSTRACT:",
          f"{textwrap.fill(content, width=80)}",
          f"{'=' * 80}\n"
      ]
      
      return "\n".join(lines)