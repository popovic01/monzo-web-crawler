import requests
from bs4 import BeautifulSoup
from collections import deque
from .utils import normalise_url, is_valid_url, extract_internal_links

class Crawler:

    def __init__(self, initial_url: str):
        # set of visited URLs
        self.visited_urls = set()
        # queue of URLs to visit
        self.urls_to_visit = deque()
        self.urls_to_visit.append(normalise_url(initial_url))

    def crawl(self):
        # process queue until empty
        while len(self.urls_to_visit) > 0:
            current_url = self.urls_to_visit.popleft()

            if current_url in self.visited_urls:
                continue

            print(f"Crawling URL: {current_url}")

            try:
                response = requests.get(current_url, timeout=10)
                response.raise_for_status()  # raise an error for bad responses
                # extract the content and parse it with BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')
                links = extract_internal_links(current_url, soup)
                self.visited_urls.add(current_url)
                print(f"Links found on page ({len(links)}):")
                if links:
                    for link in links:
                        print(f" - {link}")
                        if link != current_url and is_valid_url(link):
                            normalised_link = normalise_url(link)
                            if (normalised_link not in self.visited_urls and
                                normalised_link not in self.urls_to_visit):
                                self.urls_to_visit.append(normalised_link)
                else:
                    print(" - None")
            except requests.RequestException as e:
                print(f"Error fetching {current_url}: {e}")
                # continue to next URL
