from abc import ABC, ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from ...model.enums import TemplateApplyScanStrategy
from ._base import _Config


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


class TemplateConfigLoadable(metaclass=ABCMeta):
    @abstractmethod
    def _load_templatable_config(self) -> None:
        pass

    @abstractmethod
    def _deserialize_template_yaml_config(self, yaml_config: Dict) -> _Config:
        pass

    @abstractmethod
    def _set_config_in_data_model(self, config: _Config, **kwargs) -> None:
        pass


@dataclass(eq=False)
class TemplateConfig(_Config):
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
