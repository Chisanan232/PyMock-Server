import re
from enum import Enum
from typing import Union


class OpenAPIVersion(Enum):
    V2 = "OpenAPI V2"
    V3 = "OpenAPI V3"

    @staticmethod
    def to_enum(v: Union[str, "OpenAPIVersion"]) -> "OpenAPIVersion":
        if isinstance(v, str):
            if re.search(r"OpenAPI V[2-3]", v):
                return OpenAPIVersion(v)
            if re.search(r"2\.\d(\.\d)?.{0,8}", v):
                return OpenAPIVersion.V2
            if re.search(r"3\.\d(\.\d)?.{0,8}", v):
                return OpenAPIVersion.V3
            raise NotImplementedError(
                f"PyFake-API-Server doesn't support parsing OpenAPI configuration with version '{v}'."
            )
        else:
            return v
