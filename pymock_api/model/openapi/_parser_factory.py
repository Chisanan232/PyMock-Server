from typing import Dict

from ._parse import (
    OpenAPIObjectParser,
    OpenAPIParser,
    OpenAPIPathParser,
    OpenAPIRequestParametersParser,
    OpenAPIResponseParser,
    OpenAPITagParser,
)


class OpenAPIParserFactory:

    def entire_config(self, file: str = "", data: Dict = {}) -> OpenAPIParser:
        return OpenAPIParser(file=file, data=data)

    def tag(self, data: Dict) -> OpenAPITagParser:
        return OpenAPITagParser(data=data)

    def path(self, data: Dict) -> OpenAPIPathParser:
        return OpenAPIPathParser(data=data)

    def request_parameters(self, data: Dict) -> OpenAPIRequestParametersParser:
        return OpenAPIRequestParametersParser(data=data)

    def response(self, data: Dict) -> OpenAPIResponseParser:
        return OpenAPIResponseParser(data=data)

    def object(self, data: Dict) -> OpenAPIObjectParser:
        return OpenAPIObjectParser(data=data)
