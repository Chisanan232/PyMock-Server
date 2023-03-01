"""*The utility functions for converting data to data objects.*

This module focuses on converting the Python objects to specific data format objects. All the input data this module
receives should be the Python objects, e.g., *str*, *dict*, etc. In this module case, it should be *dict* type object.
"""

from typing import Any, Dict

from ..model.api_config import (
    HTTP,
    APIConfig,
    BaseConfig,
    HTTPRequest,
    HTTPResponse,
    MockAPI,
    MockAPIs,
)


class Convert:
    """*The process converts value to specific data objects*"""

    @classmethod
    def api_config(cls, data: Dict[str, Any]) -> APIConfig:
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
                            'response': {'value': '{ "responseCode": "200", "errorMessage": "OK", "content": "This is Test home." }'}
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
        name = data.get("name", None)
        description = data.get("description", None)
        mocked_apis = data.get("mocked_apis", None)

        return APIConfig(name=name, description=description, apis=_Convert.mock_apis(data=mocked_apis))


class _Convert:
    """*The process converts value to data objects*"""

    @classmethod
    def mock_apis(cls, data: Dict[str, Any]) -> MockAPIs:
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
        base_config = cls.base(data=data.get("base", None))
        mock_apis = {}
        for mock_api_name in data.keys():
            if mock_api_name == "base":
                continue
            mock_api = cls.mock_api(data=data.get(mock_api_name, None))
            mock_apis[mock_api_name] = mock_api
        return MockAPIs(base=base_config, apis=mock_apis)

    @classmethod
    def base(cls, data: Dict[str, Any]) -> BaseConfig:
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
        url = data.get("url", None)
        return BaseConfig(url=url)

    @classmethod
    def mock_api(cls, data: Dict[str, Any]) -> MockAPI:
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
                            'parameters': [{'param1': 'val1'}]
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
        url = data.get("url", None)
        http_data = data.get("http", None)
        http = cls.http(http_data) if http_data else None
        return MockAPI(url=url, http=http)

    @classmethod
    def http(cls, data: Dict[str, Any]) -> HTTP:
        """Convert data to **HTTP** type object.

        The data structure should be like following:

        * Example data:
        .. code-block:: python

            {
                'http': {
                    'request': {
                        'method': 'GET',
                        'parameters': [{'param1': 'val1'}]
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
        request = data.get("request", None)
        response = data.get("response", None)
        http_request = cls.http_request(data=request) if request else None
        http_response = cls.http_response(data=response) if response else None
        return HTTP(request=http_request, response=http_response)

    @classmethod
    def http_request(cls, data: Dict[str, Any]) -> HTTPRequest:
        """Convert data to **HTTPRequest** type object.

        The data structure should be like following:

        * Example data:
        .. code-block:: python

            {
                'request': {
                    'method': 'GET',
                    'parameters': [{'param1': 'val1'}]
                },
            }

        Args:
            data (Dict[str, Any]): Target data to convert.

        Returns:
            A **HTTPRequest** type object.

        """
        method = data.get("method", None)
        parameters = data.get("parameters", None)
        return HTTPRequest(method=method, parameters=parameters)

    @classmethod
    def http_response(cls, data: Dict[str, Any]) -> HTTPResponse:
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
        value = data.get("value", None)
        return HTTPResponse(value=value)
