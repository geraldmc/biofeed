"""Command-line interface for BioFeed."""
import re 
from urllib.request import urlopen
import argparse
import sys
from typing import List, Optional

from biofeed.core.controller import ReaderController
from biofeed.core.formatter import ArticleFormatter
from bs4 import BeautifulSoup
from urllib.error import URLError, HTTPError

def handle_feeds_command(controller: ReaderController, args: argparse.Namespace) -> None:
    """Handle the 'feeds' command."""
    if args.list:
        feeds = controller.get_available_feeds()
        print("\nAvailable feeds:")
        for feed in feeds:
            #print(f"  {feed['id']}: {feed['name']} ({feed['category']})")
            print(f"{feed['id']}\t\t{feed['name']}")

        
        active_feed = controller.get_active_feed()
        if active_feed:
            print(f"\nActive feed: {active_feed.name}")
    
    elif args.add:
        name, url = args.add
        category = args.category or "general"
        feed_id = controller.add_feed(name, url, category=category)
        print(f"Added feed '{name}' with ID '{feed_id}'")
    
    elif args.remove:
        controller.remove_feed(args.remove)
        print(f"Removed feed '{args.remove}'")
    
    elif args.select:
        controller.select_feed(args.select)
        print(f"Selected feed '{args.select}'")

def handle_list_command(controller: ReaderController, formatter: ArticleFormatter, args: argparse.Namespace) -> None:
    """Handle the 'list' command."""
    # Select feed if specified
    if args.feed:
        controller.select_feed(args.feed)
    
    active_feed = controller.get_active_feed()
    if not active_feed:
        print("No feed selected. Use 'feeds --select FEED_ID' to select a feed.")
        return
    
    print(f"\nArticles from {active_feed.name}:")
    articles = controller.get_recent_articles(count=args.count)
    print(formatter.format_article_list(articles, include_summary=args.summary))

def handle_read_command(controller: ReaderController, formatter: ArticleFormatter, args: argparse.Namespace) -> None:
    """Handle the 'read' command."""
    active_feed = controller.get_active_feed()
    if not active_feed:
      print("No feed selected. Use 'feeds --select FEED_ID' to select a feed.")
      return  
    
    try:
      article = controller.get_article(args.article_id)
      
      # Clean article content based on feed source
      feed_name = controller.get_active_feed().name
      
      try:
        if 'PLOS' in feed_name:
          # Handle PLOS articles
          p = re.compile('<p>(.*?)</p>')
          m = p.match(article.content)
          if m:  # Did we find a match? FIXME: Raise error if not
            text = article.content[m.span()[1]:]
            article.content = text.replace('\n', '')
            
        elif 'Oxford' in feed_name:
          # Handle Oxford articles
          soup = BeautifulSoup(article.content, "html.parser")
          for data in soup(['style', 'script']):
            data.decompose()
          article.content = ' '.join(soup.stripped_strings)
          
          # Remove prefix if present
          prefix_to_remove = "Abstract Motivation"
          if article.content.startswith(prefix_to_remove):
            article.content = article.content[len(prefix_to_remove):].lstrip()
            
        elif 'Nature' in feed_name:
          # Handle Nature articles with error handling
          try:
            html = urlopen(article.link, timeout=10).read()
            soup = BeautifulSoup(html, features="html.parser")
            content_div = soup.find('div', attrs={'class':'c-article-section__content'})
            if content_div:
                article.content = content_div.text
          except (URLError, HTTPError) as e:
            print(f"Warning: Could not fetch full content from Nature: {e}")
                  
      except Exception as parse_error:
        print(f"Warning: Error cleaning content: {parse_error}")
        # Continue with original content if parsing fails
          
      print(formatter.format_article_detail(article))
        
    except ValueError as e:
        print(f"Error: {e}")

def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Browse bioinformatics articles from various feeds.")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Feed commands
    feed_parser = subparsers.add_parser("feeds", help="Manage feed sources")
    feed_parser.add_argument("--list", action="store_true", help="List available feeds")
    feed_parser.add_argument("--add", nargs=2, metavar=("NAME", "URL"), help="Add a new feed")
    feed_parser.add_argument("--category", help="Category for the new feed (used with --add)")
    feed_parser.add_argument("--remove", metavar="FEED_ID", help="Remove a feed")
    feed_parser.add_argument("--select", metavar="FEED_ID", help="Select active feed")
    
    # Article commands
    list_parser = subparsers.add_parser("list", help="List recent articles")
    list_parser.add_argument("--count", type=int, default=10, help="Number of articles to list")
    list_parser.add_argument("--feed", help="Feed to list articles from")
    list_parser.add_argument("--summary", action="store_true", help="Include article summaries")
    
    read_parser = subparsers.add_parser("read", help="Read an article")
    read_parser.add_argument("article_id", help="ID of the article to read")
    
    return parser.parse_args(args)

def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the biofeed CLI."""
    parsed_args = parse_args(args)
    controller = ReaderController()
    formatter = ArticleFormatter()
    
    if parsed_args.command == "feeds":
        handle_feeds_command(controller, parsed_args)
    elif parsed_args.command == "list":
        handle_list_command(controller, formatter, parsed_args)
    elif parsed_args.command == "read":
        handle_read_command(controller, formatter, parsed_args)
    else:
        # Default action: list articles from active feed
        active_feed = controller.get_active_feed()
        if active_feed:
            print(f"\nArticles from {active_feed.name}:")
            articles = controller.get_recent_articles()
            print(formatter.format_article_list(articles))
        else:
            print("No feed selected. Use 'feeds --select FEED_ID' to select a feed.")
            parse_args(["--help"])
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())