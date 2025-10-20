"""Small utility helpers for the crawler."""
from urllib.parse import urlparse, urljoin, urldefrag, parse_qsl, urlencode, urlunparse
import os

_INVALID_EXTENSIONS = (
    ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg",
    ".zip", ".mp4", ".mp3", ".doc", ".docx",
    ".xls", ".xlsx", ".json", ".csv", ".ico", ".css", ".js"
)

def is_valid_url(url) -> bool:
    """
    Return True if `url` is a valid http(s) URL with a network location.
    Accepts `str`. Returns False for `None` or other types.

    Errors such as malformed inputs are handled and result in False.
    """
    if url is None:
        return False
    if not isinstance(url, str):
        return False

    try:
        parsed = urlparse(url)
        scheme = (parsed.scheme or "").lower()

        if scheme not in ('http', 'https'):
            print("Not a valid url. Scheme must be http or https.")
            return False
        if not parsed.netloc:
            print(f"Skipping {url}: missing network location.")
            return False
        path = parsed.path.lower()
        # skip URLs that point to non-HTML resources (e.g., PDFs, images)
        if any(path.endswith(ext) for ext in _INVALID_EXTENSIONS):
            return False
        return True
    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error parsing URL {url}: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error validating URL {url}: {e}")
        return False

def normalize_url(url: str) -> str:
    """
    Normalize a URL for deduplication:
    - remove fragment part (#...)
    - lowercase the domain
    - strip trailing slash from path for consistency

    Raises:
    ValueError: if `url` is None or cannot be parsed/handled.
    """
    if url is None:
        raise ValueError("URL must not be None")

    try:
        if not isinstance(url, str):
            raise ValueError("URL must be a string")

        # remove fragment
        url, _ = urldefrag(url)
        p = urlparse(url)
        # lowercase the domain
        netloc = p.netloc.lower()
        path = p.path.rstrip("/") or "/"

        normalized = urlunparse((p.scheme, netloc, path, p.params, p.query, ""))
        return normalized
    except Exception as e:
        raise ValueError(f"Failed to normalize URL: {e}") from e

def extract_internal_links(starting_url: str, soup):
    """
    Return unique normalized internal links found in `soup` for `starting_url`.
    - `starting_url` should be the page URL (used for resolving relative links and netloc check).
    - Skips mailto/javascript/fragment-only links and common non-HTML extensions.
    - Preserves query parameters but strips fragments.
    """
    starting_url = normalize_url(starting_url)
    start_netloc = urlparse(starting_url).netloc.lower()

    found_links = set()
    for link in soup.select('a[href]'):
        # print(f"link: {link}")
        url = link.get('href')
        # skip empty and non-http links
        if not url:
            continue
        url = url.strip()
        if url == '' or url.startswith('#') or url.startswith('mailto:') or url.startswith('javascript:'):
            continue

        # converting relative URLs to absolute URLs
        if url.startswith('http://') or url.startswith('https://'):
            absolute_url = url
        else:
            absolute_url = urljoin(starting_url, url)
        # print(f"Absolute_url: {absolute_url}")

        # skip non-http(s) links
        ext = os.path.splitext(urlparse(absolute_url).path)[1].lower()
        if ext in _INVALID_EXTENSIONS:
            continue

        # remove fragment and normalize
        try:
            absolute_url = normalize_url(absolute_url)
        except ValueError:
            continue
        parsed = urlparse(absolute_url)

        # enforce single-subdomain rule (exact netloc match)
        if parsed.netloc.lower() != start_netloc:
            continue

        found_links.add(absolute_url)
    return found_links

# exported names
__all__ = ["is_valid_url", "normalize_url", "extract_internal_links"]
