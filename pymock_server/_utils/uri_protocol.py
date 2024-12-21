from enum import Enum
from typing import Union


class URISchema(Enum):
    HTTP: str = "http"
    HTTPS: str = "https"
    File: str = "file"
    FTP: str = "ftp"
    Mail_To: str = "mailto"
    LDAP: str = "ldap"
    NEWS: str = "news"
    TEL: str = "tel"
    TELNET: str = "telnet"
    URN: str = "urn"

    @staticmethod
    def to_enum(v: Union[str, "URISchema"]):
        if isinstance(v, URISchema):
            return v
        else:
            for schema in URISchema:
                if schema.value.lower() == str(v).lower():
                    return schema
            raise ValueError(f"Cannot find the URI schema '{v}'.")

    def generate_value_regex(self) -> str:
        if self is URISchema.HTTP:
            return r"http://www\.(\w{1,24}|\.){1,7}\.(com|org)"
        elif self is URISchema.HTTPS:
            return r"https://www\.(\w{1,24}|\.){1,7}\.(com|org)"
        elif self is URISchema.File:
            return r"file://(\w{1,10}|/){1,11}\.(jpg|jpeg|png|text|txt|py|md)"
        elif self is URISchema.FTP:
            return r"ftp://ftp\.(\w{2,3}|\.){5,7}/(\w{1,10}|/){1,3}\.(jpg|jpeg|png|text|txt|py|md)"
        elif self is URISchema.Mail_To:
            return r"mailto://\w{1,124}@(gmail|outlook|yahoo).com"
        elif self is URISchema.LDAP:
            return r"ldap://ldap\.(\w{1,24}|\.){1,7}/c=GB"
        elif self is URISchema.NEWS:
            return r"news://com\.(\w{1,24}|\.){1,7}\.www.servers.unix"
        elif self is URISchema.TEL:
            return r"tel:\+1-886-\d{3}-\d{4}"
        elif self is URISchema.TELNET:
            return r"telnet://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,4}/"
        elif self is URISchema.URN:
            return r"urn:(\w{1,24}|:){1,7}"
        else:
            raise ValueError(f"Not support generate the URI with schema *{self}*.")


class IPVersion(Enum):
    IPv4: str = "ipv4"
    IPv6: str = "ipv6"
