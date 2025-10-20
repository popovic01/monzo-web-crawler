from crawler import Crawler
from crawler import CrawlerMultithreading
from crawler.utils import is_valid_url

initial_url = input("Enter initial url: ")

if is_valid_url(initial_url):
    # crawler = CrawlerMultithreading(initial_url)
    crawler = Crawler(initial_url)
    crawler.crawl()
