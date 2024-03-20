import re

import pytest

from pymock_api.model.api_config import IteratorItem
from pymock_api.model.api_config.apis import APIParameter, HTTPRequest

from ....._values import (
    _Test_API_Parameter,
    _Test_Iterable_Parameter_Item_Name,
    _Test_Iterable_Parameter_Item_Value,
    _Test_Iterable_Parameter_Items,
    _Test_Iterable_Parameter_With_MultiValue,
    _TestConfig,
)
from .._base import (
    CheckableTestSuite,
    ConfigTestSpec,
    _assertion_msg,
    set_checking_test_data,
)
from ..template._base import TemplatableConfigTestSuite


class TestHTTPReqeust(TemplatableConfigTestSuite, CheckableTestSuite):
    test_data_dir = "request"
    set_checking_test_data(test_data_dir)

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
