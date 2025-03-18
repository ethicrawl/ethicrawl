import pytest

from ethicrawl.config import SitemapConfig


class TestSitemapConfig:
    def test_properties(self):
        sc = SitemapConfig()
        sc.follow_external
        sc.max_depth
        sc.validate_urls

        sc.follow_external = False
        sc.max_depth = 5
        sc.validate_urls = True

        with pytest.raises(ValueError, match="max_depth must be at least 1"):
            sc.max_depth = 0
        with pytest.raises(TypeError, match="max_depth must be an integer"):
            sc.max_depth = 1.0
        with pytest.raises(TypeError, match="follow_external must be a boolean"):
            sc.follow_external = "foo"
        with pytest.raises(TypeError, match="validate_urls must be a boolean"):
            sc.validate_urls = "foo"
