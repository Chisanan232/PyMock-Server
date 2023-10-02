import fnmatch
import glob
import os
import re
from abc import ABC, ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from ..._utils.file_opt import YAML, _BaseFileOperation
from ...model.enums import TemplateApplyScanStrategy
from ._base import SelfType, _Config


@dataclass(eq=False)
class TemplateSetting(_Config, ABC):
    base_file_path: str = "./"
    config_path: str = field(default_factory=str)
    config_path_format: str = field(default_factory=str)

    def __post_init__(self) -> None:
        if not self.config_path_format:
            self.config_path_format = self._default_config_path_format

    def _compare(self, other: "TemplateSetting") -> bool:
        return (
            self.base_file_path == other.base_file_path
            and self.config_path == other.config_path
            and self.config_path_format == other.config_path_format
        )

    def serialize(self, data: Optional["TemplateSetting"] = None) -> Optional[Dict[str, Any]]:
        base_file_path: str = self._get_prop(data, prop="base_file_path")
        config_path: str = self._get_prop(data, prop="config_path")
        config_path_format: str = self._get_prop(data, prop="config_path_format")
        return {
            "base_file_path": base_file_path,
            "config_path": config_path,
            "config_path_format": config_path_format,
        }

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["TemplateSetting"]:
        self.base_file_path = data.get("base_file_path", "./")
        self.config_path = data.get("config_path", "")
        self.config_path_format = data.get("config_path_format", self._default_config_path_format)
        return self

    @property
    @abstractmethod
    def _default_config_path_format(self) -> str:
        pass


class TemplateAPI(TemplateSetting):
    @property
    def _default_config_path_format(self) -> str:
        return "{{ api.tag }}/{{ api.__name__ }}.yaml"


class TemplateRequest(TemplateSetting):
    @property
    def _default_config_path_format(self) -> str:
        return "{{ api.tag }}/{{ api.__name__ }}-request.yaml"


class TemplateResponse(TemplateSetting):
    @property
    def _default_config_path_format(self) -> str:
        return "{{ api.tag }}/{{ api.__name__ }}-response.yaml"


@dataclass(eq=False)
class TemplateValues(_Config):
    api: TemplateAPI = TemplateAPI()
    request: TemplateRequest = TemplateRequest()
    response: TemplateResponse = TemplateResponse()

    def _compare(self, other: "TemplateValues") -> bool:
        return self.api == other.api and self.request == other.request and self.response == other.response

    def serialize(self, data: Optional["TemplateValues"] = None) -> Optional[Dict[str, Any]]:
        api = self.api or self._get_prop(data, prop="api")
        request = self.request or self._get_prop(data, prop="request")
        response = self.response or self._get_prop(data, prop="response")
        if not (api and request and response):
            # TODO: Should raise exception?
            return None
        return {"api": api.serialize(), "request": request.serialize(), "response": response.serialize()}

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["TemplateValues"]:
        self.api = TemplateAPI().deserialize(data.get("api", {}))
        self.request = TemplateRequest().deserialize(data.get("request", {}))
        self.response = TemplateResponse().deserialize(data.get("response", {}))
        return self


@dataclass(eq=False)
class TemplateApply(_Config):
    scan_strategy: Optional[TemplateApplyScanStrategy] = None
    api: List[Union[str, Dict[str, List[str]]]] = field(default_factory=list)

    def _compare(self, other: "TemplateApply") -> bool:
        return self.scan_strategy is other.scan_strategy and self.api == other.api

    def serialize(self, data: Optional["TemplateApply"] = None) -> Optional[Dict[str, Any]]:
        scan_strategy: TemplateApplyScanStrategy = self.scan_strategy or TemplateApplyScanStrategy.to_enum(
            self._get_prop(data, prop="scan_strategy")
        )
        if not scan_strategy:
            raise ValueError("Necessary argument *scan_strategy* is missing.")
        if not isinstance(scan_strategy, TemplateApplyScanStrategy):
            raise TypeError(
                "Argument *scan_strategy* data type is invalid. It only accepts *TemplateApplyScanStrategy* type value."
            )

        api: str = self._get_prop(data, prop="api")
        return {
            "scan_strategy": scan_strategy.value,
            "api": api,
        }

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["TemplateApply"]:
        self.scan_strategy = TemplateApplyScanStrategy.to_enum(data.get("scan_strategy", None))
        if not self.scan_strategy:
            raise ValueError("Schema key *scan_strategy* cannot be empty.")
        self.api = data.get("api")  # type: ignore[assignment]
        return self


@dataclass(eq=False)
class TemplateConfig(_Config):
    """The data model which could be set details attribute by section *template*."""

    activate: bool = False
    values: TemplateValues = TemplateValues()
    apply: TemplateApply = TemplateApply(scan_strategy=TemplateApplyScanStrategy.FILE_NAME_FIRST)

    def _compare(self, other: "TemplateConfig") -> bool:
        return self.activate == other.activate and self.values == other.values and self.apply == other.apply

    def serialize(self, data: Optional["TemplateConfig"] = None) -> Optional[Dict[str, Any]]:
        activate: bool = self.activate or self._get_prop(data, prop="activate")
        values: TemplateValues = self.values or self._get_prop(data, prop="values")
        apply: TemplateApply = self.apply or self._get_prop(data, prop="apply")
        if not (values and apply and activate is not None):
            # TODO: Should it ranse an exception outside?
            return None
        return {
            "activate": activate,
            "values": values.serialize(),
            "apply": apply.serialize(),
        }

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["TemplateConfig"]:
        self.activate = data.get("activate", False)
        self.values = TemplateValues().deserialize(data.get("values", {}))
        self.apply = TemplateApply().deserialize(data.get("apply", {}))
        return self


class TemplateConfigLoadable(metaclass=ABCMeta):
    """The data model which could load template configuration."""

    _config_file_name: str = "api.yaml"
    _configuration: _BaseFileOperation = YAML()

    @property
    def config_file_name(self) -> str:
        return self._config_file_name

    @config_file_name.setter
    def config_file_name(self, n: str) -> None:
        self._config_file_name = n

    def _load_templatable_config(self) -> None:
        # Run dividing feature process
        # 1. Use the templatable values set target file paths and list all of them
        #       (hint: glob.glob, os.path.isdir, os.path.isfile).
        # 2. Read the file and deserialize its content as data model.
        # 3. Set the data model at current object's property.
        # 4. Run step #1 to step #3 again and again until finish reading all files.
        # 5. Extract the core logic as template method to object *TemplatableConfig*.

        # # Has tag or doesn't have tag
        # apply_apis = self.template.apply.api
        # if isinstance(apply_apis[0], str):
        #     pass
        # elif isinstance(apply_apis[0], dict):
        #     pass
        # else:
        #     pass

        # TODO: Modify to use property *config_path* or *config_path_format*
        customize_config_file_format = "**"
        config_file_format = f"[!_**]{customize_config_file_format}"
        # all_paths = glob.glob(f"{self._base_path}**/[!_*]*.yaml", recursive=True)
        all_paths = glob.glob(f"{self._config_base_path}{config_file_format}")
        all_paths.remove(f"{self._config_base_path}{self.config_file_name}")
        for path in all_paths:
            if os.path.isdir(path):
                # Has tag as directory
                # TODO: Modify to use property *config_path* or *config_path_format*
                for path_with_tag in glob.glob(f"{path}/{self._config_file_format}.yaml"):
                    # In the tag directory, it's config
                    self._deserialize_and_set_template_config(path_with_tag)
            else:
                assert os.path.isfile(path) is True
                if fnmatch.fnmatch(path, f"{self._config_file_format}.yaml"):
                    # Doesn't have tag, it's config
                    self._deserialize_and_set_template_config(path)

    @property
    @abstractmethod
    def _config_base_path(self) -> str:
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
        return self._deserialize_as_template_config.deserialize(yaml_config)

    @property
    @abstractmethod
    def _deserialize_as_template_config(self) -> _Config:
        pass

    @abstractmethod
    def _set_template_config(self, config: _Config, **kwargs) -> None:
        pass


@dataclass(eq=False)
class _TemplatableConfig(_Config, ABC):
    apply_template_props: bool = True

    # The settings which could be set by section *template* or override the values
    base_file_path: str = "./"
    config_path: str = field(default_factory=str)
    config_path_format: str = field(default_factory=str)

    _current_template: TemplateConfig = TemplateConfig()
    _has_apply_template_props_in_config: bool = False

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
                setattr(self, key, value)

        _update_template_prop("apply_template_props")
        _update_template_prop("base_file_path")
        _update_template_prop("config_path")
        _update_template_prop("config_path_format")
        return self
