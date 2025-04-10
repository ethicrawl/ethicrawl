from ethicrawl.context.queue import Queue
from ethicrawl.core import ResourceList


class TestQueue:
    def test_queue(self):
        q = Queue()
        assert isinstance(q.pending, ResourceList)
        assert isinstance(q.processed, ResourceList)
        assert isinstance(q.failed, ResourceList)
