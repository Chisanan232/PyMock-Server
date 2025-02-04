import random
from typing import Any, List, Type, Union

import pytest

from fake_api_server.command.subcommand import SubCommandLine

# isort: off
from test.unit_test.model._enums import EnumTestSuite

# isort: on


def _random_adjust_char_case(v: str) -> str:
    random_char_index = random.randrange(0, len(v))
    random_char = v[random_char_index]
    random_char = random_char.lower() if random_char.isupper() else random_char.lower()
    return v[0:random_char_index] + random_char + v[random_char_index + 1 : len(v)]


SUBCMD_TEST_DATA: List[Union[str, SubCommandLine]] = []
SUBCMD_TEST_DATA.extend([subcmd for subcmd in SubCommandLine])
SUBCMD_TEST_DATA.extend([_random_adjust_char_case(subcmd.value) for subcmd in SubCommandLine])


class TestConfigLoadingOrder(EnumTestSuite):
    @pytest.fixture(scope="function")
    def enum_obj(self) -> Type[SubCommandLine]:
        return SubCommandLine

    @pytest.mark.parametrize("value", SUBCMD_TEST_DATA)
    def test_to_enum(self, value: Any, enum_obj: Type[SubCommandLine]):
        super().test_to_enum(value, enum_obj)

    def test_invalid_value(self, enum_obj: Type[SubCommandLine]):
        with pytest.raises(ValueError):
            enum_obj.to_enum("invalid value")
