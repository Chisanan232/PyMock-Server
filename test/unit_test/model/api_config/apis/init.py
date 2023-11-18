import re
from typing import List, Optional, Union
from unittest.mock import Mock, patch

import pytest

from pymock_api._utils import JSON, YAML
from pymock_api._utils.file_opt import _BaseFileOperation
from pymock_api.model import HTTP, MockAPI
from pymock_api.model.api_config import ResponseProperty
from pymock_api.model.api_config.apis import APIParameter, HTTPRequest, HTTPResponse
from pymock_api.model.enums import Format, ResponseStrategy

from ....._values import _Test_Response_Properties, _Test_Tag, _Test_URL, _TestConfig
from .._base import (
    MOCK_MODEL,
    MOCK_RETURN_VALUE,
    CheckableTestSuite,
    DividableTestSuite,
    MockModel,
    _assertion_msg,
    set_checking_test_data,
)
from ..template import TemplatableConfigTestSuite

_MockAPI_Test_Data: List[tuple] = []
_HTTP_Test_Data: List[tuple] = []


def reset_mock_api_test_data() -> None:
    global _MockAPI_Test_Data
    _MockAPI_Test_Data.clear()


def add_mock_api_test_data(test_scenario: tuple) -> None:
    global _MockAPI_Test_Data
    _MockAPI_Test_Data.append(test_scenario)


def reset_http_test_data() -> None:
    global _HTTP_Test_Data
    _HTTP_Test_Data.clear()


def add_http_test_data(test_scenario: tuple) -> None:
    global _HTTP_Test_Data
    _HTTP_Test_Data.append(test_scenario)


class TestMockAPI(TemplatableConfigTestSuite, CheckableTestSuite, DividableTestSuite):
    test_data_dir = "api"
    set_checking_test_data(
        test_data_dir, reset_callback=reset_mock_api_test_data, opt_globals_callback=add_mock_api_test_data
    )

    @pytest.fixture(scope="function")
    def sut(self) -> MockAPI:
        return MockAPI(url=_Test_URL, http=self._Mock_Model.http, tag=_Test_Tag)

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

    @pytest.mark.parametrize("invalid_value", [[], (), 123])
    def test_prop_tag_with_invalid_obj(self, invalid_value: object, sut_with_nothing: MockAPI):
        with pytest.raises(TypeError) as exc_info:
            sut_with_nothing.tag = invalid_value
        assert re.search("only accepts str type value", str(exc_info.value), re.IGNORECASE)

    def _expected_serialize_value(self) -> dict:
        return _TestConfig.Mock_API

    def _expected_deserialize_value(self, obj: MockAPI) -> None:
        assert isinstance(obj, MockAPI)
        assert obj.url == _Test_URL
        assert obj.http.request.method == _TestConfig.Request.get("method", None)
        assert obj.http.request.parameters == [self._Mock_Model.api_parameter]
        assert obj.http.response.value == _TestConfig.Response.get("value", None)
        assert obj.tag == _Test_Tag

    @pytest.mark.parametrize(
        ("formatter", "format_object"),
        [
            (Format.JSON, JSON),
            (Format.YAML, YAML),
        ],
    )
    def test_valid_format(self, formatter: str, format_object: _BaseFileOperation, sut: MockAPI):
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
        assert sut_with_nothing.tag == ""

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
        assert sut_with_nothing.tag == ""

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

    @pytest.mark.parametrize(
        ("http_resp", "response_strategy", "response_value"),
        [
            # string strategy response
            (None, ResponseStrategy.STRING, "PyTest response"),
            (HTTP(), ResponseStrategy.STRING, "PyTest response"),
            (HTTP(response=HTTPResponse(strategy=ResponseStrategy.STRING)), ResponseStrategy.STRING, "PyTest response"),
            # file strategy response
            (None, ResponseStrategy.FILE, "File path"),
            (HTTP(), ResponseStrategy.FILE, "File path"),
            (HTTP(response=HTTPResponse(strategy=ResponseStrategy.STRING)), ResponseStrategy.FILE, "File path"),
            # object strategy response with object value
            (None, ResponseStrategy.OBJECT, MockModel().response_properties),
            (HTTP(), ResponseStrategy.OBJECT, MockModel().response_properties),
            (
                HTTP(response=HTTPResponse(strategy=ResponseStrategy.STRING)),
                ResponseStrategy.OBJECT,
                MockModel().response_properties,
            ),
            # object strategy response with dict value
            (None, ResponseStrategy.OBJECT, _Test_Response_Properties),
            (HTTP(), ResponseStrategy.OBJECT, _Test_Response_Properties),
            (
                HTTP(response=HTTPResponse(strategy=ResponseStrategy.STRING)),
                ResponseStrategy.OBJECT,
                _Test_Response_Properties,
            ),
        ],
    )
    def test_set_valid_response(
        self,
        http_resp: Optional[HTTPResponse],
        response_strategy: ResponseStrategy,
        response_value: Union[str, list],
        sut_with_nothing: MockAPI,
    ):
        # Pro-process
        sut_with_nothing.http = http_resp

        assert sut_with_nothing.http == http_resp
        if response_strategy is ResponseStrategy.OBJECT:
            sut_with_nothing.set_response(strategy=response_strategy, iterable_value=response_value)
        else:
            sut_with_nothing.set_response(strategy=response_strategy, value=response_value)

        assert sut_with_nothing.http
        assert sut_with_nothing.http.response
        if response_strategy is ResponseStrategy.STRING:
            under_test_response_value = sut_with_nothing.http.response.value
        elif response_strategy is ResponseStrategy.FILE:
            under_test_response_value = sut_with_nothing.http.response.path
        elif response_strategy is ResponseStrategy.OBJECT:
            under_test_response_value = sut_with_nothing.http.response.properties
            response_value = [ResponseProperty().deserialize(v) if isinstance(v, dict) else v for v in response_value]
        else:
            assert False, "Invalid response strategy."
        assert under_test_response_value == response_value
        assert sut_with_nothing.tag == ""

    def test_set_invalid_response(self, sut_with_nothing: MockAPI):
        with pytest.raises(TypeError) as exc_info:
            sut_with_nothing.set_response(strategy="Invalid response strategy")
        assert re.search(r".{0,32}invalid response strategy.{0,32}", str(exc_info.value), re.IGNORECASE)

    @pytest.mark.parametrize(
        ("test_data_path", "criteria"),
        _MockAPI_Test_Data,
    )
    def test_is_work(self, sut_with_nothing: MockAPI, test_data_path: str, criteria: bool):
        super().test_is_work(sut_with_nothing, test_data_path, criteria)

    @property
    def _lower_layer_data_modal_for_divide(self) -> HTTP:
        return self._Mock_Model.http


class TestHTTP(TemplatableConfigTestSuite, CheckableTestSuite, DividableTestSuite):
    test_data_dir = "http"
    set_checking_test_data(test_data_dir, reset_callback=reset_http_test_data, opt_globals_callback=add_http_test_data)

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
            (MOCK_MODEL.http_request, False),
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
            (MOCK_MODEL.http_response, False),
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

    @pytest.mark.parametrize(
        ("test_data_path", "criteria"),
        _HTTP_Test_Data,
    )
    def test_is_work(self, sut_with_nothing: HTTP, test_data_path: str, criteria: bool):
        super().test_is_work(sut_with_nothing, test_data_path, criteria)

    @property
    def _lower_layer_data_modal_for_divide(self) -> HTTPRequest:
        return self._Mock_Model.http_request
