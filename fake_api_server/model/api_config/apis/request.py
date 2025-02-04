from dataclasses import dataclass, field
from pydoc import locate
from typing import Any, Dict, List, Optional, Union

from fake_api_server._utils.file.operation import YAML, _BaseFileOperation
from fake_api_server.model.api_config._base import _Checkable, _Config
from fake_api_server.model.api_config.template._base_wrapper import (
    _DividableOnlyTemplatableConfig,
)
from fake_api_server.model.api_config.template.file import TemplateConfigPathRequest

from ._property import BaseProperty


@dataclass(eq=False)
class APIParameter(BaseProperty):
    default: Optional[Any] = None

    def _compare(self, other: "APIParameter") -> bool:  # type: ignore[override]
        # TODO: Let it could automatically scan what properties it has and compare all of their value.
        return super()._compare(other) and self.default == other.default

    @property
    def key(self) -> str:
        return "parameters.<parameter item>"

    @_Config._clean_empty_value
    def serialize(self, data: Optional["APIParameter"] = None) -> Optional[Dict[str, Any]]:
        serialized_data = super().serialize(data)
        if serialized_data is not None:
            default: Union[str, list] = self._get_prop(data, prop="default")
            if locate(self.value_type) is list:  # type: ignore[arg-type]
                default = []
            serialized_data["default"] = default
        return serialized_data

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["APIParameter"]:
        super().deserialize(data)
        self.default = data.get("default", None)
        return self

    def is_work(self) -> bool:
        if not self.condition_should_be_true(
            config_key=f"{self.absolute_model_key}.default",
            condition=(self.required is True and self.default is not None),
            err_msg="It's meaningless if it has default value but it is required. The default value setting should not be None if the required is 'False'.",
        ):
            return False
        return super().is_work()


@dataclass(eq=False)
class HTTPRequest(_DividableOnlyTemplatableConfig, _Checkable):
    """*The **http.request** section in **mocked_apis.<api>***"""

    config_file_tail: str = "-request"

    method: str = field(default_factory=str)
    parameters: List[APIParameter] = field(default_factory=list)

    _configuration: _BaseFileOperation = YAML()

    def _compare(self, other: "HTTPRequest") -> bool:
        templatable_config = super()._compare(other)
        return templatable_config and self.method == other.method and self.parameters == other.parameters

    @property
    def key(self) -> str:
        return "request"

    def serialize(self, data: Optional["HTTPRequest"] = None) -> Optional[Dict[str, Any]]:
        method: str = self._get_prop(data, prop="method")
        all_parameters = (data or self).parameters if (data and data.parameters) or self.parameters else None
        parameters = [param.serialize() for param in (all_parameters or [])]
        if not method:
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

        def _deserialize_parameter(parameter: dict) -> APIParameter:
            api_parameter = APIParameter()
            api_parameter.absolute_model_key = self.key
            api_parameter._current_template = self._current_template
            return api_parameter.deserialize(data=parameter)

        super().deserialize(data)

        self.method = data.get("method", None)
        parameters: List[dict] = data.get("parameters", None)
        if parameters and not isinstance(parameters, list):
            raise TypeError("Argument *parameters* should be a list type value.")
        self.parameters = [_deserialize_parameter(parameter) for parameter in parameters] if parameters else []
        return self

    @property
    def _template_setting(self) -> TemplateConfigPathRequest:
        return self._current_template.file.config_path_values.request

    def get_one_param_by_name(self, name: str) -> Optional[APIParameter]:
        for param in self.parameters:
            if param.name == name:
                return param
        return None

    def is_work(self) -> bool:
        if not self.should_not_be_none(
            config_key=f"{self.absolute_model_key}.method",
            config_value=self.method,
        ):
            return False
        if not self.should_be_valid(
            config_key=f"{self.absolute_model_key}.method",
            config_value=self.method,
            criteria=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTION"],
        ):
            return False
        if self.parameters:

            def _p_is_work(p: APIParameter) -> bool:
                p.stop_if_fail = self.stop_if_fail
                return p.is_work()

            is_work_params = list(filter(lambda p: _p_is_work(p), self.parameters))
            if len(is_work_params) != len(self.parameters):
                return False
        return True
