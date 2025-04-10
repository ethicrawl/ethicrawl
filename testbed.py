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
