import pytest
import requests
from unittest.mock import patch, Mock
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from bs4 import BeautifulSoup
from crawler import Crawler, extract_internal_links

HTML_SAMPLE = """
<html>
  <body>
    <a href="https://monzo.com/about">About</a>
    <a href="/careers">Careers</a>
    <a href="https://external.com">External</a>
    <a href="#fragment">Fragment</a>
    <a href="mailto:info@monzo.com">Email</a>
  </body>
</html>
"""

@patch("requests.get")
def test_crawl_single_page(mock_get):
    # mock HTML response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = HTML_SAMPLE.encode("utf-8")
    mock_get.return_value = mock_response

    crawler = Crawler("https://monzo.com")
    crawler.crawl()

    # verify URLs visited
    assert "https://monzo.com" in crawler.visited_urls
    assert any("about" in url for url in crawler.visited_urls)

def test_extract_internal_links_filters_external():
    soup = BeautifulSoup(HTML_SAMPLE, "html.parser")
    links = extract_internal_links("https://monzo.com", soup)

    assert "https://monzo.com/about" in links
    assert "https://monzo.com/careers" in links
    assert all("external.com" not in link for link in links)
    assert all(not link.startswith("mailto:") for link in links)
    assert all(not link.startswith("#") for link in links)

@patch("requests.get")
def test_crawl_handles_request_exception(mock_get):
    mock_get.side_effect = requests.RequestException("Network error")

    crawler = Crawler("https://monzo.com")
    crawler.crawl()

    # crawler should handle the error and move on
    assert len(crawler.visited_urls) == 0
