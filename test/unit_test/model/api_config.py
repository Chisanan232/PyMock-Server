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
    _Mock_APIs,
    _Test_HTTP_Method,
    _Test_HTTP_Req_Params,
    _Test_HTTP_Resp,
    _Test_URL,
)

_assertion_msg = "Its property's value should be same as we set."


class TestAPIConfig:

    _test_value: APIConfigValue = APIConfigValue()

    @pytest.fixture(scope="function")
    def api_config(self) -> APIConfig:
        return APIConfig(
            name=self._test_value.name, description=self._test_value.description, apis=self._test_value.apis
        )

    def test___len___with_value(self, api_config: APIConfig):
        api_config.apis = _Mock_APIs.keys()
        assert len(api_config) == len(
            _Mock_APIs.keys()
        ), "The size of *APIConfig* data object should be same as *MockAPIs* data object."

    def test___len___with_non_value(self, api_config: APIConfig):
        api_config.apis = None
        assert len(api_config) == 0, "The size of *APIConfig* data object should be '0' if property *apis* is None."

    def test_has_apis_with_value(self, api_config: APIConfig):
        api_config.apis = _Mock_APIs.keys()
        assert api_config.has_apis() is True, "It should be 'True' if its property *apis* has value."

    def test_has_apis_with_no_value(self, api_config: APIConfig):
        api_config.apis = None
        assert api_config.has_apis() is False, "It should be 'False' if its property *apis* is None."

    def test_name(self, api_config: APIConfig):
        assert api_config.name == self._test_value.name, _assertion_msg

    def test_description(self, api_config: APIConfig):
        assert api_config.description == self._test_value.description, _assertion_msg

    def test_apis(self, api_config: APIConfig):
        assert api_config.apis == _Mock_APIs, _assertion_msg


class TestMockAPIs:

    _mock_base_config: Mock = None

    @pytest.fixture(scope="function")
    def mock_apis(self) -> MockAPIs:
        return MockAPIs(base=self.mock_base_config, apis=_Mock_APIs)

    @property
    def mock_base_config(self) -> Mock:
        if not self._mock_base_config:
            self._mock_base_config = Mock(BaseConfig(url=_Base_URL))
        return self._mock_base_config

    def test___len__(self, mock_apis: MockAPIs):
        assert len(mock_apis) == len(
            _Mock_APIs.keys()
        ), f"The size of *MockAPIs* data object should be same as object '{_Mock_APIs}'."

    def test_base(self, mock_apis: MockAPIs):
        assert mock_apis.base == self.mock_base_config, _assertion_msg

    def test_apis(self, mock_apis: MockAPIs):
        assert mock_apis.apis == _Mock_APIs, _assertion_msg


class TestBaseConfig:
    @pytest.fixture(scope="function")
    def base_config(self) -> BaseConfig:
        return BaseConfig(url=_Base_URL)

    def test_url(self, base_config: BaseConfig):
        assert base_config.url == _Base_URL, _assertion_msg


class TestMockAPI:

    _http: Mock = None

    @pytest.fixture(scope="function")
    def mock_api(self) -> MockAPI:
        return MockAPI(url=_Test_URL, http=self.mock_http)

    @property
    def mock_http(self) -> Mock:
        if not self._http:
            self._http = Mock(HTTP(request=Mock(), response=Mock()))
        return self._http

    def test_url(self, mock_api: MockAPI):
        assert mock_api.url == _Test_URL, _assertion_msg

    def test_http(self, mock_api: MockAPI):
        assert mock_api.http == self.mock_http, _assertion_msg


class TestHTTP:

    _mock_http_req: Mock = None
    _mock_http_resp: Mock = None

    @pytest.fixture(scope="function")
    def http(self) -> HTTP:
        return HTTP(request=self.mock_http_req, response=self.mock_http_resp)

    @property
    def mock_http_req(self) -> Mock:
        if not self._mock_http_req:
            self._mock_http_req = Mock(HTTPRequest(method=Mock()))
        return self._mock_http_req

    @property
    def mock_http_resp(self) -> Mock:
        if not self._mock_http_resp:
            self._mock_http_resp = Mock(HTTPResponse(value=Mock()))
        return self._mock_http_resp

    def test_request(self, http: HTTP):
        assert http.request == self.mock_http_req, _assertion_msg

    def test_response(self, http: HTTP):
        assert http.response == self.mock_http_resp, _assertion_msg


class TestHTTPReqeust:
    @pytest.fixture(scope="function")
    def http_req(self) -> HTTPRequest:
        return HTTPRequest(method=_Test_HTTP_Method)

    def test_method(self, http_req: HTTPRequest):
        assert http_req.method == _Test_HTTP_Method, _assertion_msg

    def test_parameters(self, http_req: HTTPRequest):
        assert http_req.parameters == {}, "Its default value should be empty dict object."
        http_req.parameters = _Test_HTTP_Req_Params
        assert http_req.parameters == _Test_HTTP_Req_Params, _assertion_msg


class TestHTTPResponse:
    @pytest.fixture(scope="function")
    def http_resp(self) -> HTTPResponse:
        return HTTPResponse(value=_Test_HTTP_Resp)

    def test_value(self, http_resp: HTTPResponse):
        assert http_resp.value == _Test_HTTP_Resp, _assertion_msg
