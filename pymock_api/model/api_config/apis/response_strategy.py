from enum import Enum


class ResponseStrategy(Enum):
    STRING: str = "string"
    FILE: str = "file"
    OBJECT: str = "object"
