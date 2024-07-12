from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from .._base import _Checkable, _Config
from .file import TemplateFileConfig


@dataclass(eq=False)
class TemplateConfig(_Config, _Checkable):

    activate: bool = field(default=False)
    file: TemplateFileConfig = field(default_factory=TemplateFileConfig)

    def _compare(self, other: "TemplateConfig") -> bool:
        return self.activate == other.activate and self.file == other.file

    @property
    def key(self) -> str:
        return "template"

    def serialize(self, data: Optional["TemplateConfig"] = None) -> Optional[Dict[str, Any]]:
        activate: bool = self.activate or self._get_prop(data, prop="activate")
        template_file_config: TemplateFileConfig = self.file or self._get_prop(data, prop="file")
        if not (template_file_config and activate is not None):
            return None
        serialized_data = {
            "activate": activate,
            "file": template_file_config.serialize(),
        }
        return serialized_data

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["TemplateConfig"]:
        self.activate = data.get("activate", False)

        template_file_config = TemplateFileConfig()
        template_file_config.absolute_model_key = self.key
        self.file = template_file_config.deserialize(data.get("file", {}))
        return self

    def is_work(self) -> bool:
        if not self.props_should_not_be_none(
            under_check={
                f"{self.absolute_model_key}.activate": self.activate,
            },
            accept_empty=False,
        ):
            return False

        if not self.props_should_not_be_none(
            under_check={
                f"{self.absolute_model_key}.file": self.file,
            },
        ):
            return False

        self.file.stop_if_fail = self.stop_if_fail
        return isinstance(self.activate, bool) and self.file.is_work()
