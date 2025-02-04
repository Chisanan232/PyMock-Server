from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from fake_api_server.model.api_config._base import _Checkable, _Config

from ._load.key import ConfigLoadingOrder


@dataclass(eq=False)
class LoadConfig(_Config, _Checkable):
    includes_apis: bool = field(default=True)
    order: List[ConfigLoadingOrder] = field(default_factory=list)

    _default_order: List[ConfigLoadingOrder] = field(init=False, repr=False)
    _absolute_key: str = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._default_order = [o for o in ConfigLoadingOrder]
        self._convert_order()

    def _convert_order(self) -> None:
        if self.order:
            is_str = list(map(lambda e: isinstance(e, str), self.order))
            if True in is_str:
                self.order = [ConfigLoadingOrder(o) for o in self.order]
        else:
            self.order = self._default_order

    def _compare(self, other: "LoadConfig") -> bool:
        return self.includes_apis == other.includes_apis and self.order == other.order

    @property
    def key(self) -> str:
        return "load_config"

    def serialize(self, data: Optional["LoadConfig"] = None) -> Optional[Dict[str, Any]]:
        includes_apis: bool = self._get_prop(data, prop="includes_apis")
        order: List[Union[str, ConfigLoadingOrder]] = self._get_prop(data, prop="order")
        return {
            "includes_apis": includes_apis,
            "order": [o.value if isinstance(o, ConfigLoadingOrder) else o for o in order],
        }

    @_Config._ensure_process_with_not_none_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["LoadConfig"]:
        self.includes_apis = data.get("includes_apis", True)
        self.order = [ConfigLoadingOrder(o) for o in (data.get("order", self._default_order) or [])]
        return self

    def is_work(self) -> bool:
        if not self.props_should_not_be_none(
            under_check={
                f"{self.absolute_model_key}.includes_apis": self.includes_apis,
                f"{self.absolute_model_key}.order": self.order,
            },
        ):
            return False
        if self.order:
            for o in self.order:
                assert self.should_be_valid(
                    config_key=f"{self.absolute_model_key}.order",
                    config_value=o,
                    criteria=[c for c in ConfigLoadingOrder],
                )
        return True


@dataclass(eq=False)
class TemplateConfigPathSetting(_Config, _Checkable, ABC):
    config_path_format: str = field(default_factory=str)

    _absolute_key: str = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if not self.config_path_format:
            self.config_path_format = self._default_config_path_format

    def _compare(self, other: "TemplateConfigPathSetting") -> bool:
        return self.config_path_format == other.config_path_format

    def serialize(self, data: Optional["TemplateConfigPathSetting"] = None) -> Optional[Dict[str, Any]]:
        config_path_format: str = self._get_prop(data, prop="config_path_format")
        return {
            "config_path_format": config_path_format,
        }

    @_Config._ensure_process_with_not_none_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["TemplateConfigPathSetting"]:
        self.config_path_format = data.get("config_path_format", self._default_config_path_format)
        return self

    @property
    @abstractmethod
    def _default_config_path_format(self) -> str:
        pass

    def is_work(self) -> bool:
        # TODO: Check the path format
        return True


class TemplateConfigPathAPI(TemplateConfigPathSetting):
    @property
    def key(self) -> str:
        return "api"

    @property
    def _default_config_path_format(self) -> str:
        return "**-api.yaml"


class TemplateConfigPathHTTP(TemplateConfigPathSetting):
    @property
    def key(self) -> str:
        return "http"

    @property
    def _default_config_path_format(self) -> str:
        return "**-http.yaml"


class TemplateConfigPathRequest(TemplateConfigPathSetting):
    @property
    def key(self) -> str:
        return "request"

    @property
    def _default_config_path_format(self) -> str:
        return "**-request.yaml"


class TemplateConfigPathResponse(TemplateConfigPathSetting):
    @property
    def key(self) -> str:
        return "response"

    @property
    def _default_config_path_format(self) -> str:
        return "**-response.yaml"


@dataclass(eq=False)
class TemplateConfigPathValues(_Config, _Checkable):
    base_file_path: str = field(default="./")
    api: TemplateConfigPathAPI = field(default_factory=TemplateConfigPathAPI)
    http: TemplateConfigPathHTTP = field(default_factory=TemplateConfigPathHTTP)
    request: TemplateConfigPathRequest = field(default_factory=TemplateConfigPathRequest)
    response: TemplateConfigPathResponse = field(default_factory=TemplateConfigPathResponse)

    _absolute_key: str = field(init=False, repr=False)

    def _compare(self, other: "TemplateConfigPathValues") -> bool:
        return (
            self.base_file_path == other.base_file_path
            and self.api == other.api
            and self.http == other.http
            and self.request == other.request
            and self.response == other.response
        )

    @property
    def key(self) -> str:
        return "config_path_values"

    def serialize(self, data: Optional["TemplateConfigPathValues"] = None) -> Optional[Dict[str, Any]]:
        base_file_path: str = self._get_prop(data, prop="base_file_path")
        api = self.api or self._get_prop(data, prop="api")
        http = self.http or self._get_prop(data, prop="http")
        request = self.request or self._get_prop(data, prop="request")
        response = self.response or self._get_prop(data, prop="response")
        if not (api and request and response):
            # TODO: Should raise exception?
            return None
        return {
            "base_file_path": base_file_path,
            "api": api.serialize(),
            "http": http.serialize(),
            "request": request.serialize(),
            "response": response.serialize(),
        }

    @_Config._ensure_process_with_not_none_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["TemplateConfigPathValues"]:
        self.base_file_path = data.get("base_file_path", "./")

        template_api = TemplateConfigPathAPI()
        template_api.absolute_model_key = self.key
        self.api = template_api.deserialize(data.get("api", {}))

        template_http = TemplateConfigPathHTTP()
        template_http.absolute_model_key = self.key
        self.http = template_http.deserialize(data.get("http", {}))

        template_request = TemplateConfigPathRequest()
        template_request.absolute_model_key = self.key
        self.request = template_request.deserialize(data.get("request", {}))

        template_response = TemplateConfigPathResponse()
        template_response.absolute_model_key = self.key
        self.response = template_response.deserialize(data.get("response", {}))
        return self

    def is_work(self) -> bool:
        # TODO: Check the path format
        self.api.stop_if_fail = self.stop_if_fail
        self.http.stop_if_fail = self.stop_if_fail
        self.request.stop_if_fail = self.stop_if_fail
        self.response.stop_if_fail = self.stop_if_fail
        return self.api.is_work() and self.http.is_work() and self.request.is_work() and self.response.is_work()


@dataclass(eq=False)
class TemplateApply(_Config, _Checkable):
    api: List[Union[str, Dict[str, List[str]]]] = field(default_factory=list)

    _absolute_key: str = field(init=False, repr=False)

    def _compare(self, other: "TemplateApply") -> bool:
        return self.api == other.api

    @property
    def key(self) -> str:
        return "apply"

    def serialize(self, data: Optional["TemplateApply"] = None) -> Optional[Dict[str, Any]]:
        api: str = self._get_prop(data, prop="api")
        return {
            "api": api,
        }

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["TemplateApply"]:
        self.api = data.get("api")  # type: ignore[assignment]
        return self

    def is_work(self) -> bool:
        if self.api is None or len(self.api) == 0:
            return True
        else:
            all_ele_is_str = list(map(lambda a: isinstance(a, str), self.api))
            all_ele_is_dict = list(map(lambda a: isinstance(a, dict), self.api))
            ele_is_str = set(all_ele_is_str)
            ele_is_dict = set(all_ele_is_dict)
            if len(ele_is_str) == 1 and len(ele_is_dict) == 1 and (True in ele_is_str or True in ele_is_dict):
                return True
        return False


@dataclass(eq=False)
class TemplateFileConfig(_Config, _Checkable):
    """The data model which could be set details attribute by section *template*."""

    activate: bool = field(default=False)
    load_config: LoadConfig = field(default_factory=LoadConfig)
    config_path_values: TemplateConfigPathValues = field(default_factory=TemplateConfigPathValues)
    apply: TemplateApply = field(default_factory=TemplateApply)

    _absolute_key: str = field(init=False, repr=False)

    def _compare(self, other: "TemplateFileConfig") -> bool:
        return (
            self.activate == other.activate
            and self.load_config == other.load_config
            and self.config_path_values == other.config_path_values
            and self.apply == other.apply
        )

    @property
    def key(self) -> str:
        return "file"

    def serialize(self, data: Optional["TemplateFileConfig"] = None) -> Optional[Dict[str, Any]]:
        activate: bool = self.activate or self._get_prop(data, prop="activate")
        load_config: LoadConfig = self.load_config or self._get_prop(data, prop="load_config")
        config_path_values: TemplateConfigPathValues = self.config_path_values or self._get_prop(
            data, prop="config_path_values"
        )
        apply: TemplateApply = self.apply or self._get_prop(data, prop="apply")
        if not (config_path_values and apply and activate is not None):
            # TODO: Should it ranse an exception outside?
            return None
        return {
            "activate": activate,
            "load_config": load_config.serialize(),
            "config_path_values": config_path_values.serialize(),
            "apply": apply.serialize(),
        }

    @_Config._ensure_process_with_not_none_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["TemplateFileConfig"]:
        self.activate = data.get("activate", False)

        load_config = LoadConfig()
        load_config.absolute_model_key = self.key
        self.load_config = load_config.deserialize(data.get("load_config", {}))

        template_values = TemplateConfigPathValues()
        template_values.absolute_model_key = self.key
        self.config_path_values = template_values.deserialize(data.get("config_path_values", {}))

        template_apply = TemplateApply()
        template_apply.absolute_model_key = self.key
        self.apply = template_apply.deserialize(data.get("apply", {}))
        return self

    def is_work(self) -> bool:
        if not self.props_should_not_be_none(
            under_check={
                f"{self.absolute_model_key}.activate": self.activate,
            },
            accept_empty=False,
        ):
            return False
        self.load_config.stop_if_fail = self.stop_if_fail
        self.config_path_values.stop_if_fail = self.stop_if_fail
        if self.apply:
            self.apply.stop_if_fail = self.stop_if_fail
        return (
            isinstance(self.activate, bool)
            and self.load_config.is_work()
            and self.config_path_values.is_work()
            and (self.apply.is_work() if self.apply else True)
        )
