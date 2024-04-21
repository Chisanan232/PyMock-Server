from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ._base import _Checkable, _Config


@dataclass(eq=False)
class IteratorItem(_Config, _Checkable):
    name: str = field(default_factory=str)
    required: Optional[bool] = None
    value_type: Optional[str] = None  # A type value as string
    items: Optional[List["IteratorItem"]] = None

    _absolute_key: str = field(init=False, repr=False)

    def _compare(self, other: "IteratorItem") -> bool:
        return (
            self.name == other.name
            and self.required == other.required
            and self.value_type == other.value_type
            and self.items == other.items
        )

    def __post_init__(self) -> None:
        if self.items is not None:
            self._convert_items()

    def _convert_items(self):
        def _deserialize_item(i: dict) -> IteratorItem:
            item = IteratorItem(
                name=i.get("name", ""),
                value_type=i.get("type", None),
                required=i.get("required", True),
                items=i.get("items", None),
            )
            item.absolute_model_key = self.key
            return item

        if False in list(map(lambda i: isinstance(i, (dict, IteratorItem)), self.items)):
            raise TypeError("The data type of key *items* must be dict or IteratorItem.")
        self.items = [_deserialize_item(i) if isinstance(i, dict) else i for i in self.items]

    @property
    def key(self) -> str:
        return "<item>"

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
        if self.items:
            serialized_data["items"] = [item.serialize() for item in self.items]
        return serialized_data

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["IteratorItem"]:
        self.name = data.get("name", None)
        self.required = data.get("required", None)
        self.value_type = data.get("type", None)
        items = [IteratorItem().deserialize(item) for item in (data.get("items", []) or [])]
        self.items = items if items else None
        return self

    def is_work(self) -> bool:
        if not self.props_should_not_be_none(
            under_check={
                f"{self.absolute_model_key}.required": self.required,
            },
            accept_empty=False,
        ):
            return False
        if not self.props_should_not_be_none(
            under_check={
                f"{self.absolute_model_key}.value_type": self.value_type,
            },
            accept_empty=False,
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
