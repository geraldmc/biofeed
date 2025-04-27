"""Tests for the fastfeedparser module."""
import pathlib
import pytest

import fastfeedparser

# Get fixtures directory
CWD = pathlib.Path(__file__).resolve().parent
FIXTURES = f"{CWD}/fixtures"

@pytest.fixture
def local_feeds():
  """Use local files instead of downloading."""
  biorxiv = f"{FIXTURES}/biorxiv_20250413.xml"
  bmc = f"{FIXTURES}/bmc_20250413.xml"
  nature = f"{FIXTURES}/nature_20250319.xml"
  oxford = f"{FIXTURES}/oxford_20250413.xml"
  plos = f"{FIXTURES}/plos_20250413.xml"

  feeds = [biorxiv, bmc, nature, oxford, plos] 
  return feeds

# Tests
#
def test_feedparser(local_feeds):
  """Can we read the site titles and links?"""
  #FIXME: Testing the feed, or the content?
  for feed in local_feeds:
    with open(feed) as f:
      xml_content = f.read()
      # Parse the feed data
      myfeed = fastfeedparser.parse(xml_content)
      assert xml_content, f"Failed to parse feed: {myfeed}"
      # Check if a site title is present
      assert hasattr(xml_content, 'title'), f"No title found in feed: {myfeed}"
      # Check if the feed has entries
      assert hasattr(myfeed, 'entries'), f"No entries found in feed: {myfeed}"
      # Check if the first entry has a title
      assert hasattr(myfeed.entries[0], 'title'), f"No title found in first entry of feed: {myfeed}"
      # Check if the first entry has a link`
      assert hasattr(myfeed.entries[0], 'link'), f"No link found in first entry of feed: {myfeed}"