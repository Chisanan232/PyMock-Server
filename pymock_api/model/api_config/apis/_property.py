from abc import ABC
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .._base import _Checkable, _Config
from ..item import IteratorItem


@dataclass(eq=False)
class BaseProperty(_Config, _Checkable, ABC):
    name: str = field(default_factory=str)
    required: Optional[bool] = None
    value_type: Optional[str] = None  # A type value as string
    value_format: Optional[str] = None
    items: Optional[List[IteratorItem]] = None

    def _compare(self, other: "BaseProperty") -> bool:
        return (
            self.name == other.name
            and self.required == other.required
            and self.value_type == other.value_type
            and self.value_format == other.value_format
            and self.items == other.items
        )

    def __post_init__(self) -> None:
        if self.items is not None:
            self._convert_items()

    def _convert_items(self):
        def _deserialize_item(i: dict) -> IteratorItem:
            item = IteratorItem(
                name=i.get("name", ""), value_type=i.get("type", None), required=i.get("required", True)
            )
            item.absolute_model_key = self.key
            return item

        if False in list(map(lambda i: isinstance(i, (dict, IteratorItem)), self.items)):
            raise TypeError("The data type of key *items* must be dict or IteratorItem.")
        self.items = [_deserialize_item(i) if isinstance(i, dict) else i for i in self.items]

    def serialize(self, data: Optional["BaseProperty"] = None) -> Optional[Dict[str, Any]]:
        name: str = self._get_prop(data, prop="name")
        required: bool = self._get_prop(data, prop="required")
        value_type: type = self._get_prop(data, prop="value_type")
        value_format: str = self._get_prop(data, prop="value_format")
        if not (name and value_type) or (required is None):
            return None
        serialized_data = {
            "name": name,
            "required": required,
            "type": value_type,
            "format": value_format,
        }
        if self.items:
            serialized_data["items"] = [item.serialize() for item in self.items]
        return serialized_data

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["BaseProperty"]:
        self.name = data.get("name", None)
        self.required = data.get("required", None)
        self.value_type = data.get("type", None)
        self.value_format = data.get("format", None)
        items = [IteratorItem().deserialize(item) for item in (data.get("items", []) or [])]
        self.items = items if items else None
        return self

    def is_work(self) -> bool:
        # Check the data type first
        # 1. Check the data type (value_type)
        # 2. Use the data type check others,
        #   2-1.Not iterable object -> name, required
        #   2-2.Iterable object -> name, required, items
        if not self.props_should_not_be_none(
            under_check={
                f"{self.absolute_model_key}.name": self.name,
                f"{self.absolute_model_key}.value_type": self.value_type,
            },
            accept_empty=False,
        ):
            return False

        if not self.should_not_be_none(
            config_key=f"{self.absolute_model_key}.required",
            config_value=self.required,
            accept_empty=False,
        ):
            return False

        if not self.condition_should_be_true(
            config_key=f"{self.absolute_model_key}.items",
            condition=(self.value_type not in ["list", "tuple", "set", "dict"] and len(self.items or []) != 0)
            or (self.value_type in ["list", "tuple", "set", "dict"] and not (self.items or [])),
            err_msg="It's meaningless if it has item setting but its data type is not collection. The items value setting sould not be None if the data type is one of collection types.",
        ):
            return False
        if self.items:

            def _i_is_work(i: IteratorItem) -> bool:
                i.stop_if_fail = self.stop_if_fail
                return i.is_work()

            is_work_props = list(filter(lambda i: _i_is_work(i), self.items))
            if len(is_work_props) != len(self.items):
                return False
        return True
