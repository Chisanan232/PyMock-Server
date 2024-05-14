import re
from typing import Any, List

import pytest

from pymock_api.model.api_config import IteratorItem
from pymock_api.model.api_config._base import _HasItemsPropConfig

from ...._values import _Test_Response_Property_Details_Dict
from ._base import CheckableTestSuite, _assertion_msg, set_checking_test_data


class TestIteratorItem(CheckableTestSuite):
    test_data_dir = "item"
    set_checking_test_data(test_data_dir)

    @pytest.fixture(scope="function")
    def sut(self) -> IteratorItem:
        return IteratorItem(
            name=_Test_Response_Property_Details_Dict["name"],
            required=_Test_Response_Property_Details_Dict["required"],
            value_type=_Test_Response_Property_Details_Dict["type"],
            items=_Test_Response_Property_Details_Dict["items"],
        )

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> IteratorItem:
        return IteratorItem()

    def test_value_attributes(self, sut: IteratorItem):
        assert sut.name == _Test_Response_Property_Details_Dict["name"], _assertion_msg
        assert sut.required is _Test_Response_Property_Details_Dict["required"], _assertion_msg
        assert sut.value_type == _Test_Response_Property_Details_Dict["type"], _assertion_msg
        if sut.items:
            for item in sut.items:
                assert list(
                    filter(lambda i: i["name"] == item.name, _Test_Response_Property_Details_Dict["items"])
                ), _assertion_msg
                assert list(
                    filter(lambda i: i["required"] == item.required, _Test_Response_Property_Details_Dict["items"])
                ), _assertion_msg
                assert list(
                    filter(lambda i: i["type"] == item.value_type, _Test_Response_Property_Details_Dict["items"])
                ), _assertion_msg

    def _expected_serialize_value(self) -> Any:
        return _Test_Response_Property_Details_Dict

    def _expected_deserialize_value(self, obj: IteratorItem) -> None:
        assert isinstance(obj, IteratorItem)
        assert obj.name == _Test_Response_Property_Details_Dict["name"]
        assert obj.required is _Test_Response_Property_Details_Dict["required"]
        assert obj.value_type == _Test_Response_Property_Details_Dict["type"]
        if obj.items:
            for item in obj.items:
                assert list(
                    filter(lambda i: i["name"] == item.name, _Test_Response_Property_Details_Dict["items"])
                ), _assertion_msg
                assert list(
                    filter(lambda i: i["required"] == item.required, _Test_Response_Property_Details_Dict["items"])
                ), _assertion_msg
                assert list(
                    filter(lambda i: i["type"] == item.value_type, _Test_Response_Property_Details_Dict["items"])
                ), _assertion_msg

    def test_cannot_serialize_with_invalid_element_in_items(self):
        with pytest.raises(TypeError) as exc_info:
            IteratorItem(items="invalid value")
        assert re.search(
            r".{0,32}key \*items\*.{0,32}be 'dict' or '" + re.escape(_HasItemsPropConfig.__name__) + r"'.{0,32}",
            str(exc_info.value),
            re.IGNORECASE,
        )

    @pytest.mark.parametrize(
        "items_data",
        [
            # Miss columns
            [
                {"name": "id", "required": True, "type": "str"},
                {"name": "name", "required": True, "type": "str"},
            ],
            # Have columns it doesn't have
            [
                {"name": "id", "required": True, "type": "str"},
                {"name": "name", "required": True, "type": "str"},
                {"name": "what_is_this", "required": True, "type": "str"},
            ],
            # Details in property *items* are different
            [
                {"name": "id", "required": True, "type": "str"},
                {"name": "name", "required": True, "type": "str"},
                {"name": "project", "required": False, "type": "list", "items": [{"required": True, "type": "str"}]},
                {
                    "name": "responsibility",
                    "required": True,
                    "type": "list",
                    "items": [
                        {"name": "project", "required": True, "type": "str"},
                        {
                            "name": "language",
                            "required": True,
                            "type": "list",
                            "items": [{"required": True, "type": "str"}],
                        },
                    ],
                },
            ],
            # Details in property *items.items* are different
            [
                {"name": "id", "required": True, "type": "str"},
                {"name": "name", "required": True, "type": "str"},
                {"name": "project", "required": True, "type": "list", "items": [{"required": True, "type": "int"}]},
                {
                    "name": "responsibility",
                    "required": True,
                    "type": "list",
                    "items": [
                        {"name": "project", "required": True, "type": "str"},
                        {
                            "name": "language",
                            "required": True,
                            "type": "list",
                            "items": [{"required": True, "type": "str"}],
                        },
                    ],
                },
            ],
        ],
    )
    def test_compare_with_other_has_different_element(self, items_data: List[dict]):
        item = IteratorItem(
            name="data",
            required=True,
            value_type="dict",
            items=[
                {"name": "id", "required": True, "type": "str"},
                {"name": "name", "required": True, "type": "str"},
                {"name": "project", "required": True, "type": "list", "items": [{"required": True, "type": "str"}]},
                {
                    "name": "responsibility",
                    "required": True,
                    "type": "list",
                    "items": [
                        {"name": "project", "required": True, "type": "str"},
                        {
                            "name": "language",
                            "required": True,
                            "type": "list",
                            "items": [{"required": True, "type": "str"}],
                        },
                    ],
                },
            ],
        )
        diff_item = IteratorItem(
            name=item.name,
            required=item.required,
            value_type=item.value_type,
            items=items_data,
        )
        assert item != diff_item
