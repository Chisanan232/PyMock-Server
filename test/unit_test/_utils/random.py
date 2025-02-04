import datetime
import logging
import re
from abc import abstractmethod
from typing import List, Type

import pytest

from fake_api_server._utils.random import (
    BaseRandomGenerator,
    RandomBigDecimal,
    RandomBoolean,
    RandomDate,
    RandomDateTime,
    RandomEMail,
    RandomFromSequence,
    RandomInteger,
    RandomIP,
    RandomString,
    RandomURI,
    RandomUUID,
)
from fake_api_server._utils.uri_protocol import IPVersion, URIScheme

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

    def test_generate_with_multiple_usernames(self, generator: Type[RandomEMail]):
        usernames: List[str] = ["user1", "test", "wow"]

        random_email = generator.generate(usernames=usernames)
        logger.info(f"the randomly e-mail: {random_email}")

        email_username_regex = f"({'|'.join(usernames)})"
        email_service_regex = f"({'|'.join(generator._EMail_Service)})"
        assert re.search(email_username_regex + r"@" + email_service_regex + ".com", random_email)


class TestRandomUUID(BaseRandomGeneratorTestSuite):
    @pytest.fixture(scope="function")
    def generator(self) -> Type[RandomUUID]:
        return RandomUUID

    def test_generate(self, generator: Type[RandomUUID]):
        random_uuid = generator.generate()
        assert re.search(r"\w{8}-\w{4}-\w{4}-\w{4}-\w{12}", random_uuid)


class TestRandomURI(BaseRandomGeneratorTestSuite):
    @pytest.fixture(scope="function")
    def generator(self) -> Type[RandomURI]:
        return RandomURI

    @pytest.mark.parametrize("scheme", [s for s in URIScheme])
    def test_generate(self, generator: Type[RandomURI], scheme: URIScheme) -> None:
        random_uri = generator.generate(scheme)
        logger.info(f"The random URI value is: {random_uri}")
        expect_regex = scheme.generate_value_regex()
        assert re.search(expect_regex, random_uri)

    def test_generate_with_invalid_scheme(self, generator: RandomURI):
        with pytest.raises(ValueError):
            generator.generate(scheme="invalid URI scheme")


class TestRandomIP(BaseRandomGeneratorTestSuite):
    @pytest.fixture(scope="function")
    def generator(self) -> Type[RandomIP]:
        return RandomIP

    @pytest.mark.parametrize(
        ("ip_version", "expect_regex"),
        [
            (IPVersion.IPv4, r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"),
            (
                IPVersion.IPv6,
                r"(\d|[a-f]){4}:(\d|[a-f]){4}:(\d|[a-f]){4}:(\d|[a-f]){4}:(\d|[a-f]){4}:(\d|[a-f]){4}:(\d|[a-f]){4}:(\d|[a-f]){4}",
            ),
        ],
    )
    def test_generate(self, generator: Type[RandomIP], ip_version: IPVersion, expect_regex: str) -> None:
        random_ip_address = generator.generate(ip_version)
        logger.info(f"The random IP address is: {random_ip_address}")
        assert re.search(expect_regex, random_ip_address)

    def test_generate_with_invalid_version(self, generator: RandomURI):
        with pytest.raises(NotImplementedError):
            generator.generate(version="invalid IP protocol version")
