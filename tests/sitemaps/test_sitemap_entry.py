import pytest

from ethicrawl.sitemaps import SitemapEntry


class TestSitemapEntry:
    def test_sitemap_entry(self):
        url = "https://www.example.com"
        timestamps = [
            "2023-12-25",  # %Y-%m-%d
            "2023-12-25T14:30:45",  # %Y-%m-%dT%H:%M:%S
            "2023-12-25T14:30:45Z",  # %Y-%m-%dT%H:%M:%SZ
            "2023-12-25T14:30:45+0000",  # %Y-%m-%dT%H:%M:%S%z (no colon)
            "2023-12-25T14:30:45+00:00",  # %Y-%m-%dT%H:%M:%S%:z (with colon)
            "2023-12-25T14:30:45.123456Z",  # %Y-%m-%dT%H:%M:%S.%fZ (with microseconds)
            "2023-12-25T14:30:45.123456",  # %Y-%m-%dT%H:%M:%S.%f (microseconds, no Z)
        ]
        for lastmod in timestamps:
            assert SitemapEntry(url, lastmod).lastmod == lastmod

        with pytest.raises(ValueError, match="Invalid lastmod date format: foo"):
            SitemapEntry(url, "foo")

        with pytest.raises(TypeError, match="expected lastmod to be str"):
            SitemapEntry(url, 58)

        assert SitemapEntry(url).lastmod == None
        assert "2023-12-25" in str(SitemapEntry(url, "2023-12-25"))
        assert url in str(SitemapEntry(url))
