import re
from typing import List, TypeVar, Generic, Union, Pattern, Iterator
from ethicrawl.core.resource import Resource

T = TypeVar("T", bound=Resource)


class ResourceList(Generic[T]):
    """A specialized collection for Resource objects with helpful operations."""

    def __init__(self, items: List[T] = None):
        """Initialize with optional list of Resource objects."""
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
        """Add a Resource to the list with type checking."""
        if not isinstance(item, Resource):
            raise TypeError(f"Only Resource objects can be added, got {type(item)}")
        self._items.append(item)
        return self

    def extend(self, items: List[T]) -> "ResourceList[T]":
        """Add multiple Resources to the list with type checking."""
        for item in items:
            self.append(item)
        return self

    # def deduplicate(self) -> "ResourceList[T]":
    #     """Remove duplicate resources based on URL."""
    #     seen = set()
    #     result = ResourceList()
    #     for item in self._items:
    #         url_str = str(item.url)
    #         if url_str not in seen:
    #             seen.add(url_str)
    #             result.append(item)
    #     return result

    def filter(self, pattern: Union[str, Pattern]) -> "ResourceList[T]":
        """Filter resources by regex pattern."""
        if isinstance(pattern, str):
            pattern = re.compile(pattern)

        result = ResourceList()
        for item in self._items:
            if pattern.search(str(item.url)):
                result.append(item)
        return result

    # def sort_by(
    #     self, key_func: Callable[[T], any], reverse: bool = False
    # ) -> "ResourceList[T]":
    #     """Sort by a custom key function."""
    #     return ResourceList(sorted(self._items, key=key_func, reverse=reverse))

    def to_list(self) -> List[T]:
        """Convert to a plain Python list."""
        return self._items.copy()
