from typing import Type

import pytest

from pymock_api.model.openapi._parser import APIParser
from pymock_api.model.openapi._schema_parser import OpenAPIV2PathSchemaParser

from ._test_case import DeserializeV2OpenAPIConfigTestCaseFactory

DeserializeV2OpenAPIConfigTestCaseFactory.load()
DESERIALIZE_V2_OPENAPI_DOC_TEST_CASE = DeserializeV2OpenAPIConfigTestCaseFactory.get_test_case()
PARSE_V2_OPENAPI_REQUEST_PARAMETERS_TEST_CASE = DESERIALIZE_V2_OPENAPI_DOC_TEST_CASE.entire_api_http_request_parameters
PARSE_V2_OPENAPI_RESPONSES_TEST_CASE = DESERIALIZE_V2_OPENAPI_DOC_TEST_CASE.entire_api_http_response


class DummyPathSchemaParser(OpenAPIV2PathSchemaParser):
    pass


class TestAPIParser:

    @pytest.fixture(scope="function")
    def parser(self) -> Type[APIParser]:
        return APIParser
