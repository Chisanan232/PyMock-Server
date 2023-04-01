import re
from abc import ABCMeta, abstractmethod
from typing import Any, Dict, Optional, Union
from unittest.mock import Mock, patch

import pytest

from pymock_api.model.api_config import (
    HTTP,
    APIConfig,
    BaseConfig,
    HTTPRequest,
    HTTPResponse,
    MockAPI,
    MockAPIs,
    _Config,
)

from ..._values import (
    APIConfigValue,
    _Base_URL,
    _Config_Description,
    _Config_Name,
    _Test_Config,
    _Test_HTTP_Resp,
    _Test_URL,
    _TestConfig,
)

_assertion_msg = "Its property's value should be same as we set."
MOCK_RETURN_VALUE: Mock = Mock()


def test_config_get_prop():
    class FakeConfig(_Config):
        def _compare(self, other: "_Config") -> bool:
            pass

        def serialize(self, data: Optional["_Config"] = None) -> Optional[Dict[str, Any]]:
            pass

        def deserialize(self, data: Dict[str, Any]) -> Optional["_Config"]:
            pass

    class Dummy:
        pass

    with pytest.raises(AttributeError) as exc_info:
        FakeConfig()._get_prop(data=Dummy(), prop="not_exist_prop")
    assert re.search(r"Cannot find attribute", str(exc_info.value), re.IGNORECASE)


class ConfigTestSpec(metaclass=ABCMeta):
    @pytest.fixture(scope="function")
    @abstractmethod
    def sut(self) -> _Config:
        pass

    @pytest.fixture(scope="function")
    @abstractmethod
    def sut_with_nothing(self) -> _Config:
        pass

    def test_eq_operation_with_valid_object(self, sut: _Config, sut_with_nothing: _Config):
        assert sut != sut_with_nothing

    def test_eq_operation_with_invalid_object(self, sut: _Config):
        with pytest.raises(TypeError) as exc_info:
            sut == "Invalid object"
        assert re.search(r"data types is different", str(exc_info), re.IGNORECASE)

    @abstractmethod
    def test_value_attributes(self, sut: _Config):
        pass

    def test_serialize(self, sut: _Config):
        assert sut.serialize() == self._expected_serialize_value()

    @abstractmethod
    def _expected_serialize_value(self) -> Any:
        pass

    def test_serialize_with_none(self, sut_with_nothing: _Config):
        assert sut_with_nothing.serialize() is None

    def test_deserialize(self, sut_with_nothing: _Config):
        obj = sut_with_nothing.deserialize(data=self._expected_serialize_value())
        self._expected_deserialize_value(obj)

    @abstractmethod
    def _expected_deserialize_value(self, obj: _Config) -> None:
        pass

    def test_deserialize_with_invalid_data(self, sut_with_nothing: _Config):
        assert sut_with_nothing.deserialize(data={}) is None


class TestAPIConfig(ConfigTestSpec):
    _test_value: APIConfigValue = APIConfigValue()
    _mock_mock_apis: MockAPIs = None

    @pytest.fixture(scope="function")
    def sut(self) -> APIConfig:
        return APIConfig(name=_Config_Name, description=_Config_Description, apis=self.mock_mock_apis)

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> APIConfig:
        return APIConfig()

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

    def test___len___with_value(self, sut: APIConfig):
        sut.apis = _TestConfig.Mock_APIs
        assert len(sut) == len(
            list(filter(lambda k: k != "base", _TestConfig.Mock_APIs.keys()))
        ), "The size of *APIConfig* data object should be same as *MockAPIs* data object."

    def test___len___with_non_value(self):
        assert len(APIConfig()) == 0, "The size of *APIConfig* data object should be '0' if property *apis* is None."

    def test_has_apis_with_value(self, sut: APIConfig):
        sut.apis = _TestConfig.Mock_APIs
        assert sut.has_apis() is True, "It should be 'True' if its property *apis* has value."

    def test_has_apis_with_no_value(self):
        assert APIConfig().has_apis() is False, "It should be 'False' if its property *apis* is None."

    def test_value_attributes(self, sut: APIConfig):
        assert sut.name == _Config_Name, _assertion_msg
        assert sut.description == _Config_Description, _assertion_msg
        assert sut.apis.base.url == _TestConfig.API_Config.get("mocked_apis").get("base").get("url"), _assertion_msg
        assert list(sut.apis.apis.keys())[0] in _TestConfig.API_Config.get("mocked_apis").keys(), _assertion_msg

    @pytest.mark.parametrize(
        ("setting_val", "should_call_deserialize"),
        [
            ({}, False),
            ({"test": "test"}, True),
            (Mock(MockAPIs()), False),
        ],
    )
    @patch.object(MockAPIs, "deserialize", return_value=MOCK_RETURN_VALUE)
    def test_prop_apiswith_valid_obj(
        self,
        mock_deserialize: Mock,
        setting_val: Union[dict, BaseConfig],
        should_call_deserialize: bool,
        sut_with_nothing: APIConfig,
    ):
        # Run target function
        sut_with_nothing.apis = setting_val
        # Verify the running result
        if should_call_deserialize:
            mock_deserialize.assert_called_once_with(data=setting_val)
            assert sut_with_nothing.apis == MOCK_RETURN_VALUE
        else:
            mock_deserialize.assert_not_called()
            assert sut_with_nothing.apis == setting_val

    @patch.object(MockAPIs, "deserialize", return_value=MOCK_RETURN_VALUE)
    def test_prop_apis_with_invalid_obj(self, mock_deserialize: Mock, sut_with_nothing: APIConfig):
        with pytest.raises(TypeError) as exc_info:
            sut_with_nothing.apis = "Invalid object"
        mock_deserialize.assert_not_called()
        assert re.search(r"Setter .{1,32} only accepts .{1,32} type object.", str(exc_info.value), re.IGNORECASE)

    def _expected_serialize_value(self) -> dict:
        return _TestConfig.API_Config

    def _expected_deserialize_value(self, obj: APIConfig) -> None:
        assert isinstance(obj, APIConfig)
        assert obj.name == _Config_Name
        assert obj.description == _Config_Description
        assert obj.apis.base.url == _TestConfig.API_Config.get("mocked_apis").get("base").get("url")
        assert list(obj.apis.apis.keys())[0] in _TestConfig.API_Config.get("mocked_apis").keys(), _assertion_msg

    @patch("pymock_api._utils.file_opt.YAML.read", return_value=_TestConfig.API_Config)
    def test_from_yaml_file(self, mock_read_yaml: Mock, sut: APIConfig):
        config = sut.from_yaml(path="test-api.yaml")
        mock_read_yaml.assert_called_once_with("test-api.yaml")
        assert isinstance(config, APIConfig)
        assert config.name == _Config_Name
        assert config.description == _Config_Description
        assert config.apis.serialize() == _TestConfig.Mock_APIs

    @patch("pymock_api._utils.file_opt.YAML.write", return_value=None)
    def test_to_yaml_file(self, mock_write_yaml: Mock, sut: APIConfig):
        sut.to_yaml(path=_Test_Config)
        mock_write_yaml.assert_called_once_with(path=_Test_Config, config=sut.serialize())


class TestMockAPIs(ConfigTestSpec):
    _mock_base_config: BaseConfig = None
    _mock_mock_apis: Dict[str, MockAPI] = None

    @pytest.fixture(scope="function")
    def sut(self) -> MockAPIs:
        return MockAPIs(base=self.mock_base_config, apis=self.mock_mock_api)

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> MockAPIs:
        return MockAPIs()

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

    def test___len__(self, sut: MockAPIs):
        assert len(sut) == len(
            self.mock_mock_api.keys()
        ), f"The size of *MockAPIs* data object should be same as object '{self.mock_mock_api}'."

    def test_value_attributes(self, sut: MockAPIs):
        assert sut.base == self.mock_base_config, _assertion_msg
        assert sut.apis == self.mock_mock_api, _assertion_msg

    @pytest.mark.parametrize(
        ("setting_val", "should_call_deserialize"),
        [
            ({}, False),
            ({"test": "test"}, True),
            (Mock(BaseConfig()), False),
        ],
    )
    @patch.object(BaseConfig, "deserialize", return_value=MOCK_RETURN_VALUE)
    def test_prop_base_with_valid_obj(
        self,
        mock_deserialize: Mock,
        setting_val: Union[dict, BaseConfig],
        should_call_deserialize: bool,
        sut_with_nothing: MockAPIs,
    ):
        # Run target function
        sut_with_nothing.base = setting_val
        # Verify the running result
        if should_call_deserialize:
            mock_deserialize.assert_called_once_with(data=setting_val)
            assert sut_with_nothing.base == MOCK_RETURN_VALUE
        else:
            mock_deserialize.assert_not_called()
            assert sut_with_nothing.base == setting_val

    @patch.object(BaseConfig, "deserialize", return_value=MOCK_RETURN_VALUE)
    def test_prop_base_with_invalid_obj(self, mock_deserialize: Mock, sut_with_nothing: MockAPIs):
        with pytest.raises(TypeError) as exc_info:
            sut_with_nothing.base = "Invalid object"
        mock_deserialize.assert_not_called()
        assert re.search(r"Setter .{1,32} only accepts .{1,32} type object.", str(exc_info.value), re.IGNORECASE)

    @pytest.mark.parametrize(
        ("setting_val", "should_call_deserialize"),
        [
            ({}, False),
            ({"test": "test"}, True),
            ({"test": Mock(MockAPI())}, False),
        ],
    )
    @patch.object(MockAPI, "deserialize", return_value=MOCK_RETURN_VALUE)
    def test_prop_apis_with_valid_obj(
        self,
        mock_deserialize: Mock,
        setting_val: Union[dict, BaseConfig],
        should_call_deserialize: bool,
        sut_with_nothing: MockAPIs,
    ):
        # Run target function
        sut_with_nothing.apis = setting_val
        # Verify the running result
        if should_call_deserialize:
            expected_apis = {}
            for api_name, api_value in setting_val.items():
                mock_deserialize.assert_called_once_with(data=api_value)
                expected_apis[api_name] = MOCK_RETURN_VALUE
                assert sut_with_nothing.apis[api_name] == MOCK_RETURN_VALUE
            assert sut_with_nothing.apis == expected_apis
        else:
            mock_deserialize.assert_not_called()
            assert sut_with_nothing.apis == setting_val

    @pytest.mark.parametrize(
        ("setting_val", "expected_err", "err_msg_regex"),
        [
            ("Invalid object", TypeError, r"Setter .{1,32} only accepts .{1,32} type object."),
            ({"t1": "test", "t2": Mock(MockAPI())}, ValueError, r".{1,32} multiple types .{1,64} unify .{1,32} type"),
        ],
    )
    @patch.object(MockAPI, "deserialize", return_value=MOCK_RETURN_VALUE)
    def test_prop_apis_with_invalid_obj(
        self,
        mock_deserialize: Mock,
        setting_val: Union[str, dict],
        expected_err: Exception,
        err_msg_regex,
        sut_with_nothing: MockAPIs,
    ):
        with pytest.raises(expected_err) as exc_info:
            sut_with_nothing.apis = setting_val
        mock_deserialize.assert_not_called()
        assert re.search(err_msg_regex, str(exc_info.value), re.IGNORECASE)

    @pytest.mark.parametrize(
        "test_data",
        [
            {"base": "base_info"},
            {"base": "base_info", "api_name": "api_info"},
        ],
    )
    @patch.object(MockAPI, "deserialize", return_value=None)
    @patch.object(BaseConfig, "deserialize", return_value=None)
    def test_deserialize_with_nonideal_value(
        self, mock_deserialize_base: Mock, mock_deserialize_mock_api: Mock, test_data: dict, sut_with_nothing: MockAPIs
    ):
        assert sut_with_nothing.deserialize(data=test_data) is None
        if len(test_data.keys()) > 1:
            mock_deserialize_base.assert_called_once_with(data="base_info")
            mock_deserialize_mock_api.assert_called_once_with(data="api_info")
        else:
            mock_deserialize_base.assert_not_called()
            mock_deserialize_mock_api.assert_not_called()

    def _expected_serialize_value(self) -> Any:
        return _TestConfig.Mock_APIs

    def _expected_deserialize_value(self, obj: MockAPIs) -> None:
        assert isinstance(obj, MockAPIs)
        assert obj.base.url == _Base_URL
        assert obj.apis == self.mock_mock_api


class TestBaseConfig(ConfigTestSpec):
    @pytest.fixture(scope="function")
    def sut(self) -> BaseConfig:
        return BaseConfig(url=_Base_URL)

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> BaseConfig:
        return BaseConfig()

    def test_value_attributes(self, sut: BaseConfig):
        assert sut.url == _Base_URL, _assertion_msg

    def _expected_serialize_value(self) -> dict:
        return _TestConfig.Base

    def _expected_deserialize_value(self, obj: BaseConfig) -> None:
        assert isinstance(obj, BaseConfig)
        assert obj.url == _Base_URL


class TestMockAPI(ConfigTestSpec):
    _http: HTTP = None

    @pytest.fixture(scope="function")
    def sut(self) -> MockAPI:
        return MockAPI(url=_Test_URL, http=self.mock_http)

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> MockAPI:
        return MockAPI()

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

    def test_value_attributes(self, sut: MockAPI):
        assert sut.url == _Test_URL, _assertion_msg
        assert sut.http == self.mock_http, _assertion_msg

    @pytest.mark.parametrize(
        ("setting_val", "should_call_deserialize"),
        [
            ({"test": "test"}, True),
            (Mock(HTTP()), False),
        ],
    )
    @patch.object(HTTP, "deserialize", return_value=MOCK_RETURN_VALUE)
    def test_prop_http_with_valid_obj(
        self,
        mock_deserialize: Mock,
        setting_val: Union[dict, HTTP],
        should_call_deserialize: bool,
        sut_with_nothing: MockAPI,
    ):
        # Run target function
        sut_with_nothing.http = setting_val
        # Verify the running result
        if should_call_deserialize:
            mock_deserialize.assert_called_once_with(data=setting_val)
            assert sut_with_nothing.http == MOCK_RETURN_VALUE
        else:
            mock_deserialize.assert_not_called()
            assert sut_with_nothing.http == setting_val

    @patch.object(HTTP, "deserialize", return_value=MOCK_RETURN_VALUE)
    def test_prop_http_with_invalid_obj(self, mock_deserialize: Mock, sut_with_nothing: MockAPI):
        with pytest.raises(TypeError) as exc_info:
            sut_with_nothing.http = "Invalid object"
        mock_deserialize.assert_not_called()
        assert re.search(r"Setter .{1,32} only accepts .{1,32} type object.", str(exc_info.value), re.IGNORECASE)

    def _expected_serialize_value(self) -> dict:
        return _TestConfig.Mock_API

    def _expected_deserialize_value(self, obj: MockAPI) -> None:
        assert isinstance(obj, MockAPI)
        assert obj.url == _Test_URL
        assert obj.http.request.method == _TestConfig.Request.get("method", None)
        assert obj.http.request.parameters == _TestConfig.Request.get("parameters", None)
        assert obj.http.response.value == _TestConfig.Response.get("value", None)


class TestHTTP(ConfigTestSpec):
    _mock_http_req: HTTPRequest = None
    _mock_http_resp: HTTPResponse = None

    @pytest.fixture(scope="function")
    def sut(self) -> HTTP:
        return HTTP(request=self.mock_http_req, response=self.mock_http_resp)

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> HTTP:
        return HTTP()

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

    def test_value_attributes(self, sut: HTTP):
        assert sut.request == self.mock_http_req, _assertion_msg
        assert sut.response == self.mock_http_resp, _assertion_msg

    @pytest.mark.parametrize(
        ("setting_val", "should_call_deserialize"),
        [
            ({"test": "test"}, True),
            (Mock(HTTPRequest()), False),
        ],
    )
    @patch.object(HTTPRequest, "deserialize", return_value=MOCK_RETURN_VALUE)
    def test_prop_request_with_valid_obj(
        self,
        mock_deserialize: Mock,
        setting_val: Union[dict, HTTPRequest],
        should_call_deserialize: bool,
        sut_with_nothing: HTTP,
    ):
        # Run target function
        sut_with_nothing.request = setting_val
        # Verify the running result
        if should_call_deserialize:
            mock_deserialize.assert_called_once_with(data=setting_val)
            assert sut_with_nothing.request == MOCK_RETURN_VALUE
        else:
            mock_deserialize.assert_not_called()
            assert sut_with_nothing.request == setting_val

    @patch.object(HTTPRequest, "deserialize", return_value=MOCK_RETURN_VALUE)
    def test_prop_request_with_invalid_obj(self, mock_deserialize: Mock, sut_with_nothing: HTTP):
        with pytest.raises(TypeError) as exc_info:
            sut_with_nothing.request = "Invalid object"
        mock_deserialize.assert_not_called()
        assert re.search(r"Setter .{1,32} only accepts .{1,32} type object.", str(exc_info.value), re.IGNORECASE)

    @pytest.mark.parametrize(
        ("setting_val", "should_call_deserialize"),
        [
            ({"test": "test"}, True),
            (Mock(HTTPResponse()), False),
        ],
    )
    @patch.object(HTTPResponse, "deserialize", return_value=MOCK_RETURN_VALUE)
    def test_prop_response_with_valid_obj(
        self,
        mock_deserialize: Mock,
        setting_val: Union[dict, HTTPResponse],
        should_call_deserialize: bool,
        sut_with_nothing: HTTP,
    ):
        # Run target function
        sut_with_nothing.response = setting_val
        # Verify the running result
        if should_call_deserialize:
            mock_deserialize.assert_called_once_with(data=setting_val)
            assert sut_with_nothing.response == MOCK_RETURN_VALUE
        else:
            mock_deserialize.assert_not_called()
            assert sut_with_nothing.response == setting_val

    @patch.object(HTTPResponse, "deserialize", return_value=MOCK_RETURN_VALUE)
    def test_prop_response_with_invalid_obj(self, mock_deserialize: Mock, sut_with_nothing: HTTP):
        with pytest.raises(TypeError) as exc_info:
            sut_with_nothing.response = "Invalid object"
        mock_deserialize.assert_not_called()
        assert re.search(r"Setter .{1,32} only accepts .{1,32} type object.", str(exc_info.value), re.IGNORECASE)

    def _expected_serialize_value(self) -> dict:
        return _TestConfig.Http

    def _expected_deserialize_value(self, obj: HTTP) -> None:
        assert isinstance(obj, HTTP)
        assert obj.request.method == _TestConfig.Request.get("method", None)
        assert obj.request.parameters == _TestConfig.Request.get("parameters", None)
        assert obj.response.value == _TestConfig.Response.get("value", None)


class TestHTTPReqeust(ConfigTestSpec):
    @pytest.fixture(scope="function")
    def sut(self) -> HTTPRequest:
        return HTTPRequest(
            method=_TestConfig.Request.get("method", None), parameters=_TestConfig.Request.get("parameters", {})
        )

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> HTTPRequest:
        return HTTPRequest()

    def test_value_attributes(self, sut: HTTPRequest):
        assert sut.method == _TestConfig.Request.get("method", None), _assertion_msg
        assert sut.parameters == _TestConfig.Request.get("parameters", {}), _assertion_msg

    def _expected_serialize_value(self) -> dict:
        return _TestConfig.Request

    def _expected_deserialize_value(self, obj: HTTPRequest) -> None:
        assert isinstance(obj, HTTPRequest)
        assert obj.method == _TestConfig.Request.get("method", None)
        assert obj.parameters == _TestConfig.Request.get("parameters", None)


class TestHTTPResponse(ConfigTestSpec):
    @pytest.fixture(scope="function")
    def sut(self) -> HTTPResponse:
        return HTTPResponse(value=_Test_HTTP_Resp)

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> HTTPResponse:
        return HTTPResponse()

    def test_value_attributes(self, sut: HTTPResponse):
        assert sut.value == _Test_HTTP_Resp, _assertion_msg

    def _expected_serialize_value(self) -> dict:
        return _TestConfig.Response

    def _expected_deserialize_value(self, obj: HTTPResponse) -> None:
        assert isinstance(obj, HTTPResponse)
        assert obj.value == _TestConfig.Response.get("value", None)
