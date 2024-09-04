from typing import Type

import pytest

from pymock_api.model.enums import OpenAPIVersion
from pymock_api.model.openapi._base import set_openapi_version
from pymock_api.model.openapi._parser import APIParser
from pymock_api.model.openapi._schema_parser import (
    OpenAPIV2PathSchemaParser,
    OpenAPIV2SchemaParser,
)
from pymock_api.model.openapi._tmp_data_model import (
    TmpHttpConfigV2,
    set_component_definition,
)

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

    @pytest.mark.parametrize(("api_detail", "entire_config"), PARSE_V2_OPENAPI_RESPONSES_TEST_CASE)
    def test__process_http_response(self, parser: Type[APIParser], api_detail: dict, entire_config: dict):
        # Pre-process
        set_openapi_version(OpenAPIVersion.V2)
        set_component_definition(OpenAPIV2SchemaParser(data=entire_config))

        # Run target function under test
        print(f"[DEBUG in test] api_detail: {api_detail}")
        parser_instance = parser(parser=OpenAPIV2PathSchemaParser(data=api_detail))
        response_data = parser_instance.process_responses()
        print(f"[DEBUG in test] response_data: {response_data}")

        # Verify
        resp_200 = api_detail["responses"]["200"]
        resp_200_model = TmpHttpConfigV2.deserialize(resp_200)
        if resp_200_model.has_ref():
            should_check_name = True
        else:
            should_check_name = False
            # response_content = resp_200_model.content
            # resp_val_format = list(filter(lambda f: f in response_content.keys(), ["application/json", "*/*"]))
            # response_detail = response_content[resp_val_format[0]]["schema"]
            # if not response_detail:
            #     should_check_name = False
            # else:
            #     should_check_name = True
        print(f"[DEBUG in test] should_check_name: {should_check_name}")

        # assert isinstance(response_data, ResponseProperty)
        data_details = response_data.data
        assert data_details is not None and isinstance(data_details, list)
        for d in data_details:
            if should_check_name:
                assert d.name
                assert d.value_type
            assert d.required is not None
            assert d.format is None  # FIXME: Should activate this verify after support this feature
            if d.value_type == "list":
                assert d.items is not None
                for item in d.items:
                    assert item.name
                    assert item.value_type
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
