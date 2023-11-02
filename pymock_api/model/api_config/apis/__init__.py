from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type, Union

from ...._utils import YAML
from ...._utils.file_opt import JSON
from ...enums import Format, ResponseStrategy
from .._base import _Checkable, _Config
from ..template import TemplateAPI, TemplateHTTP, _TemplatableConfig
from .request import APIParameter, HTTPRequest
from .response import HTTPResponse, ResponseProperty


@dataclass(eq=False)
class HTTP(_TemplatableConfig, _Checkable):
    """*The **http** section in **mocked_apis.<api>***"""

    config_file_tail: str = "-http"

    request: Optional[HTTPRequest] = None
    response: Optional[HTTPResponse] = None

    _request: Optional[HTTPRequest] = field(init=False, repr=False)
    _response: Optional[HTTPResponse] = field(init=False, repr=False)

    def _compare(self, other: "HTTP") -> bool:
        templatable_config = super()._compare(other)
        return templatable_config and self.request == other.request and self.response == other.response

    @property
    def key(self) -> str:
        return "http"

    @property  # type: ignore[no-redef]
    def request(self) -> Optional[HTTPRequest]:
        return self._request

    @request.setter
    def request(self, req: Union[dict, HTTPRequest]) -> None:
        if req:
            if isinstance(req, dict):
                self._request = HTTPRequest().deserialize(data=req)
            elif isinstance(req, HTTPRequest):
                self._request = req
            elif isinstance(req, property):
                # For initialing
                self._request = None
            else:
                raise TypeError("Setter *HTTP.request* only accepts dict or HTTPRequest type object.")
        else:
            self._request = None

    @property  # type: ignore[no-redef]
    def response(self) -> Optional[HTTPResponse]:
        return self._response

    @response.setter
    def response(self, resp: Union[dict, HTTPResponse]) -> None:
        if resp:
            if isinstance(resp, dict):
                self._response = HTTPResponse().deserialize(data=resp)
            elif isinstance(resp, HTTPResponse):
                self._response = resp
            elif isinstance(resp, property):
                # For initialing
                self._response = None
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
        self.request = self._deserialize_as(HTTPRequest, with_data=req)  # type: ignore[assignment]
        self.response = self._deserialize_as(HTTPResponse, with_data=resp)  # type: ignore[assignment]
        return self

    @property
    def _template_setting(self) -> TemplateHTTP:
        return self._current_template.values.http

    def is_work(self) -> bool:
        if not self.props_should_not_be_none(
            under_check={
                f"{self.absolute_model_key}.request": self.request,
                f"{self.absolute_model_key}.response": self.response,
            }
        ):
            return False
        assert self.request is not None
        assert self.response is not None
        return self.request.is_work() and self.response.is_work()


@dataclass(eq=False)
class MockAPI(_TemplatableConfig, _Checkable):
    """*The **<api>** section in **mocked_apis***"""

    config_file_tail: str = "-api"

    url: str = field(default_factory=str)
    http: Optional[HTTP] = None
    tag: str = field(default_factory=str)

    _url: str = field(init=False, repr=False)
    _http: Optional[HTTP] = field(init=False, repr=False)
    _tag: str = field(init=False, repr=False)

    def _compare(self, other: "MockAPI") -> bool:
        templatable_config = super()._compare(other)
        return templatable_config and self.url == other.url and self.http == other.http

    @property
    def key(self) -> str:
        return "<mock API>"

    @property  # type: ignore[no-redef]
    def url(self) -> Optional[str]:
        return self._url

    @url.setter
    def url(self, url: str) -> None:
        self._url = url

    @property  # type: ignore[no-redef]
    def http(self) -> Optional[HTTP]:
        return self._http

    @http.setter
    def http(self, http: Union[dict, HTTP]) -> None:
        if http:
            if isinstance(http, dict):
                self._http = HTTP().deserialize(data=http)
            elif isinstance(http, HTTP):
                self._http = http
            elif isinstance(http, property):
                # For initialing
                self._http = None
            else:
                raise TypeError(f"Setter *MockAPI.http* only accepts dict or HTTP type object. But it got '{http}'.")
        else:
            self._http = None

    @property  # type: ignore[no-redef]
    def tag(self) -> str:
        return self._tag

    @tag.setter
    def tag(self, tag: str) -> None:
        if isinstance(tag, str):
            self._tag = tag
        elif isinstance(tag, property):
            # For initialing
            self._tag = ""
        else:
            raise TypeError(f"Setter *MockAPI.tag* only accepts str type value. But it got '{tag}'.")

    def serialize(self, data: Optional["MockAPI"] = None) -> Optional[Dict[str, Any]]:
        url = (data.url if data else None) or self.url
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
        self.http = self._deserialize_as(HTTP, with_data=http_info)  # type: ignore[assignment]
        self.tag = data.get("tag", "")
        return self

    def is_work(self) -> bool:
        # TODO: Check the URL format
        if not self.should_not_be_none(
            config_key=f"{self.absolute_model_key}.http",
            config_value=self.http,
        ):
            return False

        if not self.should_not_be_none(
            config_key=f"{self.absolute_model_key}.url",
            config_value=self.url,
            accept_empty=False,
        ):
            return False

        assert self.http is not None
        return self.http.is_work()

    @property
    def _template_setting(self) -> TemplateAPI:
        return self._current_template.values.api

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
