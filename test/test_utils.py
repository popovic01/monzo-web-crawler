import pytest
import sys
import os
from urllib.parse import urlparse
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from crawler import is_valid_url, normalise_url

def test_is_valid_url_with_valid_http():
    url = "http://example.com"
    assert is_valid_url(url) is True

def test_is_valid_url_with_https():
    url = "https://example.com/page"
    assert is_valid_url(url) is True

def test_is_valid_url_with_invalid_scheme():
    url = "ftp://example.com"
    assert is_valid_url(url) is False

def test_is_valid_url_with_malformed_url():
    url = "htp:/invalid"
    assert is_valid_url(url) is False

def test_is_valid_url_with_none():
    assert is_valid_url(None) is False

def test_normalise_url_removes_fragment():
    url = "https://example.com/path#section"
    normalised = normalise_url(url)
    assert "#" not in normalised

def test_normalise_url_lowers_netloc():
    url = "https://EXAMPLE.com/test"
    normalised = normalise_url(url)
    parsed = urlparse(normalised)
    assert parsed.netloc == "example.com"