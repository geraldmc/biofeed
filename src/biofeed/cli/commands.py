"""Command-line interface for BioFeed."""
import re 
from urllib.request import urlopen
import argparse
import sys
from typing import List, Optional

from biofeed.core.controller import ReaderController
from biofeed.core.formatter import ArticleFormatter
from bs4 import BeautifulSoup
import textwrap

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
    try: # SOME feeds have idiosyncracies in how they handle article content
        article = controller.get_article(args.article_id)
        # Handle cleaning content for PLOS articles
        if 'PLOS' in controller.get_active_feed().name:
          # Get the HTML content from the article
          p = re.compile('<p>(.*?)</p>')
          m = p.match(article.content)
          text = article.content[m.span()[1]:]
          text = text.replace('\n', '')
          article.content = text
        # Handle cleaning content for Oxford articles
        elif 'Oxford' in controller.get_active_feed().name:
          soup = BeautifulSoup(article.content, "html.parser")
          for data in soup(['style', 'script']):
              # Remove tags
              data.decompose()
          text = ' '.join(soup.stripped_strings)
          article.content = text[20:]
        elif 'Nature' in controller.get_active_feed().name:
          html = urlopen(article.link).read()
          soup = BeautifulSoup(html, features="html.parser")
          subtext = soup.find('div', attrs={'class':'c-article-section__content'})
          article.content = subtext.text
        elif 'BMC' in controller.get_active_feed().name:
          pass # no operation needed for BMC articles
        elif 'bioRxiv' in controller.get_active_feed().name:
          pass # no operation needed for bioRxiv articles
        else:
          pass # no operation
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