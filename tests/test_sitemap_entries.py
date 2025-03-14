import pytest
from datetime import datetime
from ethicrawl.sitemaps.sitemap_entries import SitemapEntry, IndexEntry, UrlsetEntry
from ethicrawl.core.url import Url
from ethicrawl.core.resource import Resource


class TestSitemapEntry:
    def test_initialization(self):
        """Test basic initialization of SitemapEntry."""
        entry = SitemapEntry("https://example.com")
        assert str(entry.url) == "https://example.com"
        assert entry.lastmod is None

        # Test with lastmod
        entry = SitemapEntry("https://example.com", lastmod="2023-01-01")
        assert entry.lastmod == "2023-01-01"

    def test_lastmod_validation(self):
        """Test validation of different lastmod date formats."""
        # Test valid dates
        valid_dates = [
            "2023-01-01",
            "2023-01-01T12:30:45",
            "2023-01-01T12:30:45Z",
            "2023-01-01T12:30:45+0100",
            "2023-01-01T12:30:45.123Z",
            "2023-01-01T12:30:45.123456",
        ]

        for date in valid_dates:
            entry = SitemapEntry("https://example.com", lastmod=date)
            assert entry.lastmod == date

        # Test invalid dates
        invalid_dates = [
            "2023-13-01",  # Invalid month
            "2023/01/01",  # Wrong format
            "January 1, 2023",  # Not ISO format
            "tomorrow",  # Not a date
        ]

        for date in invalid_dates:
            with pytest.raises(ValueError):
                SitemapEntry("https://example.com", lastmod=date)

    def test_string_representation(self):
        """Test string representation of entries."""
        # Without lastmod
        entry = SitemapEntry("https://example.com")
        assert str(entry) == "https://example.com"

        # With lastmod
        entry = SitemapEntry("https://example.com", lastmod="2023-01-01")
        assert str(entry) == "https://example.com (last modified: 2023-01-01)"

    def test_hash_behavior(self):
        """Test that entries with same URL hash to same value."""
        entry1 = SitemapEntry("https://example.com")
        entry2 = SitemapEntry("https://example.com")
        entry3 = SitemapEntry("https://example.org")

        # Same URLs should hash the same regardless of other attributes
        assert hash(entry1) == hash(entry2)
        assert hash(entry1) != hash(entry3)

        # Works in sets
        entries = {entry1, entry2, entry3}
        assert len(entries) == 2

    def test_resource_inheritance(self):
        """Test that SitemapEntry inherits from Resource."""
        entry = SitemapEntry("https://example.com")
        assert isinstance(entry, Resource)

        # Check that Resource methods work
        assert entry.url.netloc == "example.com"


class TestIndexEntry:
    def test_initialization(self):
        """Test initialization of IndexEntry."""
        entry = IndexEntry("https://example.com/sitemap1.xml")
        assert str(entry.url) == "https://example.com/sitemap1.xml"
        assert entry.lastmod is None

        # With lastmod
        entry = IndexEntry("https://example.com/sitemap1.xml", lastmod="2023-01-01")
        assert entry.lastmod == "2023-01-01"

    def test_repr_format(self):
        """Test the repr format of IndexEntry."""
        entry = IndexEntry("https://example.com/sitemap1.xml", lastmod="2023-01-01")
        repr_str = repr(entry)
        assert "SitemapIndexEntry" in repr_str
        assert "url='https://example.com/sitemap1.xml'" in repr_str
        assert "lastmod='2023-01-01'" in repr_str

    def test_inheritance(self):
        """Test that IndexEntry inherits from SitemapEntry."""
        entry = IndexEntry("https://example.com/sitemap1.xml")
        assert isinstance(entry, SitemapEntry)


class TestUrlsetEntry:
    def test_initialization(self):
        """Test initialization of UrlsetEntry."""
        # Basic initialization
        entry = UrlsetEntry("https://example.com/page")
        assert str(entry.url) == "https://example.com/page"
        assert entry.lastmod is None
        assert entry.changefreq is None
        assert entry.priority is None

        # Full initialization
        entry = UrlsetEntry(
            "https://example.com/page",
            lastmod="2023-01-01",
            changefreq="daily",
            priority=0.8,
        )
        assert entry.lastmod == "2023-01-01"
        assert entry.changefreq == "daily"
        assert entry.priority == 0.8

    def test_changefreq_validation(self):
        """Test validation of changefreq values."""
        # Valid frequencies
        valid_freqs = [
            "always",
            "hourly",
            "daily",
            "weekly",
            "monthly",
            "yearly",
            "never",
        ]

        for freq in valid_freqs:
            entry = UrlsetEntry("https://example.com", changefreq=freq)
            assert entry.changefreq == freq

        # Invalid frequencies
        invalid_freqs = ["biweekly", "quarterly", "sometimes", "123"]

        for freq in invalid_freqs:
            with pytest.raises(ValueError):
                UrlsetEntry("https://example.com", changefreq=freq)

        # Uppercase should be normalized to lowercase
        entry = UrlsetEntry("https://example.com", changefreq="DAILY")
        assert entry.changefreq == "daily"

    def test_priority_validation(self):
        """Test validation of priority values."""
        # Valid priorities
        valid_priorities = [0, 0.1, 0.5, 0.9, 1.0, "0.7"]

        for priority in valid_priorities:
            entry = UrlsetEntry("https://example.com", priority=priority)
            assert isinstance(entry.priority, float)

        # Invalid priorities
        invalid_priorities = [-0.1, 1.1, "high", "not-a-number"]

        for priority in invalid_priorities:
            with pytest.raises(ValueError):
                UrlsetEntry("https://example.com", priority=priority)

    def test_string_representation(self):
        """Test string representation with all fields."""
        entry = UrlsetEntry(
            "https://example.com",
            lastmod="2023-01-01",
            changefreq="weekly",
            priority=0.8,
        )
        str_repr = str(entry)

        assert "https://example.com" in str_repr
        assert "last modified: 2023-01-01" in str_repr
        assert "frequency: weekly" in str_repr
        assert "priority: 0.8" in str_repr

    def test_repr_format(self):
        """Test repr format of UrlsetEntry."""
        entry = UrlsetEntry(
            "https://example.com",
            lastmod="2023-01-01",
            changefreq="weekly",
            priority=0.8,
        )
        repr_str = repr(entry)

        assert "SitemapUrlsetEntry" in repr_str
        assert "url='https://example.com'" in repr_str
        assert "lastmod='2023-01-01'" in repr_str
        assert "changefreq='weekly'" in repr_str
        assert "priority=0.8" in repr_str
