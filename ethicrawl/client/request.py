from ethicrawl.core import Resource


class Request(Resource):
    """Request representation of an operation to be performed on a resource.

    Request extends Resource to represent an operation that can be performed.
    This maintains the URL identity of the resource while providing a
    foundation for additional request-specific properties like headers,
    parameters, or operation types.

    This class serves as a base class for protocol-specific request
    implementations, such as HttpRequest.

    Attributes:
        url: URL of the resource (inherited from Resource)
    """

    pass
