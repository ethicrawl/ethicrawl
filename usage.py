from ethicrawl import Ethicrawl
from ethicrawl.client import HttpClient
from ethicrawl.config import Config
from ethicrawl.sitemaps import Sitemap
from ethicrawl.logger import Logger
from ethicrawl.core import EthicrawlContext

from ethicrawl.sitemaps.node_factory import NodeFactory

# from ethicrawl.logger.formatter import GeoCitiesFormatter


def setup_logging():
    """Configure logging for the application"""
    config = Config()
    # config.logger.level = "INFO"
    # config.logger.console_enabled = True
    # config.logger.use_colors = True
    config.logger.set_component_level("robots", "DEBUG")
    config.logger.set_component_level("sitemap", "DEBUG")

    # config.logger.set_component_level("sitemaps", "WARNING")

    # Initialize logging
    Logger.setup_logging()


if __name__ == "__main__":

    setup_logging()

    # site = "https://gb.maxmara.com"
    site = "https://zadig-et-voltaire.com"

    # client = http_client = HttpClient.with_selenium(headless=False)  # selenium
    client = HttpClient()  # requests

    context = EthicrawlContext(site, client)

    ec = Ethicrawl(site, http_client=client)  # .with_selenium(headless=False))

    # index = NodeFactory.create_index(
    #     context, ec._robots_handler.get_sitemaps(), loc=f"{site}/robots.txt"
    # )

    from ethicrawl.sitemaps.sitemap_nodes import IndexNode
    from ethicrawl.sitemaps.sitemap_urls import SitemapIndexUrl

    index = IndexNode(context)
    index.items = ec._robots_handler.sitemaps

    # from ethicrawl.sitemaps.sitemap import Sitemap

    uk_usd_filter = r"uk_en|usd_store_en"
    # Better API design
    # tree = Sitemap(context, url_filter=uk_usd_filter).from_robots().items()

    # tree = Sitemap().items(context, index)

    # Better API design
    # Most streamlined approach
    # sample product url = https://zadig-et-voltaire.com/eu/uk/p/WWDR02501404/dress-women-ramelil-dress-encre-wwdr02501
    product_filter = r"/p/._?/"  # probably not escaped correctly
    products = (
        Sitemap(context)
        .filter(uk_usd_filter)
        .from_robots()
        .items()
        .filter(product_filter)
    )
