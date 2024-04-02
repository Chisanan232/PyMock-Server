import re
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


class ConfigLoadingOrderKey(Enum):
    APIs: str = "apis"
    APPLY: str = "apply"
    FILE: str = "file"


"""
Data structure sample:
{
    "MockAPI": {
        ConfigLoadingOrderKey.APIs.value: <Callable at memory xxxxa>,
        ConfigLoadingOrderKey.APPLY.value: <Callable at memory xxxxb>,
        ConfigLoadingOrderKey.FILE.value: <Callable at memory xxxxc>,
    },
    "HTTP": {
        ConfigLoadingOrderKey.APIs.value: <Callable at memory xxxxd>,
        ConfigLoadingOrderKey.APPLY.value: <Callable at memory xxxxe>,
        ConfigLoadingOrderKey.FILE.value: <Callable at memory xxxxf>,
    },
}
"""
ConfigLoadingFunction: Dict[str, Dict[str, Callable]] = {}


def set_loading_function(data_model_key: str, **kwargs) -> None:
    global ConfigLoadingFunction
    if False in [str(k).lower() in [str(o.value).lower() for o in ConfigLoadingOrder] for k in kwargs.keys()]:
        raise KeyError("The arguments only have *apis*, *file* and *apply* for setting loading function data.")
    if data_model_key not in ConfigLoadingFunction.keys():
        ConfigLoadingFunction[data_model_key] = {}
    ConfigLoadingFunction[data_model_key].update(**kwargs)


class ConfigLoadingOrder(Enum):
    APIs: str = ConfigLoadingOrderKey.APIs.value
    APPLY: str = ConfigLoadingOrderKey.APPLY.value
    FILE: str = ConfigLoadingOrderKey.FILE.value

    @staticmethod
    def to_enum(v: Union[str, "ConfigLoadingOrder"]) -> "ConfigLoadingOrder":
        if isinstance(v, str):
            return ConfigLoadingOrder(v.lower())
        else:
            return v

    def get_loading_function(self, data_modal_key: str) -> Callable:
        return ConfigLoadingFunction[data_modal_key][self.value]

    def get_loading_function_args(self, *args) -> Optional[tuple]:
        if self is ConfigLoadingOrder.APIs:
            if args:
                return args
        return ()


class OpenAPIVersion(Enum):
    V2: str = "OpenAPI V2"
    V3: str = "OpenAPI V3"

    @staticmethod
    def to_enum(v: Union[str, "OpenAPIVersion"]) -> "OpenAPIVersion":
        if isinstance(v, str):
            if re.search(r"OpenAPI V[2-3]", v):
                return OpenAPIVersion(v)
            if re.search(r"2\.[0-9]\.[0-9].{0,8}", v):
                return OpenAPIVersion.V2
            if re.search(r"3\.[0-9]\.[0-9].{0,8}", v):
                return OpenAPIVersion.V3
            raise NotImplementedError(f"PyMock-API doesn't support parsing OpenAPI configuration with version '{v}'.")
        else:
            return v
