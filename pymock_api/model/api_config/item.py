from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from ._base import _Config


@dataclass(eq=False)
class IteratorItem(_Config):
    name: str = field(default_factory=str)
    required: Optional[bool] = None
    value_type: Optional[str] = None  # A type value as string

    def _compare(self, other: "IteratorItem") -> bool:
        return self.name == other.name and self.required == other.required and self.value_type == other.value_type

    def serialize(self, data: Optional["IteratorItem"] = None) -> Optional[Dict[str, Any]]:
        name: str = self._get_prop(data, prop="name")
        required: bool = self._get_prop(data, prop="required")
        value_type: type = self._get_prop(data, prop="value_type")
        if not value_type or (required is None):
            return None
        serialized_data = {
            "required": required,
            "type": value_type,
        }
        if name:
            serialized_data["name"] = name
        return serialized_data

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["IteratorItem"]:
        self.name = data.get("name", None)
        self.required = data.get("required", None)
        self.value_type = data.get("type", None)
        return self

    def is_work(self) -> bool:
        if not self.name or self.required is None or not self.value_type:
            return False
        return True
