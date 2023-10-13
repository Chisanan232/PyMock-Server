import fnmatch
import glob
import os
import pathlib
import re
from abc import ABC, ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type, Union

from ..._utils.file_opt import YAML, _BaseFileOperation
from ...model.enums import ConfigLoadingOrder, set_loading_function
from ._base import SelfType, _Config


@dataclass(eq=False)
class LoadConfig(_Config):
    includes_apis: bool = True
    order: List[ConfigLoadingOrder] = field(default_factory=list)

    _default_order: List[ConfigLoadingOrder] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._default_order = [ConfigLoadingOrder.APIs]
        if self.order is not None:
            self._convert_order()

    def _convert_order(self) -> None:
        is_str = list(map(lambda e: isinstance(e, str), self.order))
        if True in is_str:
            self.order = [ConfigLoadingOrder.to_enum(o) for o in self.order]

    def _compare(self, other: "LoadConfig") -> bool:
        return self.includes_apis == other.includes_apis and self.order == other.order

    def serialize(self, data: Optional["LoadConfig"] = None) -> Optional[Dict[str, Any]]:
        includes_apis: bool = self._get_prop(data, prop="includes_apis")
        order: List[Union[str, ConfigLoadingOrder]] = self._get_prop(data, prop="order")
        if not order:
            order = [str(o.value) for o in self._default_order]
        return {
            "includes_apis": includes_apis,
            "order": [o.value if isinstance(o, ConfigLoadingOrder) else o for o in order],
        }

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["LoadConfig"]:
        self.includes_apis = data.get("includes_apis", True)
        self.order = [ConfigLoadingOrder.to_enum(o) for o in data.get("order", self._default_order)]
        return self


@dataclass(eq=False)
class TemplateSetting(_Config, ABC):
    config_path_format: str = field(default_factory=str)

    def __post_init__(self) -> None:
        if not self.config_path_format:
            self.config_path_format = self._default_config_path_format

    def _compare(self, other: "TemplateSetting") -> bool:
        return self.config_path_format == other.config_path_format

    def serialize(self, data: Optional["TemplateSetting"] = None) -> Optional[Dict[str, Any]]:
        config_path_format: str = self._get_prop(data, prop="config_path_format")
        return {
            "config_path_format": config_path_format,
        }

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["TemplateSetting"]:
        self.config_path_format = data.get("config_path_format", self._default_config_path_format)
        return self

    @property
    @abstractmethod
    def _default_config_path_format(self) -> str:
        pass


class TemplateAPI(TemplateSetting):
    @property
    def _default_config_path_format(self) -> str:
        return "**-api.yaml"


class TemplateHTTP(TemplateSetting):
    @property
    def _default_config_path_format(self) -> str:
        return "**-http.yaml"


class TemplateRequest(TemplateSetting):
    @property
    def _default_config_path_format(self) -> str:
        return "**-request.yaml"


class TemplateResponse(TemplateSetting):
    @property
    def _default_config_path_format(self) -> str:
        return "**-response.yaml"


@dataclass(eq=False)
class TemplateValues(_Config):
    base_file_path: str = "./"
    api: TemplateAPI = TemplateAPI()
    http: TemplateHTTP = TemplateHTTP()
    request: TemplateRequest = TemplateRequest()
    response: TemplateResponse = TemplateResponse()

    def _compare(self, other: "TemplateValues") -> bool:
        return (
            self.base_file_path == other.base_file_path
            and self.api == other.api
            and self.http == other.http
            and self.request == other.request
            and self.response == other.response
        )

    def serialize(self, data: Optional["TemplateValues"] = None) -> Optional[Dict[str, Any]]:
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

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["TemplateValues"]:
        self.base_file_path = data.get("base_file_path", "./")
        self.api = TemplateAPI().deserialize(data.get("api", {}))
        self.http = TemplateHTTP().deserialize(data.get("http", {}))
        self.request = TemplateRequest().deserialize(data.get("request", {}))
        self.response = TemplateResponse().deserialize(data.get("response", {}))
        return self


@dataclass(eq=False)
class TemplateApply(_Config):
    api: List[Union[str, Dict[str, List[str]]]] = field(default_factory=list)

    def _compare(self, other: "TemplateApply") -> bool:
        return self.api == other.api

    def serialize(self, data: Optional["TemplateApply"] = None) -> Optional[Dict[str, Any]]:
        api: str = self._get_prop(data, prop="api")
        return {
            "api": api,
        }

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["TemplateApply"]:
        self.api = data.get("api")  # type: ignore[assignment]
        return self


@dataclass(eq=False)
class TemplateConfig(_Config):
    """The data model which could be set details attribute by section *template*."""

    activate: bool = False
    load_config: LoadConfig = LoadConfig()
    values: TemplateValues = TemplateValues()
    apply: TemplateApply = TemplateApply()

    def _compare(self, other: "TemplateConfig") -> bool:
        return (
            self.activate == other.activate
            and self.load_config == other.load_config
            and self.values == other.values
            and self.apply == other.apply
        )

    def serialize(self, data: Optional["TemplateConfig"] = None) -> Optional[Dict[str, Any]]:
        activate: bool = self.activate or self._get_prop(data, prop="activate")
        load_config: LoadConfig = self.load_config or self._get_prop(data, prop="load_config")
        values: TemplateValues = self.values or self._get_prop(data, prop="values")
        apply: TemplateApply = self.apply or self._get_prop(data, prop="apply")
        if not (values and apply and activate is not None):
            # TODO: Should it ranse an exception outside?
            return None
        return {
            "activate": activate,
            "load_config": load_config.serialize(),
            "values": values.serialize(),
            "apply": apply.serialize(),
        }

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["TemplateConfig"]:
        self.activate = data.get("activate", False)
        self.load_config = LoadConfig().deserialize(data.get("load_config", {}))
        self.values = TemplateValues().deserialize(data.get("values", {}))
        self.apply = TemplateApply().deserialize(data.get("apply", {}))
        return self


class TemplateConfigLoadable(metaclass=ABCMeta):
    """The data model which could load template configuration."""

    _config_file_name: str = "api.yaml"
    _configuration: _BaseFileOperation = YAML()

    def __init__(self):
        set_loading_function(
            apis=self._load_mocked_apis_from_data,
            apply=self._load_templatable_config_by_apply,
            file=self._load_templatable_config,
        )

    @property
    def config_file_name(self) -> str:
        return self._config_file_name

    @config_file_name.setter
    def config_file_name(self, n: str) -> None:
        self._config_file_name = n

    def _load_mocked_apis_config(self, mocked_apis_data: dict) -> None:
        loading_order = self._template_config.load_config.order

        if self._template_config.load_config.includes_apis:
            if (ConfigLoadingOrder.APIs not in loading_order) or (
                ConfigLoadingOrder.APIs in loading_order and not self._template_config.activate
            ):
                self._load_mocked_apis_from_data(mocked_apis_data)

        if self._template_config.activate:
            for load_config in loading_order:
                args = (mocked_apis_data,)
                args = load_config.get_loading_function_args(*args)  # type: ignore[assignment]
                load_config.get_loading_function()(*args)

    def _load_templatable_config(self) -> None:
        customize_config_file_format = "**"
        config_file_format = f"[!_**]{customize_config_file_format}"
        # all_paths = glob.glob(f"{self._base_path}**/[!_*]*.yaml", recursive=True)
        config_base_path = self._template_config.values.base_file_path
        all_paths = glob.glob(f"{config_base_path}{config_file_format}")
        if os.path.exists(f"{config_base_path}{self.config_file_name}"):
            all_paths.remove(f"{config_base_path}{self.config_file_name}")
        for path in all_paths:
            if os.path.isdir(path):
                # Has tag as directory
                for path_with_tag in glob.glob(f"{path}/{self._config_file_format}.yaml"):
                    # In the tag directory, it's config
                    self._deserialize_and_set_template_config(path_with_tag)
            else:
                assert os.path.isfile(path) is True
                if fnmatch.fnmatch(path, f"{self._config_file_format}.yaml"):
                    # Doesn't have tag, it's config
                    self._deserialize_and_set_template_config(path)

    def _load_templatable_config_by_apply(self) -> None:
        apply_apis = self._template_config.apply.api
        all_ele_is_dict = list(map(lambda e: isinstance(e, dict), apply_apis))
        config_path_format = self._config_file_format
        config_base_path = self._template_config.values.base_file_path
        if False in all_ele_is_dict:
            # no tag API
            for api in apply_apis:
                assert isinstance(api, str)
                api_config = config_path_format.replace("**", api)
                config_path = str(pathlib.Path(config_base_path, f"{api_config}.yaml"))
                self._deserialize_and_set_template_config(config_path)
        else:
            # API with tag
            for tag_apis in apply_apis:
                assert isinstance(tag_apis, dict)
                for tag, apis in tag_apis.items():
                    for api in apis:
                        api_config = config_path_format.replace("**", api)
                        config_path = str(pathlib.Path(config_base_path, tag, f"{api_config}.yaml"))
                        self._deserialize_and_set_template_config(config_path)

    @property
    @abstractmethod
    def _template_config(self) -> TemplateConfig:
        pass

    @property
    @abstractmethod
    def _config_file_format(self) -> str:
        pass

    def _deserialize_and_set_template_config(self, path: str) -> None:
        config = self._deserialize_template_config(path)
        assert config is not None, "Configuration should not be empty."
        args = {
            "path": path,
        }
        self._set_template_config(config, **args)

    def _deserialize_template_config(self, path: str) -> Optional[_Config]:
        # Read YAML config
        yaml_config = self._configuration.read(path)
        # Deserialize YAML config content as PyMock data model
        config = self._deserialize_as_template_config
        config.base_file_path = str(pathlib.Path(path).parent)
        config.config_path = pathlib.Path(path).name
        return config.deserialize(yaml_config)

    @property
    @abstractmethod
    def _deserialize_as_template_config(self) -> "_TemplatableConfig":
        pass

    @abstractmethod
    def _set_template_config(self, config: _Config, **kwargs) -> None:
        pass

    def _load_mocked_apis_from_data(self, mocked_apis_data: dict) -> None:
        self._set_mocked_apis()
        if mocked_apis_data:
            for mock_api_name in mocked_apis_data.keys():
                api_config = self._deserialize_as_template_config
                api_config.config_path = f"{mock_api_name}{api_config.config_file_tail}.yaml"
                self._set_mocked_apis(
                    api_key=mock_api_name,
                    api_config=api_config.deserialize(data=mocked_apis_data.get(mock_api_name, None)),
                )

    @abstractmethod
    def _set_mocked_apis(self, api_key: str = "", api_config: Optional[_Config] = None) -> None:
        pass


@dataclass(eq=False)
class _TemplatableConfig(_Config, ABC):
    apply_template_props: bool = True

    # The settings which could be set by section *template* or override the values
    base_file_path: str = ""
    config_path: str = field(default_factory=str)
    config_file_tail: str = field(default_factory=str)
    config_path_format: str = field(default_factory=str)

    _default_base_file_path: str = "./"

    # Attributes for inner usage
    _current_template: TemplateConfig = TemplateConfig()
    _has_apply_template_props_in_config: bool = False

    # Component for inner usage
    _configuration: _BaseFileOperation = YAML()

    def _compare(self, other: SelfType) -> bool:
        return self.apply_template_props == other.apply_template_props

    def serialize(self, data: Optional[SelfType] = None) -> Optional[Dict[str, Any]]:
        apply_template_props: bool = self._get_prop(data, prop="apply_template_props")
        if self._has_apply_template_props_in_config:
            return {
                "apply_template_props": apply_template_props,
            }
        else:
            return {}

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional[SelfType]:
        def _update_template_prop(key: Any) -> None:
            value = data.get(key, None)
            if value is not None:
                self._has_apply_template_props_in_config = True
                # Note: Override the value which be set by upper layer from template config
                setattr(self, key, value)

        _update_template_prop("apply_template_props")
        _update_template_prop("base_file_path")
        _update_template_prop("config_path")
        _update_template_prop("config_path_format")

        # Update the tail part of file name to let it could find the dividing configuration
        old_config_file_tail = self.config_file_tail
        self.config_file_tail = (self.config_path_format or self._template_setting.config_path_format).replace("**", "")
        self.config_path = self.config_path.replace(old_config_file_tail, self.config_file_tail)

        if self.apply_template_props:
            data = self._get_dividing_config(data)
        return self

    def _get_dividing_config(self, data: dict) -> dict:
        base_file_path = (
            self.base_file_path or self._current_template.values.base_file_path or self._default_base_file_path
        )
        dividing_config_path = str(pathlib.Path(base_file_path, self.config_path))
        if dividing_config_path and os.path.exists(dividing_config_path) and os.path.isfile(dividing_config_path):
            dividing_data = self._configuration.read(dividing_config_path)
            data.update(**dividing_data)
        return data

    @property
    @abstractmethod
    def _template_setting(self) -> TemplateSetting:
        pass

    def _deserialize_as(
        self, data_model: Type["_TemplatableConfig"], with_data: dict
    ) -> Optional["_TemplatableConfig"]:
        if with_data:
            config = data_model(_current_template=self._current_template)
            config.base_file_path = self.base_file_path
            config.config_path = self.config_path.replace(self.config_file_tail, config.config_file_tail)
            return config.deserialize(data=with_data)
        else:
            return None
