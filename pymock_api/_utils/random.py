import random
import string
from abc import ABCMeta, abstractmethod
from collections import namedtuple
from decimal import Decimal
from typing import Any, Sequence


class BaseRandomGenerator(metaclass=ABCMeta):

    def __init__(self):
        raise RuntimeError("Please don't instantiate this object.")

    @staticmethod
    @abstractmethod
    def generate(*args, **kwargs) -> Any:
        pass


class RandomString(BaseRandomGenerator):
    @staticmethod
    def generate(size: int = 10) -> str:
        return "".join([random.choice(string.ascii_letters) for _ in range(size)])


ValueRange = namedtuple("ValueRange", ("min", "max"), defaults=(-127, 128))


class RandomInteger(BaseRandomGenerator):
    @staticmethod
    def generate(value_range: ValueRange = ValueRange()) -> int:
        return random.randint(value_range.min, value_range.max)


class RandomBigDecimal(BaseRandomGenerator):
    @staticmethod
    def generate(
        integer_range: ValueRange = ValueRange(), decimal_range: ValueRange = ValueRange(min=0, max=128)
    ) -> Decimal:
        integer = RandomInteger.generate(value_range=integer_range)
        decimal = RandomInteger.generate(value_range=decimal_range)
        return Decimal(f"{integer}.{decimal}")


class RandomBoolean(BaseRandomGenerator):
    @staticmethod
    def generate() -> bool:
        return random.choice([True, False])


class RandomFromSequence(BaseRandomGenerator):
    @staticmethod
    def generate(sequence: Sequence) -> bool:
        return random.choice(sequence)
