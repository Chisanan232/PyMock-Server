import datetime
import logging
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
    RandomEMail,
    RandomFromSequence,
    RandomInteger,
    RandomString,
    RandomUUID,
)

logger = logging.getLogger(__name__)


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


class TestRandomEMail(BaseRandomGeneratorTestSuite):
    @pytest.fixture(scope="function")
    def generator(self) -> Type[RandomEMail]:
        return RandomEMail

    def test_generate(self, generator: Type[RandomEMail]):
        random_email = generator.generate()
        logger.info(f"the randomly e-mail: {random_email}")
        assert re.search(r"\w{1,124}@(gmail|outlook|yahoo).com", random_email)


class TestRandomUUID(BaseRandomGeneratorTestSuite):
    @pytest.fixture(scope="function")
    def generator(self) -> Type[RandomUUID]:
        return RandomUUID

    def test_generate(self, generator: Type[RandomUUID]):
        random_uuid = generator.generate()
        assert re.search(r"\w{8}-\w{4}-\w{4}-\w{4}-\w{12}", random_uuid)
