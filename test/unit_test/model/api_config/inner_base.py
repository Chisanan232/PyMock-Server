import re
from typing import Any, Dict, Optional
from unittest.mock import MagicMock

import pytest

from fake_api_server.model.api_config import _Checkable, _Config


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

        @property
        def key(self) -> str:
            pass

        def serialize(self, data: Optional["_Config"] = None) -> Optional[Dict[str, Any]]:
            pass

        def deserialize(self, data: Dict[str, Any]) -> Optional["_Config"]:
            pass

        def is_work(self) -> bool:
            pass

    class Dummy:
        pass

    with pytest.raises(AttributeError) as exc_info:
        FakeConfig()._get_prop(data=Dummy(), prop="not_exist_prop")
    assert re.search(r"Cannot find attribute", str(exc_info.value), re.IGNORECASE)


class FakeCheckableConfig(_Checkable):
    pass


class TestCheckableConfig:
    @pytest.fixture(scope="function")
    def checkable_config(self) -> _Checkable:
        return FakeCheckableConfig()

    def test_fail_should_be_valid(self, checkable_config: _Checkable):
        with pytest.raises(AssertionError) as exc_info:
            checkable_config.should_be_valid(config_key="key", config_value="value", criteria="invalid type criteria")
        assert re.search(r"only accept 'list' type", str(exc_info.value), re.IGNORECASE)

    def test_should_be_valid_callback(self, checkable_config: _Checkable):
        mock_callback_func = MagicMock()
        checkable_config.should_be_valid(
            config_key="key",
            config_value="invalid value",
            criteria=["invalid value"],
            valid_callback=mock_callback_func,
        )
        mock_callback_func.assert_called_once_with("key", "invalid value", ["invalid value"])
