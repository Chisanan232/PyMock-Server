import json
import pathlib
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ...enums import ResponseStrategy
from .._base import _Checkable, _Config
from ..item import IteratorItem
from ..template import TemplateResponse, _TemplatableConfig


@dataclass(eq=False)
class ResponseProperty(_Config, _Checkable):
    name: str = field(default_factory=str)
    required: Optional[bool] = None
    value_type: Optional[str] = None  # A type value as string
    value_format: Optional[str] = None
    items: Optional[List[IteratorItem]] = None

    _absolute_key: str = field(init=False, repr=False)

    def _compare(self, other: "ResponseProperty") -> bool:
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

    @property
    def key(self) -> str:
        return "properties.<property item>"

    def serialize(self, data: Optional["ResponseProperty"] = None) -> Optional[Dict[str, Any]]:
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
    def deserialize(self, data: Dict[str, Any]) -> Optional["ResponseProperty"]:
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

        return True


@dataclass(eq=False)
class HTTPResponse(_TemplatableConfig, _Checkable):
    """*The **http.response** section in **mocked_apis.<api>***"""

    strategy: Optional[ResponseStrategy] = None
    """
    Strategy:
    * string: Return the value as string data directly.
    * file: Return the data which be recorded in the file path as response.
    * object: Return the response which be composed as object by some properties.
    """

    config_file_tail: str = "-response"

    # Strategy: string
    value: str = field(default_factory=str)

    # Strategy: file
    path: str = field(default_factory=str)

    # Strategy: object
    properties: List[ResponseProperty] = field(default_factory=list)

    def _compare(self, other: "HTTPResponse") -> bool:
        templatable_config = super()._compare(other)
        if not self.strategy:
            raise ValueError("Miss necessary argument *strategy*.")
        if self.strategy is not other.strategy:
            raise TypeError("Different HTTP response strategy cannot compare with each other.")
        if ResponseStrategy.to_enum(self.strategy) is ResponseStrategy.STRING:
            return templatable_config and self.value == other.value
        elif ResponseStrategy.to_enum(self.strategy) is ResponseStrategy.FILE:
            return templatable_config and self.path == other.path
        elif ResponseStrategy.to_enum(self.strategy) is ResponseStrategy.OBJECT:
            return templatable_config and self.properties == other.properties
        else:
            raise NotImplementedError

    def __post_init__(self) -> None:
        if self.strategy is not None:
            self._convert_strategy()
        if self.properties is not None:
            self._convert_properties()

    def _convert_strategy(self) -> None:
        if isinstance(self.strategy, str):
            self.strategy = ResponseStrategy.to_enum(self.strategy)

    def _convert_properties(self):
        if False in list(map(lambda i: isinstance(i, (dict, ResponseProperty)), self.properties)):
            raise TypeError("The data type of key *properties* must be dict or ResponseProperty.")
        self.properties = [ResponseProperty().deserialize(i) if isinstance(i, dict) else i for i in self.properties]

    @property
    def key(self) -> str:
        return "response"

    def serialize(self, data: Optional["HTTPResponse"] = None) -> Optional[Dict[str, Any]]:
        serialized_data = super().serialize(data)
        assert serialized_data is not None
        strategy: ResponseStrategy = self.strategy or ResponseStrategy.to_enum(self._get_prop(data, prop="strategy"))
        if not strategy:
            raise ValueError("Necessary argument *strategy* is missing.")
        if not isinstance(strategy, ResponseStrategy):
            raise TypeError("Argument *strategy* data type is invalid. It only accepts *ResponseStrategy* type value.")
        if strategy is ResponseStrategy.STRING:
            value: str = self._get_prop(data, prop="value")
            serialized_data.update(
                {
                    "strategy": strategy.value,
                    "value": value,
                }
            )
            return serialized_data
        elif strategy is ResponseStrategy.FILE:
            path: str = self._get_prop(data, prop="path")
            serialized_data.update(
                {
                    "strategy": strategy.value,
                    "path": path,
                }
            )
            return serialized_data
        elif strategy is ResponseStrategy.OBJECT:
            all_properties = (data or self).properties if (data and data.properties) or self.properties else None
            properties = [prop.serialize() for prop in (all_properties or [])]
            serialized_data.update(
                {
                    "strategy": strategy.value,
                    "properties": properties,
                }
            )
            return serialized_data
        else:
            raise NotImplementedError

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["HTTPResponse"]:
        """Convert data to **HTTPResponse** type object.

        The data structure should be like following:

        * Example data:
        .. code-block:: python

            {
                'response': {
                    'value': 'This is Google home API.'
                }
            }

        Args:
            data (Dict[str, Any]): Target data to convert.

        Returns:
            A **HTTPResponse** type object.

        """

        def _deserialize_response_property(prop: dict) -> ResponseProperty:
            response_property = ResponseProperty()
            response_property.absolute_model_key = self.key
            return response_property.deserialize(prop)

        super().deserialize(data)

        self.strategy = ResponseStrategy.to_enum(data.get("strategy", None))
        if not self.strategy:
            raise ValueError("Schema key *strategy* cannot be empty.")
        if self.strategy is ResponseStrategy.STRING:
            self.value = data.get("value", None)
        elif self.strategy is ResponseStrategy.FILE:
            self.path = data.get("path", None)
        elif self.strategy is ResponseStrategy.OBJECT:
            properties = [_deserialize_response_property(prop) for prop in (data.get("properties", []) or [])]
            self.properties = properties if properties else None  # type: ignore[assignment]
        else:
            raise NotImplementedError
        return self

    @property
    def _template_setting(self) -> TemplateResponse:
        return self._current_template.values.response

    def is_work(self) -> bool:
        assert self.strategy is not None
        if ResponseStrategy.to_enum(self.strategy) is ResponseStrategy.STRING:
            return self.should_not_be_none(
                config_key=f"{self.absolute_model_key}.value",
                config_value=self.value,
                valid_callback=self._chk_response_value_validity,
            )
        elif ResponseStrategy.to_enum(self.strategy) is ResponseStrategy.FILE:
            return self.should_not_be_none(
                config_key=f"{self.absolute_model_key}.path",
                config_value=self.path,
                accept_empty=False,
                valid_callback=self._chk_response_value_validity,
            )
        elif ResponseStrategy.to_enum(self.strategy) is ResponseStrategy.OBJECT:
            if not self.should_not_be_none(
                config_key=f"{self.absolute_model_key}.properties",
                config_value=self.properties,
                accept_empty=False,
                valid_callback=self._chk_response_value_validity,
            ):
                return False
        else:
            raise NotImplementedError
        return True

    def _chk_response_value_validity(self, config_key: str, config_value: Any) -> bool:  # type: ignore[return]
        response_strategy = config_key.split(".")[-1]
        assert response_strategy in [
            "value",
            "path",
            "properties",
        ], f"It has unexpected schema usage '{config_key}' in configuration."
        if response_strategy == "value":
            assert isinstance(
                config_value, str
            ), "If HTTP response strategy is *string*, the data type of response value must be *str*."
            if re.search(r"\{.{0,99999999}}", config_value):
                try:
                    json.loads(config_value)
                except:
                    print(
                        "If HTTP response strategy is *string* and its value seems like JSON format, its format is not a valid JSON format."
                    )
                    self._config_is_wrong = True
                    if self._stop_if_fail:
                        self._exit_program(1)
                    return False
            return True
        elif response_strategy == "path":
            assert isinstance(
                config_value, str
            ), "If HTTP response strategy is *file*, the data type of response value must be *str*."
            if not pathlib.Path(config_value).exists():
                print("The file which is the response content doesn't exist.")
                self._config_is_wrong = True
                if self._stop_if_fail:
                    self._exit_program(1)
                return False
            return True
        elif response_strategy == "properties":
            assert isinstance(
                config_value, list
            ), "If HTTP response strategy is *object*, the data type of response value must be *list*."
            for v in config_value:
                assert isinstance(v, ResponseProperty)
                v.stop_if_fail = self.stop_if_fail
                return v.is_work()
