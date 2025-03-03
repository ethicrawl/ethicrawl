from ethicrawl import EthiCrawl, HttpClient

if __name__ == "__main__":
    ethicrawl = EthiCrawl("https://gb.maxmara.com/", http_client=HttpClient.with_selenium(headless=False),)
