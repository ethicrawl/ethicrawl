# Integration test for migrating system to support concurrency - verify original API behaviour is unchanged

from ethicrawl.client import Client
from ethicrawl.core import Url
from ethicrawl.client.http import HttpResponse
from ethicrawl.error import RobotDisallowedError, DomainWhitelistError
from ethicrawl import Ethicrawl
from ethicrawl.sitemaps import IndexEntry

ec = Ethicrawl()


base_url = "https://www.bbc.co.uk"
sample_url = "https://www.bbc.co.uk/food/recipes/applecrumble_2971"
sample_img = (
    "https://ichef.bbci.co.uk/food/ic/food_16x9_1600/recipes/applecrumble_2971_16x9.jpg"
)
disallowed_url = "https://www.bbc.co.uk/search/crumble"

ec.bind(base_url)

indexes = ec.robots.sitemaps.filter(r"food")
urls = ec.sitemaps.parse(indexes).filter(r"(?=.*2971)(?=.*apple)(?=.*crumble)")

crumble: IndexEntry = urls[-1]

assert crumble.url == sample_url

crumble_page: HttpResponse = ec.get(crumble.url)
print(crumble_page.status_code, len(crumble_page.content))

try:
    ec.get(sample_img)
except DomainWhitelistError as e:
    print(e)
    ec.whitelist(Url(sample_img).base)

crumble_img: HttpResponse = ec.get(sample_img)

print(crumble_img.status_code, len(crumble_img.content))

# robots currently broken

try:
    ec.get(disallowed_url)
except RobotDisallowedError as e:
    print(e)

ec.unbind()

# (venv) ➜  ethicrawl git:(async_support) ✗ python testbed.py
# 2025-03-30 20:30:19,085 - ethicrawl.https_www_bbc_co_uk.robots - INFO - Server returned 200 - using robots.txt
# 2025-03-30 20:30:19,086 - ethicrawl.https_www_bbc_co_uk - INFO - Successfully bound to https://www.bbc.co.uk
# routing https://www.bbc.co.uk/food/sitemap.xml via the scheduler
# routing https://www.bbc.co.uk/food/recipes/applecrumble_2971 via the scheduler
# 200 398564
# Cannot access URL 'https://ichef.bbci.co.uk/food/ic/food_16x9_1600/recipes/applecrumble_2971_16x9.jpg' - domain not whitelisted.'
# 2025-03-30 20:30:23,849 - ethicrawl.https_ichef_bbci_co_uk.robots - INFO - Server returned 200 - using robots.txt
# 2025-03-30 20:30:23,850 - ethicrawl.https_www_bbc_co_uk - INFO - Successfully bound to https://ichef.bbci.co.uk
# routing https://ichef.bbci.co.uk/food/ic/food_16x9_1600/recipes/applecrumble_2971_16x9.jpg via the scheduler
# 200 227229
# routing https://www.bbc.co.uk/search/crumble via the scheduler
# 2025-03-30 20:30:26,266 - ethicrawl.http_www_example_com.client.requests - WARNING - Client error: HTTP 404 for https://www.bbc.co.uk/search/crumble
# 2025-03-30 20:30:26,266 - ethicrawl.http_www_example_com.client - WARNING - Client error fetching https://www.bbc.co.uk/search/crumble: HTTP 404
# 2025-03-30 20:30:26,266 - ethicrawl.https_www_bbc_co_uk - INFO - Unbinding from www.bbc.co.uk
