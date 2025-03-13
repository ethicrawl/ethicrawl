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
        Url("https://assets.zadig-et-voltaire.com:443/"),
    }

    resource = Resource(url)

    store_filter = r"uk_en|usd_store_en"
    product_filter = r"/p/[^/]+/"

    # client = HttpClient().with_chromium(headless=False)  # chromium
    client = HttpClient()  # requests

    ethicrawl = Ethicrawl()
    ethicrawl.bind(url, client)  # the first bind establishes the root domain

    for url in additional_urls:
        ethicrawl.whitelist(url, client)

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

        print(
            len(list(set(sitemaps.filter(product_filter)))),
            list(set(sitemaps.filter(product_filter)))[0],
        )

        # result = sitemap.entries()

    # Clean up
    ethicrawl.unbind()

"""
(venv) ➜  ethicrawl git:(develop) ✗ python usage.py
2025-03-13 07:13:18,687 - ethicrawl.https_helios_zadig-et-voltaire_com.robots - INFO - Fetching robots.txt: https://helios.zadig-et-voltaire.com/robots.txt
2025-03-13 07:13:19,762 - ethicrawl.https_helios_zadig-et-voltaire_com.robots - INFO - https://helios.zadig-et-voltaire.com/robots.txt not found (404) - allowing all URLs
2025-03-13 07:13:19,762 - ethicrawl.https_zadig-et-voltaire_com - INFO - Whitelisted domain: helios.zadig-et-voltaire.com
2025-03-13 07:13:19,776 - ethicrawl.https_assets_zadig-et-voltaire_com_443.robots - INFO - Fetching robots.txt: https://assets.zadig-et-voltaire.com:443/robots.txt
2025-03-13 07:13:21,025 - ethicrawl.https_assets_zadig-et-voltaire_com_443.robots - INFO - Successfully parsed https://assets.zadig-et-voltaire.com:443/robots.txt
2025-03-13 07:13:21,025 - ethicrawl.https_assets_zadig-et-voltaire_com_443.robots - INFO - No sitemaps found in https://assets.zadig-et-voltaire.com:443/robots.txt
2025-03-13 07:13:21,025 - ethicrawl.https_zadig-et-voltaire_com - INFO - Whitelisted domain: assets.zadig-et-voltaire.com:443
2025-03-13 07:13:21,025 - ethicrawl.https_zadig-et-voltaire_com.robots - INFO - Fetching robots.txt: https://zadig-et-voltaire.com/robots.txt
2025-03-13 07:13:22,291 - ethicrawl.https_zadig-et-voltaire_com.robots - INFO - Successfully parsed https://zadig-et-voltaire.com/robots.txt
2025-03-13 07:13:22,291 - ethicrawl.https_zadig-et-voltaire_com.robots - INFO - Discovered 9 sitemaps in https://zadig-et-voltaire.com/robots.txt
2025-03-13 07:13:22,291 - ethicrawl.https_zadig-et-voltaire_com.robots - DEBUG - Discovered: https://zadig-et-voltaire.com/media/sitemap_be_en.xml in https://zadig-et-voltaire.com/robots.txt
2025-03-13 07:13:22,291 - ethicrawl.https_zadig-et-voltaire_com.robots - DEBUG - Discovered: https://zadig-et-voltaire.com/media/sitemap_ch_en.xml in https://zadig-et-voltaire.com/robots.txt
2025-03-13 07:13:22,291 - ethicrawl.https_zadig-et-voltaire_com.robots - DEBUG - Discovered: https://zadig-et-voltaire.com/media/sitemap_de_de.xml in https://zadig-et-voltaire.com/robots.txt
2025-03-13 07:13:22,291 - ethicrawl.https_zadig-et-voltaire_com.robots - DEBUG - Discovered: https://zadig-et-voltaire.com/media/sitemap_es_es.xml in https://zadig-et-voltaire.com/robots.txt
2025-03-13 07:13:22,291 - ethicrawl.https_zadig-et-voltaire_com.robots - DEBUG - Discovered: https://zadig-et-voltaire.com/media/sitemap_fr_fr.xml in https://zadig-et-voltaire.com/robots.txt
2025-03-13 07:13:22,291 - ethicrawl.https_zadig-et-voltaire_com.robots - DEBUG - Discovered: https://zadig-et-voltaire.com/media/sitemap_it_it.xml in https://zadig-et-voltaire.com/robots.txt
2025-03-13 07:13:22,291 - ethicrawl.https_zadig-et-voltaire_com.robots - DEBUG - Discovered: https://zadig-et-voltaire.com/media/sitemap_row_en.xml in https://zadig-et-voltaire.com/robots.txt
2025-03-13 07:13:22,291 - ethicrawl.https_zadig-et-voltaire_com.robots - DEBUG - Discovered: https://zadig-et-voltaire.com/media/sitemap_uk_en.xml in https://zadig-et-voltaire.com/robots.txt
2025-03-13 07:13:22,291 - ethicrawl.https_zadig-et-voltaire_com.robots - DEBUG - Discovered: https://zadig-et-voltaire.com/media/sitemap_usd_store_en.xml in https://zadig-et-voltaire.com/robots.txt
2025-03-13 07:13:22,292 - ethicrawl.https_zadig-et-voltaire_com.sitemap - DEBUG - Traversing IndexNode at depth 0, has 2 items
2025-03-13 07:13:22,292 - ethicrawl.https_zadig-et-voltaire_com.sitemap - DEBUG - Processing item: https://zadig-et-voltaire.com/media/sitemap_uk_en.xml
2025-03-13 07:13:23,673 - ethicrawl.https_zadig-et-voltaire_com.sitemap - DEBUG - Root tag: urlset
2025-03-13 07:13:23,749 - ethicrawl.https_zadig-et-voltaire_com.sitemap - DEBUG - Created UrlsetNode with 1776 items
2025-03-13 07:13:23,750 - ethicrawl.https_zadig-et-voltaire_com.sitemap - DEBUG - Found urlset with 1776 URLs
2025-03-13 07:13:23,750 - ethicrawl.https_zadig-et-voltaire_com.sitemap - DEBUG - Processing item: https://zadig-et-voltaire.com/media/sitemap_usd_store_en.xml
2025-03-13 07:13:24,770 - ethicrawl.https_zadig-et-voltaire_com.sitemap - DEBUG - Root tag: urlset
2025-03-13 07:13:24,827 - ethicrawl.https_zadig-et-voltaire_com.sitemap - DEBUG - Created UrlsetNode with 1455 items
2025-03-13 07:13:24,828 - ethicrawl.https_zadig-et-voltaire_com.sitemap - DEBUG - Found urlset with 1455 URLs
2589 https://zadig-et-voltaire.com/eu/uk/p/LWSG00001323/card-holder-women-zv-pass-card-holder-record-lwsg00001 | last modified: 2025-03-04 | frequency: daily | priority: 1.0
"""
