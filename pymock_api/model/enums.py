from collections import namedtuple
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, Optional, Union


class Format(Enum):
    TEXT: str = "text"
    YAML: str = "yaml"
    JSON: str = "json"


class SampleType(Enum):
    ALL: str = "response_all"
    RESPONSE_AS_STR: str = "response_as_str"
    RESPONSE_AS_JSON: str = "response_as_json"
    RESPONSE_WITH_FILE: str = "response_with_file"


class ResponseStrategy(Enum):
    STRING: str = "string"
    FILE: str = "file"
    OBJECT: str = "object"

    @staticmethod
    def to_enum(v: Union[str, "ResponseStrategy"]) -> "ResponseStrategy":
        if isinstance(v, str):
            return ResponseStrategy(v.lower())
        else:
            return v


class TemplateApplyScanStrategy(Enum):
    BY_FILE_NAME: str = "by_file_name"
    BY_CONFIG_LIST: str = "by_config_list"
    FILE_NAME_FIRST: str = "file_name_first"
    CONFIG_LIST_FIRST: str = "config_list_first"

    @staticmethod
    def to_enum(v: Union[str, "TemplateApplyScanStrategy"]) -> "TemplateApplyScanStrategy":
        if isinstance(v, str):
            return TemplateApplyScanStrategy(v.lower())
        else:
            return v


ConfigLoadingFunction: Dict[str, Optional[Callable]] = {
    "apis": None,
    "apply": None,
    "file": None,
}


def set_loading_function(**kwargs) -> None:
    global ConfigLoadingFunction
    if False in [v in ConfigLoadingFunction.keys() for v in kwargs.keys()]:
        raise KeyError("The arguments only have *apis*, *file* and *apply* for setting loading function data.")
    ConfigLoadingFunction.update(**kwargs)


class ConfigLoadingOrder(Enum):
    APIs: str = "apis"
    APPLY: str = "apply"
    FILE: str = "file"

    @staticmethod
    def to_enum(v: Union[str, "ConfigLoadingOrder"]) -> "ConfigLoadingOrder":
        if isinstance(v, str):
            return ConfigLoadingOrder(v.lower())
        else:
            return v

    def get_loading_function(self) -> Callable:
        return ConfigLoadingFunction[self.value]  # type: ignore[return-value]
