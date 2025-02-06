import datetime
import random
import string
import uuid
from abc import ABCMeta, abstractmethod
from collections import namedtuple
from decimal import Decimal
from typing import Any, List, Optional, Sequence

from fake_api_server._utils.uri_protocol import IPVersion, URIScheme

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
    def generate(cls, size: ValueSize = ValueSize(min=1)) -> str:
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
    _DateTime_Format: str = "%Y-%m-%d"

    @classmethod
    def generate(cls) -> str:
        return RandomFromSequence.generate([cls._generate_and_format_value(d) for d in range(0, 30)])

    @classmethod
    def _generate_and_format_value(cls, days: int) -> str:
        return cls._generate_value_from_now(days=days).strftime(cls._DateTime_Format)

    @classmethod
    def _generate_value_from_now(cls, days: int) -> datetime.datetime:
        return datetime.datetime.now() - datetime.timedelta(days=days)


class RandomDateTime(RandomDate):
    _DateTime_Format: str = "%Y-%m-%dT%H:%M:%SZ"

    @classmethod
    def generate(cls) -> str:
        return RandomFromSequence.generate([cls._generate_and_format_value(d) for d in range(0, 30)])


class RandomEMail(BaseRandomGenerator):
    _EMail_Service: List[str] = ["gmail", "outlook", "yahoo"]

    @classmethod
    def generate(cls, size: ValueSize = ValueSize(min=1), usernames: Optional[Sequence] = None) -> str:
        mail_user_name = RandomString.generate(size)
        if usernames:
            mail_user_name = RandomFromSequence.generate(usernames)
        mail_server = RandomFromSequence.generate(cls._EMail_Service)
        return f"{mail_user_name}@{mail_server}.com"


class RandomUUID(BaseRandomGenerator):
    @classmethod
    def generate(cls) -> str:
        return str(uuid.uuid1())


class RandomIP(BaseRandomGenerator):
    @classmethod
    def generate(cls, version: IPVersion) -> str:
        def _randomly_int() -> int:
            return RandomInteger.generate(value_range=ValueSize(min=1, max=256))

        if version is IPVersion.IPv4:
            ip_address = ".".join([str(_randomly_int()) for _ in range(4)])
        elif version is IPVersion.IPv6:

            def _random_hex_string() -> str:
                return hex(RandomInteger.generate(value_range=ValueSize(min=0, max=16)))[-1]

            def _random_one_part() -> str:
                return "".join([_random_hex_string() for _ in range(4)])

            ip_address = ":".join([_random_one_part() for _ in range(8)])
        else:
            raise NotImplementedError(f"Not support the IP version *{version}*.")

        return ip_address


class RandomURI(BaseRandomGenerator):
    @classmethod
    def generate(cls, scheme: URIScheme = URIScheme.HTTPS) -> str:
        return cls._generate_uri_by_scheme(scheme)

    @classmethod
    def _generate_uri_by_scheme(cls, scheme: URIScheme) -> str:
        if scheme in (URIScheme.HTTP, URIScheme.HTTPS):
            # ex: http://www.ietf.org/rfc/rfc2396.txt
            authority = cls._generate_domain(prefix="www", suffix=["com", "org"])
            query = cls._generate_query(use_equal=True)
            fragment = RandomString.generate()
            return f"{scheme.value}://{authority}?{query}#{fragment}"
        elif scheme is URIScheme.File:
            # ex: file://username/wow/Download/test.txt
            path = cls._generate_file_path(only_file=False)
            return f"{scheme.value}://{path}"
        elif scheme is URIScheme.FTP:
            # ex: ftp://ftp.is.co.za/rfc/rfc1808.txt
            authority = cls._generate_domain(
                prefix="ftp", body_size=ValueSize(min=3, max=4), body_ele_size=ValueSize(min=2, max=3)
            )
            path = cls._generate_file_path(only_file=True)
            return f"{scheme.value}://{authority}/{path}"
        elif scheme is URIScheme.Mail_To:
            # ex: mailto:John.Doe@example.com
            return f"{scheme.value}://{RandomEMail.generate()}"
        elif scheme is URIScheme.LDAP:
            # ex: ldap://[2001:db8::7]/c=GB?objectClass?one
            authority = cls._generate_domain(prefix="ldap")
            path = "c=GB"
            query = cls._generate_query(use_equal=False)
            return f"{scheme.value}://{authority}/{path}?{query}"
        elif scheme is URIScheme.NEWS:
            # ex: news:comp.infosystems.www.servers.unix
            path = cls._generate_domain(prefix="www", suffix=["com"], reverse=True)
            return f"{scheme.value}://{path}.servers.unix"
        elif scheme is URIScheme.TEL:
            # ex: tel:+1-816-555-1212
            path = cls._generate_phone_number()
            return f"{scheme.value}:{path}"
        elif scheme is URIScheme.TELNET:
            # ex: telnet://192.0.2.16:80/
            ip_address = cls._generate_ip_address(version=IPVersion.IPv4)
            port = RandomInteger.generate(value_range=ValueSize(min=10, max=10000))
            authority = f"{ip_address}:{port}"
            return f"{scheme.value}://{authority}/"
        elif scheme is URIScheme.URN:
            # ex: urn:oasis:names:specification:docbook:dtd:xml:4.1.2
            path = cls._generate_urn()
            return f"{scheme.value}:{path}"
        else:
            raise ValueError(f"Not support generate the URI with scheme *{scheme}*.")

    @classmethod
    def _generate_domain(
        cls,
        prefix: str = "",
        suffix: List[str] = [],
        body_size: ValueSize = ValueSize(min=1, max=4),
        body_ele_size: ValueSize = ValueSize(min=2, max=24),
        reverse: bool = False,
    ) -> str:
        # note: https://datatracker.ietf.org/doc/html/rfc1035
        # note: https://datatracker.ietf.org/doc/html/rfc2255
        domain_eles = [prefix] if prefix else []

        body_size_val = RandomInteger.generate(body_size)
        domain_body = [RandomString.generate(size=body_ele_size) for _ in range(body_size_val)]
        domain_eles.extend(domain_body)
        if suffix:
            domain_suffix = RandomFromSequence.generate(suffix)
            domain_eles.append(domain_suffix)

        if reverse:
            domain_eles.reverse()

        domain = ".".join(domain_eles)
        return domain

    @classmethod
    def _generate_query(cls, use_equal: bool = True) -> str:
        condition_name = RandomString.generate(size=ValueSize(min=2, max=12))
        condition_value = RandomString.generate(size=ValueSize(min=2, max=12))
        query = f"{condition_name}={condition_value}" if use_equal else f"{condition_name}?{condition_value}"
        return query

    @classmethod
    def _generate_file_path(cls, only_file: bool) -> str:
        file_extensions: List = [".jpg", ".jpeg", ".png", ".text", ".txt", ".py", ".md"]
        file_extension = RandomFromSequence.generate(file_extensions)

        path_depth: ValueSize
        if only_file:
            path_depth = ValueSize(min=1, max=2)
        else:
            path_depth = ValueSize(min=1, max=6)
        path_depth_int = RandomInteger.generate(path_depth)
        file_path_eles = [RandomString.generate(size=ValueSize(min=1, max=10)) for _ in range(path_depth_int)]
        file_name = f"{file_path_eles[-1]}{file_extension}"
        file_path_eles.pop(-1)
        file_path_eles.append(file_name)
        return "/".join(file_path_eles)

    @classmethod
    def _generate_phone_number(cls) -> str:
        internal_number = "886"

        def _randomly_int() -> int:
            return RandomInteger.generate(value_range=ValueSize(min=1, max=9))

        prefix_number = "".join([str(_randomly_int()) for _ in range(3)])
        suffix_number = "".join([str(_randomly_int()) for _ in range(4)])

        return f"+1-{internal_number}-{prefix_number}-{suffix_number}"

    @classmethod
    def _generate_ip_address(cls, version: IPVersion) -> str:
        return RandomIP.generate(version=version)

    @classmethod
    def _generate_urn(
        cls, body_size: ValueSize = ValueSize(min=1, max=4), body_ele_size: ValueSize = ValueSize(min=2, max=24)
    ) -> str:
        domain_eles = []
        body_size_val = RandomInteger.generate(body_size)
        domain_body = [RandomString.generate(size=body_ele_size) for _ in range(body_size_val)]
        domain_eles.extend(domain_body)
        urn = ":".join(domain_eles)
        return urn
