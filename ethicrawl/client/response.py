from dataclasses import dataclass

from ethicrawl.core import Resource

from .request import Request


@dataclass
class Response(Resource):

    request: Request
    content: bytes = bytes()

    def __post_init__(self):
        """Validate response attributes."""
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
