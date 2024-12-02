from enum import Enum
from typing import Union


class HTTPMethod(Enum):
    """HTTP methods

    Methods from the following RFCs are all observed:

        * RFC 7231: Hypertext Transfer Protocol (HTTP/1.1), obsoletes 2616
        * RFC 5789: PATCH Method for HTTP
    """

    def __contains__(cls, member: Union[str, "Enum"]) -> bool:
        if not isinstance(member, (str, Enum)):
            raise TypeError(
                "unsupported operand type(s) for 'in': '%s' and '%s'"
                % (type(member).__qualname__, cls.__class__.__qualname__)
            )
        member_value = member if isinstance(member, str) else member.value
        return member_value.upper() in [m.value.upper() for m in HTTPMethod]

    CONNECT = "CONNECT"
    DELETE = "DELETE"
    GET = "GET"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    PATCH = "PATCH"
    POST = "POST"
    PUT = "PUT"
    TRACE = "TRACE"
