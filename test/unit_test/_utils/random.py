import datetime
import re
from abc import abstractmethod
from typing import Type

import pytest

from pymock_server._utils.random import (
    BaseRandomGenerator,
    RandomBigDecimal,
    RandomBoolean,
    RandomDate,
    RandomDateTime,
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


class BaseRandomGeneratorTestSuite:

    @pytest.fixture(scope="function")
    @abstractmethod
    def generator(self) -> Type[BaseRandomGenerator]:
        pass

    @abstractmethod
    def test_generate(self, generator: Type[BaseRandomGenerator]):
        pass


class TestRandomDate(BaseRandomGeneratorTestSuite):
    @pytest.fixture(scope="function")
    def generator(self) -> Type[RandomDate]:
        return RandomDate

    def test_generate(self, generator: Type[RandomDate]):
        random_date = generator.generate()
        assert re.search(r"\d{4}-\d{1,2}-\d{1,2}", random_date)
        now = datetime.datetime.now()
        random_date_obj = datetime.datetime.strptime(random_date, generator._DateTime_Format)
        assert now - datetime.timedelta(days=30) <= random_date_obj <= now + datetime.timedelta(days=0)


class TestRandomDateTime(BaseRandomGeneratorTestSuite):
    @pytest.fixture(scope="function")
    def generator(self) -> Type[RandomDateTime]:
        return RandomDateTime

    def test_generate(self, generator: Type[RandomDateTime]):
        random_date = generator.generate()
        assert re.search(r"\d{4}-\d{1,2}-\d{1,2}T\d{1,2}:\d{1,2}:\d{1,2}Z", random_date)
        now = datetime.datetime.now()
        random_date_obj = datetime.datetime.strptime(random_date, generator._DateTime_Format)
        assert now - datetime.timedelta(days=30) <= random_date_obj <= now + datetime.timedelta(days=0)
