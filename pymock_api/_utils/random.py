import random
import string
from abc import ABCMeta, abstractmethod
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
    def generate(size: int = 10) -> Any:
        return "".join([random.choice(string.ascii_letters) for _ in range(size)])


class RandomInteger(BaseRandomGenerator):
    @staticmethod
    def generate(min_value: int = -127, max_value: int = 128) -> Any:
        return random.randint(min_value, max_value)
