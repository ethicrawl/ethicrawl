from dataclasses import dataclass

from ethicrawl.core import Resource

from .request import Request


@dataclass
class Response(Resource):
    """Response representation of a resource request operation.

    Response extends Resource to represent the result of a client request operation.
    This ensures that responses maintain the URL identity of their source resource
    while adding request tracking and content storage capabilities.

    By inheriting from Resource, Response objects can be used anywhere a Resource
    is expected, which enables chaining of operations. This design provides a
    consistent pattern where the output of one operation can serve as the input
    to another.

    Attributes:
        url: URL of the response (inherited from Resource)
        request: The Request object that generated this response
        content: Binary content returned by the operation (empty bytes by default)

    Example:
        >>> from ethicrawl.client import Response, Request
        >>> from ethicrawl.core import Resource, Url
        >>> req = Request(Url("https://example.com"))
        >>> resp = Response(req.url, req, b"<html>Example</html>")
        >>> resp.url == req.url  # Maintains resource identity
        True
        >>> len(resp.content)
        22
    """

    request: Request
    content: bytes = bytes()

    def __post_init__(self):
        """Validate response attributes.

        Performs type checking and value validation:
        - Ensures content is bytes or None
        - Ensures request is a Request instance

        Raises:
            TypeError: If any attribute has an invalid type
        """
        # Validate content is bytes
        if self.content is not None and not isinstance(self.content, bytes):
            raise TypeError(
                f"content must be bytes or None, got {type(self.content).__name__}"
            )

        # Validate request
        if not isinstance(self.request, Request):
            raise TypeError(
                f"request must be an Request instance, got {type(self.request).__name__}"
            )
