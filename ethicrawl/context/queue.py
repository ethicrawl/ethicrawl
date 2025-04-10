from ethicrawl.core import ResourceList


class Queue:
    """Resource queue for asynchronous operations.

    This class is intended for managing groups of resources in an asynchronous
    processing pipeline. Currently sketched out for future implementation.

    Note:
        This class is not currently used in the synchronous implementation.
        It is intended for future asynchronous processing capabilities.

    Attributes:
        pending: List of resources waiting to be processed
        processed: List of resources that have been successfully processed
        failed: List of resources that encountered errors during processing
    """

    pending: ResourceList = ResourceList()
    processed: ResourceList = ResourceList()
    failed: ResourceList = ResourceList()
