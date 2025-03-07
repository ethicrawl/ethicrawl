# from ethicrawl import Ethicrawl
# from ethicrawl.client import HttpClient
# from ethicrawl.config import Config
# from ethicrawl.sitemaps import Sitemap
# from ethicrawl.logger import Logger
# from ethicrawl.core import EthicrawlContext
# from ethicrawl.sitemaps.node_factory import NodeFactory
from ethicrawl.core import EthicrawlContext
from ethicrawl.sitemaps.sitemap_nodes import IndexNode
from ethicrawl.sitemaps import Sitemap

# from ethicrawl.logger.formatter import GeoCitiesFormatter

from ethicrawl import Ethicrawl, HttpClient
from ethicrawl.core import Url

# from ethicrawl.logger.logger import Logger
import logging

# def setup_logging():
#     """Configure logging for the application"""
#     config = Config()
#     # config.logger.level = "INFO"
#     # config.logger.console_enabled = True
#     # config.logger.use_colors = True
#     config.logger.set_component_level("robots", "DEBUG")
#     config.logger.set_component_level("sitemap", "DEBUG")

#     # config.logger.set_component_level("sitemaps", "WARNING")

#     # Initialize logging
#     Logger.setup_logging()


if __name__ == "__main__":

    # setup_logging()

    visit_site = False
    config_test = False

    # site = "https://gb.maxmara.com"
    url = Url("https://zadig-et-voltaire.com/", validate=True)
    store_filter = r"uk_en|usd_store_en"
    product_filter = r"/p/[^/]+/"

    # client = http_client = HttpClient.with_chromium(headless=False)  # chromium
    # client = HttpClient()  # requests

    client = HttpClient()  # .with_chromium(headless=False)

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

        config.http.rate_limit = 1

    ethicrawl.unbind()
    ethicrawl.bind(url, client)

    print(ethicrawl.config.to_dict())

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

{
    "http": {
        "headers": {},
        "jitter": 0.2,
        "max_retries": 3,
        "rate_limit": 0.5,
        "retry_delay": 1.0,
        "timeout": 30.0,
        "user_agent": "Ethicrawl/1.0",
    },
    "logger": {
        "component_levels": {},
        "console_enabled": True,
        "file_enabled": False,
        "file_path": None,
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "level": 20,
        "use_colors": True,
    },
}
"""
{
    "http": {
        "headers": {},
        "jitter": 0.2,
        "max_retries": 3,
        "rate_limit": 0.5,
        "retry_delay": 1.0,
        "timeout": 30.0,
        "user_agent": "Ethicrawl/1.0",
    },
    "logger": {
        "component_levels": {},
        "console_enabled": true,
        "file_enabled": false,
        "file_path": null,
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "level": 20,
        "use_colors": true,
    },
}
{
    "http": {
        "headers": {},
        "jitter": 0.2,
        "max_retries": 3,
        "rate_limit": 1.0,
        "retry_delay": 1.0,
        "timeout": 30.0,
        "user_agent": "Ethicrawl/1.0",
    },
    "logger": {
        "component_levels": {},
        "console_enabled": true,
        "file_enabled": false,
        "file_path": null,
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "level": 20,
        "use_colors": true,
    },
}
"""
