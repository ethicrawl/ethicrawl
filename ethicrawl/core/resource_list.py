from re import compile as re_compile
from typing import Generic, Iterable, Iterator, Pattern, TypeVar

from ethicrawl.core.resource import Resource

T = TypeVar("T", bound=Resource)


class ResourceList(Generic[T]):
    """Collection of Resource objects with filtering capabilities.

    ResourceList provides list-like functionality specialized for managing
    collections of Resources with additional filtering methods and type safety.
    The class is generic and can contain any subclass of Resource.

    Note:
        This class has no public attributes as all storage is private.

    Examples:
        >>> from ethicrawl.core import Resource, ResourceList
        >>> resources = ResourceList()
        >>> resources.append(Resource("https://example.com/page1"))
        >>> resources.append(Resource("https://example.com/page2"))
        >>> len(resources)
        2
        >>> filtered = resources.filter(r"page1")
        >>> len(filtered)
        1
    """

    def __init__(self, items: list[T] | None = None):
        """Initialize a resource list with optional initial items.

        Args:
            items: Optional list of Resource objects to initialize with

        Raises:
            TypeError: If items is not a list or contains non-Resource objects
        """
        self._items: list[T] = []
        if items and isinstance(items, list):
            self.extend(items)
        elif items:
            raise TypeError(f"Expected list got {type(items).__name__}")

    def __iter__(self) -> Iterator[T]:
        return iter(self._items)

    def __getitem__(self, index: int | slice) -> T | "ResourceList[T]":
        """Get items by index or slice.

        Args:
            index: Integer index or slice object

        Returns:
            Single Resource when indexed with integer, ResourceList when sliced
        """
        if isinstance(index, slice):
            result: ResourceList = ResourceList()
            result.extend(self._items[index])
            return result
        return self._items[index]

    def __len__(self) -> int:
        return len(self._items)

    def __str__(self) -> str:
        return str(self._items)

    def __repr__(self) -> str:
        return f"ResourceList({repr(self._items)})"

    def append(self, item: T) -> "ResourceList[T]":
        """Add a resource to the list.

        Args:
            item: Resource object to add

        Returns:
            Self for method chaining

        Raises:
            TypeError: If item is not a Resource object
        """
        if not isinstance(item, Resource):
            raise TypeError(f"Expected Resource, got {type(item).__name__}")
        self._items.append(item)
        return self

    def extend(self, items: Iterable[T]) -> "ResourceList[T]":
        """Add multiple resources to the list.

        Args:
            items: Iterable of Resource objects to add

        Returns:
            Self for method chaining

        Raises:
            TypeError: If any item is not a Resource object
        """
        for item in items:
            self.append(item)
        return self

    def filter(self, pattern: str | Pattern) -> "ResourceList[T]":
        """Filter resources by URL pattern.

        Args:
            pattern: String pattern or compiled regex Pattern to match against URLs

        Returns:
            New ResourceList containing only matching resources of the same type as original
        """
        if isinstance(pattern, str):
            pattern = re_compile(pattern)

        result = ResourceList[T]()  # More explicit generic parameter
        for item in self._items:
            if pattern.search(str(item.url)):
                result.append(item)  # T is preserved
        return result

    def to_list(self) -> list[T]:
        """Convert to a standard Python list.

        Returns:
            A copy of the internal list of resources
        """
        return self._items.copy()
