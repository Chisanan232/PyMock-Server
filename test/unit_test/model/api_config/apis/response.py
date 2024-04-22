import random
import re
from typing import Any

import pytest

from pymock_api.model.api_config import ResponseProperty, _Config
from pymock_api.model.api_config.apis import HTTPResponse
from pymock_api.model.api_config.apis._property import _HasItemsPropConfig
from pymock_api.model.enums import ResponseStrategy

from ....._values import (
    _Test_HTTP_Resp,
    _Test_Response_Property_Dict,
    _Test_Response_Property_List,
    _TestConfig,
)
from .._base import (
    CheckableTestSuite,
    ConfigTestSpec,
    MockModel,
    _assertion_msg,
    set_checking_test_data,
)
from ..template._base import TemplatableConfigTestSuite


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
            r".{0,32}key \*items\*.{0,32}be 'dict' or '" + re.escape(_HasItemsPropConfig.__name__) + r"'.{0,32}",
            str(exc_info.value),
            re.IGNORECASE,
        )


class TestResponsePropertyWithNestedData(TestResponseProperty):
    @pytest.fixture(scope="function")
    def sut(self) -> ResponseProperty:
        return ResponseProperty(
            name=_Test_Response_Property_Dict["name"],
            required=_Test_Response_Property_Dict["required"],
            value_type=_Test_Response_Property_Dict["type"],
            value_format=_Test_Response_Property_Dict["format"],
            items=_Test_Response_Property_Dict["items"],
        )

    def test_value_attributes(self, sut: ResponseProperty):
        assert sut.name == _Test_Response_Property_Dict["name"], _assertion_msg
        assert sut.required is _Test_Response_Property_Dict["required"], _assertion_msg
        assert sut.value_type == _Test_Response_Property_Dict["type"], _assertion_msg
        assert sut.value_format == _Test_Response_Property_Dict["format"], _assertion_msg
        assert isinstance(sut.items, list)
        for item in sut.items:
            assert list(filter(lambda i: i["name"] == item.name, _Test_Response_Property_Dict["items"]))
            assert list(filter(lambda i: i["required"] == item.required, _Test_Response_Property_Dict["items"]))
            assert list(filter(lambda i: i["type"] == item.value_type, _Test_Response_Property_Dict["items"]))

    def _expected_serialize_value(self) -> Any:
        return _Test_Response_Property_Dict

    def _expected_deserialize_value(self, obj: ResponseProperty) -> None:
        assert isinstance(obj, ResponseProperty)
        assert obj.name == _Test_Response_Property_Dict["name"]
        assert obj.required is _Test_Response_Property_Dict["required"]
        assert obj.value_type == _Test_Response_Property_Dict["type"]
        assert obj.value_format == _Test_Response_Property_Dict["format"]
        assert isinstance(obj.items, list)
        for item in obj.items:
            assert list(filter(lambda i: i["name"] == item.name, _Test_Response_Property_Dict["items"]))
            assert list(filter(lambda i: i["required"] == item.required, _Test_Response_Property_Dict["items"]))
            assert list(filter(lambda i: i["type"] == item.value_type, _Test_Response_Property_Dict["items"]))


class TestHTTPResponse(TemplatableConfigTestSuite, CheckableTestSuite):
    test_data_dir = "response"
    set_checking_test_data(test_data_dir)

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
