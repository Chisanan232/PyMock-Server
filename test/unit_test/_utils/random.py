import re
from typing import Type

import pytest

from pymock_api._utils.random import (
    BaseRandomGenerator,
    RandomBigDecimal,
    RandomBoolean,
    RandomFromSequence,
    RandomInteger,
    RandomString,
)


@pytest.mark.parametrize(
    "random_obj", [RandomString, RandomInteger, RandomBigDecimal, RandomBoolean, RandomFromSequence]
)
def test_invalid_usage(random_obj: Type[BaseRandomGenerator]):
    with pytest.raises(RuntimeError) as exc_info:
        random_obj()
    assert re.search(r"don't instantiate", str(exc_info.value)) is not None
