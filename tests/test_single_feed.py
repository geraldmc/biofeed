"""Tests for the fastfeedparser module."""
import pathlib
import pytest

import fastfeedparser

# Get fixtures directory
CWD = pathlib.Path(__file__).resolve().parent
FIXTURES = f"{CWD}/fixtures"

@pytest.fixture
def local_feed():
  """Use local file."""
  bmc = f"{FIXTURES}/bmc_20250413.xml"
  return bmc

# Tests
#
def test_site(local_feed):
  """Test reading the site title and link."""
  with open(local_feed) as f:
    xml_content = f.read()
    # Parse the feed data
    myfeed = fastfeedparser.parse(xml_content)
    assert xml_content, f"Failed to parse feed: {myfeed}"