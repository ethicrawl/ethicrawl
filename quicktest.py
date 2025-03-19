# https://www.bbc.co.uk/news/politics/eu-regions/vote2014_sitemap.xml

from ethicrawl import Ethicrawl, HttpClient, Config

import logging, sys

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

Config().sitemap.max_depth = 2


ec = Ethicrawl()

client = HttpClient()  # .with_chrome(headless=False)

site = "https://www.bbc.co.uk"

ec.bind(site, client)

sitemaps = ec.robot.sitemaps.filter(r"https://www.bbc.co.uk/sitemap.xml")
links = ec.sitemaps.parse(sitemaps)

print(len(links))

page = ec.get("https://www.bbc.co.uk/news/videos/c4g7473l2lgo")

print(page.headers["Content-Type"])


ec.unbind()
