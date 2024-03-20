from typing import Any

import pytest

from pymock_api.model.api_config import IteratorItem

from ...._values import _Test_Iterable_Parameter_Item_Name
from ._base import CheckableTestSuite, _assertion_msg, set_checking_test_data


class TestIteratorItem(CheckableTestSuite):
    test_data_dir = "item"
    set_checking_test_data(test_data_dir)

    @pytest.fixture(scope="function")
    def sut(self) -> IteratorItem:
        return IteratorItem(
            name=_Test_Iterable_Parameter_Item_Name["name"],
            required=_Test_Iterable_Parameter_Item_Name["required"],
            value_type=_Test_Iterable_Parameter_Item_Name["type"],
        )

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> IteratorItem:
        return IteratorItem()

    def test_value_attributes(self, sut: IteratorItem):
        assert sut.name == _Test_Iterable_Parameter_Item_Name["name"], _assertion_msg
        assert sut.required is _Test_Iterable_Parameter_Item_Name["required"], _assertion_msg
        assert sut.value_type == _Test_Iterable_Parameter_Item_Name["type"], _assertion_msg

    def _expected_serialize_value(self) -> Any:
        return _Test_Iterable_Parameter_Item_Name

    def _expected_deserialize_value(self, obj: IteratorItem) -> None:
        assert isinstance(obj, IteratorItem)
        assert obj.name == _Test_Iterable_Parameter_Item_Name["name"]
        assert obj.required is _Test_Iterable_Parameter_Item_Name["required"]
        assert obj.value_type == _Test_Iterable_Parameter_Item_Name["type"]
