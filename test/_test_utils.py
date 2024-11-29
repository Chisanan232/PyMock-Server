from decimal import Decimal
from typing import Union

from pymock_api._utils.random import ValueSize


class Verify:
    @staticmethod
    def numerical_value_should_be_in_range(value: Union[int, Decimal], expect_range: ValueSize) -> None:
        if isinstance(value, Decimal):
            assert value.compare(Decimal(expect_range.min)) in [Decimal("1"), Decimal("0")]
            assert value.compare(Decimal(expect_range.max)) in [Decimal("-1"), Decimal("0")]
        else:
            assert expect_range.min <= value <= expect_range.max
