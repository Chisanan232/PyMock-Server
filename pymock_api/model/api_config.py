"""*The data objects of configuration*

content ...
"""
from abc import ABC, ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union

from .._utils.file_opt import JSON, YAML, _BaseFileOperation
from ..model.enums import Format, ResponseStrategy, TemplateApplyScanStrategy

# The truly semantically is more near like following:
#
# ConfigType = TypeVar("ConfigType" bound="_Config")
# def need_implement_func(param: ConfigType):
#     ... (implementation)
#
# However, it would have mypy issue:
# error: Argument 1 of "{method}" is incompatible with supertype "_Config"; supertype defines the argument type as
# "ConfigType"  [override]
# note: This violates the Liskov substitution principle
# note: See https://mypy.readthedocs.io/en/stable/common_issues.html#incompatible-overrides
SelfType = Any


class _Config(metaclass=ABCMeta):
    def __eq__(self, other: SelfType) -> bool:
        if other is None:
            return False
        if not isinstance(other, self.__class__):
            raise TypeError(
                f"Cannot run equal operation between these 2 objects because of their data types is different. Be "
                f"operated object: {type(self)}, another object: {type(other)}."
            )
        return self._compare(other)

    @abstractmethod
    def _compare(self, other: SelfType) -> bool:
        pass

    @abstractmethod
    def serialize(self, data: Optional[SelfType] = None) -> Optional[Dict[str, Any]]:
        pass

    @staticmethod
    def _ensure_process_with_not_empty_value(function: Callable) -> Callable:
        def _(self, data: Dict[str, Any]) -> Optional[SelfType]:
            if not data:
                return data
            return function(self, data)

        return _

    @abstractmethod
    def deserialize(self, data: Dict[str, Any]) -> Optional[SelfType]:
        pass

    def _get_prop(self, data: Optional[object], prop: str) -> Any:
        if not hasattr(data, prop) and not hasattr(self, prop):
            raise AttributeError(f"Cannot find attribute {prop} in objects {data} or {self}.")
        return (getattr(data, prop) if data else None) or getattr(self, prop)


@dataclass(eq=False)
class _TemplatableConfig(_Config, ABC):
    apply_template_props: bool = True

    _has_apply_template_props_in_config: bool = False

    def _compare(self, other: SelfType) -> bool:
        return self.apply_template_props == other.apply_template_props

    def serialize(self, data: Optional[SelfType] = None) -> Optional[Dict[str, Any]]:
        apply_template_props: bool = self._get_prop(data, prop="apply_template_props")
        if self._has_apply_template_props_in_config:
            return {
                "apply_template_props": apply_template_props,
            }
        else:
            return {}

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional[SelfType]:
        apply_template_props = data.get("apply_template_props", None)
        if apply_template_props is not None:
            self._has_apply_template_props_in_config = True
            self.apply_template_props = apply_template_props
        return self


@dataclass(eq=False)
class BaseConfig(_Config):
    """*The **base** section in **mocked_apis***"""

    url: str = field(default_factory=str)

    def _compare(self, other: "BaseConfig") -> bool:
        return self.url == other.url

    def serialize(self, data: Optional["BaseConfig"] = None) -> Optional[Dict[str, Any]]:
        url: str = self._get_prop(data, prop="url")
        if not url:
            return None
        return {
            "url": url,
        }

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["BaseConfig"]:
        """Convert data to **BaseConfig** type object.

        The data structure should be like following:

        * Example data:
        .. code-block:: python

            {
                'base': {
                    'url': '/test/v1'
                },
            }

        Args:
            data (Dict[str, Any]): Target data to convert.

        Returns:
            A **BaseConfig** type object.

        """
        self.url = data.get("url", None)
        return self


@dataclass(eq=False)
class TemplateSetting(_Config, ABC):
    base_file_path: str = "./"
    config_path: str = field(default_factory=str)
    config_path_format: str = field(default_factory=str)

    def __post_init__(self) -> None:
        if not self.config_path_format:
            self.config_path_format = self._default_config_path_format

    def _compare(self, other: "TemplateSetting") -> bool:
        return (
            self.base_file_path == other.base_file_path
            and self.config_path == other.config_path
            and self.config_path_format == other.config_path_format
        )

    def serialize(self, data: Optional["TemplateSetting"] = None) -> Optional[Dict[str, Any]]:
        base_file_path: str = self._get_prop(data, prop="base_file_path")
        config_path: str = self._get_prop(data, prop="config_path")
        config_path_format: str = self._get_prop(data, prop="config_path_format")
        return {
            "base_file_path": base_file_path,
            "config_path": config_path,
            "config_path_format": config_path_format,
        }

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["TemplateSetting"]:
        self.base_file_path = data.get("base_file_path", "./")
        self.config_path = data.get("config_path", "")
        self.config_path_format = data.get("config_path_format", self._default_config_path_format)
        return self

    @property
    @abstractmethod
    def _default_config_path_format(self) -> str:
        pass


class TemplateAPI(TemplateSetting):
    @property
    def _default_config_path_format(self) -> str:
        return "{{ api.tag }}/{{ api.__name__ }}.yaml"


class TemplateRequest(TemplateSetting):
    @property
    def _default_config_path_format(self) -> str:
        return "{{ api.tag }}/{{ api.__name__ }}-request.yaml"


class TemplateResponse(TemplateSetting):
    @property
    def _default_config_path_format(self) -> str:
        return "{{ api.tag }}/{{ api.__name__ }}-response.yaml"


@dataclass(eq=False)
class TemplateValues(_Config):
    api: TemplateAPI = TemplateAPI()
    request: TemplateRequest = TemplateRequest()
    response: TemplateResponse = TemplateResponse()

    def _compare(self, other: "TemplateValues") -> bool:
        return self.api == other.api and self.request == other.request and self.response == other.response

    def serialize(self, data: Optional["TemplateValues"] = None) -> Optional[Dict[str, Any]]:
        api = self.api or self._get_prop(data, prop="api")
        request = self.request or self._get_prop(data, prop="request")
        response = self.response or self._get_prop(data, prop="response")
        if not (api and request and response):
            # TODO: Should raise exception?
            return None
        return {"api": api.serialize(), "request": request.serialize(), "response": response.serialize()}

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["TemplateValues"]:
        self.api = TemplateAPI().deserialize(data.get("api", {}))
        self.request = TemplateRequest().deserialize(data.get("request", {}))
        self.response = TemplateResponse().deserialize(data.get("response", {}))
        return self


@dataclass(eq=False)
class TemplateApply(_Config):
    scan_strategy: Optional[TemplateApplyScanStrategy] = None
    api: List[Union[str, Dict[str, List[str]]]] = field(default_factory=list)

    def _compare(self, other: "TemplateApply") -> bool:
        return self.scan_strategy is other.scan_strategy and self.api == other.api

    def serialize(self, data: Optional["TemplateApply"] = None) -> Optional[Dict[str, Any]]:
        scan_strategy: TemplateApplyScanStrategy = TemplateApplyScanStrategy.to_enum(
            self.scan_strategy or self._get_prop(data, prop="scan_strategy")
        )
        if not scan_strategy:
            raise ValueError("Necessary argument *scan_strategy* is missing.")

        api: str = self._get_prop(data, prop="api")
        return {
            "scan_strategy": scan_strategy.value,
            "api": api,
        }

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["TemplateApply"]:
        self.scan_strategy = TemplateApplyScanStrategy.to_enum(data.get("scan_strategy", None))
        self.api = data.get("api")  # type: ignore[assignment]
        return self


@dataclass(eq=False)
class TemplateConfig(_Config):
    values: TemplateValues = TemplateValues()
    apply: TemplateApply = TemplateApply(scan_strategy=TemplateApplyScanStrategy.FILE_NAME_FIRST)

    def _compare(self, other: "TemplateConfig") -> bool:
        return self.values == other.values and self.apply == other.apply

    def serialize(self, data: Optional["TemplateConfig"] = None) -> Optional[Dict[str, Any]]:
        values: TemplateValues = self.values or self._get_prop(data, prop="values")
        apply: TemplateApply = self.apply or self._get_prop(data, prop="apply")
        if not (values and apply):
            # TODO: Should it ranse an exception outside?
            return None
        return {
            "values": values.serialize(),
            "apply": apply.serialize(),
        }

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["TemplateConfig"]:
        self.values = TemplateValues().deserialize(data.get("values", {}))
        self.apply = TemplateApply().deserialize(data.get("apply", {}))
        return self


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
        self.method = data.get("method", None)
        parameters: List[dict] = data.get("parameters", None)
        if parameters and not isinstance(parameters, list):
            raise TypeError("Argument *parameters* should be a list type value.")
        self.parameters = [APIParameter().deserialize(data=parameter) for parameter in parameters] if parameters else []
        return self

    def get_one_param_by_name(self, name: str) -> Optional[APIParameter]:
        for param in self.parameters:
            if param.name == name:
                return param
        return None


@dataclass(eq=False)
class ResponseProperty(_Config):
    name: str = field(default_factory=str)
    required: Optional[bool] = None
    value_type: Optional[str] = None  # A type value as string
    value_format: Optional[str] = None
    items: Optional[List[IteratorItem]] = None

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
        if False in list(map(lambda i: isinstance(i, (dict, IteratorItem)), self.items)):
            raise TypeError("The data type of key *items* must be dict or IteratorItem.")
        self.items = [
            IteratorItem(name=i.get("name", ""), value_type=i.get("type", None), required=i.get("required", True))
            if isinstance(i, dict)
            else i
            for i in self.items
        ]

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
            print(f"[DEBUG in api_config.ResponseProperty.serialize] self.items: {self.items}")
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


@dataclass(eq=False)
class HTTPResponse(_TemplatableConfig):
    """*The **http.response** section in **mocked_apis.<api>***"""

    strategy: Optional[ResponseStrategy] = None
    """
    Strategy:
    * string: Return the value as string data directly.
    * file: Return the data which be recorded in the file path as response.
    * object: Return the response which be composed as object by some properties.
    """

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

    def serialize(self, data: Optional["HTTPResponse"] = None) -> Optional[Dict[str, Any]]:
        serialized_data = super().serialize(data)
        assert serialized_data is not None
        strategy: ResponseStrategy = self.strategy or ResponseStrategy.to_enum(self._get_prop(data, prop="strategy"))
        if not strategy:
            raise ValueError("Necessary argument *strategy* is missing.")
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
        super().deserialize(data)
        self.strategy = ResponseStrategy.to_enum(data.get("strategy", None))
        if not self.strategy:
            raise ValueError("Schema key *strategy* cannot be empty.")
        if self.strategy is ResponseStrategy.STRING:
            self.value = data.get("value", None)
        elif self.strategy is ResponseStrategy.FILE:
            self.path = data.get("path", None)
        elif self.strategy is ResponseStrategy.OBJECT:
            properties = [ResponseProperty().deserialize(prop) for prop in data.get("properties", [])]
            self.properties = properties if properties else None  # type: ignore[assignment]
        else:
            raise NotImplementedError
        return self


class HTTP(_TemplatableConfig):
    """*The **http** section in **mocked_apis.<api>***"""

    _request: Optional[HTTPRequest]
    _response: Optional[HTTPResponse]

    def __init__(self, request: Optional[HTTPRequest] = None, response: Optional[HTTPResponse] = None):
        self._request = request
        self._response = response

    def _compare(self, other: "HTTP") -> bool:
        templatable_config = super()._compare(other)
        return templatable_config and self.request == other.request and self.response == other.response

    @property
    def request(self) -> Optional[HTTPRequest]:
        return self._request

    @request.setter
    def request(self, req: Union[dict, HTTPRequest]) -> None:
        if req:
            if isinstance(req, dict):
                self._request = HTTPRequest().deserialize(data=req)
            elif isinstance(req, HTTPRequest):
                self._request = req
            else:
                raise TypeError("Setter *HTTP.request* only accepts dict or HTTPRequest type object.")
        else:
            self._request = None

    @property
    def response(self) -> Optional[HTTPResponse]:
        return self._response

    @response.setter
    def response(self, resp: Union[dict, HTTPResponse]) -> None:
        if resp:
            if isinstance(resp, dict):
                self._response = HTTPResponse().deserialize(data=resp)
            elif isinstance(resp, HTTPResponse):
                self._response = resp
            else:
                raise TypeError("Setter *HTTP.response* only accepts dict or HTTPResponse type object.")
        else:
            self._response = None

    def serialize(self, data: Optional["HTTP"] = None) -> Optional[Dict[str, Any]]:
        req = (data or self).request.serialize() if (data and data.request) or self.request else None  # type: ignore
        resp = (data or self).response.serialize() if (data and data.response) or self.response else None  # type: ignore
        if not (req and resp):
            return None

        serialized_data = super().serialize(data)
        assert serialized_data is not None
        serialized_data.update(
            {
                "request": req,
                "response": resp,
            }
        )
        return serialized_data

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["HTTP"]:
        """Convert data to **HTTP** type object.

        The data structure should be like following:

        * Example data:
        .. code-block:: python

            {
                'http': {
                    'request': {
                        'method': 'GET',
                        'parameters': {'param1': 'val1'}
                    },
                    'response': {
                        'value': 'This is Google home API.'
                    }
                }
            }

        Args:
            data (Dict[str, Any]): Target data to convert.

        Returns:
            A **HTTP** type object.

        """
        super().deserialize(data)
        req = data.get("request", None)
        resp = data.get("response", None)
        self.request = HTTPRequest().deserialize(data=req) if req else None
        self.response = HTTPResponse().deserialize(data=resp) if resp else None
        return self


class MockAPI(_TemplatableConfig):
    """*The **<api>** section in **mocked_apis***"""

    _url: Optional[str]
    _http: Optional[HTTP]
    _tag: str = ""

    def __init__(self, url: Optional[str] = None, http: Optional[HTTP] = None, tag: str = ""):
        self._url = url
        self._http = http
        self._tag = tag

    def _compare(self, other: "MockAPI") -> bool:
        templatable_config = super()._compare(other)
        return templatable_config and self.url == other.url and self.http == other.http

    @property
    def url(self) -> Optional[str]:
        return self._url

    @url.setter
    def url(self, url: Optional[str]) -> None:
        self._url = url

    @property
    def http(self) -> Optional[HTTP]:
        return self._http

    @http.setter
    def http(self, http: Union[dict, HTTP]) -> None:
        if http:
            if isinstance(http, dict):
                self._http = HTTP().deserialize(data=http)
            elif isinstance(http, HTTP):
                self._http = http
            else:
                raise TypeError("Setter *MockAPI.http* only accepts dict or HTTP type object.")
        else:
            self._http = None

    @property
    def tag(self) -> str:
        return self._tag

    @tag.setter
    def tag(self, tag: str) -> None:
        if not isinstance(tag, str):
            raise TypeError("Setter *MockAPI.tag* only accepts str type value.")
        self._tag = tag

    def serialize(self, data: Optional["MockAPI"] = None) -> Optional[Dict[str, Any]]:
        url = (data.url if data else None) or self._url
        http = (data.http if data else None) or self.http
        if not (url and http):
            return None
        tag = (data.tag if data else None) or self.tag
        serialized_data = super().serialize(data)
        assert serialized_data is not None
        serialized_data.update(
            {
                "url": url,
                "http": http.serialize(data=http),
                "tag": tag,
            }
        )
        return serialized_data

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["MockAPI"]:
        """Convert data to **MockAPI** type object.

        The data structure should be like following:

        * Example data:
        .. code-block:: python

            {
                <mocked API's name>: {
                    'url': '/google',
                    'http': {
                        'request': {
                            'method': 'GET',
                            'parameters': {'param1': 'val1'}
                        },
                        'response': {
                            'value': 'This is Google home API.'
                        }
                    }
                },
            }

        Args:
            data (Dict[str, Any]): Target data to convert.

        Returns:
            A **MockAPI** type object.

        """
        super().deserialize(data)
        self.url = data.get("url", None)
        http_info = data.get("http", None)
        self.http = HTTP().deserialize(data=http_info) if http_info else None
        self.tag = data.get("tag", "")
        return self

    def set_request(self, method: str = "GET", parameters: Optional[List[Union[dict, APIParameter]]] = None) -> None:
        def _convert(param: Union[dict, APIParameter]) -> APIParameter:
            if isinstance(param, APIParameter):
                return param
            ap = APIParameter()
            ap_data_obj_fields = list(ap.__dataclass_fields__.keys())
            ap_data_obj_fields.pop(ap_data_obj_fields.index("value_type"))
            ap_data_obj_fields.append("type")
            if False in list(map(lambda p: p in ap_data_obj_fields, param.keys())):
                raise ValueError("The data format of API parameter is incorrect.")
            return ap.deserialize(param)

        if parameters and False in list(map(lambda p: isinstance(p, APIParameter), parameters)):
            params = list(map(_convert, parameters))
        else:
            params = parameters or []  # type: ignore[assignment]
        if not self.http:
            self.http = HTTP(request=HTTPRequest(method=method, parameters=params), response=HTTPResponse())
        else:
            if not self.http.request:
                self.http.request = HTTPRequest(method=method, parameters=params)
            else:
                if method:
                    self.http.request.method = method
                if parameters:
                    self.http.request.parameters = params

    def set_response(
        self, strategy: ResponseStrategy = ResponseStrategy.STRING, value: str = "", iterable_value: List = []
    ) -> None:
        if strategy is ResponseStrategy.STRING:
            http_resp = HTTPResponse(strategy=strategy, value=value)
        elif strategy is ResponseStrategy.FILE:
            http_resp = HTTPResponse(strategy=strategy, path=value)
        elif strategy is ResponseStrategy.OBJECT:
            http_resp = HTTPResponse(strategy=strategy, properties=iterable_value)
        else:
            raise TypeError(f"Invalid response strategy *{strategy}*.")

        if not self.http:
            self.http = HTTP(request=HTTPRequest(), response=http_resp)
        else:
            self.http.response = http_resp

    def format(self, f: Format) -> str:
        def _ensure_getting_serialized_data() -> Dict[str, Any]:
            serialized_data = self.serialize()
            assert serialized_data, "It must have non-empty value for formatting."
            return serialized_data

        if f == Format.JSON:
            return JSON().serialize(_ensure_getting_serialized_data())
        elif f == Format.YAML:
            return YAML().serialize(_ensure_getting_serialized_data())
        else:
            raise ValueError(f"Not support the format feature as {f}.")


class MockAPIs(_Config):
    """*The **mocked_apis** section*"""

    _template: TemplateConfig
    _base: Optional[BaseConfig]
    _apis: Dict[str, Optional[MockAPI]]

    _need_template_in_config: bool = True

    def __init__(
        self,
        template: Optional[TemplateConfig] = None,
        base: Optional[BaseConfig] = None,
        apis: Dict[str, Optional[MockAPI]] = {},
    ):
        self._template = TemplateConfig() if template is None else template
        self._base = base
        self._apis = apis

    def __len__(self):
        return len(self.apis.keys())

    def _compare(self, other: "MockAPIs") -> bool:
        return self.base == other.base and self.apis == other.apis

    @property
    def template(self) -> TemplateConfig:
        return self._template

    @template.setter
    def template(self, template: Union[dict, TemplateConfig]) -> None:
        if template:
            if isinstance(template, dict):
                self._template = TemplateConfig().deserialize(data=template)
            elif isinstance(template, TemplateConfig):
                self._template = template
            else:
                raise TypeError("Setter *MockAPIs.template* only accepts dict or TemplateConfig type object.")

    @property
    def base(self) -> Optional[BaseConfig]:
        return self._base

    @base.setter
    def base(self, base: Union[dict, BaseConfig]) -> None:
        if base:
            if isinstance(base, dict):
                self._base = BaseConfig().deserialize(data=base)
            elif isinstance(base, BaseConfig):
                self._base = base
            else:
                raise TypeError("Setter *MockAPIs.base* only accepts dict or BaseConfig type object.")
        else:
            self._base = None

    @property
    def apis(self) -> Dict[str, Optional[MockAPI]]:
        return self._apis

    @apis.setter
    def apis(self, apis: Dict[str, Union[dict, MockAPI]]) -> None:
        if apis:
            if not isinstance(apis, dict):
                raise TypeError("Setter *MockAPIs.apis* only accepts dict or MockAPI type object.")

            ele_types = set(list(map(lambda v: isinstance(v, MockAPI), apis.values())))
            if len(ele_types) != 1:
                raise ValueError("It has multiple types of the data content. Please unify these objects data type.")

            if False in ele_types:
                self._apis = {}
                for api_name, api_config in apis.items():
                    self._apis[api_name] = MockAPI().deserialize(data=(api_config or {}))
            else:
                self._apis = apis  # type: ignore
        else:
            self._apis = {}

    @property
    def set_template_in_config(self) -> bool:
        return self._need_template_in_config

    @set_template_in_config.setter
    def set_template_in_config(self, _set: bool) -> None:
        self._need_template_in_config = _set

    def serialize(self, data: Optional["MockAPIs"] = None) -> Optional[Dict[str, Any]]:
        template = (data.template if data else None) or self.template
        base = (data.base if data else None) or self.base
        apis = (data.apis if data else None) or self.apis
        if not (base and apis):
            return None

        # Process section *base*
        api_info = {  # type: ignore[var-annotated]
            "base": BaseConfig().serialize(data=base),
            "apis": {},
        }
        if self._need_template_in_config:
            api_info["template"] = template.serialize()

        # Process section *apis*
        all_mocked_apis = {}
        for api_name, api_config in apis.items():
            all_mocked_apis[api_name] = MockAPI().serialize(data=api_config)
        api_info["apis"] = all_mocked_apis

        return api_info

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["MockAPIs"]:
        """Convert data to **MockAPIs** type object.

        The data structure should be like following:

        * Example data:
        .. code-block:: python

            {
                'base': {'url': '/test/v1'},
                'apis': {
                    'google_home': {
                        'url': '/google',
                        'http': {
                            'request': {
                                'method': 'GET',
                                'parameters': [{'param1': 'val1'}]
                            },
                            'response': {
                                'value': 'This is Google home API.'
                            }
                        }
                    },
                    'test_home': {
                        'url': '/google',
                        'http': {
                            'request': {
                                'method': 'GET',
                                'parameters': [{'param1': 'val1'}]
                            },
                            'response': {
                                'value': '{ "responseCode": "200", "errorMessage": "OK", "content": "This is Test home." }'
                            }
                        },
                        'cookie': [{'TEST': 'cookie_value'}]
                    },
                    'youtube_home': {
                        'url': '/youtube',
                        'http': {
                            'request': {
                                'method': 'GET',
                                'parameters': [{'param1': 'val1'}]
                            },
                            'response': {'value': 'youtube.json'}
                        },
                        'cookie': [{'USERNAME': 'test'}, {'SESSION_EXPIRED': '2023-12-31T00:00:00.000'}]
                    }
                }
            }

        Args:
            data (Dict[str, Any]): Target data to convert.

        Returns:
            A **MockAPIs** type object.

        """
        # Processing section *template*
        template_info = data.get("template", {})
        if not template_info:
            self._need_template_in_config = False
        self.template = TemplateConfig().deserialize(data=template_info)

        # Processing section *base*
        base_info = data.get("base", None)
        self.base = BaseConfig().deserialize(data=base_info)

        # Processing section *apis*
        mocked_apis_info = data.get("apis", {})
        self.apis = {}
        if mocked_apis_info:
            for mock_api_name in mocked_apis_info.keys():
                self.apis[mock_api_name] = MockAPI().deserialize(data=mocked_apis_info.get(mock_api_name, None))
        return self

    def get_api_config_by_url(self, url: str, base: Optional[BaseConfig] = None) -> Optional[MockAPI]:
        url = url.replace(base.url, "") if base else url
        for k, v in self._apis.items():
            if v and v.url == url:
                return self._apis[k]
        return None

    def get_all_api_config_by_url(self, url: str, base: Optional[BaseConfig] = None) -> Dict[str, MockAPI]:
        url = url.replace(base.url, "") if base else url
        all_api_configs: Dict[str, MockAPI] = {}
        for k, v in self._apis.items():
            if v and v.url == url:
                all_api_configs[v.http.request.method.upper()] = self._apis[k]  # type: ignore[union-attr,assignment]
        return all_api_configs

    def group_by_url(self) -> Dict[str, List[MockAPI]]:
        apis = self._apis
        aggregated_apis: Dict[str, List[MockAPI]] = {}
        for api_name, api_config in apis.items():
            assert api_config and api_config.url
            one_url_details = aggregated_apis.get(api_config.url, [])
            one_url_details.append(api_config)
            aggregated_apis[api_config.url] = one_url_details
        return aggregated_apis


class APIConfig(_Config):
    """*The entire configuration*"""

    _name: str = ""
    _description: str = ""
    _apis: Optional[MockAPIs]

    _configuration: _BaseFileOperation = YAML()
    _need_template_in_config: bool = True

    def __init__(self, name: str = "", description: str = "", apis: Optional[MockAPIs] = None):
        self._name = name
        self._description = description
        self._apis = apis

    def __len__(self):
        return len(self._apis) if self._apis else 0

    def _compare(self, other: "APIConfig") -> bool:
        return self.name == other.name and self.description == other.description and self.apis == other.apis

    @property
    def _config_operation(self) -> _BaseFileOperation:
        return self._configuration

    def has_apis(self) -> bool:
        return len(self) != 0

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, desc: str) -> None:
        self._description = desc

    @property
    def apis(self) -> Optional[MockAPIs]:
        return self._apis

    @apis.setter
    def apis(self, apis: Union[dict, MockAPIs]) -> None:
        if apis:
            if isinstance(apis, dict):
                self._apis = MockAPIs().deserialize(data=apis)
            elif isinstance(apis, MockAPIs):
                self._apis = apis
            else:
                raise TypeError("Setter *APIConfig.apis* only accepts dict or MockAPIs type object.")
        else:
            self._apis = None

    @property
    def set_template_in_config(self) -> bool:
        return self._need_template_in_config

    @set_template_in_config.setter
    def set_template_in_config(self, _set: bool) -> None:
        self._need_template_in_config = _set

    def serialize(self, data: Optional["APIConfig"] = None) -> Optional[Dict[str, Any]]:
        name = (data.name if data else None) or self.name
        description = (data.description if data else None) or self.description
        apis = (data.apis if data else None) or self.apis
        if not apis:
            return None
        apis.set_template_in_config = self.set_template_in_config
        return {
            "name": name,
            "description": description,
            "mocked_apis": apis.serialize(),
        }

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["APIConfig"]:
        """Convert data to **APIConfig** type object.

        The data structure should be like following:

        * Example data:
        .. code-block:: python

            {
                'name': 'Test mocked API',
                'description': 'This is a test for the usage demonstration.',
                'mocked_apis': {
                    'base': {'url': '/test/v1'},
                    'apis': {
                        'google_home': {
                            'url': '/google',
                            'http': {
                                'request': {
                                    'method': 'GET',
                                    'parameters': [{'param1': 'val1'}]
                                },
                                'response': {
                                    'value': 'This is Google home API.'
                                }
                            }
                        },
                        'test_home': {
                            'url': '/google',
                            'http': {
                                'request': {
                                    'method': 'GET',
                                    'parameters': [{'param1': 'val1'}]
                                },
                                'response': {
                                    'value': '{
                                        "responseCode": "200", "errorMessage": "OK", "content": "This is Test home."
                                    }'
                                }
                            },
                            'cookie': [{'TEST': 'cookie_value'}]
                        },
                        'youtube_home': {
                            'url': '/youtube',
                            'http': {
                                'request': {
                                    'method': 'GET',
                                    'parameters': [{'param1': 'val1'}]
                                },
                                'response': {'value': 'youtube.json'}
                            },
                            'cookie': [{'USERNAME': 'test'}, {'SESSION_EXPIRED': '2023-12-31T00:00:00.000'}]
                        }
                    }
                }
            }

        Args:
            data (Dict[str, Any]): Target data to convert.

        Returns:
            A **APIConfig** type object.

        """
        self.name = data.get("name", None)
        self.description = data.get("description", None)
        mocked_apis = data.get("mocked_apis", None)
        if mocked_apis:
            mock_apis_data_model = MockAPIs()
            mock_apis_data_model.set_template_in_config = self.set_template_in_config
            self.apis = mock_apis_data_model.deserialize(data=mocked_apis)
        return self

    def from_yaml(self, path: str) -> Optional["APIConfig"]:
        return self.deserialize(data=self._config_operation.read(path))

    def to_yaml(self, path: str) -> None:
        self._config_operation.write(path=path, config=(self.serialize() or {}))
