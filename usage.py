from ethicrawl.sitemaps.sitemap_nodes import IndexNode
from ethicrawl.sitemaps.sitemap import Sitemap
from ethicrawl.core.ethicrawl import Ethicrawl
from ethicrawl.client.http_client import HttpClient
from ethicrawl.core.url import Url
from ethicrawl.core.resource import Resource

import logging


if __name__ == "__main__":

    # setup_logging()

    visit_site = True
    config_test = False

    # site = "https://gb.maxmara.com"
    url = Url("http://localhost:8000/", validate=True)
    resource = Resource(url)

    store_filter = r"uk_en|usd_store_en"
    product_filter = r"/p/[^/]+/"

    # client = HttpClient().with_chromium(headless=False)  # chromium
    client = HttpClient()  # requests

    ethicrawl = Ethicrawl()
    ethicrawl.bind(url, client)

    logger = ethicrawl.logger
    logger.setLevel(logging.DEBUG)

    context = ethicrawl.for_dev_use_only_context()

    if config_test:
        config = ethicrawl.config
        print(config.to_dict())
        print(config)

        dict = config.to_dict()

        print(dict)
        dict["http"]["jitter"] = 0.3
        print(dict)

        config.update(dict)

        ethicrawl.bind(url, client)

        print(ethicrawl.config.to_dict())
        config.http.rate_limit = 1

    # print(context.url)

    # ethicrawl = Ethicrawl(url, client)  # .with_selenium(headless=False))

    # visit_site = False

    if visit_site:
        # Get robots.txt information
        robots = ethicrawl.robots
        sitemap = Sitemap(context).parse(robots.sitemaps)

        print(list(set(sitemap)))

        # result = sitemap.entries()

    # Clean up
    ethicrawl.unbind()

# python usage.py
# 2025-03-12 18:30:40,836 - ethicrawl.http_localhost_8000.robots - INFO - Fetching robots.txt: http://localhost:8000/robots.txt
# 2025-03-12 18:30:42,068 - ethicrawl.http_localhost_8000.robots - INFO - Successfully parsed http://localhost:8000/robots.txt
# 2025-03-12 18:30:42,068 - ethicrawl.http_localhost_8000.robots - INFO - Discovered 1 sitemaps in http://localhost:8000/robots.txt
# 2025-03-12 18:30:42,068 - ethicrawl.http_localhost_8000.robots - DEBUG - Discovered: http://localhost:8000/sitemap.xml in http://localhost:8000/robots.txt
# 2025-03-12 18:30:42,069 - ethicrawl.http_localhost_8000.sitemap - DEBUG - Traversing IndexNode at depth 0, has 1 items
# 2025-03-12 18:30:42,069 - ethicrawl.http_localhost_8000.sitemap - DEBUG - Processing item: http://localhost:8000/sitemap.xml
# 2025-03-12 18:30:43,164 - ethicrawl.http_localhost_8000.sitemap - DEBUG - Root tag: sitemapindex
# 2025-03-12 18:30:43,168 - ethicrawl.http_localhost_8000.sitemap - DEBUG - Created IndexNode with 3 items
# 2025-03-12 18:30:43,168 - ethicrawl.http_localhost_8000.sitemap - DEBUG - Found index sitemap with 3 items
# 2025-03-12 18:30:43,168 - ethicrawl.http_localhost_8000.sitemap - DEBUG - Traversing IndexNode at depth 1, has 3 items
# 2025-03-12 18:30:43,168 - ethicrawl.http_localhost_8000.sitemap - DEBUG - Processing item: http://localhost:8000/products.xml
# 2025-03-12 18:30:44,599 - ethicrawl.http_localhost_8000.sitemap - DEBUG - Root tag: urlset
# 2025-03-12 18:30:44,599 - ethicrawl.http_localhost_8000.sitemap - DEBUG - Created UrlsetNode with 3 items
# 2025-03-12 18:30:44,599 - ethicrawl.http_localhost_8000.sitemap - DEBUG - Found urlset with 3 URLs
# 2025-03-12 18:30:44,599 - ethicrawl.http_localhost_8000.sitemap - DEBUG - Processing item: http://localhost:8000/categories.xml
# 2025-03-12 18:30:45,644 - ethicrawl.http_localhost_8000.sitemap - DEBUG - Root tag: urlset
# 2025-03-12 18:30:45,644 - ethicrawl.http_localhost_8000.sitemap - DEBUG - Created UrlsetNode with 2 items
# 2025-03-12 18:30:45,644 - ethicrawl.http_localhost_8000.sitemap - DEBUG - Found urlset with 2 URLs
# 2025-03-12 18:30:45,644 - ethicrawl.http_localhost_8000.sitemap - DEBUG - Processing item: http://localhost:8000/cycle1.xml
# 2025-03-12 18:30:46,927 - ethicrawl.http_localhost_8000.sitemap - DEBUG - Root tag: sitemapindex
# 2025-03-12 18:30:46,927 - ethicrawl.http_localhost_8000.sitemap - DEBUG - Created IndexNode with 1 items
# 2025-03-12 18:30:46,927 - ethicrawl.http_localhost_8000.sitemap - DEBUG - Found index sitemap with 1 items
# 2025-03-12 18:30:46,927 - ethicrawl.http_localhost_8000.sitemap - DEBUG - Traversing IndexNode at depth 2, has 1 items
# 2025-03-12 18:30:46,927 - ethicrawl.http_localhost_8000.sitemap - DEBUG - Processing item: http://localhost:8000/cycle2.xml
# 2025-03-12 18:30:48,033 - ethicrawl.http_localhost_8000.sitemap - DEBUG - Root tag: sitemapindex
# 2025-03-12 18:30:48,033 - ethicrawl.http_localhost_8000.sitemap - DEBUG - Created IndexNode with 1 items
# 2025-03-12 18:30:48,033 - ethicrawl.http_localhost_8000.sitemap - DEBUG - Found index sitemap with 1 items
# 2025-03-12 18:30:48,033 - ethicrawl.http_localhost_8000.sitemap - DEBUG - Traversing IndexNode at depth 3, has 1 items
# 2025-03-12 18:30:48,033 - ethicrawl.http_localhost_8000.sitemap - WARNING - Cycle detected: http://localhost:8000/cycle1.xml has already been processed
# [
# SitemapUrlsetEntry(url='http://localhost:8000/product1.html', lastmod='2025-02-01', changefreq='weekly', priority=0.8),
# SitemapUrlsetEntry(url='http://localhost:8000/product2.html', lastmod='2025-02-15', changefreq='weekly', priority=0.8),
# SitemapUrlsetEntry(url='http://localhost:8000/product3.html', lastmod='2025-02-20', changefreq='weekly', priority=0.8),
# SitemapUrlsetEntry(url='http://localhost:8000/category1.html', lastmod='2025-01-15', changefreq='monthly', priority=0.6),
# SitemapUrlsetEntry(url='http://localhost:8000/category2.html', lastmod='2025-01-15', changefreq='monthly', priority=0.6)
# ]
