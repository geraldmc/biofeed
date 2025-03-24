# src/reader/__main__.py (simplified)
import sys, os
import argparse
# The following is needed to run the program from the command line when
# the project root is not set in the PYTHONPATH.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # add project root to sys.path

from reader.controller import ReaderController
from reader.formatter import ArticleFormatter

def main() -> None:
    """Main entry point for the bio-reader application."""
    controller = ReaderController()
    formatter = ArticleFormatter()
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Browse bioinformatics articles from various feeds.")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Feed commands
    feed_parser = subparsers.add_parser("feeds", help="Manage feed sources")
    feed_parser.add_argument("--list", action="store_true", help="List available feeds")
    feed_parser.add_argument("--add", nargs=2, metavar=("NAME", "URL"), help="Add a new feed")
    feed_parser.add_argument("--remove", metavar="FEED_ID", help="Remove a feed")
    feed_parser.add_argument("--select", metavar="FEED_ID", help="Select active feed")
    
    # Article commands
    list_parser = subparsers.add_parser("list", help="List recent articles")
    list_parser.add_argument("--count", type=int, default=10, help="Number of articles to list")
    list_parser.add_argument("--feed", help="Feed to list articles from")
    
    read_parser = subparsers.add_parser("read", help="Read an article")
    read_parser.add_argument("article_id", help="ID of the article to read")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle commands
    if args.command == "feeds":
        if args.list:
            feeds = controller.get_available_feeds()
            print("\nAvailable feeds:")
            for feed in feeds:
                print(f"  {feed['id']}: {feed['name']} ({feed['category']})")
            
            active_feed = controller.get_active_feed()
            if active_feed:
                print(f"\nActive feed: {active_feed.name}")
        
        elif args.add:
            name, url = args.add
            feed_id = controller.add_feed(name, url)
            print(f"Added feed '{name}' with ID '{feed_id}'")
        
        elif args.remove:
            controller.remove_feed(args.remove)
            print(f"Removed feed '{args.remove}'")
        
        elif args.select:
            controller.select_feed(args.select)
            print(f"Selected feed '{args.select}'")
    
    elif args.command == "list":
        # Select feed if specified
        if args.feed:
            controller.select_feed(args.feed)
        
        active_feed = controller.get_active_feed()
        if not active_feed:
            print("No feed selected. Use 'feeds --select FEED_ID' to select a feed.")
            return
        
        print(f"\nArticles from {active_feed.name}:")
        articles = controller.get_recent_articles(count=args.count)
        print(formatter.format_article_list(articles))
    
    elif args.command == "read":
        active_feed = controller.get_active_feed()
        if not active_feed:
            print("No feed selected. Use 'feeds --select FEED_ID' to select a feed.")
            return
        
        try:
            article = controller.get_article(args.article_id)
            print(formatter.format_article_detail(article))
        except ValueError as e:
            print(f"Error: {e}")
    
    else:
        # Default action: list articles from active feed
        active_feed = controller.get_active_feed()
        if active_feed:
            print(f"\nArticles from {active_feed.name}:")
            articles = controller.get_recent_articles()
            print(formatter.format_article_list(articles))
        else:
            print("No feed selected. Use 'feeds --select FEED_ID' to select a feed.")
            parser.print_help()

if __name__ == "__main__":
    main()