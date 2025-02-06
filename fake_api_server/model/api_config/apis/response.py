import json
import logging
import pathlib
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from fake_api_server.model.api_config._base import _Checkable, _Config
from fake_api_server.model.api_config.template._base_wrapper import (
    _DividableOnlyTemplatableConfig,
)
from fake_api_server.model.api_config.template.file import TemplateConfigPathResponse

from ._property import BaseProperty
from .response_strategy import ResponseStrategy

logger = logging.getLogger(__name__)


@dataclass(eq=False)
class ResponseProperty(BaseProperty):
    is_empty: Optional[bool] = None

    def _compare(self, other: "ResponseProperty") -> bool:  # type: ignore[override]
        return super()._compare(other) and self.is_empty == other.is_empty

    @property
    def key(self) -> str:
        return "properties.<property item>"

    @_Config._clean_empty_value
    def serialize(self, data: Optional["ResponseProperty"] = None) -> Optional[Dict[str, Any]]:
        serialized_data = super().serialize(data)
        if serialized_data:
            serialized_data["is_empty"] = self._get_prop(data, prop="is_empty")
        return serialized_data

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["ResponseProperty"]:
        super().deserialize(data)
        self.is_empty = data.get("is_empty", None)
        return self

    def is_work(self) -> bool:
        response_props_chk = super().is_work()
        if response_props_chk is False:
            return False

        if not self.condition_should_be_true(
            config_key=f"{self.absolute_model_key}.is_empty",
            condition=(
                self.value_type in ["list", "tuple", "set", "dict"] and self.is_empty and len(self.items or []) != 0  # type: ignore[arg-type]
            ),
            err_msg="It's meaningless if it's collection type data and it's empty, but it has property *items* setting.",
        ):
            return False
        if not self.condition_should_be_true(
            config_key=f"{self.absolute_model_key}.is_empty",
            condition=(self.value_type not in ["list", "tuple", "set", "dict"] and self.is_empty is not None),
            err_msg="It's meaningless if it isn't collection type data, but it has property *is_empty* setting.",
        ):
            return False

        return True

    def _prop_items_is_work(self) -> bool:
        if not self.condition_should_be_true(
            config_key=f"{self.absolute_model_key}.items",
            condition=(
                self.value_type not in ["list", "tuple", "set", "dict"]
                and not self.is_empty
                and len(self.items or []) != 0
            )
            or (
                self.value_type in ["list", "tuple", "set", "dict"]
                and self.is_empty is not True
                and not (self.items or [])
            ),
            err_msg="It's meaningless if it has item setting but its data type is not collection. The items value setting sould not be None if the data type is one of collection types.",
        ):
            return False
        return True


@dataclass(eq=False)
class HTTPResponse(_DividableOnlyTemplatableConfig, _Checkable):
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
        if ResponseStrategy(self.strategy) is ResponseStrategy.STRING:
            return templatable_config and self.value == other.value
        elif ResponseStrategy(self.strategy) is ResponseStrategy.FILE:
            return templatable_config and self.path == other.path
        elif ResponseStrategy(self.strategy) is ResponseStrategy.OBJECT:
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
            self.strategy = ResponseStrategy(self.strategy)

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
        strategy: ResponseStrategy = self.strategy or ResponseStrategy(self._get_prop(data, prop="strategy"))
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
            response_property._current_template = self._current_template
            return response_property.deserialize(prop)

        super().deserialize(data)

        self.strategy = ResponseStrategy(data.get("strategy", None))
        if self.strategy is ResponseStrategy.STRING:
            self.value = data.get("value", None)
        elif self.strategy is ResponseStrategy.FILE:
            self.path = data.get("path", None)
        elif self.strategy is ResponseStrategy.OBJECT:
            properties = data.get("properties", None)
            if properties is not None:
                properties = [_deserialize_response_property(prop) for prop in (properties or [])]
            self.properties = properties
        else:
            raise NotImplementedError
        return self

    @property
    def _template_setting(self) -> TemplateConfigPathResponse:
        return self._current_template.file.config_path_values.response

    def is_work(self) -> bool:
        assert self.strategy is not None
        if ResponseStrategy(self.strategy) is ResponseStrategy.STRING:
            return self.should_not_be_none(
                config_key=f"{self.absolute_model_key}.value",
                config_value=self.value,
                valid_callback=self._chk_response_value_validity,
            )
        elif ResponseStrategy(self.strategy) is ResponseStrategy.FILE:
            return self.should_not_be_none(
                config_key=f"{self.absolute_model_key}.path",
                config_value=self.path,
                accept_empty=False,
                valid_callback=self._chk_response_value_validity,
            )
        elif ResponseStrategy(self.strategy) is ResponseStrategy.OBJECT:
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
                    logger.error(
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
                logger.error("The file which is the response content doesn't exist.")
                self._config_is_wrong = True
                if self._stop_if_fail:
                    self._exit_program(1)
                return False
            return True
        elif response_strategy == "properties":
            assert isinstance(
                config_value, list
            ), "If HTTP response strategy is *object*, the data type of response value must be *list*."

            def _resp_prop_is_work(p: ResponseProperty) -> bool:
                p.stop_if_fail = self.stop_if_fail
                return p.is_work()

            is_work_props = list(filter(lambda v: _resp_prop_is_work(v), config_value))
            if len(is_work_props) != len(config_value):
                return False
            return True
