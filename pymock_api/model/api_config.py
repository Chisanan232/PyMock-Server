"""*The data objects of configuration*

content ...
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Union


@dataclass
class BaseConfig:
    """*The **base** section in **mocked_apis***"""

    url: str = field(default_factory=str)

    def __eq__(self, other: "BaseConfig") -> bool:
        if not isinstance(other, self.__class__):
            raise TypeError("")
        return self.url == other.url

    def serialize(self, data: Optional["BaseConfig"] = None) -> Optional[Dict[str, Any]]:
        url = (data.url if data else None) or self.url
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
class HTTPRequest:
    """*The **http.request** section in **mocked_apis.<api>***"""

    method: str = field(default_factory=str)
    parameters: dict = field(default_factory=dict)

    def __eq__(self, other: "HTTPRequest") -> bool:
        if not isinstance(other, self.__class__):
            raise TypeError("")
        return self.method == other.method and self.parameters == other.parameters

    def serialize(self, data: "HTTPRequest" = None) -> Optional[Dict[str, Any]]:
        method = (data.method if data else None) or self.method
        parameters = (data.parameters if data else None) or self.parameters
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
class HTTPResponse:
    """*The **http.response** section in **mocked_apis.<api>***"""

    value: str = field(default_factory=str)

    def __eq__(self, other: "HTTPResponse") -> bool:
        if not isinstance(other, self.__class__):
            raise TypeError("")
        return self.value == other.value

    def serialize(self, data: "HTTPResponse" = None) -> Optional[Dict[str, Any]]:
        value = (data.value if data else None) or self.value
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


class HTTP:
    """*The **http** section in **mocked_apis.<api>***"""

    _request: HTTPRequest
    _response: HTTPResponse

    def __init__(self, request: HTTPRequest = None, response: HTTPResponse = None):
        self._request = request
        self._response = response

    def __eq__(self, other: "HTTP") -> bool:
        if not isinstance(other, self.__class__):
            raise TypeError("")
        return self.request == other.request and self.response == other.response

    @property
    def request(self) -> HTTPRequest:
        return self._request

    @request.setter
    def request(self, req: Union[dict, HTTPRequest]) -> None:
        if isinstance(req, dict):
            self._request = HTTPRequest().deserialize(data=req)
        elif isinstance(req, HTTPRequest):
            self._request = req
        else:
            raise TypeError("")

    @property
    def response(self) -> HTTPResponse:
        return self._response

    @response.setter
    def response(self, resp: Union[dict, HTTPResponse]) -> None:
        if isinstance(resp, dict):
            self._response = HTTPResponse().deserialize(data=resp)
        elif isinstance(resp, HTTPResponse):
            self._response = resp
        else:
            raise TypeError("")

    def serialize(self, data: "HTTP" = None) -> Optional[Dict[str, Any]]:
        if data and data.request:
            req = data.request.serialize()
        elif self._request:
            req = self._request.serialize()
        else:
            return None

        if data and data.response:
            resp = data.response.serialize()
        elif self._response:
            resp = self._response.serialize()
        else:
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
        self._request = HTTPRequest().deserialize(data=req) if req else None
        self._response = HTTPResponse().deserialize(data=resp) if resp else None
        if not (self._request and self._response):
            return None
        return self


class MockAPI:
    """*The **<api>** section in **mocked_apis***"""

    _url: str
    _http: HTTP

    def __init__(self, url: str = None, http: HTTP = None):
        self._url = url
        self._http = http

    def __eq__(self, other: "MockAPI") -> bool:
        if not isinstance(other, self.__class__):
            raise TypeError("")
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
        if isinstance(http, dict):
            self._http = HTTP().deserialize(data=http)
        elif isinstance(http, HTTP):
            self._http = http
        else:
            raise TypeError("")

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
        self._url = data.get("url", None)
        self._http = HTTP().deserialize(data=data.get("http", None))
        if not (self._url and self._http):
            return None
        return self


class MockAPIs:
    """*The **mocked_apis** section*"""

    _base: BaseConfig
    _apis: Dict[str, MockAPI]

    def __init__(self, base: BaseConfig = None, apis: Dict[str, MockAPI] = None):
        self._base = base
        self._apis = apis

    def __len__(self):
        return len(self.apis.keys())

    def __eq__(self, other: "MockAPIs") -> bool:
        if not isinstance(other, self.__class__):
            raise TypeError("")
        return self.base == other.base and self.apis == other.apis

    @property
    def base(self) -> BaseConfig:
        return self._base

    @base.setter
    def base(self, base: Union[dict, BaseConfig]) -> None:
        if isinstance(base, dict):
            self._base = BaseConfig().deserialize(data=base)
        elif isinstance(base, BaseConfig):
            self._base = base
        else:
            raise TypeError("")

    @property
    def apis(self) -> Dict[str, MockAPI]:
        return self._apis

    @apis.setter
    def apis(self, apis: Dict[str, Union[dict, MockAPI]]) -> None:
        if isinstance(apis, dict):
            ele_types = list(map(lambda v: isinstance(v, MockAPI), apis.values()))
            if False in ele_types:
                self._apis = {}
                for api_name, api_config in apis.items():
                    self._apis[api_name] = MockAPI().deserialize(data=api_config)
            else:
                self._apis = apis
        else:
            raise TypeError("")

    def serialize(self, data: "MockAPIs" = None) -> Optional[Dict[str, Any]]:
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
        self.base = BaseConfig().deserialize(data=data.get("base", None))
        self.apis = {}
        for mock_api_name in data.keys():
            if mock_api_name == "base":
                continue
            self.apis[mock_api_name] = MockAPI().deserialize(data=data.get(mock_api_name, None))
        if not (self.base and self.apis):
            return None
        return self


class APIConfig:
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
        if not isinstance(other, self.__class__):
            raise TypeError("")
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
            raise TypeError("")

    def serialize(self, data: "APIConfig" = None) -> Optional[Dict[str, Any]]:
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
        self.apis = MockAPIs().deserialize(data=data.get("mocked_apis", None))
        if not (self.name and self.description and self.apis):
            return None
        return self
