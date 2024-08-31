from enum import Enum
from typing import Union


class ContentType(Enum):
    application_json: str = "application/json"
    application_octet_stream: str = "application/octet-stream"
    all: str = "*/*"

    @staticmethod
    def to_enum(v: Union[str, "ContentType"]) -> "ContentType":
        if isinstance(v, str):
            return ContentType(v)
        else:
            return v
