import re
from typing import List, Type

import pytest

from pymock_api.model.enums import OpenAPIVersion
from pymock_api.model.openapi._base import (
    get_schema_parser_factory_with_openapi_version,
    set_component_definition,
    set_openapi_version,
    set_parser_factory,
)
from pymock_api.model.openapi._parser import APIParser
from pymock_api.model.openapi._schema_parser import (
    OpenAPIV2PathSchemaParser,
    OpenAPIV2SchemaParser,
)
from pymock_api.model.openapi.config import APIParameter

from .config import (
    OPENAPI_API_PARAMETERS_JSON,
    OPENAPI_API_PARAMETERS_JSON_FOR_API,
    OPENAPI_API_PARAMETERS_LIST_JSON_FOR_API,
    _get_all_openapi_api_doc,
)

if (
    not OPENAPI_API_PARAMETERS_LIST_JSON_FOR_API
    and not OPENAPI_API_PARAMETERS_JSON
    and not OPENAPI_API_PARAMETERS_JSON_FOR_API
):
    _get_all_openapi_api_doc()


class TestAPIParser:

    @pytest.fixture(scope="function")
    def parser(self) -> Type[APIParser]:
        return APIParser

    @pytest.mark.parametrize(("openapi_doc_data", "entire_openapi_config"), OPENAPI_API_PARAMETERS_LIST_JSON_FOR_API)
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
        parameters = parser_instance.process_api_parameters(data_modal=APIParameter, http_method="HTTP method")

        # Verify
        assert parameters and isinstance(parameters, list)
        assert len(parameters) == len(openapi_doc_data)
        type_checksum = list(map(lambda p: isinstance(p, APIParameter), parameters))
        assert False not in type_checksum

        # Finally
        set_openapi_version(OpenAPIVersion.V3)
        # Reload schema parser factory
        set_parser_factory(get_schema_parser_factory_with_openapi_version())

    @pytest.mark.parametrize(("openapi_doc_data", "entire_openapi_config"), OPENAPI_API_PARAMETERS_JSON_FOR_API)
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
        type_checksum = list(map(lambda p: isinstance(p, dict), parameters))
        assert False not in type_checksum

    @pytest.mark.parametrize("openapi_doc_data", OPENAPI_API_PARAMETERS_JSON)
    def test__process_has_ref_parameters_with_invalid_value(self, parser: Type[APIParser], openapi_doc_data: dict):
        with pytest.raises(ValueError) as exc_info:
            # Run target function
            parser_instance = parser(parser=OpenAPIV2PathSchemaParser(openapi_doc_data))
            parser_instance._process_has_ref_parameters(openapi_doc_data)

        # Verify
        assert re.search(r".{1,64}no ref.{1,64}", str(exc_info.value), re.IGNORECASE)
