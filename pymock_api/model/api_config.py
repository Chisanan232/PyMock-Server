"""*The data objects of configuration*

content ...
"""

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union

from .._utils.file_opt import YAML, _BaseFileOperation

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
class APIParameter(_Config):
    name: str = field(default_factory=str)
    required: Optional[bool] = None
    default: Optional[Any] = None
    value_type: Optional[type] = None
    value_format: Optional[str] = None
    force_naming: Optional[bool] = None

    def _compare(self, other: "APIParameter") -> bool:
        # TODO: Let it could automatically scan what properties it has and compare all of their value.
        return self.name == other.name

    def serialize(self, data: Optional["APIParameter"] = None) -> Optional[Dict[str, Any]]:
        name: str = self._get_prop(data, prop="name")
        required: bool = self._get_prop(data, prop="required")
        default: str = self._get_prop(data, prop="default")
        value_type: type = self._get_prop(data, prop="value_type")
        value_format: str = self._get_prop(data, prop="value_format")
        force_naming: bool = self._get_prop(data, prop="force_naming")
        if not (name and default and value_type and value_format) or (required is None and force_naming is None):
            return None
        return {
            "name": name,
            "required": required,
            "default": default,
            "value_type": value_type,
            "value_format": value_format,
            "force_naming": force_naming,
        }

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["APIParameter"]:
        self.name = data.get("name", None)
        self.required = data.get("required", None)
        self.default = data.get("default", None)
        self.value_type = data.get("value_type", None)
        self.value_format = data.get("value_format", None)
        self.force_naming = data.get("force_naming", None)
        return self


@dataclass(eq=False)
class HTTPRequest(_Config):
    """*The **http.request** section in **mocked_apis.<api>***"""

    method: str = field(default_factory=str)
    parameters: List[APIParameter] = field(default_factory=list)

    def _compare(self, other: "HTTPRequest") -> bool:
        return self.method == other.method and self.parameters == other.parameters

    def serialize(self, data: Optional["HTTPRequest"] = None) -> Optional[Dict[str, Any]]:
        method: str = self._get_prop(data, prop="method")
        all_parameters = (data or self).parameters if (data and data.parameters) or self.parameters else None
        parameters = [param.serialize() for param in (all_parameters or [])]
        if not (method and parameters):
            return None
        return {
            "method": method,
            "parameters": parameters,
        }

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
        self.method = data.get("method", None)
        parameters: List[dict] = data.get("parameters", None)
        if parameters and not isinstance(parameters, list):
            raise TypeError("Argument *parameters* should be a list type value.")
        self.parameters = [APIParameter().deserialize(data=parameter) for parameter in parameters] if parameters else []
        return self


@dataclass(eq=False)
class HTTPResponse(_Config):
    """*The **http.response** section in **mocked_apis.<api>***"""

    value: str = field(default_factory=str)

    def _compare(self, other: "HTTPResponse") -> bool:
        return self.value == other.value

    def serialize(self, data: Optional["HTTPResponse"] = None) -> Optional[Dict[str, Any]]:
        value: str = self._get_prop(data, prop="value")
        if not value:
            return None
        return {
            "value": value,
        }

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
        self.value = data.get("value", None)
        return self


class HTTP(_Config):
    """*The **http** section in **mocked_apis.<api>***"""

    _request: Optional[HTTPRequest]
    _response: Optional[HTTPResponse]

    def __init__(self, request: Optional[HTTPRequest] = None, response: Optional[HTTPResponse] = None):
        self._request = request
        self._response = response

    def _compare(self, other: "HTTP") -> bool:
        return self.request == other.request and self.response == other.response

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

        return {
            "request": req,
            "response": resp,
        }

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
        req = data.get("request", None)
        resp = data.get("response", None)
        self.request = HTTPRequest().deserialize(data=req) if req else None
        self.response = HTTPResponse().deserialize(data=resp) if resp else None
        return self


class MockAPI(_Config):
    """*The **<api>** section in **mocked_apis***"""

    _url: Optional[str]
    _http: Optional[HTTP]

    def __init__(self, url: Optional[str] = None, http: Optional[HTTP] = None):
        self._url = url
        self._http = http

    def _compare(self, other: "MockAPI") -> bool:
        return self.url == other.url and self.http == other.http

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

    def serialize(self, data: Optional["MockAPI"] = None) -> Optional[Dict[str, Any]]:
        url = (data.url if data else None) or self._url
        http = (data.http if data else None) or self.http
        if not (url and http):
            return None
        return {
            "url": url,
            "http": http.serialize(data=http),
        }

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
        self.url = data.get("url", None)
        http_info = data.get("http", None)
        self.http = HTTP().deserialize(data=http_info) if http_info else None
        return self


class MockAPIs(_Config):
    """*The **mocked_apis** section*"""

    _base: Optional[BaseConfig]
    _apis: Dict[str, Optional[MockAPI]]

    def __init__(self, base: Optional[BaseConfig] = None, apis: Dict[str, Optional[MockAPI]] = {}):
        self._base = base
        self._apis = apis

    def __len__(self):
        return len(self.apis.keys())

    def _compare(self, other: "MockAPIs") -> bool:
        return self.base == other.base and self.apis == other.apis

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

    def serialize(self, data: Optional["MockAPIs"] = None) -> Optional[Dict[str, Any]]:
        base = (data.base if data else None) or self.base
        apis = (data.apis if data else None) or self.apis
        if not (base and apis):
            return None
        api_info = {
            "base": BaseConfig().serialize(data=base),
        }
        for api_name, api_config in apis.items():
            api_info[api_name] = MockAPI().serialize(data=api_config)
        return api_info

    @_Config._ensure_process_with_not_empty_value
    def deserialize(self, data: Dict[str, Any]) -> Optional["MockAPIs"]:
        """Convert data to **MockAPIs** type object.

        The data structure should be like following:

        * Example data:
        .. code-block:: python

            {
                'base': {'url': '/test/v1'},
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

        Args:
            data (Dict[str, Any]): Target data to convert.

        Returns:
            A **MockAPIs** type object.

        """
        base_info = data.get("base", None)
        self.base = BaseConfig().deserialize(data=base_info)
        self.apis = {}
        for mock_api_name in data.keys():
            if mock_api_name == "base":
                continue
            self.apis[mock_api_name] = MockAPI().deserialize(data=data.get(mock_api_name, None))
        return self


class APIConfig(_Config):
    """*The entire configuration*"""

    _name: str = ""
    _description: str = ""
    _apis: Optional[MockAPIs]

    _configuration: _BaseFileOperation = YAML()

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

    def serialize(self, data: Optional["APIConfig"] = None) -> Optional[Dict[str, Any]]:
        name = (data.name if data else None) or self.name
        description = (data.description if data else None) or self.description
        apis = (data.apis if data else None) or self.apis
        if not (name and description and apis):
            return None
        return {
            "name": name,
            "description": description,
            "mocked_apis": MockAPIs().serialize(data=apis),
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

        Args:
            data (Dict[str, Any]): Target data to convert.

        Returns:
            A **APIConfig** type object.

        """
        self.name = data.get("name", None)
        self.description = data.get("description", None)
        mocked_apis = data.get("mocked_apis", None)
        if mocked_apis:
            self.apis = MockAPIs().deserialize(data=mocked_apis)
        return self

    def from_yaml(self, path: str) -> Optional["APIConfig"]:
        return self.deserialize(data=self._config_operation.read(path))

    def to_yaml(self, path: str) -> None:
        self._config_operation.write(path=path, config=(self.serialize() or {}))
