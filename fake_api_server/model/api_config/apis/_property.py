from abc import ABC
from dataclasses import dataclass, field
from pydoc import locate
from typing import Any, Dict, List, Optional, Type

from fake_api_server.model.api_config._base import _Config, _HasItemsPropConfig
from fake_api_server.model.api_config.format import _HasFormatPropConfig
from fake_api_server.model.api_config.item import IteratorItem
from fake_api_server.model.api_config.template import _BaseTemplateAccessable


@dataclass(eq=False)
class BaseProperty(_HasItemsPropConfig, _HasFormatPropConfig, _BaseTemplateAccessable, ABC):
    name: str = field(default_factory=str)
    required: Optional[bool] = None
    value_type: Optional[str] = None  # A type value as string
    items: Optional[List[IteratorItem]] = None  # type: ignore[assignment]

    def _compare(self, other: "BaseProperty") -> bool:  # type: ignore[override]
        return (
            self.name == other.name
            and self.required == other.required
            and self.value_type == other.value_type
            # Compare property *format* and *items*
            and super()._compare(other)
        )

    def _find_same_key_item_to_compare(self, self_item: "BaseProperty", other_item: "BaseProperty") -> bool:  # type: ignore[override]
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

    @_Config._clean_empty_value
    def serialize(self, data: Optional["BaseProperty"] = None) -> Optional[Dict[str, Any]]:
        name: str = self._get_prop(data, prop="name")
        required: bool = self._get_prop(data, prop="required")
        value_type: type = self._get_prop(data, prop="value_type")
        if not (name and value_type) or (required is None):
            return None
        serialized_data = {
            "name": name,
            "required": required,
            "type": value_type,
        }
        has_format_and_items_data_model = super().serialize(data)
        if has_format_and_items_data_model:
            serialized_data.update(has_format_and_items_data_model)
        return serialized_data

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["BaseProperty"]:
        self.name = data.get("name", None)
        self.required = data.get("required", None)
        self.value_type = data.get("type", None)

        # deserialize 'format' and 'items'
        super().deserialize(data)
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

        if not self._prop_items_is_work():
            return False

        assert self.value_type
        if locate(self.value_type) in [list, dict] and not self.props_should_be_none(
            under_check={
                f"{self.absolute_model_key}.format": self.value_format,
            },
        ):
            return False
        # check 'format' and 'items'
        format_and_items_chk = super().is_work()
        if format_and_items_chk is False:
            return format_and_items_chk
        return True

    def _prop_items_is_work(self) -> bool:
        if not self.condition_should_be_true(
            config_key=f"{self.absolute_model_key}.items",
            condition=(self.value_type not in ["list", "tuple", "set", "dict"] and len(self.items or []) != 0)
            or (self.value_type in ["list", "tuple", "set", "dict"] and not (self.items or [])),
            err_msg="It's meaningless if it has item setting but its data type is not collection. The items value setting sould not be None if the data type is one of collection types.",
        ):
            return False
        return True
