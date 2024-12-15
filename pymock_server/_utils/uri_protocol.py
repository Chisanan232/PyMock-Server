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


class IPVersion(Enum):
    IPv4: str = "ipv4"
    IPv6: str = "ipv6"
