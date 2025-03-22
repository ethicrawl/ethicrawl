# https://www.bbc.co.uk/news/politics/eu-regions/vote2014_sitemap.xml

from ethicrawl import Ethicrawl, HttpClient, Config
from ethicrawl.core import Headers
from ethicrawl.error import RobotDisallowedError

import logging, sys

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

Config().sitemap.max_depth = 2


site = "https://www.bbc.co.uk"
whitelist_site = "https://ichef.bbci.co.uk"

ec = Ethicrawl()

good_headers = Headers({"User-Agent": "Chrome"})
bad_headers = Headers({"User-Agent": "ClaudeBot"})

client = HttpClient(headers=good_headers)
ec.bind(whitelist_site, client)
ec.whitelist(site)

page = ec.get("https://www.bbc.co.uk/news/videos/c4g7473l2lgo")
try:
    page = ec.get("https://www.bbc.co.uk/news/videos/c4g7473l2lgo", headers=bad_headers)
except RobotDisallowedError:
    print("BBC doesn't like ClaudeBot part 1")

ec.unbind()

client = HttpClient(headers=bad_headers)

ec.bind(whitelist_site, client)
ec.whitelist(site)

try:
    page = ec.get("https://www.bbc.co.uk/news/videos/c4g7473l2lgo")
except RobotDisallowedError:
    print("BBC doesn't like ClaudeBot part 2")
page = ec.get("https://www.bbc.co.uk/news/videos/c4g7473l2lgo", headers=good_headers)

ec.unbind()

# 2025-03-21 09:35:40,182 - ethicrawl.https_ichef_bbci_co_uk - INFO - Whitelisted domain: www.bbc.co.uk
# 2025-03-21 09:35:40,214 - ethicrawl.https_www_bbc_co_uk.robots - INFO - Server returned 200 - using robots.txt
# 2025-03-21 09:35:42,577 - ethicrawl.https_ichef_bbci_co_uk - INFO - Whitelisted domain: www.bbc.co.uk
# 2025-03-21 09:35:42,616 - ethicrawl.https_www_bbc_co_uk.robots - INFO - Server returned 200 - using robots.txt
# 2025-03-21 09:35:42,616 - ethicrawl.https_www_bbc_co_uk.robots - WARNING - Permission check for https://www.bbc.co.uk/news/videos/c4g7473l2lgo with User-Agent 'ClaudeBot': denied
# BBC doesn't like ClaudeBot part 2
# 2025-03-21 09:35:42,616 - ethicrawl.https_www_bbc_co_uk.robots - WARNING - Permission check for https://www.bbc.co.uk/news/videos/c4g7473l2lgo with User-Agent 'ClaudeBot': denied
# Traceback (most recent call last):
#   File "/home/kris/code/ethicrawl/quicktest.py", line 47, in <module>
#     page = ec.get("https://www.bbc.co.uk/news/videos/c4g7473l2lgo", headers=good_headers)
#   File "/home/kris/code/ethicrawl/ethicrawl/ethicrawl.py", line 45, in wrapper
#     return func(self, *args, **kwargs)
#   File "/home/kris/code/ethicrawl/ethicrawl/ethicrawl.py", line 248, in get
#     robot.can_fetch(resource, user_agent=user_agent)
#   File "/home/kris/code/ethicrawl/ethicrawl/robots/robot.py", line 84, in can_fetch
#     raise RobotDisallowedError(
# ethicrawl.error.robot_error.RobotDisallowedError: Permission denied by robots.txt for User-Agent 'ClaudeBot' at URL 'https://www.bbc.co.uk/news/videos/c4g7473l2lgo'
# (venv) ➜  ethicrawl git:(develop) ✗
