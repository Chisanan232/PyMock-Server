from typing import Any, Dict, List, Optional, Union

from ...._utils import YAML
from ...._utils.file_opt import JSON
from ...enums import Format, ResponseStrategy
from .._base import _Config, _TemplatableConfig
from .request import APIParameter, HTTPRequest
from .response import HTTPResponse, ResponseProperty


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