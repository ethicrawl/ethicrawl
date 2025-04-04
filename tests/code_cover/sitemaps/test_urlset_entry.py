import pytest

from ethicrawl.sitemaps import UrlsetEntry, UrlsetDocument
from ethicrawl.core import Resource, ResourceList
from ethicrawl.context import Context


class TestUrlsetEntry:
    def test_urlset_entry(self):
        url = "https://www.example.com"
        repr(UrlsetEntry("https://www.example.com"))
        valid_change_freqs = [
            "always",
            "hourly",
            "daily",
            "weekly",
            "monthly",
            "yearly",
            "never",
        ]
        for freq in valid_change_freqs:
            UrlsetEntry(url, changefreq=freq)
        invalid_change_freq_types = [
            0,
            set(),
        ]
        for freq in invalid_change_freq_types:
            with pytest.raises(
                TypeError,
                match=f"changefreq must be a string, got {type(freq).__name__}",
            ):
                UrlsetEntry(url, changefreq=freq)
        with pytest.raises(
            ValueError,
            match=f"Invalid change frequency: 'foo'. Must be one of: always, hourly, daily, weekly, monthly, yearly, never",
        ):
            UrlsetEntry(url, changefreq="foo")

        entry = UrlsetEntry(url, changefreq=None)
        assert entry.changefreq is None, "changefreq should remain None"

        result = UrlsetEntry._validate_changefreq(None)
        assert result is None, "Validator should return None unchanged"

    def test_priority_validation(self):
        url = "https://www.example.com"

        # Valid priorities should work
        valid_priorities = [
            None,  # None is allowed
            0.0,  # Min boundary
            0.5,  # Middle value
            1.0,  # Max boundary
            0,  # Integer min
            1,  # Integer max
            "0.3",  # String representation
            "1",  # String integer
        ]

        for priority in valid_priorities:
            entry = UrlsetEntry(url, priority=priority)
            if priority is not None:
                assert isinstance(entry.priority, float)  # Should convert to float

        # Invalid range values
        invalid_ranges = [
            -0.1,  # Below min
            1.1,  # Above max
            -1,  # Negative integer
            2,  # Integer above max
            "1.01",  # String above max
            "-0.1",  # String below min
        ]

        for priority in invalid_ranges:
            with pytest.raises(
                ValueError, match=r"Priority must be between 0\.0 and 1\.0"
            ):
                UrlsetEntry(url, priority=priority)

        # Non-numeric strings
        invalid_strings = [
            "abc",
            "1.2.3",
            "priority",
            "",
            " ",
        ]

        for priority in invalid_strings:
            with pytest.raises(
                TypeError,
                match=f"Priority must be a number, got 'str'",
            ):
                UrlsetEntry(url, priority=priority)

    def test_none_priority_handling(self):
        """Test that None priority is preserved, not converted."""
        url = "https://www.example.com"

        # Test through constructor
        entry = UrlsetEntry(url, priority=None)
        assert entry.priority is None, "None priority should remain None"

        # Test the validator method directly
        result = UrlsetEntry._validate_priority(None)
        assert result is None, "Validator should return None unchanged"

    def test_str_representation(self):
        """Test string representation includes key fields."""
        url = "https://www.example.com"

        # Test with all fields populated
        entry = UrlsetEntry(
            url=url, priority=0.8, changefreq="daily", lastmod="2023-12-25T14:30:45Z"
        )
        str_rep = str(entry)

        # Check that all fields are represented
        assert url in str_rep, "URL should be in string representation"
        assert "0.8" in str_rep, "Priority should be in string representation"
        assert "daily" in str_rep, "Changefreq should be in string representation"
        assert "2023-12-25" in str_rep, "Lastmod should be in string representation"

        # Test with minimal fields
        basic_entry = UrlsetEntry(url=url)
        basic_str = str(basic_entry)

        # Should have URL but not the other fields
        assert url in basic_str, "URL should be in minimal string representation"
        assert "None" not in basic_str, "None values should not be explicitly shown"

        # Verify the representation is reasonably formatted
        # assert "UrlsetEntry" in str_rep, "Class name should be in representation"

    def test_entries_setter(self):
        """Test the entries setter validation."""
        # Create a document for testing
        context = Context(resource=Resource("https://www.example.com"))
        document = UrlsetDocument(context)

        # Test 1: Valid case - setting a ResourceList of UrlsetEntry objects
        entries = ResourceList(
            [
                UrlsetEntry("https://example.com/page1"),
                UrlsetEntry("https://example.com/page2", priority=0.8),
                UrlsetEntry("https://example.com/page3", changefreq="daily"),
            ]
        )

        document.entries = entries
        assert document.entries == entries, "Valid entries should be accepted"

        # Test 2: TypeError when not providing a ResourceList
        invalid_types = [
            [],  # Regular list
            {},  # Dictionary
            "string",  # String
            123,  # Integer
            None,  # None
        ]

        for invalid in invalid_types:
            with pytest.raises(TypeError, match="entries must be a ResourceList"):
                document.entries = invalid

        # Test 3: TypeError when ResourceList contains non-UrlsetEntry objects
        mixed_entries = ResourceList(
            [
                UrlsetEntry("https://example.com/valid"),
                Resource(
                    "https://example.com/invalid"
                ),  # Resource instead of UrlsetEntry
            ]
        )

        with pytest.raises(
            TypeError, match=f"entries must contain only UrlsetEntry objects"
        ):
            document.entries = mixed_entries

        # Test 4: Verify original entries remain unchanged after failed validation
        # First set valid entries
        valid_entries = ResourceList([UrlsetEntry("https://example.com/original")])
        document.entries = valid_entries

        # Try invalid set that should fail
        try:
            document.entries = "invalid"
        except TypeError:
            pass

        # Verify original entries are still there
        assert (
            document.entries == valid_entries
        ), "Failed setter should not alter existing entries"

    # @entries.setter
    # def entries(self, entries: ResourceList) -> None:
    #     """Set the URLs in this urlset.

    #     Args:
    #         entries: List of page URLs as UrlsetEntry objects

    #     Raises:
    #         TypeError: If entries is not a ResourceList or contains non-UrlsetEntry objects
    #     """
    #     if not isinstance(entries, ResourceList):
    #         raise TypeError("entries must be a ResourceList")
    #     for entry in entries:
    #         if not isinstance(entry, UrlsetEntry):
    #             raise TypeError("entries must contain only UrlsetEntry objects")
    #     self._entries = entries
