import re
from typing import Type
from unittest.mock import patch

import pytest

from pymock_api.model.enums import OpenAPIVersion
from pymock_api.model.openapi._parser_factory import (
    BaseOpenAPISchemaParserFactory,
    OpenAPIV2SchemaParserFactory,
    OpenAPIV3SchemaParserFactory,
    get_schema_parser_factory,
)


@pytest.mark.parametrize(
    ("openapi_version", "expected_factory"),
    [
        # Enum type
        (OpenAPIVersion.V2, OpenAPIV2SchemaParserFactory),
        (OpenAPIVersion.V3, OpenAPIV3SchemaParserFactory),
        # str type
        ("2.0.0", OpenAPIV2SchemaParserFactory),
        ("2.4.8", OpenAPIV2SchemaParserFactory),
        ("3.0.0", OpenAPIV3SchemaParserFactory),
        ("3.1.0", OpenAPIV3SchemaParserFactory),
    ],
)
def test_get_schema_parser_factory(
    openapi_version: OpenAPIVersion, expected_factory: Type[BaseOpenAPISchemaParserFactory]
):
    factory = get_schema_parser_factory(version=openapi_version)
    isinstance(factory, expected_factory)


@pytest.mark.parametrize(
    ("openapi_version", "expected_factory"),
    [
        ("4.0.0", OpenAPIV2SchemaParserFactory),
        ("invalid version", OpenAPIV2SchemaParserFactory),
    ],
)
def test_get_schema_parser_factory_with_invalid_version(
    openapi_version: str, expected_factory: Type[BaseOpenAPISchemaParserFactory]
):
    with patch("pymock_api.model.openapi._parser_factory.OpenAPIVersion.to_enum", return_value=openapi_version):
        with pytest.raises(NotImplementedError) as exc_info:
            get_schema_parser_factory(version=openapi_version)
        re.search(re.escape(openapi_version), str(exc_info.value), re.IGNORECASE)
