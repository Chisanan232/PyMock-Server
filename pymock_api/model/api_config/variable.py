from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..enums import ValueFormat
from ._base import _Checkable, _Config


@dataclass(eq=False)
class Variable(_Config, _Checkable):
    name: str = field(default_factory=str)
    value_format: Optional[ValueFormat] = None
    digit: Optional[str] = None
    range: Optional[str] = None
    enum: Optional[List[str]] = None

    _absolute_key: str = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.value_format is not None:
            self._convert_value_format()

    def _convert_value_format(self) -> None:
        if isinstance(self.value_format, str):
            self.value_format = ValueFormat.to_enum(self.value_format)

    def _compare(self, other: "Variable") -> bool:
        return (
            self.name == other.name
            and self.value_format == other.value_format
            and self.digit == other.digit
            and self.range == other.range
            and self.enum == other.enum
        )

    @property
    def key(self) -> str:
        return "<variable>"

    @_Config._clean_empty_value
    def serialize(self, data: Optional["Variable"] = None) -> Optional[Dict[str, Any]]:
        name: str = self._get_prop(data, prop="name")

        value_format: ValueFormat = self.value_format or ValueFormat.to_enum(self._get_prop(data, prop="value_format"))

        digit: str = self._get_prop(data, prop="digit")
        range_value: str = self._get_prop(data, prop="range")
        enum: str = self._get_prop(data, prop="enum")
        if not name or not value_format:
            return None
        serialized_data = {
            "name": name,
            "value_format": value_format.value,
            "digit": digit,
            "range": range_value,
            "enum": enum,
        }
        return serialized_data

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["Variable"]:
        self.name = data.get("name", None)

        self.value_format = ValueFormat.to_enum(data.get("value_format", None))
        if not self.value_format:
            raise ValueError("Schema key *value_format* cannot be empty.")

        if self.value_format == ValueFormat.Enum:
            self.enum = data.get("enum", None)
        else:
            self.digit = data.get("digit", None)

        self.range = data.get("range", None)
        return self

    def is_work(self) -> bool:
        if not self.props_should_not_be_none(
            under_check={
                f"{self.absolute_model_key}.name": self.name,
            },
            accept_empty=False,
        ):
            return False
        assert self.value_format
        if self.value_format is ValueFormat.Enum and not self.props_should_not_be_none(
            under_check={
                f"{self.absolute_model_key}.enum": self.enum,
            },
            accept_empty=False,
        ):
            return False

        return True
