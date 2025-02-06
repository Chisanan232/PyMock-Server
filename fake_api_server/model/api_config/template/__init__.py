from abc import ABCMeta
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from fake_api_server.model.api_config._base import _Checkable, _Config

from .common import TemplateCommonConfig
from .file import TemplateFileConfig


@dataclass(eq=False)
class TemplateConfig(_Config, _Checkable):

    activate: bool = field(default=False)
    file: TemplateFileConfig = field(default_factory=TemplateFileConfig)
    common_config: Optional[TemplateCommonConfig] = None

    def _compare(self, other: "TemplateConfig") -> bool:
        return self.activate == other.activate and self.file == other.file and self.common_config == other.common_config

    @property
    def key(self) -> str:
        return "template"

    def serialize(self, data: Optional["TemplateConfig"] = None) -> Optional[Dict[str, Any]]:
        activate: bool = self.activate or self._get_prop(data, prop="activate")
        template_file_config: TemplateFileConfig = self.file or self._get_prop(data, prop="file")
        template_common_config: Optional[TemplateCommonConfig] = self.common_config or self._get_prop(
            data, prop="common_config"
        )
        if not (activate is not None and template_file_config and template_common_config):
            return None
        serialized_data = {
            "activate": activate,
            "file": template_file_config.serialize(),
        }
        if template_common_config:
            serialized_data["common_config"] = template_common_config.serialize()
        return serialized_data

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["TemplateConfig"]:
        self.activate = data.get("activate", False)

        template_file_config = TemplateFileConfig()
        template_file_config.absolute_model_key = self.key
        self.file = template_file_config.deserialize(data.get("file", {}))

        template_common_config_data = data.get("common_config", {})
        if template_common_config_data:
            template_common_config = TemplateCommonConfig()
            template_common_config.absolute_model_key = self.key
            self.common_config = template_common_config.deserialize(template_common_config_data)
        return self

    def is_work(self) -> bool:
        if not self.props_should_not_be_none(
            under_check={
                f"{self.absolute_model_key}.activate": self.activate,
            },
            accept_empty=False,
        ):
            return False

        self.file.stop_if_fail = self.stop_if_fail
        if self.common_config:
            self.common_config.stop_if_fail = self.stop_if_fail
            if not self.common_config.is_work():
                return False
        return isinstance(self.activate, bool) and self.file.is_work()


@dataclass(eq=False)
class _BaseTemplateAccessable(metaclass=ABCMeta):
    _current_template: TemplateConfig = field(default_factory=TemplateConfig, repr=False)
