import re
from typing import Type
from unittest.mock import patch

import pytest

from pymock_api.model.enums import OpenAPIVersion
from pymock_api.model.openapi._parser_factory import (
    BaseOpenAPIParserFactory,
    OpenAPIV2ParserFactory,
    OpenAPIV3ParserFactory,
    get_parser_factory,
)


@pytest.mark.parametrize(
    ("openapi_version", "expected_factory"),
    [
        # Enum type
        (OpenAPIVersion.V2, OpenAPIV2ParserFactory),
        (OpenAPIVersion.V3, OpenAPIV3ParserFactory),
        # str type
        ("2.0.0", OpenAPIV2ParserFactory),
        ("2.4.8", OpenAPIV2ParserFactory),
        ("3.0.0", OpenAPIV3ParserFactory),
        ("3.1.0", OpenAPIV3ParserFactory),
    ],
)
def test_get_parser_factory(openapi_version: OpenAPIVersion, expected_factory: Type[BaseOpenAPIParserFactory]):
    factory = get_parser_factory(version=openapi_version)
    isinstance(factory, expected_factory)


@pytest.mark.parametrize(
    ("openapi_version", "expected_factory"),
    [
        ("4.0.0", OpenAPIV2ParserFactory),
        ("invalid version", OpenAPIV2ParserFactory),
    ],
)
def test_get_parser_factory_with_invalid_version(
    openapi_version: OpenAPIVersion, expected_factory: Type[BaseOpenAPIParserFactory]
):
    with patch("pymock_api.model.openapi._parser_factory.OpenAPIVersion.to_enum", return_value=openapi_version):
        with pytest.raises(NotImplementedError) as exc_info:
            get_parser_factory(version=openapi_version)
        re.search(re.escape(openapi_version), str(exc_info.value), re.IGNORECASE)
