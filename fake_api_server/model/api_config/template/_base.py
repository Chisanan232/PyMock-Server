import os
import pathlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Type

from fake_api_server._utils import YAML
from fake_api_server._utils.file.operation import _BaseFileOperation
from fake_api_server.model.api_config._base import SelfType, _Config

from . import _BaseTemplateAccessable
from .file import TemplateConfigPathSetting


@dataclass(eq=False)
class _BaseTemplatableConfig(_Config, _BaseTemplateAccessable, ABC):
    apply_template_props: bool = field(default=True)

    # The settings which could be set by section *template* or override the values
    base_file_path: str = field(default_factory=str)
    config_path: str = field(default_factory=str)
    config_file_tail: str = field(default_factory=str)
    config_path_format: str = field(default_factory=str)

    _default_base_file_path: str = field(default="./")
    _absolute_key: str = field(init=False, repr=False)

    # Attributes for inner usage
    _has_apply_template_props_in_config: bool = field(default=False)

    # Component for inner usage
    _configuration: _BaseFileOperation = field(default_factory=YAML)

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
            self.base_file_path
            or self._current_template.file.config_path_values.base_file_path
            or self._default_base_file_path
        )
        dividing_config_path = str(pathlib.Path(base_file_path, self.config_path))
        if dividing_config_path and os.path.exists(dividing_config_path) and os.path.isfile(dividing_config_path):
            dividing_data = self._configuration.read(dividing_config_path)
            data.update(**dividing_data)
        return data

    @property
    @abstractmethod
    def _template_setting(self) -> TemplateConfigPathSetting:
        pass

    def _deserialize_as(
        self,
        data_model: Type["_BaseTemplatableConfig"],
        with_data: dict = {},
    ) -> Optional["_BaseTemplatableConfig"]:
        with_data = {} if with_data is None else with_data
        config = data_model(_current_template=self._current_template)
        config.base_file_path = self.base_file_path
        config.config_path = self.config_path.replace(self.config_file_tail, config.config_file_tail)
        config.absolute_model_key = self.key
        return config.deserialize(data=with_data)
