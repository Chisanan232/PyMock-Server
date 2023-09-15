import random
import re
from typing import Any, List, Optional, Union
from unittest.mock import Mock, patch

import pytest

from pymock_api._utils import YAML
from pymock_api._utils.file_opt import JSON
from pymock_api.model import HTTP, APIParameter, HTTPRequest, HTTPResponse, MockAPI
from pymock_api.model.api_config import IteratorItem, ResponseProperty, _Config
from pymock_api.model.enums import Format, ResponseStrategy

from ....._values import (
    _Test_API_Parameter,
    _Test_HTTP_Resp,
    _Test_Iterable_Parameter_Item_Name,
    _Test_Iterable_Parameter_Item_Value,
    _Test_Iterable_Parameter_Items,
    _Test_Iterable_Parameter_With_MultiValue,
    _Test_Response_Properties,
    _Test_Response_Property_List,
    _Test_Tag,
    _Test_URL,
    _TestConfig,
)
from .._base import (
    MOCK_MODEL,
    MOCK_RETURN_VALUE,
    ConfigTestSpec,
    MockModel,
    _assertion_msg,
)
from ..template import TemplatableConfigTestSuite


class TestMockAPI(TemplatableConfigTestSuite):
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


class TestHTTP(TemplatableConfigTestSuite):
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


class TestHTTPReqeust(TemplatableConfigTestSuite):
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
        assert sut.items is None, _assertion_msg

    def _expected_serialize_value(self) -> dict:
        return _Test_API_Parameter

    def _expected_deserialize_value(self, obj: APIParameter) -> None:
        assert isinstance(obj, APIParameter)
        assert obj.name == _Test_API_Parameter["name"]
        assert obj.required is _Test_API_Parameter["required"]
        assert obj.default == _Test_API_Parameter["default"]
        assert obj.value_type == _Test_API_Parameter["type"]
        assert obj.value_format == _Test_API_Parameter["format"]
        assert obj.items is None

    def test_serialize_api_parameter_with_iterable_items(self, sut_with_nothing: APIParameter):
        sut_with_nothing.deserialize(_Test_Iterable_Parameter_With_MultiValue)
        serialized_data = sut_with_nothing.serialize()
        assert serialized_data == _Test_Iterable_Parameter_With_MultiValue

    def test_deserialize_api_parameter_with_iterable_items(self, sut_with_nothing: APIParameter):
        sut_with_nothing.deserialize(_Test_Iterable_Parameter_With_MultiValue)
        assert sut_with_nothing.name == _Test_Iterable_Parameter_With_MultiValue["name"]
        assert sut_with_nothing.required == _Test_Iterable_Parameter_With_MultiValue["required"]
        assert sut_with_nothing.default == _Test_Iterable_Parameter_With_MultiValue["default"]
        assert sut_with_nothing.value_type == _Test_Iterable_Parameter_With_MultiValue["type"]
        assert sut_with_nothing.value_format == _Test_Iterable_Parameter_With_MultiValue["format"]
        assert len(sut_with_nothing.items) == len(_Test_Iterable_Parameter_Items)
        assert [item.serialize() for item in sut_with_nothing.items] == _Test_Iterable_Parameter_With_MultiValue[
            "items"
        ]

    @pytest.mark.parametrize("items_value", [_Test_Iterable_Parameter_With_MultiValue])
    def test_converting_at_prop_items_with_valid_value(self, items_value: dict):
        under_test = APIParameter(
            name=items_value["name"],
            required=items_value["required"],
            default=items_value["default"],
            value_type=items_value["type"],
            value_format=items_value["format"],
            items=items_value["items"],
        )
        assert isinstance(under_test.items, list)
        assert False not in list(map(lambda i: isinstance(i, IteratorItem), under_test.items))
        for i in under_test.items:
            assert i.name in [
                _Test_Iterable_Parameter_Item_Name["name"],
                _Test_Iterable_Parameter_Item_Value["name"],
            ], _assertion_msg
            if i.name == _Test_Iterable_Parameter_Item_Name["name"]:
                criteria = _Test_Iterable_Parameter_Item_Name
            elif i.name == _Test_Iterable_Parameter_Item_Value["name"]:
                criteria = _Test_Iterable_Parameter_Item_Value
            else:
                raise ValueError("")
            assert i.required == criteria["required"]
            assert i.value_type == criteria["type"]

    def test_converting_at_prop_items_with_invalid_value(self):
        with pytest.raises(TypeError) as exc_info:
            APIParameter(
                name="name",
                required=False,
                value_type="str",
                items=[1, [], ()],
            )
        assert re.search(
            r".{0,64}data type.{0,64}key \*items\*.{0,64}be dict or IteratorItem.{0,64}",
            str(exc_info.value),
            re.IGNORECASE,
        )


class TestResponseProperty(ConfigTestSpec):
    @pytest.fixture(scope="function")
    def sut(self) -> ResponseProperty:
        return ResponseProperty(
            name=_Test_Response_Property_List["name"],
            required=_Test_Response_Property_List["required"],
            value_type=_Test_Response_Property_List["type"],
            value_format=_Test_Response_Property_List["format"],
            items=_Test_Response_Property_List["items"],
        )

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> ResponseProperty:
        return ResponseProperty()

    def test_value_attributes(self, sut: ResponseProperty):
        assert sut.name == _Test_Response_Property_List["name"], _assertion_msg
        assert sut.required is _Test_Response_Property_List["required"], _assertion_msg
        assert sut.value_type == _Test_Response_Property_List["type"], _assertion_msg
        assert sut.value_format == _Test_Response_Property_List["format"], _assertion_msg
        assert isinstance(sut.items, list)
        for item in sut.items:
            assert list(filter(lambda i: i["name"] == item.name, _Test_Response_Property_List["items"]))
            assert list(filter(lambda i: i["required"] == item.required, _Test_Response_Property_List["items"]))
            assert list(filter(lambda i: i["type"] == item.value_type, _Test_Response_Property_List["items"]))

    def _expected_serialize_value(self) -> Any:
        return _Test_Response_Property_List

    def _expected_deserialize_value(self, obj: ResponseProperty) -> None:
        assert isinstance(obj, ResponseProperty)
        assert obj.name == _Test_Response_Property_List["name"]
        assert obj.required is _Test_Response_Property_List["required"]
        assert obj.value_type == _Test_Response_Property_List["type"]
        assert obj.value_format == _Test_Response_Property_List["format"]
        assert isinstance(obj.items, list)
        for item in obj.items:
            assert list(filter(lambda i: i["name"] == item.name, _Test_Response_Property_List["items"]))
            assert list(filter(lambda i: i["required"] == item.required, _Test_Response_Property_List["items"]))
            assert list(filter(lambda i: i["type"] == item.value_type, _Test_Response_Property_List["items"]))

    def test_convert_invalid_items(self, sut_with_nothing: ResponseProperty):
        with pytest.raises(TypeError) as exc_info:
            ResponseProperty(items=["invalid element"])
        assert re.search(
            r".{0,32}key \*items\*.{0,32}be dict or IteratorItem.{0,32}", str(exc_info.value), re.IGNORECASE
        )


class TestHTTPResponse(TemplatableConfigTestSuite):
    @pytest.fixture(scope="function")
    def sut(self) -> HTTPResponse:
        return HTTPResponse(strategy=ResponseStrategy.STRING, value=_Test_HTTP_Resp)

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> HTTPResponse:
        return HTTPResponse(strategy=ResponseStrategy.STRING)

    def test_value_attributes(self, sut: HTTPResponse):
        assert sut.value == _Test_HTTP_Resp, _assertion_msg

    def test_serialize_with_none(self, sut_with_nothing: _Config):
        serialized_data = sut_with_nothing.serialize()
        assert serialized_data is not None
        assert serialized_data["strategy"] == ResponseStrategy.STRING.value
        assert serialized_data["value"] == ""

    def _expected_serialize_value(self) -> dict:
        return _TestConfig.Response

    def _expected_deserialize_value(self, obj: HTTPResponse) -> None:
        assert isinstance(obj, HTTPResponse)
        assert obj.value == _TestConfig.Response.get("value", None)

    @pytest.mark.parametrize(
        ("compare", "be_compared"),
        [
            (None, random.choice([s for s in ResponseStrategy])),
            (None, None),
        ],
    )
    def test_invalid_compare_with_missing_strategy(self, compare: ResponseStrategy, be_compared: ResponseStrategy):
        with pytest.raises(ValueError) as exc_info:
            HTTPResponse(strategy=compare) == HTTPResponse(strategy=be_compared)
        assert re.search(r".{0,32}Miss.{0,32}strategy.{0,32}", str(exc_info.value), re.IGNORECASE)

    @pytest.mark.parametrize(
        ("compare", "be_compared"),
        [
            (ResponseStrategy.STRING, None),
            (ResponseStrategy.FILE, None),
            (ResponseStrategy.OBJECT, None),
            (ResponseStrategy.STRING, ResponseStrategy.FILE),
            (ResponseStrategy.FILE, ResponseStrategy.OBJECT),
            (ResponseStrategy.OBJECT, ResponseStrategy.STRING),
        ],
    )
    def test_invalid_compare(self, compare: ResponseStrategy, be_compared: ResponseStrategy):
        with pytest.raises(TypeError) as exc_info:
            HTTPResponse(strategy=compare) == HTTPResponse(strategy=be_compared)
        assert re.search(
            r".{0,32}different HTTP response strategy.{0,32}cannot compare.{0,32}", str(exc_info.value), re.IGNORECASE
        )

    @pytest.mark.parametrize(
        ("strategy", "expected_strategy"),
        [
            ("string", ResponseStrategy.STRING),
            ("file", ResponseStrategy.FILE),
            ("object", ResponseStrategy.OBJECT),
        ],
    )
    def test_set_str_type_strategy(self, strategy: str, expected_strategy: ResponseStrategy):
        resp = HTTPResponse(strategy=strategy)
        assert resp.strategy is expected_strategy

    def test_invalid_set_properties(self):
        with pytest.raises(TypeError) as exc_info:
            HTTPResponse(strategy=ResponseStrategy.OBJECT, properties=["invalid property value"])
        assert re.search(
            r".{0,32}data type.{0,32}\*properties\*.{0,32}be dict or ResponseProperty.{0,32}",
            str(exc_info.value),
            re.IGNORECASE,
        )

    @pytest.mark.parametrize(
        "response",
        [
            HTTPResponse(strategy=None, value="some string value"),
            HTTPResponse(strategy=None, path="file path"),
            HTTPResponse(strategy=None, properties=MockModel().response_properties),
        ],
    )
    def test_serialize_as_none_with_strategy(self, response: HTTPResponse):
        with pytest.raises(ValueError) as exc_info:
            response.serialize()
        assert re.search(r".{0,32}strategy.{0,32}missing.{0,32}", str(exc_info.value), re.IGNORECASE)

    @pytest.mark.parametrize(
        ("response", "verify_key"),
        [
            (HTTPResponse(strategy=ResponseStrategy.STRING, value=None), "value"),
            (HTTPResponse(strategy=ResponseStrategy.FILE, path=None), "path"),
            (HTTPResponse(strategy=ResponseStrategy.OBJECT, properties=None), "properties"),
            (HTTPResponse(strategy=ResponseStrategy.STRING, value=""), "value"),
            (HTTPResponse(strategy=ResponseStrategy.FILE, path=""), "path"),
            (HTTPResponse(strategy=ResponseStrategy.OBJECT, properties=[]), "properties"),
        ],
    )
    def test_serialize_with_strategy_and_empty_value(self, response: HTTPResponse, verify_key: str):
        serialized_data = response.serialize()
        assert serialized_data is not None
        assert serialized_data["strategy"] == response.strategy.value
        verify_value = [] if response.strategy is ResponseStrategy.OBJECT else getattr(response, verify_key)
        assert serialized_data[verify_key] == verify_value

    @pytest.mark.parametrize(
        ("response", "expected_data"),
        [
            (
                HTTPResponse(strategy=ResponseStrategy.STRING, value="OK"),
                {"strategy": ResponseStrategy.STRING.value, "value": "OK"},
            ),
            (
                HTTPResponse(strategy=ResponseStrategy.FILE, path="file path"),
                {"strategy": ResponseStrategy.FILE.value, "path": "file path"},
            ),
            (
                HTTPResponse(strategy=ResponseStrategy.OBJECT, properties=MockModel().response_properties),
                {
                    "strategy": ResponseStrategy.OBJECT.value,
                    "properties": [p.serialize() for p in MockModel().response_properties],
                },
            ),
        ],
    )
    def test_serialize_with_strategy(self, response: HTTPResponse, expected_data: dict):
        assert response.serialize() == expected_data

    @pytest.mark.parametrize(
        ("data", "expected_response"),
        [
            (
                {"strategy": ResponseStrategy.STRING.value, "value": "OK"},
                HTTPResponse(strategy=ResponseStrategy.STRING, value="OK"),
            ),
            (
                {"strategy": ResponseStrategy.FILE.value, "path": "file path"},
                HTTPResponse(strategy=ResponseStrategy.FILE, path="file path"),
            ),
            (
                {
                    "strategy": ResponseStrategy.OBJECT.value,
                    "properties": [p.serialize() for p in MockModel().response_properties],
                },
                HTTPResponse(strategy=ResponseStrategy.OBJECT, properties=MockModel().response_properties),
            ),
        ],
    )
    def test_valid_deserialize_with_strategy(self, data: dict, expected_response: HTTPResponse):
        assert HTTPResponse().deserialize(data=data) == expected_response

    def test_deserialize_with_missing_strategy(self):
        with pytest.raises(ValueError) as exc_info:
            HTTPResponse().deserialize(data={"miss strategy": ""})
        assert re.search(r".{0,32}strategy.{0,32}cannot be empty.{0,32}", str(exc_info.value), re.IGNORECASE)

    def test_serialize_with_invalid_strategy(self, sut_with_nothing: HTTPResponse):
        with pytest.raises(TypeError) as exc_info:
            sut_with_nothing.strategy = "invalid strategy"
            sut_with_nothing.serialize()
        assert re.search(r".{0,128}data type is invalid.{0,128}", str(exc_info.value), re.IGNORECASE)
