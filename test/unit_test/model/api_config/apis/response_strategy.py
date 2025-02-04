from typing import Any, Type

import pytest

from fake_api_server.model.api_config.apis import ResponseStrategy

# isort: off
from test.unit_test.model._enums import EnumTestSuite

# isort: on


class TestResponseStrategy(EnumTestSuite):
    @pytest.fixture(scope="function")
    def enum_obj(self) -> Type[ResponseStrategy]:
        return ResponseStrategy

    @pytest.mark.parametrize(
        "value",
        [
            ResponseStrategy.STRING,
            ResponseStrategy.FILE,
            "string",
            "object",
        ],
    )
    def test_to_enum(self, value: Any, enum_obj: Type[ResponseStrategy]):
        super().test_to_enum(value, enum_obj)
