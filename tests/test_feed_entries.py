import pathlib
import pytest

import fastfeedparser

# Get fixtures directory
CWD = pathlib.Path(__file__).resolve().parent
FIXTURES = f"{CWD}/fixtures"

@pytest.fixture
def local_feed():
  """Use local file."""
  plos = f"{FIXTURES}/plos_20250413.xml"
  return plos

def test_title_link(local_feed):
  """Test parsing a local feed."""
  with open(local_feed) as f:
    xml_content = f.read()
    # Parse the feed data
    myfeed = fastfeedparser.parse(xml_content)
    assert myfeed['feed']['title'] == 'PLOS Computational Biology: New Articles'
    assert myfeed['feed']['link'] == 'https://journals.plos.org/ploscompbiol/'

def test_entry_title(local_feed):
  """Test parsing a local feed."""
  with open(local_feed) as f:
    xml_content = f.read()
    # Parse the feed data
    myfeed = fastfeedparser.parse(xml_content)
    assert myfeed['entries'][2]['title'] == 'Virtual epilepsy patient cohort: Generation and evaluation'

def test_published_updated_date(local_feed):
  """Test parsing a local feed."""
  with open(local_feed) as f:
    xml_content = f.read()
    # Parse the feed data
    myfeed = fastfeedparser.parse(xml_content)
    assert myfeed['entries'][2].published == '2025-04-11T14:00:00+00:00'
    assert myfeed['entries'][2].updated == '2025-04-11T14:00:00+00:00'