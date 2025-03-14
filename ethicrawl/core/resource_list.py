import re
from typing import List, TypeVar, Generic, Union, Pattern, Iterator
from ethicrawl.core.resource import Resource

T = TypeVar("T", bound=Resource)


class ResourceList(Generic[T]):
    """
    A specialized collection for Resource objects with helpful operations.

    ResourceList provides a type-safe container for working with collections
    of Resource objects, with additional functionality like pattern filtering.
    It implements standard container methods so it can be used like a regular list.

    Examples:
        >>> from ethicrawl import Resource, ResourceList, Url
        >>> # Create with initial items
        >>> resources = ResourceList([
        ...     Resource("https://example.com/page1"),
        ...     Resource("https://example.com/page2"),
        ...     Resource("https://example.com/products/item")
        ... ])
        >>>
        >>> # Filter by pattern
        >>> product_pages = resources.filter(r"/products/")
        >>> len(product_pages)
        1
        >>>
        >>> # Use list-like operations
        >>> resources.append(Resource("https://example.com/contact"))
        >>> len(resources)
        4

    Attributes:
        _items (List[Resource]): Internal list of resources
    """

    def __init__(self, items: List[T] = None):
        """
        Initialize with optional list of Resource objects.

        Args:
            items (List[Resource], optional): Initial resources to add
        """
        self._items: List[T] = []
        if items:
            self.extend(items)

    def __iter__(self) -> Iterator[T]:
        return iter(self._items)

    def __getitem__(self, index) -> Union[T, List[T]]:
        return self._items[index]

    def __len__(self) -> int:
        return len(self._items)

    def __str__(self) -> str:
        return str(self._items)

    def __repr__(self) -> str:
        return f"ResourceList({repr(self._items)})"

    def append(self, item: T) -> "ResourceList[T]":
        """
        Add a Resource to the list with type checking.

        Args:
            item (Resource): Resource to add

        Returns:
            ResourceList: Self for method chaining

        Raises:
            TypeError: If item is not a Resource object
        """
        if not isinstance(item, Resource):
            raise TypeError(f"Only Resource objects can be added, got {type(item)}")
        self._items.append(item)
        return self

    def extend(self, items: List[T]) -> "ResourceList[T]":
        """
        Add multiple Resources to the list with type checking.

        Args:
            items (List[Resource]): Resources to add

        Returns:
            ResourceList: Self for method chaining

        Raises:
            TypeError: If any item is not a Resource object
        """
        for item in items:
            self.append(item)
        return self

    def filter(self, pattern: Union[str, Pattern]) -> "ResourceList[T]":
        """
        Filter resources by regex pattern matching against their URLs.

        This method returns a new ResourceList containing only resources whose
        URL matches the given pattern.

        Args:
            pattern (str or re.Pattern): Regular expression pattern to match
                                       Can be a string or compiled regex pattern

        Returns:
            ResourceList: New list containing only matching resources

        Examples:
            >>> resources = ResourceList([
            ...     Resource("https://example.com/product-123"),
            ...     Resource("https://example.com/about")
            ... ])
            >>> product_pages = resources.filter(r"product-[0-9]+")
            >>> len(product_pages)
            1
        """
        if isinstance(pattern, str):
            pattern = re.compile(pattern)

        result = ResourceList()
        for item in self._items:
            if pattern.search(str(item.url)):
                result.append(item)
        return result

    def to_list(self) -> List[T]:
        """
        Convert to a plain Python list.

        Returns:
            List[Resource]: A standard Python list containing the resources
        """
        return self._items.copy()
