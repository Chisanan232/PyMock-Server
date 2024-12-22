from typing import List, Tuple, Union

import pytest

from pymock_server._utils.uri_protocol import URIScheme

_Test_Data: List[Tuple[Union[str, URIScheme], str]] = []
uri_enum = [(uri, uri) for uri in URIScheme]
uri_enum_value = [(uri.value, uri) for uri in URIScheme]
_Test_Data.extend(uri_enum)
_Test_Data.extend(uri_enum_value)


class TestURIScheme:
    @pytest.mark.parametrize(("value", "expected"), _Test_Data)
    def test_to_enum(self, value: Union[str, URIScheme], expected: URIScheme) -> None:
        assert URIScheme.to_enum(value) is expected

    def test_to_enum_with_invalid(self):
        with pytest.raises(ValueError):
            URIScheme.to_enum("invalid value")

    @pytest.mark.parametrize(
        ("schema", "expect_regex"),
        [
            (URIScheme.HTTP, r"http://www\.(\w{1,24}|\.){1,7}\.(com|org)"),
            (URIScheme.HTTPS, r"https://www\.(\w{1,24}|\.){1,7}\.(com|org)"),
            (URIScheme.File, r"file://(\w{1,10}|/){1,11}\.(jpg|jpeg|png|text|txt|py|md)"),
            (URIScheme.FTP, r"ftp://ftp\.(\w{2,3}|\.){5,7}/(\w{1,10}|/){1,3}\.(jpg|jpeg|png|text|txt|py|md)"),
            (URIScheme.Mail_To, r"mailto://\w{1,124}@(gmail|outlook|yahoo).com"),
            (URIScheme.LDAP, r"ldap://ldap\.(\w{1,24}|\.){1,7}/c=GB"),
            (URIScheme.NEWS, r"news://com\.(\w{1,24}|\.){1,7}\.www.servers.unix"),
            (URIScheme.TEL, r"tel:\+1-886-\d{3}-\d{4}"),
            (URIScheme.TELNET, r"telnet://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,4}/"),
            (URIScheme.URN, r"urn:(\w{1,24}|:){1,7}"),
        ],
    )
    def test_generate_value_regex(self, schema: URIScheme, expect_regex: str) -> None:
        random_uri_regex = schema.generate_value_regex()
        assert expect_regex == random_uri_regex
