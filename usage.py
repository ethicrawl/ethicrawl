import logging
from ethicrawl import EthiCrawl
from ethicrawl.client import HttpClient
from ethicrawl.sitemaps import SitemapFactory
from ethicrawl.config import Config
import random


def setup_logging():
    """Configure logging for the application"""
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Create console handler and set level
    console = logging.StreamHandler()
    console.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.WARNING)  # Set base level for all loggers
    root_logger.addHandler(console)

    # Configure ethicrawl loggers specifically
    ethicrawl_logger = logging.getLogger("ethicrawl")
    ethicrawl_logger.setLevel(logging.INFO)  # More detailed for our library

    # ethicrawl_logger.setLevel(logging.TRACE)

    # You can also set specific component levels if needed
    # logging.getLogger("ethicrawl.gb_maxmara_com.robots").setLevel(logging.DEBUG)


if __name__ == "__main__":
    c = Config()

    print(c.http.timeout)
    c.http.timeout = 20
    print(c.http.timeout)

    try:
        c.http.timeout = -5  # Should raise ValueError
    except ValueError as e:
        print(f"Validation error: {e}")

    try:
        c.http.jitter = 1.5  # Should raise ValueError
    except ValueError as e:
        print(f"Validation error: {e}")

    c.update({"_lock": "bob", "http": {"timeout": 27}})

    print(c._lock, c.http.timeout)

    print(c)
    print(c.to_dict())

    d = c.to_dict()

    d["http"]["timeout"] = 25

    c.update(d)

    print(c)

# python usage.py
# 30.0
# 20.0
# Validation error: timeout must be positive
# Validation error: jitter must be between 0 and 1
# <unlocked _thread.RLock object owner=0 count=0 at 0x774d45dd0e40> 27.0
# {
#   "http": {
#     "headers": {},
#     "jitter": 0.2,
#     "max_retries": 3,
#     "rate_limit": 0.5,
#     "retry_delay": 1.0,
#     "timeout": 27.0,
#     "user_agent": "EthiCrawl/1.0"
#   }
# }
# {'http': {'headers': {}, 'jitter': 0.2, 'max_retries': 3, 'rate_limit': 0.5, 'retry_delay': 1.0, 'timeout': 27.0, 'user_agent': 'EthiCrawl/1.0'}}
# {
#   "http": {
#     "headers": {},
#     "jitter": 0.2,
#     "max_retries": 3,
#     "rate_limit": 0.5,
#     "retry_delay": 1.0,
#     "timeout": 25.0,
#     "user_agent": "EthiCrawl/1.0"
#   }
# }
