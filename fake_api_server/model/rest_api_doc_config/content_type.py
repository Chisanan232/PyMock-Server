from enum import Enum
from typing import Union


class ContentType(Enum):
    APPLICATION_JSON = "application/json"
    APPLICATION_OCTET_STREAM = "application/octet-stream"
    ALL = "*/*"

    @staticmethod
    def to_enum(v: Union[str, "ContentType"]) -> "ContentType":
        if isinstance(v, str):
            return ContentType(v)
        else:
            return v
