import re
from typing import List, Type, Union

import pytest

from pymock_api.model.enums import OpenAPIVersion
from pymock_api.model.openapi._base import (
    get_schema_parser_factory_with_openapi_version,
    set_openapi_version,
    set_parser_factory,
)
from pymock_api.model.openapi._parser import APIParameterParser, APIParser
from pymock_api.model.openapi._schema_parser import (
    OpenAPIV2PathSchemaParser,
    OpenAPIV2SchemaParser,
    _ReferenceObjectParser,
)
from pymock_api.model.openapi._tmp_data_model import (
    RequestParameter,
    set_component_definition,
)

from ._test_case import DeserializeV2OpenAPIConfigTestCaseFactory

DeserializeV2OpenAPIConfigTestCaseFactory.load()
DESERIALIZE_V2_OPENAPI_DOC_TEST_CASE = DeserializeV2OpenAPIConfigTestCaseFactory.get_test_case()
PARSE_FAIL_V2_OPENAPI_REQUEST_PARAMETERS_NO_REFERENCE_INFO_TEST_CASE = (
    DESERIALIZE_V2_OPENAPI_DOC_TEST_CASE.reference_api_http_request_parameters
)
PARSE_V2_OPENAPI_REQUEST_PARAMETERS_WITH_REFERENCE_INFO_TEST_CASE = (
    DESERIALIZE_V2_OPENAPI_DOC_TEST_CASE.general_api_http_request_parameters
)
PARSE_V2_OPENAPI_REQUEST_PARAMETERS_TEST_CASE = DESERIALIZE_V2_OPENAPI_DOC_TEST_CASE.entire_api_http_request_parameters
PARSE_V2_OPENAPI_RESPONSES_TEST_CASE = DESERIALIZE_V2_OPENAPI_DOC_TEST_CASE.entire_api_http_response


class DummyPathSchemaParser(OpenAPIV2PathSchemaParser):
    pass


class TestAPIParameterParser:

    @pytest.fixture(scope="function")
    def parser(self) -> Type[APIParameterParser]:
        return APIParameterParser

    def test_parse_schema_with_invalid_value(self, parser: Type[APIParameterParser]):
        invalid_values = {}
        with pytest.raises(ValueError) as exc_info:
            parser_instance = parser(DummyPathSchemaParser({}))
            parser_instance.process_parameter(invalid_values, accept_no_schema=False)
        assert re.search(r".{0,64}doesn't have key 'schema'.{0,64}", str(exc_info.value), re.IGNORECASE)

    @pytest.mark.parametrize(
        ("ut_data", "expect_data"),
        [
            # General case (list type value)
            (
                [
                    {
                        "name": "value",
                        "required": True,
                        "type": "number",
                        "default": "None",
                    },
                    {
                        "name": "id",
                        "required": True,
                        "type": "integer",
                        "default": "None",
                    },
                ],
                [
                    {
                        "name": "value",
                        "required": True,
                        "type": "int",
                        "default": "None",
                    },
                    {
                        "name": "id",
                        "required": True,
                        "type": "int",
                        "default": "None",
                    },
                ],
            ),
            # General case (dict type value)
            (
                {
                    "type": "string",
                    "enum": [
                        "ENUM1",
                        "ENUM2",
                    ],
                },
                [
                    {
                        "type": "str",
                        "enum": [
                            "ENUM1",
                            "ENUM2",
                        ],
                    },
                ],
            ),
        ],
    )
    def test__ensure_data_type_is_pythonic_type_in_items(self, ut_data: Union[list, dict], expect_data: List[dict]):
        parser = APIParameterParser(parser="Dummy parser")
        assert parser._ensure_data_type_is_pythonic_type_in_items(ut_data) == expect_data


class TestAPIParser:

    @pytest.fixture(scope="function")
    def parser(self) -> Type[APIParser]:
        return APIParser

    @pytest.mark.parametrize(
        ("openapi_doc_data", "entire_openapi_config"), PARSE_V2_OPENAPI_REQUEST_PARAMETERS_TEST_CASE
    )
    def test__process_api_params(
        self, parser: Type[APIParser], openapi_doc_data: List[dict], entire_openapi_config: dict
    ):
        # Pre-process
        set_openapi_version(OpenAPIVersion.V2)
        set_component_definition(OpenAPIV2SchemaParser(data=entire_openapi_config))
        parser_instance = parser(parser=OpenAPIV2PathSchemaParser({"parameters": openapi_doc_data}))
        # Reload schema parser factory
        set_parser_factory(get_schema_parser_factory_with_openapi_version())

        # Run target function
        parameters = parser_instance.process_api_parameters(http_method="HTTP method")

        # Verify
        assert parameters and isinstance(parameters, list)
        assert len(parameters) == len(openapi_doc_data)
        type_checksum = list(map(lambda p: isinstance(p, RequestParameter), parameters))
        assert False not in type_checksum

        # Finally
        set_openapi_version(OpenAPIVersion.V3)
        # Reload schema parser factory
        set_parser_factory(get_schema_parser_factory_with_openapi_version())

    @pytest.mark.parametrize(
        ("openapi_doc_data", "entire_openapi_config"), PARSE_V2_OPENAPI_REQUEST_PARAMETERS_WITH_REFERENCE_INFO_TEST_CASE
    )
    def test__process_has_ref_parameters_with_valid_value(
        self, parser: Type[APIParser], openapi_doc_data: dict, entire_openapi_config: dict
    ):
        # Pre-process
        set_component_definition(OpenAPIV2SchemaParser(data=entire_openapi_config))

        # Run target function
        parser_instance = parser(parser=OpenAPIV2PathSchemaParser(openapi_doc_data))
        parameters = parser_instance._process_has_ref_parameters(openapi_doc_data)

        # Verify
        assert parameters and isinstance(parameters, list)
        assert len(parameters) == len(entire_openapi_config["definitions"]["UpdateFooRequest"]["properties"].keys())
        type_checksum = list(map(lambda p: isinstance(p, RequestParameter), parameters))
        assert False not in type_checksum

    @pytest.mark.parametrize("openapi_doc_data", PARSE_FAIL_V2_OPENAPI_REQUEST_PARAMETERS_NO_REFERENCE_INFO_TEST_CASE)
    def test__process_has_ref_parameters_with_invalid_value(self, parser: Type[APIParser], openapi_doc_data: dict):
        with pytest.raises(ValueError) as exc_info:
            # Run target function
            parser_instance = parser(parser=OpenAPIV2PathSchemaParser(openapi_doc_data))
            parser_instance._process_has_ref_parameters(openapi_doc_data)

        # Verify
        assert re.search(r".{1,64}no ref.{1,64}", str(exc_info.value), re.IGNORECASE)

    @pytest.mark.parametrize(("api_detail", "entire_config"), PARSE_V2_OPENAPI_RESPONSES_TEST_CASE)
    def test__process_http_response(self, parser: Type[APIParser], api_detail: dict, entire_config: dict):
        # Pre-process
        set_component_definition(OpenAPIV2SchemaParser(data=entire_config))

        # Run target function under test
        print(f"[DEBUG in test] api_detail: {api_detail}")
        parser_instance = parser(parser=OpenAPIV2PathSchemaParser(data=api_detail))
        response_data = parser_instance.process_responses()
        print(f"[DEBUG in test] response_data: {response_data}")

        # Verify
        resp_200 = api_detail["responses"]["200"]
        if _ReferenceObjectParser.has_schema(resp_200):
            should_check_name = True
        else:
            response_content = resp_200["content"]
            resp_val_format = list(filter(lambda f: f in response_content.keys(), ["application/json", "*/*"]))
            response_detail = response_content[resp_val_format[0]]["schema"]
            if not response_detail:
                should_check_name = False
            else:
                should_check_name = True
        print(f"[DEBUG in test] should_check_name: {should_check_name}")

        # assert isinstance(response_data, ResponseProperty)
        data_details = response_data.data
        assert data_details is not None and isinstance(data_details, list)
        for d in data_details:
            if should_check_name:
                assert d.name
                assert d.type
            assert d.required is not None
            assert d.format is None  # FIXME: Should activate this verify after support this feature
            if d.type == "list":
                assert d.items is not None
                for item in d.items:
                    assert item.name
                    assert item.type
                    assert item.required is not None
        # assert False
        # else:
        #     assert data_details is not None and isinstance(data_details, dict)
        #     for v in data_details.values():
        #         if isinstance(v, str):
        #             if should_check_name:
        #                 assert v in [
        #                     "random string value",
        #                     "random integer value",
        #                     "random boolean value",
        #                     "random file output stream",
        #                     "FIXME: Handle the reference",
        #                 ]
        #             else:
        #                 assert v == "empty value"
        #         else:
        #             for item in v:
        #                 for item_value in item.values():
        #                     if should_check_name:
        #                         assert item_value in [
        #                             "random string value",
        #                             "random integer value",
        #                             "random boolean value",
        #                         ]
        #                     else:
        #                         assert item_value == "empty value"
