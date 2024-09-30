from enum import Enum


class Format(Enum):
    TEXT: str = "text"
    YAML: str = "yaml"
    JSON: str = "json"


class SampleType(Enum):
    ALL: str = "response_all"
    RESPONSE_AS_STR: str = "response_as_str"
    RESPONSE_AS_JSON: str = "response_as_json"
    RESPONSE_WITH_FILE: str = "response_with_file"


# _PropertyDefaultRequired = namedtuple("_PropertyDefaultRequired", ("empty", "general"))
# _Default_Required: _PropertyDefaultRequired = _PropertyDefaultRequired(empty=False, general=True)


class ResponseStrategy(Enum):
    STRING: str = "string"
    FILE: str = "file"
    OBJECT: str = "object"
