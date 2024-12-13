import datetime
import random
import string
from abc import ABCMeta, abstractmethod
from collections import namedtuple
from decimal import Decimal
from typing import Any, Sequence

ValueSize = namedtuple("ValueSize", ("min", "max"), defaults=(-127, 128))
DigitRange = namedtuple("DigitRange", ("integer", "decimal"))


class BaseRandomGenerator(metaclass=ABCMeta):

    def __init__(self):
        raise RuntimeError("Please don't instantiate this object.")

    @classmethod
    @abstractmethod
    def generate(cls, *args, **kwargs) -> Any:
        pass


class RandomString(BaseRandomGenerator):
    @classmethod
    def generate(cls, size: ValueSize = ValueSize()) -> str:
        string_size = random.randint(size.min, size.max)
        return "".join([random.choice(string.ascii_letters) for _ in range(string_size)])


class RandomInteger(BaseRandomGenerator):
    @classmethod
    def generate(cls, value_range: ValueSize = ValueSize()) -> int:
        return random.randint(value_range.min, value_range.max)


class RandomBigDecimal(BaseRandomGenerator):
    @classmethod
    def generate(
        cls, integer_range: ValueSize = ValueSize(), decimal_range: ValueSize = ValueSize(min=0, max=128)
    ) -> Decimal:
        integer = RandomInteger.generate(value_range=integer_range)
        decimal = RandomInteger.generate(value_range=decimal_range)
        return Decimal(f"{integer}.{decimal}")


class RandomBoolean(BaseRandomGenerator):
    @classmethod
    def generate(cls) -> bool:
        return random.choice([True, False])


class RandomFromSequence(BaseRandomGenerator):
    @classmethod
    def generate(cls, sequence: Sequence) -> Any:
        return random.choice(sequence)


class RandomDate(BaseRandomGenerator):
    @classmethod
    def generate(cls) -> str:
        return RandomFromSequence.generate(
            [(datetime.datetime.now() - datetime.timedelta(days=d)).strftime("%Y-%m-%d") for d in range(0, 30)]
        )


class RandomDateTime(BaseRandomGenerator):
    @classmethod
    def generate(cls) -> str:
        return RandomFromSequence.generate(
            [
                (datetime.datetime.now() - datetime.timedelta(days=d)).strftime("%Y-%m-%dT%H:%M:%SZ")
                for d in range(0, 30)
            ]
        )
