from ethicrawl.core import ResourceList


class Queue:
    pending: ResourceList = ResourceList()
    processed: ResourceList = ResourceList()
    failed: ResourceList = ResourceList()
