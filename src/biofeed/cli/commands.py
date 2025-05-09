# src/biofeed/cli/commands.py
"""Command-line interface for BioFeed using Typer."""

import typer
from rich import print
from typing import Optional, List
import sys

from biofeed.core.controller import ReaderController
from biofeed.core.formatter import ArticleFormatter

# Create the main app and controller
app = typer.Typer(help="Stay up-to-date with the latest bioinformatics publications from various feeds.")
controller = ReaderController()
formatter = ArticleFormatter()

# Define a feeds subcommand group
feeds_app = typer.Typer(help="Manage feed sources")
app.add_typer(feeds_app, name="feeds")

@feeds_app.callback(invoke_without_command=True)
def feeds_main(ctx: typer.Context):
    """Manage feed sources."""
    if ctx.invoked_subcommand is None:
        # Default behavior when just 'feeds' is called - list feeds
        feeds_list()

@feeds_app.command("list")
def feeds_list():
    """List available feeds."""
    feeds = controller.get_available_feeds()
    typer.echo("\nAvailable feeds:")
    for feed in feeds:
        typer.echo(f"{feed['id']}\t\t{feed['name']}")
    
    active_feed = controller.get_active_feed()
    if active_feed:
        typer.echo(f"\nActive feed: {active_feed.name}")

@feeds_app.command("add")
def feeds_add(
    name: str = typer.Argument(..., help="Display name for the feed"),
    url: str = typer.Argument(..., help="URL of the feed"),
    category: str = typer.Option("general", help="Category for the new feed")
):
    """Add a new feed."""
    feed_id = controller.add_feed(name, url, category=category)
    typer.echo(f"Added feed '{name}' with ID '{feed_id}'")

@feeds_app.command("remove")
def feeds_remove(
    feed_id: str = typer.Argument(..., help="ID of the feed to remove")
):
    """Remove a feed."""
    controller.remove_feed(feed_id)
    typer.echo(f"Removed feed '{feed_id}'")

@feeds_app.command("select")
def feeds_select(
    feed_id: str = typer.Argument(..., help="ID of the feed to select")
):
    """Select active feed."""
    controller.select_feed(feed_id)
    typer.echo(f"Selected feed '{feed_id}'")

@app.command()
def list(
    count: int = typer.Option(10, "--count", "-c", help="Number of articles to list"),
    feed: Optional[str] = typer.Option(None, "--feed", "-f", help="Feed to list articles from"),
    summary: bool = typer.Option(False, "--summary", "-s", help="Include article summaries")
):
    """List recent articles."""
    # Select feed if specified
    if feed:
        try:
            controller.select_feed(feed)
        except ValueError:
            typer.echo(f"Error: Feed '{feed}' not found")
            raise typer.Exit(1)
    
    active_feed = controller.get_active_feed()
    if not active_feed:
        typer.echo("No feed selected. Use 'feeds select FEED_ID' to select a feed.")
        raise typer.Exit(1)
    
    typer.echo(f"\nArticles from {active_feed.name}:")
    try:
        articles = controller.get_recent_articles(count=count)
        formatted_articles = formatter.format_article_list(articles, include_summary=summary)
        typer.echo(formatted_articles)
    except Exception as e:
        typer.echo(f"Error retrieving articles: {e}")
        raise typer.Exit(1)

@app.command()
def read(
    article_id: str = typer.Argument(..., help="ID of the article to read")
):
    """Read an article."""
    active_feed = controller.get_active_feed()
    if not active_feed:
        typer.echo("No feed selected. Use 'feeds select FEED_ID' to select a feed.")
        raise typer.Exit(1)
    
    try:
        article = controller.get_article(article_id)
        typer.echo(formatter.format_article_detail(article))
    except ValueError as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(1)

@app.callback(invoke_without_command=True)
def main_callback(ctx: typer.Context):
    """Main callback that runs if no subcommand is provided."""
    if ctx.invoked_subcommand is None:
        # Default behavior - list articles from active feed
        active_feed = controller.get_active_feed()
        if active_feed:
            typer.echo(f"\nArticles from {active_feed.name}:")
            articles = controller.get_recent_articles()
            typer.echo(formatter.format_article_list(articles))
        else:
            typer.echo("No feed selected. Use 'feeds select FEED_ID' to select a feed.")
            # Show help
            ctx.obj = {}
            ctx.invoke(app)

def main():
    """Main entry point for the biofeed CLI."""
    app()
    return 0

if __name__ == "__main__":
    sys.exit(main())