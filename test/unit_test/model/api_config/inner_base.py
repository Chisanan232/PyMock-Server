import re
from typing import Any, Dict, Optional

import pytest

from pymock_api.model.api_config import _Config


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

        def is_work(self) -> bool:
            pass

    class Dummy:
        pass

    with pytest.raises(AttributeError) as exc_info:
        FakeConfig()._get_prop(data=Dummy(), prop="not_exist_prop")
    assert re.search(r"Cannot find attribute", str(exc_info.value), re.IGNORECASE)
