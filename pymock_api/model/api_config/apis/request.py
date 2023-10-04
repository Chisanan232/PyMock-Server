import glob
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ...._utils.file_opt import YAML, _BaseFileOperation
from .._base import _Config
from ..item import IteratorItem
from ..template import _TemplatableConfig


@dataclass(eq=False)
class APIParameter(_Config):
    name: str = field(default_factory=str)
    required: Optional[bool] = None
    default: Optional[Any] = None
    value_type: Optional[str] = None  # A type value as string
    value_format: Optional[str] = None
    items: Optional[List[IteratorItem]] = None

    def _compare(self, other: "APIParameter") -> bool:
        # TODO: Let it could automatically scan what properties it has and compare all of their value.
        return (
            self.name == other.name
            and self.required == other.required
            and self.default == other.default
            and self.value_type == other.value_type
            and self.value_format == other.value_format
            and self.items == other.items
        )

    def __post_init__(self) -> None:
        if self.items is not None:
            self._convert_items()

    def _convert_items(self):
        if False in list(map(lambda i: isinstance(i, (dict, IteratorItem)), self.items)):
            raise TypeError("The data type of key *items* must be dict or IteratorItem.")
        self.items = [
            IteratorItem(name=i.get("name", ""), value_type=i.get("type", None), required=i.get("required", True))
            if isinstance(i, dict)
            else i
            for i in self.items
        ]

    def serialize(self, data: Optional["APIParameter"] = None) -> Optional[Dict[str, Any]]:
        name: str = self._get_prop(data, prop="name")
        required: bool = self._get_prop(data, prop="required")
        default: str = self._get_prop(data, prop="default")
        value_type: type = self._get_prop(data, prop="value_type")
        value_format: str = self._get_prop(data, prop="value_format")
        if not (name and value_type) or (required is None):
            return None
        serialized_data = {
            "name": name,
            "required": required,
            "default": default,
            "type": value_type,
            "format": value_format,
        }
        if self.items:
            print(f"[DEBUG in api_config.APIParameter.serialize] self.items: {self.items}")
            serialized_data["items"] = [item.serialize() for item in self.items]
        return serialized_data

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["APIParameter"]:
        self.name = data.get("name", None)
        self.required = data.get("required", None)
        self.default = data.get("default", None)
        self.value_type = data.get("type", None)
        self.value_format = data.get("format", None)
        items = [IteratorItem().deserialize(item) for item in data.get("items", [])]
        self.items = items if items else None
        return self


@dataclass(eq=False)
class HTTPRequest(_TemplatableConfig):
    """*The **http.request** section in **mocked_apis.<api>***"""

    method: str = field(default_factory=str)
    parameters: List[APIParameter] = field(default_factory=list)

    _configuration: _BaseFileOperation = YAML()

    def _compare(self, other: "HTTPRequest") -> bool:
        templatable_config = super()._compare(other)
        return templatable_config and self.method == other.method and self.parameters == other.parameters

    def serialize(self, data: Optional["HTTPRequest"] = None) -> Optional[Dict[str, Any]]:
        method: str = self._get_prop(data, prop="method")
        all_parameters = (data or self).parameters if (data and data.parameters) or self.parameters else None
        parameters = [param.serialize() for param in (all_parameters or [])]
        if not (method and parameters):
            return None
        serialized_data = super().serialize(data)
        assert serialized_data is not None
        serialized_data.update(
            {
                "method": method,
                "parameters": parameters,
            }
        )
        return serialized_data

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["HTTPRequest"]:
        """Convert data to **HTTPRequest** type object.

        The data structure should be like following:

        * Example data:
        .. code-block:: python

            {
                'request': {
                    'method': 'GET',
                    'parameters': {'param1': 'val1'}
                },
            }

        Args:
            data (Dict[str, Any]): Target data to convert.

        Returns:
            A **HTTPRequest** type object.

        """
        super().deserialize(data)

        # FIXME: Extract the running process order as a single function
        if self.apply_template_props:
            data = self._get_dividing_config(data)

        self.method = data.get("method", None)
        parameters: List[dict] = data.get("parameters", None)
        if parameters and not isinstance(parameters, list):
            raise TypeError("Argument *parameters* should be a list type value.")
        self.parameters = [APIParameter().deserialize(data=parameter) for parameter in parameters] if parameters else []
        return self

    @property
    def _template_base_file_path(self) -> str:
        return self._current_template.values.request.base_file_path

    @property
    def _template_config_file_path(self) -> str:
        return self._current_template.values.request.config_path_format

    def get_one_param_by_name(self, name: str) -> Optional[APIParameter]:
        for param in self.parameters:
            if param.name == name:
                return param
        return None
