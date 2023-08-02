import re
from abc import ABCMeta, abstractmethod
from typing import Any, Dict, List, Optional, Union
from unittest.mock import Mock, patch

import pytest

from pymock_api._utils import YAML
from pymock_api._utils.file_opt import JSON
from pymock_api.model.api_config import (
    HTTP,
    APIConfig,
    APIParameter,
    BaseConfig,
    HTTPRequest,
    HTTPResponse,
    MockAPI,
    MockAPIs,
    _Config,
)
from pymock_api.model.enums import Format

from ..._values import (
    _Base_URL,
    _Config_Description,
    _Config_Name,
    _Test_API_Parameter,
    _Test_Config,
    _Test_HTTP_Resp,
    _Test_URL,
    _TestConfig,
)

_assertion_msg = "Its property's value should be same as we set."
MOCK_RETURN_VALUE: Mock = Mock()


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (None, None),
        ({}, {}),
        ({"any_key": "any_value"}, {"any_key": "any_value", "flag": "has run *test_function*"}),
    ],
)
def test_ensure_process_with_not_empty_value(data: Optional[Dict[str, str]], expected: Optional[Dict[str, str]]):
    class FakeObject:
        @_Config._ensure_process_with_not_empty_value
        def test_function(self, data: Dict[str, Any]) -> Any:
            data["flag"] = "has run *test_function*"
            return data

    fo = FakeObject()
    assert fo.test_function(data=data) == expected


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


class MockModel:
    @property
    def mock_apis(self) -> MockAPIs:
        return MockAPIs(base=self.base_config, apis=self.mock_api)

    @property
    def base_config(self) -> BaseConfig:
        return BaseConfig(url=_Base_URL)

    @property
    def mock_api(self) -> Dict[str, MockAPI]:
        return {"test_config": MockAPI(url=_Test_URL, http=self.http)}

    @property
    def http(self) -> HTTP:
        return HTTP(request=self.http_request, response=self.http_response)

    @property
    def http_request(self) -> HTTPRequest:
        return HTTPRequest(method=_TestConfig.Request.get("method"), parameters=[self.api_parameter])

    @property
    def api_parameter(self) -> APIParameter:
        return APIParameter(
            name=_Test_API_Parameter["name"],
            required=_Test_API_Parameter["required"],
            default=_Test_API_Parameter["default"],
            value_type=_Test_API_Parameter["type"],
            value_format=_Test_API_Parameter["format"],
        )

    @property
    def http_response(self) -> HTTPResponse:
        return HTTPResponse(value=_Test_HTTP_Resp)


class ConfigTestSpec(metaclass=ABCMeta):
    _Mock_Model = MockModel()

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
        assert sut_with_nothing.deserialize(data={}) == {}


class TestAPIConfig(ConfigTestSpec):
    @pytest.fixture(scope="function")
    def sut(self) -> APIConfig:
        return APIConfig(name=_Config_Name, description=_Config_Description, apis=self._Mock_Model.mock_apis)

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> APIConfig:
        return APIConfig()

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
            assert sut_with_nothing.apis == (setting_val if setting_val else None)

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
    @pytest.fixture(scope="function")
    def sut(self) -> MockAPIs:
        return MockAPIs(base=self._Mock_Model.base_config, apis=self._Mock_Model.mock_api)

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> MockAPIs:
        return MockAPIs()

    def test___len__(self, sut: MockAPIs):
        assert len(sut) == len(
            self._Mock_Model.mock_api.keys()
        ), f"The size of *MockAPIs* data object should be same as object '{self._Mock_Model.mock_api}'."

    def test_value_attributes(self, sut: MockAPIs):
        assert sut.base == self._Mock_Model.base_config, _assertion_msg
        assert sut.apis == self._Mock_Model.mock_api, _assertion_msg

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
            assert sut_with_nothing.base == (setting_val if setting_val else None)

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
        assert sut_with_nothing.deserialize(data=test_data) is not None
        mock_deserialize_base.assert_called_once_with(data="base_info")
        if len(test_data.keys()) > 1:
            mock_deserialize_mock_api.assert_called_once_with(data="api_info")
        else:
            mock_deserialize_mock_api.assert_not_called()

    def _expected_serialize_value(self) -> Any:
        return _TestConfig.Mock_APIs

    def _expected_deserialize_value(self, obj: MockAPIs) -> None:
        assert isinstance(obj, MockAPIs)
        assert obj.base.url == _Base_URL
        assert obj.apis == self._Mock_Model.mock_api

    def test_get_api_config_by_url(self, sut: MockAPIs):
        api_config = sut.get_api_config_by_url(url=_Test_URL)
        assert api_config.url == _Test_URL
        assert api_config.http.request.method == _TestConfig.Request.get("method")
        assert api_config.http.request.parameters == [self._Mock_Model.api_parameter]
        assert api_config.http.response.value == _Test_HTTP_Resp

    def test_fail_get_api_config_by_url(self, sut: MockAPIs):
        api_config = sut.get_api_config_by_url(url="Not exist this path's API config")
        assert api_config is None


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
    @pytest.fixture(scope="function")
    def sut(self) -> MockAPI:
        return MockAPI(url=_Test_URL, http=self._Mock_Model.http)

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> MockAPI:
        return MockAPI()

    def test_value_attributes(self, sut: MockAPI):
        assert sut.url == _Test_URL, _assertion_msg
        assert sut.http == self._Mock_Model.http, _assertion_msg

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
        assert obj.http.request.parameters == [self._Mock_Model.api_parameter]
        assert obj.http.response.value == _TestConfig.Response.get("value", None)

    @pytest.mark.parametrize(
        ("formatter", "format_object"),
        [
            (Format.JSON, JSON),
            (Format.YAML, YAML),
        ],
    )
    def test_valid_format(self, formatter: str, format_object, sut: MockAPI):
        with patch.object(format_object, "serialize") as mock_formatter:
            format_str = sut.format(formatter)
            assert format_str
            mock_formatter.assert_called_once_with(sut.serialize())

    def test_invalid_format(self, sut: MockAPI):
        invalid_format = "not support or invalid format type"
        with pytest.raises(ValueError) as exc_info:
            sut.format(invalid_format)
        assert re.search(r".{0,64}not support.{0,64}" + re.escape(invalid_format), str(exc_info.value), re.IGNORECASE)

    @pytest.mark.parametrize("http_req", [None, HTTP(), HTTP(request=HTTPRequest())])
    def test_set_valid_request(self, http_req: Optional[HTTPRequest], sut_with_nothing: MockAPI):
        # Pro-process
        sut_with_nothing.http = http_req

        assert sut_with_nothing.http == http_req
        ut_method = "POST"
        ut_parameters = [{"name": "arg1", "required": False, "default": "val1", "type": "str"}]
        sut_with_nothing.set_request(method=ut_method, parameters=ut_parameters)

        assert sut_with_nothing.http
        assert sut_with_nothing.http.request
        assert sut_with_nothing.http.request.method == ut_method
        assert sut_with_nothing.http.request.parameters == [
            APIParameter(name="arg1", required=False, default="val1", value_type="str")
        ]

    @pytest.mark.parametrize(
        "api_params",
        [
            None,
            [],
            [{"name": "arg1", "required": False, "default": "val1", "type": "str"}],
            [APIParameter(name="arg2", required=False, default=0, value_type="int")],
            [
                {"name": "arg1", "required": False, "default": "val1", "type": "str"},
                APIParameter(name="arg2", required=False, default=0, value_type="int"),
            ],
        ],
    )
    def test_set_valid_request_with_params(
        self, api_params: Optional[List[Union[dict, APIParameter]]], sut_with_nothing: MockAPI
    ):
        ut_method = "POST"
        ut_parameters = api_params
        sut_with_nothing.set_request(method=ut_method, parameters=ut_parameters)

        assert sut_with_nothing.http
        assert sut_with_nothing.http.request
        assert sut_with_nothing.http.request.method == ut_method
        api_params_in_config = sut_with_nothing.http.request.parameters
        assert len(api_params_in_config) == len(api_params or [])
        if api_params:
            for p in api_params_in_config:
                one_params = list(
                    filter(lambda _p: p.name == (_p.name if isinstance(_p, APIParameter) else _p["name"]), api_params)
                )
                assert one_params
                expect_param = one_params[0]
                assert p.name == (expect_param.name if isinstance(expect_param, APIParameter) else expect_param["name"])
                assert p.required is (
                    expect_param.required if isinstance(expect_param, APIParameter) else expect_param["required"]
                )
                assert p.value_type == (
                    expect_param.value_type if isinstance(expect_param, APIParameter) else expect_param["type"]
                )
                assert p.default == (
                    expect_param.default if isinstance(expect_param, APIParameter) else expect_param["default"]
                )

    @pytest.mark.parametrize(
        "params",
        [
            {"name": "arg1", "required": False, "default": "val1", "type": "str", "invalid_key": ""},
            {"name": "arg1", "required": False, "default": "val1", "value_type": "str"},
        ],
    )
    def test_set_invalid_request(self, params: dict, sut_with_nothing: MockAPI):
        ut_method = "POST"
        ut_parameters = [params]
        with pytest.raises(ValueError) as exc_info:
            sut_with_nothing.set_request(method=ut_method, parameters=ut_parameters)
        assert re.search(r".{1,64}format.{1,64}is incorrect.{1,64}", str(exc_info.value), re.IGNORECASE)

    @pytest.mark.parametrize("http_resp", [None, HTTP(), HTTP(response=HTTPResponse())])
    def test_set_response(self, http_resp: Optional[HTTPResponse], sut_with_nothing: MockAPI):
        # Pro-process
        sut_with_nothing.http = http_resp

        assert sut_with_nothing.http == http_resp
        ut_value = "PyTest response"
        sut_with_nothing.set_response(value=ut_value)

        assert sut_with_nothing.http
        assert sut_with_nothing.http.response
        assert sut_with_nothing.http.response.value == ut_value


class TestHTTP(ConfigTestSpec):
    @pytest.fixture(scope="function")
    def sut(self) -> HTTP:
        return HTTP(request=self._Mock_Model.http_request, response=self._Mock_Model.http_response)

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> HTTP:
        return HTTP()

    def test_value_attributes(self, sut: HTTP):
        assert sut.request == self._Mock_Model.http_request, _assertion_msg
        assert sut.response == self._Mock_Model.http_response, _assertion_msg

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
        assert obj.request.parameters == [self._Mock_Model.api_parameter]
        assert obj.response.value == _TestConfig.Response.get("value", None)


class TestHTTPReqeust(ConfigTestSpec):
    @pytest.fixture(scope="function")
    def sut(self) -> HTTPRequest:
        return HTTPRequest(method=_TestConfig.Request.get("method", None), parameters=[self._Mock_Model.api_parameter])

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> HTTPRequest:
        return HTTPRequest()

    def test_value_attributes(self, sut: HTTPRequest):
        assert sut.method == _TestConfig.Request.get("method", None), _assertion_msg
        assert sut.parameters == [self._Mock_Model.api_parameter], _assertion_msg

    def _expected_serialize_value(self) -> dict:
        return _TestConfig.Request

    def _expected_deserialize_value(self, obj: HTTPRequest) -> None:
        assert isinstance(obj, HTTPRequest)
        assert obj.method == _TestConfig.Request.get("method", None)
        assert obj.parameters == [self._Mock_Model.api_parameter]

    def test_deserialize_fail(self, sut_with_nothing: HTTPRequest):
        utd = {
            "method": "HTTP method",
            "parameters": "a value which data type is not list",
        }
        with pytest.raises(TypeError) as exc_info:
            sut_with_nothing.deserialize(data=utd)
        assert str(exc_info.value) == "Argument *parameters* should be a list type value."

    def test_get_one_param_by_name(self, sut: HTTPRequest):
        param = sut.get_one_param_by_name(_Test_API_Parameter["name"])
        assert param == self._Mock_Model.api_parameter

    def test_fail_get_one_param_by_name(self, sut: HTTPRequest):
        param = sut.get_one_param_by_name("Not exist argument")
        assert param is None


class TestAPIParameter(ConfigTestSpec):
    @pytest.fixture(scope="function")
    def sut(self) -> APIParameter:
        return APIParameter(
            name=_Test_API_Parameter["name"],
            required=_Test_API_Parameter["required"],
            default=_Test_API_Parameter["default"],
            value_type=_Test_API_Parameter["type"],
            value_format=_Test_API_Parameter["format"],
        )

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> APIParameter:
        return APIParameter()

    def test_value_attributes(self, sut: APIParameter):
        assert sut.name == _Test_API_Parameter["name"], _assertion_msg
        assert sut.required is _Test_API_Parameter["required"], _assertion_msg
        assert sut.default == _Test_API_Parameter["default"], _assertion_msg
        assert sut.value_type == _Test_API_Parameter["type"], _assertion_msg
        assert sut.value_format == _Test_API_Parameter["format"], _assertion_msg

    def _expected_serialize_value(self) -> dict:
        return _Test_API_Parameter

    def _expected_deserialize_value(self, obj: APIParameter) -> None:
        assert isinstance(obj, APIParameter)
        assert obj.name == _Test_API_Parameter["name"]
        assert obj.required is _Test_API_Parameter["required"]
        assert obj.default == _Test_API_Parameter["default"]
        assert obj.value_type == _Test_API_Parameter["type"]
        assert obj.value_format == _Test_API_Parameter["format"]


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
