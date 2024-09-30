from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Any, Type

import pytest

from pymock_api.model.enums import ResponseStrategy


class EnumTestSuite(metaclass=ABCMeta):
    @pytest.fixture(scope="function")
    @abstractmethod
    def enum_obj(self) -> Type[Enum]:
        pass

    def test_to_enum(self, value: Any, enum_obj: Type[Enum]):
        if hasattr(enum_obj, "to_enum"):
            result = enum_obj.to_enum(value)
        else:
            result = enum_obj(value)
        assert isinstance(result, enum_obj)


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
