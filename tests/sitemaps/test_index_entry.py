from ethicrawl.sitemaps import IndexEntry


class TestIndexEntry:
    def test_index_entry(self):
        repr(IndexEntry("https://www.example.com"))
