import random
import string
from abc import ABCMeta, abstractmethod
from collections import namedtuple
from typing import Any


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
