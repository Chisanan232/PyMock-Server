import logging
from typing import List, Tuple, Union

import pytest

from pymock_server._utils.uri_protocol import URISchema

logger = logging.getLogger(__name__)

_Test_Data: List[Tuple[Union[str, URISchema], str]] = []
uri_enum = [(uri, uri) for uri in URISchema]
uri_enum_value = [(uri.value, uri) for uri in URISchema]
_Test_Data.extend(uri_enum)
_Test_Data.extend(uri_enum_value)


class TestURISchema:
    @pytest.mark.parametrize(("value", "expected"), _Test_Data)
    def test_to_enum(self, value: Union[str, URISchema], expected: URISchema) -> None:
        assert URISchema.to_enum(value) is expected

    def test_to_enum_with_invalid(self):
        with pytest.raises(ValueError):
            URISchema.to_enum("invalid value")

    @pytest.mark.parametrize(
        ("schema", "expect_regex"),
        [
            (URISchema.HTTP, r"http://www\.(\w{1,24}|\.){1,7}\.(com|org)"),
            (URISchema.HTTPS, r"https://www\.(\w{1,24}|\.){1,7}\.(com|org)"),
            (URISchema.File, r"file://(\w{1,10}|/){1,11}\.(jpg|jpeg|png|text|txt|py|md)"),
            (URISchema.FTP, r"ftp://ftp\.(\w{2,3}|\.){5,7}/(\w{1,10}|/){1,3}\.(jpg|jpeg|png|text|txt|py|md)"),
            (URISchema.Mail_To, r"mailto://\w{1,124}@(gmail|outlook|yahoo).com"),
            (URISchema.LDAP, r"ldap://ldap\.(\w{1,24}|\.){1,7}/c=GB"),
            (URISchema.NEWS, r"news://com\.(\w{1,24}|\.){1,7}\.www.servers.unix"),
            (URISchema.TEL, r"tel:\+1-886-\d{3}-\d{4}"),
            (URISchema.TELNET, r"telnet://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,4}/"),
            (URISchema.URN, r"urn:(\w{1,24}|:){1,7}"),
        ],
    )
    def test_generate_value_regex(self, schema: URISchema, expect_regex: str) -> None:
        random_uri_regex = schema.generate_value_regex()
        logger.info(f"The random URI format regular expression is: {random_uri_regex}")
        assert expect_regex == random_uri_regex
