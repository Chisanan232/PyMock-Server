import json
import pathlib
from collections import namedtuple
from typing import List, Tuple

from pymock_api.model.enums import ResponseStrategy
from pymock_api.model.openapi._schema_parser import (
    OpenAPIV2SchemaParser,
    _ReferenceObjectParser,
    set_component_definition,
)

from ...._base_test_case import BaseTestCaseFactory

# For version 2 OpenAPI
OPENAPI_API_DOC_JSON: List[tuple] = []
OPENAPI_ONE_API_JSON: List[tuple] = []
OPENAPI_API_PARAMETERS_JSON: List[tuple] = []
OPENAPI_API_PARAMETERS_JSON_FOR_API: List[Tuple[dict, dict]] = []
OPENAPI_API_PARAMETERS_LIST_JSON_FOR_API: List[Tuple[dict, dict]] = []
OPENAPI_API_RESPONSES_FOR_API: List[Tuple[ResponseStrategy, dict, dict]] = []
OPENAPI_API_RESPONSES_PROPERTY_FOR_API: List[Tuple[ResponseStrategy, dict, dict]] = []

# For version 3 OpenAPI
OPENAPI_API_DOC_WITH_DIFFERENT_VERSION_JSON: List[tuple] = []


V2OpenAPIDocConfigTestCase = namedtuple(
    "V2OpenAPIDocConfigTestCase",
    (
        "entire_config",
        "each_apis",
        "entire_api_http_request_parameters",
        "general_api_http_request_parameters",
        "reference_api_http_request_parameters",
        "entire_api_http_response_with_strategy",
        "each_api_http_response_with_strategy",
    ),
)


class DeserializeV2OpenAPIConfigTestCaseFactory(BaseTestCaseFactory):

    @classmethod
    def get_test_case(cls) -> V2OpenAPIDocConfigTestCase:
        return V2OpenAPIDocConfigTestCase(
            entire_config=OPENAPI_API_DOC_JSON,
            each_apis=OPENAPI_ONE_API_JSON,
            entire_api_http_request_parameters=OPENAPI_API_PARAMETERS_LIST_JSON_FOR_API,
            general_api_http_request_parameters=OPENAPI_API_PARAMETERS_JSON_FOR_API,
            reference_api_http_request_parameters=OPENAPI_API_PARAMETERS_JSON,
            entire_api_http_response_with_strategy=OPENAPI_API_RESPONSES_FOR_API,
            each_api_http_response_with_strategy=OPENAPI_API_RESPONSES_PROPERTY_FOR_API,
        )

    @classmethod
    def load(cls) -> None:
        if not OPENAPI_API_DOC_JSON:
            cls._load_all_openapi_api_doc()

    @classmethod
    def _load_all_openapi_api_doc(cls) -> None:

        def _generate_test_case_callback(file_path: str) -> None:
            with open(file_path, "r", encoding="utf-8") as file_stream:
                openapi_api_docs = json.loads(file_stream.read())
                OPENAPI_API_DOC_JSON.append(openapi_api_docs)
                apis: dict = openapi_api_docs["paths"]
                for api_path, api_props in apis.items():
                    for api_detail in api_props.values():
                        # For testing API details
                        OPENAPI_ONE_API_JSON.append((api_detail, openapi_api_docs))

                        # For testing API response
                        for strategy in ResponseStrategy:
                            OPENAPI_API_RESPONSES_FOR_API.append((strategy, api_detail, openapi_api_docs))

                        # For testing API response properties
                        status_200_response = api_detail.get("responses", {}).get("200", {})
                        set_component_definition(OpenAPIV2SchemaParser(data=openapi_api_docs))
                        if _ReferenceObjectParser.has_schema(status_200_response):
                            response_schema = _ReferenceObjectParser.get_schema_ref(status_200_response)
                            response_schema_properties = response_schema.get("properties", None)
                            if response_schema_properties:
                                for k, v in response_schema_properties.items():
                                    for strategy in ResponseStrategy:
                                        OPENAPI_API_RESPONSES_PROPERTY_FOR_API.append((strategy, v, openapi_api_docs))

                        # For testing API request parameters
                        OPENAPI_API_PARAMETERS_LIST_JSON_FOR_API.append((api_detail["parameters"], openapi_api_docs))

                        # For testing API request parameters
                        for param in api_detail["parameters"]:
                            if param.get("schema", {}).get("$ref", None) is None:
                                OPENAPI_API_PARAMETERS_JSON.append(param)
                            else:
                                OPENAPI_API_PARAMETERS_JSON_FOR_API.append((param, openapi_api_docs))

        cls._iterate_files_by_path(
            path=(
                str(pathlib.Path(__file__).parent.parent.parent.parent),
                "data",
                "deserialize_openapi_config_test",
                "entire_config",
                "*.json",
            ),
            generate_test_case_callback=_generate_test_case_callback,
        )


class DeserializeV3OpenAPIConfigTestCaseFactory(BaseTestCaseFactory):

    @classmethod
    def get_test_case(cls) -> List[tuple]:
        return OPENAPI_API_DOC_WITH_DIFFERENT_VERSION_JSON

    @classmethod
    def load(cls) -> None:

        def _generate_test_case_callback(file_path: str) -> None:
            with open(file_path, "r", encoding="utf-8") as file_stream:
                openapi_api_docs = json.loads(file_stream.read())
                OPENAPI_API_DOC_WITH_DIFFERENT_VERSION_JSON.append(openapi_api_docs)

        cls._iterate_files_by_path(
            path=(
                str(pathlib.Path(__file__).parent.parent.parent.parent),
                "data",
                "deserialize_openapi_config_test",
                "different_version",
                "*.json",
            ),
            generate_test_case_callback=_generate_test_case_callback,
        )
