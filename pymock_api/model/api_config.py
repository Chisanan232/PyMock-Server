"""*The data objects of configuration*

content ...
"""

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Union


class _Config(metaclass=ABCMeta):
    @abstractmethod
    def __eq__(self, other: "_Config") -> bool:
        if not isinstance(other, self.__class__):
            raise TypeError(
                f"Cannot run equal operation between these 2 objects because of their data types is different. Be operated object: {type(self)}, another object: {type(other)}."
            )

    @abstractmethod
    def serialize(self, data: Optional["_Config"] = None) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def deserialize(self, data: Dict[str, Any]) -> Optional["_Config"]:
        pass

    def _get_prop(self, data: Optional[object], prop: str) -> Any:
        if not hasattr(data, prop) and not hasattr(self, prop):
            raise AttributeError(f"Cannot find attribute {prop} in objects {data} or {self}.")
        return (getattr(data, prop) if data else None) or getattr(self, prop)


@dataclass
class BaseConfig(_Config):
    """*The **base** section in **mocked_apis***"""

    url: str = field(default_factory=str)

    def __eq__(self, other: "BaseConfig") -> bool:
        super().__eq__(other)
        return self.url == other.url

    def serialize(self, data: Optional["BaseConfig"] = None) -> Optional[Dict[str, Any]]:
        url: str = self._get_prop(data, prop="url")
        if not url:
            return None
        return {
            "url": url,
        }

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
        if not self.url:
            return None
        return self


@dataclass
class HTTPRequest(_Config):
    """*The **http.request** section in **mocked_apis.<api>***"""

    method: str = field(default_factory=str)
    parameters: dict = field(default_factory=dict)

    def __eq__(self, other: "HTTPRequest") -> bool:
        super().__eq__(other)
        return self.method == other.method and self.parameters == other.parameters

    def serialize(self, data: "HTTPRequest" = None) -> Optional[Dict[str, Any]]:
        method: str = self._get_prop(data, prop="method")
        parameters: str = self._get_prop(data, prop="parameters")
        if not (method and parameters):
            return None
        return {
            "method": method,
            "parameters": parameters,
        }

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
        self.parameters = data.get("parameters", None)
        if not (self.method and self.parameters):
            return None
        return self


@dataclass
class HTTPResponse(_Config):
    """*The **http.response** section in **mocked_apis.<api>***"""

    value: str = field(default_factory=str)

    def __eq__(self, other: "HTTPResponse") -> bool:
        super().__eq__(other)
        return self.value == other.value

    def serialize(self, data: "HTTPResponse" = None) -> Optional[Dict[str, Any]]:
        value: str = self._get_prop(data, prop="value")
        if not value:
            return None
        return {
            "value": value,
        }

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
        if not self.value:
            return None
        return self


class HTTP(_Config):
    """*The **http** section in **mocked_apis.<api>***"""

    _request: HTTPRequest
    _response: HTTPResponse

    def __init__(self, request: HTTPRequest = None, response: HTTPResponse = None):
        self._request = request
        self._response = response

    def __eq__(self, other: "HTTP") -> bool:
        super().__eq__(other)
        return self.request == other.request and self.response == other.response

    @property
    def request(self) -> HTTPRequest:
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
            self._request = req

    @property
    def response(self) -> HTTPResponse:
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
            self._response = resp

    def serialize(self, data: "HTTP" = None) -> Optional[Dict[str, Any]]:
        req = (data or self).request.serialize() if (data and data.request) or self.request else None
        resp = (data or self).response.serialize() if (data and data.response) or self.response else None
        if not (req and resp):
            return None

        return {
            "request": req,
            "response": resp,
        }

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
        if not (self.request and self.response):
            return None
        return self


class MockAPI(_Config):
    """*The **<api>** section in **mocked_apis***"""

    _url: str
    _http: HTTP

    def __init__(self, url: str = None, http: HTTP = None):
        self._url = url
        self._http = http

    def __eq__(self, other: "MockAPI") -> bool:
        super().__eq__(other)
        return self.url == other.url and self.http == other.http

    @property
    def url(self) -> str:
        return self._url

    @url.setter
    def url(self, url: str) -> None:
        self._url = url

    @property
    def http(self) -> HTTP:
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
            self._http = http

    def serialize(self, data: "MockAPI" = None) -> Optional[Dict[str, Any]]:
        url = (data.url if data else None) or self._url
        http = (data.http if data else None) or self.http
        if not (url and http):
            return None
        return {
            "url": url,
            "http": http.serialize(data=http),
        }

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
        if not (self.url and self.http):
            return None
        return self


class MockAPIs(_Config):
    """*The **mocked_apis** section*"""

    _base: BaseConfig
    _apis: Dict[str, MockAPI]

    def __init__(self, base: BaseConfig = None, apis: Dict[str, MockAPI] = None):
        self._base = base
        self._apis = apis

    def __len__(self):
        return len(self.apis.keys())

    def __eq__(self, other: "MockAPIs") -> bool:
        super().__eq__(other)
        return self.base == other.base and self.apis == other.apis

    @property
    def base(self) -> BaseConfig:
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
            self._base = base

    @property
    def apis(self) -> Dict[str, MockAPI]:
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
                    self._apis[api_name] = MockAPI().deserialize(data=api_config)
            else:
                self._apis = apis
        else:
            self._apis = apis

    def serialize(self, data: "MockAPIs" = None) -> Union[Dict[str, Any]]:
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
        if not base_info:
            return None
        if len(data.keys()) == 1:
            return None
        self.base = BaseConfig().deserialize(data=base_info)
        self.apis = {}
        for mock_api_name in data.keys():
            if mock_api_name == "base":
                continue
            self.apis[mock_api_name] = MockAPI().deserialize(data=data.get(mock_api_name, None))
        if not (self.base and self.apis):
            return None
        return self


class APIConfig(_Config):
    """*The entire configuration*"""

    _name: str = ""
    _description: str = ""
    _apis: MockAPIs

    def __init__(self, name: str = None, description: str = None, apis: MockAPIs = None):
        self._name = name
        self._description = description
        self._apis = apis

    def __len__(self):
        return len(self._apis) if self._apis else 0

    def __eq__(self, other: "APIConfig") -> bool:
        super().__eq__(other)
        return self.name == other.name and self.description == other.description and self.apis == other.apis

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
    def apis(self) -> MockAPIs:
        return self._apis

    @apis.setter
    def apis(self, apis: Union[dict, MockAPIs]) -> None:
        if isinstance(apis, dict):
            self._apis = MockAPIs().deserialize(data=apis)
        elif isinstance(apis, MockAPIs):
            self._apis = apis
        else:
            raise TypeError("Setter *APIConfig.apis* only accepts dict or MockAPIs type object.")

    def serialize(self, data: "APIConfig" = None) -> Union[Dict[str, Any]]:
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
        if not (self.name and self.description and self.apis):
            return None
        return self
