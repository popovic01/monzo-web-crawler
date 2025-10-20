from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup
from queue import Queue
from urllib.parse import urlparse, urljoin
from .utils import normalize_url, is_valid_url, extract_internal_links
import threading

class CrawlerMultithreading:
    def __init__(self, initial_url: str, max_threads: int = 5):
        normalized_url = normalize_url(initial_url)
        if not is_valid_url(normalized_url):
            raise ValueError("Invalid initial URL")

        self.visited_urls = set()
        self.visited_lock = threading.Lock()
        self.urls_to_visit = Queue()
        self.urls_to_visit.put(normalized_url)
        self.max_threads = max_threads

    def worker(self):
        while True:
            try:
                current_url = self.urls_to_visit.get(timeout=3)  # timeout to allow threads to exit
            except Empty:
                break  # queue is empty, exit thread

            with self.visited_lock:
                if current_url in self.visited_urls:
                    self.urls_to_visit.task_done()
                    continue
                self.visited_urls.add(current_url)

            print(f"Crawling URL: {current_url}")

            try:
                response = requests.get(current_url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')

                # Extract internal links and filter out already visited
                links = [
                    link for link in extract_internal_links(current_url, soup)
                    if is_valid_url(link)
                ]

                if links:
                    print(f"Links found on page ({len(links)}):")
                    for link in links:
                        print(f" - {link}")
                else:
                    print(" - None")

                # Enqueue new URLs
                new_links = []
                with self.visited_lock:
                    for link in links:
                        if link not in self.visited_urls:
                            self.urls_to_visit.put(link)
                            new_links.append(link)
            except requests.RequestException as e:
                print(f"Error fetching {current_url}: {e}")
            finally:
                self.urls_to_visit.task_done()

    def crawl(self):
        threads = []
        for _ in range(self.max_threads):
            t = threading.Thread(target=self.worker)
            t.daemon = True  # allow program to exit if threads are blocked
            t.start()
            threads.append(t)

        self.urls_to_visit.join()

        # Wait for all threads to finish
        for t in threads:
            t.join()

        print("\nCrawling complete.")
        print(f"Total pages visited: {len(self.visited_urls)}")
