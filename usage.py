from ethicrawl.sitemaps.sitemap_nodes import IndexNode
from ethicrawl.sitemaps.sitemap import Sitemap
from ethicrawl.core.ethicrawl import Ethicrawl
from ethicrawl.client.http_client import HttpClient
from ethicrawl.core.url import Url

import logging


if __name__ == "__main__":

    # setup_logging()

    visit_site = True
    config_test = False

    # site = "https://gb.maxmara.com"
    url = Url("https://zadig-et-voltaire.com/", validate=True)
    store_filter = r"uk_en|usd_store_en"
    product_filter = r"/p/[^/]+/"

    client = HttpClient.with_chromium(headless=False)  # chromium
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

    if visit_site:  # dont connect unless we need to test something specifically
        robots = ethicrawl.robots
        index = IndexNode(context)
        index.items = robots.sitemaps
        sitemap = Sitemap(context).from_index(index)
        result = sitemap.items()
        print(result.items[-1], len(result))

    ethicrawl.unbind()

    index = IndexNode(robots.sitemaps)  # should break as we're unbound!

    # filtered_robots = ethicrawl.robots.items.filter(store_filter)
    # product_urls = ethicrawl.sitemaps(filtered_robots).items.filter(product_filter)


# (venv) ➜  ethicrawl git:(develop) ✗ python usage.py
# 2025-03-07 15:19:56,849 - ethicrawl.zadig-et-voltaire_com.robots - INFO - Fetching robots.txt: https://zadig-et-voltaire.com//robots.txt
# 2025-03-07 15:20:02,142 - ethicrawl.zadig-et-voltaire_com.robots - INFO - Successfully parsed https://zadig-et-voltaire.com//robots.txt
# 2025-03-07 15:20:02,142 - ethicrawl.zadig-et-voltaire_com.robots - INFO - Discovered 9 sitemaps in https://zadig-et-voltaire.com//robots.txt
# 2025-03-07 15:20:02,142 - ethicrawl.zadig-et-voltaire_com.robots - DEBUG - Discovered: https://zadig-et-voltaire.com/media/sitemap_be_en.xml in https://zadig-et-voltaire.com//robots.txt
# 2025-03-07 15:20:02,142 - ethicrawl.zadig-et-voltaire_com.robots - DEBUG - Discovered: https://zadig-et-voltaire.com/media/sitemap_ch_en.xml in https://zadig-et-voltaire.com//robots.txt
# 2025-03-07 15:20:02,142 - ethicrawl.zadig-et-voltaire_com.robots - DEBUG - Discovered: https://zadig-et-voltaire.com/media/sitemap_de_de.xml in https://zadig-et-voltaire.com//robots.txt
# 2025-03-07 15:20:02,142 - ethicrawl.zadig-et-voltaire_com.robots - DEBUG - Discovered: https://zadig-et-voltaire.com/media/sitemap_es_es.xml in https://zadig-et-voltaire.com//robots.txt
# 2025-03-07 15:20:02,142 - ethicrawl.zadig-et-voltaire_com.robots - DEBUG - Discovered: https://zadig-et-voltaire.com/media/sitemap_fr_fr.xml in https://zadig-et-voltaire.com//robots.txt
# 2025-03-07 15:20:02,142 - ethicrawl.zadig-et-voltaire_com.robots - DEBUG - Discovered: https://zadig-et-voltaire.com/media/sitemap_it_it.xml in https://zadig-et-voltaire.com//robots.txt
# 2025-03-07 15:20:02,142 - ethicrawl.zadig-et-voltaire_com.robots - DEBUG - Discovered: https://zadig-et-voltaire.com/media/sitemap_row_en.xml in https://zadig-et-voltaire.com//robots.txt
# 2025-03-07 15:20:02,142 - ethicrawl.zadig-et-voltaire_com.robots - DEBUG - Discovered: https://zadig-et-voltaire.com/media/sitemap_uk_en.xml in https://zadig-et-voltaire.com//robots.txt
# 2025-03-07 15:20:02,143 - ethicrawl.zadig-et-voltaire_com.robots - DEBUG - Discovered: https://zadig-et-voltaire.com/media/sitemap_usd_store_en.xml in https://zadig-et-voltaire.com//robots.txt
# 2025-03-07 15:20:02,143 - ethicrawl.zadig-et-voltaire_com.sitemap - DEBUG - Processing sitemap: https://zadig-et-voltaire.com/media/sitemap_be_en.xml
# 2025-03-07 15:20:08,269 - ethicrawl.zadig-et-voltaire_com.sitemap - DEBUG - Processing sitemap: https://zadig-et-voltaire.com/media/sitemap_ch_en.xml
# 2025-03-07 15:20:14,098 - ethicrawl.zadig-et-voltaire_com.sitemap - DEBUG - Processing sitemap: https://zadig-et-voltaire.com/media/sitemap_de_de.xml
# 2025-03-07 15:20:20,312 - ethicrawl.zadig-et-voltaire_com.sitemap - DEBUG - Processing sitemap: https://zadig-et-voltaire.com/media/sitemap_es_es.xml
# 2025-03-07 15:20:26,825 - ethicrawl.zadig-et-voltaire_com.sitemap - DEBUG - Processing sitemap: https://zadig-et-voltaire.com/media/sitemap_fr_fr.xml
# 2025-03-07 15:20:33,235 - ethicrawl.zadig-et-voltaire_com.sitemap - DEBUG - Processing sitemap: https://zadig-et-voltaire.com/media/sitemap_it_it.xml
# 2025-03-07 15:20:39,538 - ethicrawl.zadig-et-voltaire_com.sitemap - DEBUG - Processing sitemap: https://zadig-et-voltaire.com/media/sitemap_row_en.xml
# 2025-03-07 15:20:45,663 - ethicrawl.zadig-et-voltaire_com.sitemap - DEBUG - Processing sitemap: https://zadig-et-voltaire.com/media/sitemap_uk_en.xml
# 2025-03-07 15:20:52,035 - ethicrawl.zadig-et-voltaire_com.sitemap - DEBUG - Processing sitemap: https://zadig-et-voltaire.com/media/sitemap_usd_store_en.xml
# 2025-03-07 15:20:58,098 - ethicrawl.zadig-et-voltaire_com.sitemap - INFO - Visited 9 sitemaps and found 13689 unique URLs
# https://zadig-et-voltaire.com/us/en/archive | last modified: 2025-03-07 | frequency: daily | priority: 1.0 13689
