from dataclasses import dataclass, field
from pydoc import locate
from typing import Any, Dict, List, Optional, Type

from ._base import _Config, _HasItemsPropConfig
from .format import _HasFormatPropConfig


@dataclass(eq=False)
class IteratorItem(_HasFormatPropConfig, _HasItemsPropConfig):
    name: str = field(default_factory=str)
    required: Optional[bool] = None
    value_type: Optional[str] = None  # A type value as string
    items: Optional[List["IteratorItem"]] = None  # type: ignore[assignment]

    _absolute_key: str = field(init=False, repr=False)

    def _compare(self, other: "IteratorItem") -> bool:  # type: ignore[override]
        return (
            self.name == other.name
            and self.required == other.required
            and self.value_type == other.value_type
            # Compare property *items*
            and super()._compare(other)
        )

    def _find_same_key_item_to_compare(self, self_item: "IteratorItem", other_item: "IteratorItem") -> bool:  # type: ignore[override]
        return self_item.name == other_item.name

    def _item_type(self) -> Type["IteratorItem"]:
        return IteratorItem

    def _deserialize_empty_item(self) -> "IteratorItem":
        return IteratorItem()

    def _deserialize_item_with_data(self, i: dict) -> "IteratorItem":
        item = IteratorItem(
            name=i.get("name", None),
            value_type=i.get("type", None),
            required=i.get("required", True),
            items=i.get("items", None),
        )
        item.absolute_model_key = self.key
        return item

    @property
    def key(self) -> str:
        return "<item>"

    def serialize(self, data: Optional["IteratorItem"] = None) -> Optional[Dict[str, Any]]:  # type: ignore[override]
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
        # serialize 'items'
        items = super().serialize(data)
        if items:
            serialized_data.update(items)
        return serialized_data

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["IteratorItem"]:
        self.name = data.get("name", None)
        self.required = data.get("required", None)
        self.value_type = data.get("type", None)

        # deserialize 'items'
        super().deserialize(data)
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
        assert self.value_type
        if locate(self.value_type) in [list, dict]:
            if not self.props_should_not_be_none(
                under_check={
                    f"{self.absolute_model_key}.items": self.items,
                },
                accept_empty=False,
            ):
                return False

            if not self.props_should_be_none(
                under_check={
                    f"{self.absolute_model_key}.format": self.value_format,
                },
            ):
                return False

        # check 'items'
        items_chk = super().is_work()
        if items_chk is False:
            return items_chk
        return True
