from enum import Enum
from typing import Callable, Dict, Optional


class ConfigLoadingOrderKey(Enum):
    APIs = "apis"
    APPLY = "apply"
    FILE = "file"


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
    APIs = ConfigLoadingOrderKey.APIs.value
    APPLY = ConfigLoadingOrderKey.APPLY.value
    FILE = ConfigLoadingOrderKey.FILE.value

    def get_loading_function(self, data_modal_key: str) -> Callable:
        return ConfigLoadingFunction[data_modal_key][self.value]

    def get_loading_function_args(self, *args) -> Optional[tuple]:
        if self is ConfigLoadingOrder.APIs and len(args) > 0:
            return args
        return ()
