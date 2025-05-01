"""Tests for the fastfeedparser module."""
import pathlib
import pytest

import fastfeedparser
from biofeed.core.controller import ReaderController

# Get fixtures directory
CWD = pathlib.Path(__file__).resolve().parent
FIXTURES = f"{CWD}/fixtures"

@pytest.fixture
def local_feed():
  """Use local file."""
  oxford = f"{FIXTURES}/oxford_20250413.xml"
  return oxford

# Tests
#
def test_site(local_feed):
  """Test parsing a local feed."""
  with open(local_feed) as f:
    xml_content = f.read()
    # Parse the feed data
    myfeed = fastfeedparser.parse(xml_content)
    assert xml_content, f"Failed to parse feed: {myfeed}"

def test_select_feed():
  """Test selecting a feed."""
  rc = ReaderController()
  fs = rc.select_feed('oxford')
  assert fs.name == 'Oxford Bioinformatics'
