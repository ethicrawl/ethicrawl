from ethicrawl.sitemaps.sitemap_nodes import IndexNode
from ethicrawl.sitemaps.sitemaps import Sitemaps
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
    url = Url("https://zadig-et-voltaire.com/", validate=True)
    additional_urls = {
        Url("https://helios.zadig-et-voltaire.com/"),
        Url("https://assets.zadig-et-voltaire.com/"),
    }

    resource = Resource(url)

    store_filter = r"uk_en|usd_store_en"
    product_filter = r"/p/[^/]+/"

    # client = HttpClient().with_chromium(headless=False)  # chromium
    client = HttpClient()  # .with_chromium(headless=False)  # requests

    ethicrawl = Ethicrawl()
    ethicrawl.bind(url, client)  # the first bind establishes the root domain

    logger = ethicrawl.logger
    logger.setLevel(logging.DEBUG)

    # context = ethicrawl.for_dev_use_only_context()

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
        sitemaps = ethicrawl.sitemaps.parse(robots.sitemaps.filter(store_filter))

        # allowed page:
        product_url = Url(
            "https://zadig-et-voltaire.com/eu/uk/p/WWCR01291424/camisole-women-christy-camisole-100--silk-officer-wwcr01291"
        )
        ethicrawl.get(product_url).status_code
        # disallowed page:
        cache_url = Url("https://zadig-et-voltaire.com/uk/cache-invalidation")
        try:
            ethicrawl.get(cache_url).status_code
        except ValueError as e:
            pass

        # image url (should fail if domain not bound)
        image_url = Url(
            "https://assets.zadig-et-voltaire.com/W/W/WWCR01291_OFFICER_SHOOTING_6763e73b1152a.jpg"
        )
        try:
            ethicrawl.get(image_url).status_code
        except ValueError as e:
            pass

        for url in additional_urls:
            ethicrawl.whitelist(url, client)

        ethicrawl.get(image_url).status_code

        print(
            len(list(set(sitemaps.filter(product_filter)))),
            list(set(sitemaps.filter(product_filter)))[0],
        )

        # result = sitemap.entries()

    # Clean up
    ethicrawl.unbind()

"""
(venv) ➜  ethicrawl git:(develop) ✗ python usage.py
2025-03-13 10:45:22,429 - ethicrawl.https_zadig-et-voltaire_com.robots - INFO - Fetching robots.txt: https://zadig-et-voltaire.com/robots.txt
2025-03-13 10:45:23,968 - ethicrawl.https_zadig-et-voltaire_com.robots - INFO - Successfully parsed https://zadig-et-voltaire.com/robots.txt
2025-03-13 10:45:23,968 - ethicrawl.https_zadig-et-voltaire_com.robots - INFO - Discovered 9 sitemaps in https://zadig-et-voltaire.com/robots.txt
2025-03-13 10:45:23,968 - ethicrawl.https_zadig-et-voltaire_com.robots - DEBUG - Discovered: https://zadig-et-voltaire.com/media/sitemap_be_en.xml in https://zadig-et-voltaire.com/robots.txt
2025-03-13 10:45:23,968 - ethicrawl.https_zadig-et-voltaire_com.robots - DEBUG - Discovered: https://zadig-et-voltaire.com/media/sitemap_ch_en.xml in https://zadig-et-voltaire.com/robots.txt
2025-03-13 10:45:23,969 - ethicrawl.https_zadig-et-voltaire_com.robots - DEBUG - Discovered: https://zadig-et-voltaire.com/media/sitemap_de_de.xml in https://zadig-et-voltaire.com/robots.txt
2025-03-13 10:45:23,969 - ethicrawl.https_zadig-et-voltaire_com.robots - DEBUG - Discovered: https://zadig-et-voltaire.com/media/sitemap_es_es.xml in https://zadig-et-voltaire.com/robots.txt
2025-03-13 10:45:23,969 - ethicrawl.https_zadig-et-voltaire_com.robots - DEBUG - Discovered: https://zadig-et-voltaire.com/media/sitemap_fr_fr.xml in https://zadig-et-voltaire.com/robots.txt
2025-03-13 10:45:23,969 - ethicrawl.https_zadig-et-voltaire_com.robots - DEBUG - Discovered: https://zadig-et-voltaire.com/media/sitemap_it_it.xml in https://zadig-et-voltaire.com/robots.txt
2025-03-13 10:45:23,969 - ethicrawl.https_zadig-et-voltaire_com.robots - DEBUG - Discovered: https://zadig-et-voltaire.com/media/sitemap_row_en.xml in https://zadig-et-voltaire.com/robots.txt
2025-03-13 10:45:23,969 - ethicrawl.https_zadig-et-voltaire_com.robots - DEBUG - Discovered: https://zadig-et-voltaire.com/media/sitemap_uk_en.xml in https://zadig-et-voltaire.com/robots.txt
2025-03-13 10:45:23,969 - ethicrawl.https_zadig-et-voltaire_com.robots - DEBUG - Discovered: https://zadig-et-voltaire.com/media/sitemap_usd_store_en.xml in https://zadig-et-voltaire.com/robots.txt
2025-03-13 10:45:23,969 - ethicrawl.https_zadig-et-voltaire_com.sitemap - DEBUG - Traversing IndexNode at depth 0, has 2 items
2025-03-13 10:45:23,969 - ethicrawl.https_zadig-et-voltaire_com.sitemap - DEBUG - Processing item: https://zadig-et-voltaire.com/media/sitemap_uk_en.xml
2025-03-13 10:45:25,191 - ethicrawl.https_zadig-et-voltaire_com.sitemap - DEBUG - Root tag: urlset
2025-03-13 10:45:25,265 - ethicrawl.https_zadig-et-voltaire_com.sitemap - DEBUG - Created UrlsetNode with 1776 items
2025-03-13 10:45:25,265 - ethicrawl.https_zadig-et-voltaire_com.sitemap - DEBUG - Found urlset with 1776 URLs
2025-03-13 10:45:25,266 - ethicrawl.https_zadig-et-voltaire_com.sitemap - DEBUG - Processing item: https://zadig-et-voltaire.com/media/sitemap_usd_store_en.xml
2025-03-13 10:45:26,250 - ethicrawl.https_zadig-et-voltaire_com.sitemap - DEBUG - Root tag: urlset
2025-03-13 10:45:26,310 - ethicrawl.https_zadig-et-voltaire_com.sitemap - DEBUG - Created UrlsetNode with 1455 items
2025-03-13 10:45:26,311 - ethicrawl.https_zadig-et-voltaire_com.sitemap - DEBUG - Found urlset with 1455 URLs
2025-03-13 10:45:26,314 - ethicrawl.https_zadig-et-voltaire_com.robots - DEBUG - Permission check for https://zadig-et-voltaire.com/eu/uk/p/WWCR01291424/camisole-women-christy-camisole-100--silk-officer-wwcr01291: allowed
2025-03-13 10:45:27,537 - ethicrawl.https_zadig-et-voltaire_com.robots - WARNING - Permission check for https://zadig-et-voltaire.com/uk/cache-invalidation: denied
2025-03-13 10:45:27,537 - ethicrawl.https_zadig-et-voltaire_com - WARNING - Domain not allowed: assets.zadig-et-voltaire.com
2025-03-13 10:45:27,550 - ethicrawl.https_helios_zadig-et-voltaire_com.robots - INFO - Fetching robots.txt: https://helios.zadig-et-voltaire.com/robots.txt
2025-03-13 10:45:28,893 - ethicrawl.https_helios_zadig-et-voltaire_com.robots - WARNING - https://helios.zadig-et-voltaire.com/robots.txt not found (404) - allowing all URLs
2025-03-13 10:45:28,893 - ethicrawl.https_zadig-et-voltaire_com - INFO - Whitelisted domain: helios.zadig-et-voltaire.com
2025-03-13 10:45:28,899 - ethicrawl.https_assets_zadig-et-voltaire_com.robots - INFO - Fetching robots.txt: https://assets.zadig-et-voltaire.com/robots.txt
2025-03-13 10:45:30,108 - ethicrawl.https_assets_zadig-et-voltaire_com.robots - INFO - Successfully parsed https://assets.zadig-et-voltaire.com/robots.txt
2025-03-13 10:45:30,108 - ethicrawl.https_assets_zadig-et-voltaire_com.robots - INFO - No sitemaps found in https://assets.zadig-et-voltaire.com/robots.txt
2025-03-13 10:45:30,108 - ethicrawl.https_zadig-et-voltaire_com - INFO - Whitelisted domain: assets.zadig-et-voltaire.com
2589 https://zadig-et-voltaire.com/us/en/p/KMSW01779310/sweater-men-marko-jumper-kmsw01779 | last modified: 2025-03-13 | frequency: daily | priority: 1.0
"""
