import glob
import json
import os
import pathlib
from typing import List, Tuple

from pymock_api.model.enums import ResponseStrategy
from pymock_api.model.openapi._base import _YamlSchema, set_component_definition
from pymock_api.model.openapi._schema_parser import OpenAPIV2SchemaParser

OPENAPI_API_DOC_JSON: List[tuple] = []
OPENAPI_ONE_API_JSON: List[tuple] = []
OPENAPI_API_PARAMETERS_JSON: List[tuple] = []
OPENAPI_API_PARAMETERS_JSON_FOR_API: List[Tuple[dict, dict]] = []
OPENAPI_API_PARAMETERS_LIST_JSON_FOR_API: List[Tuple[dict, dict]] = []
OPENAPI_API_RESPONSES_FOR_API: List[Tuple[ResponseStrategy, dict, dict]] = []
OPENAPI_API_RESPONSES_PROPERTY_FOR_API: List[Tuple[ResponseStrategy, dict, dict]] = []
OPENAPI_API_DOC_WITH_DIFFERENT_VERSION_JSON: List[tuple] = []


def get_all_openapi_api_doc() -> None:
    json_dir = os.path.join(
        str(pathlib.Path(__file__).parent.parent.parent.parent),
        "data",
        "deserialize_openapi_config_test",
        "entire_config",
        "*.json",
    )
    global OPENAPI_API_DOC_JSON
    for json_config_path in glob.glob(json_dir):
        with open(json_config_path, "r", encoding="utf-8") as file_stream:
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
                    if _YamlSchema.has_schema(status_200_response):
                        response_schema = _YamlSchema.get_schema_ref(status_200_response)
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


def ensure_load_openapi_test_cases() -> None:
    if not OPENAPI_API_DOC_JSON:
        get_all_openapi_api_doc()
