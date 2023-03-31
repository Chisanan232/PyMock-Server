from typing import Dict
from unittest.mock import Mock

import pytest

from pymock_api.model.api_config import (
    HTTP,
    APIConfig,
    BaseConfig,
    HTTPRequest,
    HTTPResponse,
    MockAPI,
    MockAPIs,
)

from ..._values import (
    APIConfigValue,
    _Base_URL,
    _Config_Description,
    _Config_Name,
    _Mock_APIs,
    _Test_HTTP_Method,
    _Test_HTTP_Req_Params,
    _Test_HTTP_Resp,
    _Test_URL,
    _TestConfig,
)

_assertion_msg = "Its property's value should be same as we set."


class TestAPIConfig:

    _test_value: APIConfigValue = APIConfigValue()
    _mock_mock_apis: MockAPIs = None

    @pytest.fixture(scope="function")
    def api_config(self) -> APIConfig:
        return APIConfig(name=_Config_Name, description=_Config_Description, apis=self.mock_mock_apis)

    @property
    def mock_mock_apis(self) -> MockAPIs:
        if not self._mock_mock_apis:
            self._mock_mock_apis = MockAPIs(base=self.mock_base_config, apis=self.mock_mock_api)
        return self._mock_mock_apis

    @property
    def mock_base_config(self) -> BaseConfig:
        return BaseConfig(url=_Base_URL)

    @property
    def mock_mock_api(self) -> Dict[str, MockAPI]:
        return {"test_config": MockAPI(url=_Test_URL, http=self.mock_http)}

    @property
    def mock_http(self) -> HTTP:
        return HTTP(request=self.mock_request, response=self.mock_response)

    @property
    def mock_request(self) -> HTTPRequest:
        return HTTPRequest(
            method=_TestConfig.Request.get("method"), parameters=_TestConfig.Request.get("parameters", {})
        )

    @property
    def mock_response(self) -> HTTPResponse:
        return HTTPResponse(value=_Test_HTTP_Resp)

    def test___len___with_value(self, api_config: APIConfig):
        api_config.apis = _TestConfig.Mock_APIs
        assert len(api_config) == len(
            list(filter(lambda k: k != "base", _TestConfig.Mock_APIs.keys()))
        ), "The size of *APIConfig* data object should be same as *MockAPIs* data object."

    def test___len___with_non_value(self):
        assert len(APIConfig()) == 0, "The size of *APIConfig* data object should be '0' if property *apis* is None."

    def test_has_apis_with_value(self, api_config: APIConfig):
        api_config.apis = _TestConfig.Mock_APIs
        assert api_config.has_apis() is True, "It should be 'True' if its property *apis* has value."

    def test_has_apis_with_no_value(self):
        assert APIConfig().has_apis() is False, "It should be 'False' if its property *apis* is None."

    def test_name(self, api_config: APIConfig):
        assert api_config.name == _Config_Name, _assertion_msg

    def test_description(self, api_config: APIConfig):
        assert api_config.description == _Config_Description, _assertion_msg

    def test_apis(self, api_config: APIConfig):
        assert api_config.apis.base.url == _TestConfig.API_Config.get("mocked_apis").get("base").get(
            "url"
        ), _assertion_msg
        assert list(api_config.apis.apis.keys())[0] in _TestConfig.API_Config.get("mocked_apis").keys(), _assertion_msg

    def test_serialize(self, api_config: APIConfig):
        assert api_config.serialize() == _TestConfig.API_Config

    def test_deserialize(self, api_config: APIConfig):
        mock_apis_config = api_config.deserialize(data=_TestConfig.API_Config)
        assert isinstance(mock_apis_config, APIConfig)
        assert mock_apis_config.name == _Config_Name
        assert mock_apis_config.description == _Config_Description
        assert mock_apis_config.apis.base.url == _TestConfig.API_Config.get("mocked_apis").get("base").get("url")
        assert (
            list(mock_apis_config.apis.apis.keys())[0] in _TestConfig.API_Config.get("mocked_apis").keys()
        ), _assertion_msg


class TestMockAPIs:

    _mock_base_config: BaseConfig = None
    _mock_mock_apis: Dict[str, MockAPI] = None

    @pytest.fixture(scope="function")
    def mock_apis(self) -> MockAPIs:
        return MockAPIs(base=self.mock_base_config, apis=self.mock_mock_api)

    @property
    def mock_base_config(self) -> BaseConfig:
        if not self._mock_base_config:
            self._mock_base_config = BaseConfig(url=_Base_URL)
        return self._mock_base_config

    @property
    def mock_mock_api(self) -> Dict[str, MockAPI]:
        if not self._mock_mock_apis:
            self._mock_mock_apis = {"test_config": MockAPI(url=_Test_URL, http=self.mock_http)}
        return self._mock_mock_apis

    @property
    def mock_http(self) -> HTTP:
        return HTTP(request=self.mock_request, response=self.mock_response)

    @property
    def mock_request(self) -> HTTPRequest:
        return HTTPRequest(
            method=_TestConfig.Request.get("method"), parameters=_TestConfig.Request.get("parameters", {})
        )

    @property
    def mock_response(self) -> HTTPResponse:
        return HTTPResponse(value=_Test_HTTP_Resp)

    def test___len__(self, mock_apis: MockAPIs):
        assert len(mock_apis) == len(
            self.mock_mock_api.keys()
        ), f"The size of *MockAPIs* data object should be same as object '{self.mock_mock_api}'."

    def test_base(self, mock_apis: MockAPIs):
        assert mock_apis.base == self.mock_base_config, _assertion_msg

    def test_apis(self, mock_apis: MockAPIs):
        assert mock_apis.apis == self.mock_mock_api, _assertion_msg

    def test_serialize(self, mock_apis: MockAPIs):
        assert mock_apis.serialize() == _TestConfig.Mock_APIs

    def test_deserialize(self, mock_apis: MockAPIs):
        mock_apis = mock_apis.deserialize(data=_TestConfig.Mock_APIs)
        assert isinstance(mock_apis, MockAPIs)
        assert mock_apis.base.url == _Base_URL
        assert mock_apis.apis == self.mock_mock_api


class TestBaseConfig:
    @pytest.fixture(scope="function")
    def base_config(self) -> BaseConfig:
        return BaseConfig(url=_Base_URL)

    def test_url(self, base_config: BaseConfig):
        assert base_config.url == _Base_URL, _assertion_msg

    def test_serialize(self, base_config: BaseConfig):
        assert base_config.serialize() == _TestConfig.Base

    def test_deserialize(self, base_config: BaseConfig):
        base_config = base_config.deserialize(data=_TestConfig.Base)
        assert isinstance(base_config, BaseConfig)
        assert base_config.url == _Base_URL


class TestMockAPI:

    _http: HTTP = None

    @pytest.fixture(scope="function")
    def mock_api(self) -> MockAPI:
        return MockAPI(url=_Test_URL, http=self.mock_http)

    @property
    def mock_http(self) -> HTTP:
        if not self._http:
            self._http = HTTP(request=self.mock_request, response=self.mock_response)
        return self._http

    @property
    def mock_request(self) -> HTTPRequest:
        return HTTPRequest(
            method=_TestConfig.Request.get("method"), parameters=_TestConfig.Request.get("parameters", {})
        )

    @property
    def mock_response(self) -> HTTPResponse:
        return HTTPResponse(value=_Test_HTTP_Resp)

    def test_url(self, mock_api: MockAPI):
        assert mock_api.url == _Test_URL, _assertion_msg

    def test_http(self, mock_api: MockAPI):
        assert mock_api.http == self.mock_http, _assertion_msg

    def test_serialize(self, mock_api: MockAPI):
        assert mock_api.serialize() == _TestConfig.Mock_API

    def test_deserialize(self, mock_api: MockAPI):
        mock_api = mock_api.deserialize(data=_TestConfig.Mock_API)
        assert isinstance(mock_api, MockAPI)
        assert mock_api.url == _Test_URL
        assert mock_api.http.request.method == _TestConfig.Request.get("method", None)
        assert mock_api.http.request.parameters == _TestConfig.Request.get("parameters", None)
        assert mock_api.http.response.value == _TestConfig.Response.get("value", None)


class TestHTTP:

    _mock_http_req: HTTPRequest = None
    _mock_http_resp: HTTPResponse = None

    @pytest.fixture(scope="function")
    def http(self) -> HTTP:
        return HTTP(request=self.mock_http_req, response=self.mock_http_resp)

    @property
    def mock_http_req(self) -> HTTPRequest:
        if not self._mock_http_req:
            self._mock_http_req = HTTPRequest(
                method=_TestConfig.Request.get("method"), parameters=_TestConfig.Request.get("parameters", {})
            )
        return self._mock_http_req

    @property
    def mock_http_resp(self) -> HTTPResponse:
        if not self._mock_http_resp:
            self._mock_http_resp = HTTPResponse(value=_TestConfig.Response.get("value"))
        return self._mock_http_resp

    def test_request(self, http: HTTP):
        assert http.request == self.mock_http_req, _assertion_msg

    def test_response(self, http: HTTP):
        assert http.response == self.mock_http_resp, _assertion_msg

    def test_serialize(self, http: HTTP):
        assert http.serialize() == _TestConfig.Http

    def test_deserialize(self, http: HTTP):
        http = http.deserialize(data=_TestConfig.Http)
        assert isinstance(http, HTTP)
        assert http.request.method == _TestConfig.Request.get("method", None)
        assert http.request.parameters == _TestConfig.Request.get("parameters", None)
        assert http.response.value == _TestConfig.Response.get("value", None)


class TestHTTPReqeust:
    @pytest.fixture(scope="function")
    def http_req(self) -> HTTPRequest:
        return HTTPRequest(
            method=_TestConfig.Request.get("method", None), parameters=_TestConfig.Request.get("parameters", {})
        )

    def test_method(self, http_req: HTTPRequest):
        assert http_req.method == _TestConfig.Request.get("method", None), _assertion_msg

    def test_parameters(self, http_req: HTTPRequest):
        assert http_req.parameters == _TestConfig.Request.get("parameters", {}), _assertion_msg

    def test_serialize(self, http_req: HTTPRequest):
        assert http_req.serialize() == _TestConfig.Request

    def test_deserialize(self, http_req: HTTPRequest):
        resp = http_req.deserialize(data=_TestConfig.Request)
        assert isinstance(resp, HTTPRequest)
        assert resp.method == _TestConfig.Request.get("method", None)
        assert resp.parameters == _TestConfig.Request.get("parameters", None)


class TestHTTPResponse:
    @pytest.fixture(scope="function")
    def http_resp(self) -> HTTPResponse:
        return HTTPResponse(value=_Test_HTTP_Resp)

    def test_value(self, http_resp: HTTPResponse):
        assert http_resp.value == _Test_HTTP_Resp, _assertion_msg

    def test_serialize(self, http_resp: HTTPResponse):
        assert http_resp.serialize() == _TestConfig.Response

    def test_deserialize(self, http_resp: HTTPResponse):
        resp = http_resp.deserialize(data=_TestConfig.Response)
        assert isinstance(resp, HTTPResponse)
        assert resp.value == _TestConfig.Response.get("value", None)
