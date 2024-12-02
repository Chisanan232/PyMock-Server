from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Any, Type

import pytest


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
