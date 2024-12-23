import logging
from abc import ABCMeta, abstractmethod
from http import HTTPStatus
from typing import Any, Dict

import pytest

from pymock_server.model import OpenAPIVersion
from pymock_server.model.rest_api_doc_config._base import set_openapi_version
from pymock_server.model.rest_api_doc_config.base_config import (
    _BaseAPIConfigWithMethod,
    set_component_definition,
)
from pymock_server.model.rest_api_doc_config.config import (
    APIConfigWithMethodV2,
    APIConfigWithMethodV3,
    HttpConfigV2,
    HttpConfigV3,
    ReferenceConfigProperty,
)
from pymock_server.model.rest_api_doc_config.content_type import ContentType

logger = logging.getLogger(__name__)


_Common_Schemas: Dict[str, Dict] = {
    "schemas": {
        # For int64 format value
        "Int64FormatResponse": {
            "type": "object",
            "required": ["value"],
            "properties": {
                "value": {"type": "integer", "format": "int64"},
            },
            "title": "FooResponse",
        },
        # For string value with enums
        "EnumsFormatResponse": {
            "type": "object",
            "required": ["value"],
            "properties": {
                "value": {"type": "string", "enum": ["TYPE_1", "TYPE_2"]},
            },
            "title": "FooResponse",
        },
        # For array value with format element
        "FormatElementArrayResponse": {
            "type": "object",
            "required": ["value"],
            "properties": {
                "value": {"type": "array", "items": {"type": "integer", "format": "int64"}},
            },
            "title": "FooResponse",
        },
    },
}


class ApiDocConfigToPyMockAPIConfigAtHTTPResponseValueFormatTestSuite(metaclass=ABCMeta):
    @pytest.mark.parametrize(
        ("api_doc_config", "format_in_array"),
        [
            ({"$ref": "#/components/schemas/Int64FormatResponse"}, False),
            ({"$ref": "#/components/schemas/EnumsFormatResponse"}, False),
            ({"$ref": "#/components/schemas/FormatElementArrayResponse"}, True),
        ],
    )
    def test_convert_api_doc_config_to_adapter_to_pymock_config(
        self, api_doc_config: Dict[str, Any], format_in_array: bool
    ):
        """
        Test goal: value converting workflow at specific column *value_format*
        API document config -> adapter -> PyMock-Server config
        """
        # given
        set_openapi_version(self._api_doc_version)
        set_component_definition(_Common_Schemas)
        api_doc_http_config = self._set_response(api_doc_config)

        # when
        response_config_adapter = api_doc_http_config.to_responses_adapter()
        response_configs = [ra.to_pymock_api_config() for ra in response_config_adapter.data]

        # should
        one_resp_configs = response_configs[0]
        if format_in_array:
            assert one_resp_configs.items
            assert one_resp_configs.items[0].value_format is not None
        else:
            assert one_resp_configs.value_format is not None

    @property
    @abstractmethod
    def _api_doc_version(self) -> OpenAPIVersion:
        pass

    @abstractmethod
    def _set_response(self, api_doc_config: Dict[str, Any]) -> _BaseAPIConfigWithMethod:
        pass


class TestAPIConfigWithMethodV2(ApiDocConfigToPyMockAPIConfigAtHTTPResponseValueFormatTestSuite):

    @property
    def _api_doc_version(self) -> OpenAPIVersion:
        return OpenAPIVersion.V2

    def _set_response(self, api_doc_config: Dict[str, Any]) -> APIConfigWithMethodV2:
        return APIConfigWithMethodV2(
            responses={
                HTTPStatus.OK: HttpConfigV2(schema=ReferenceConfigProperty().deserialize(api_doc_config)),
            },
        )


class TestAPIConfigWithMethodV3(ApiDocConfigToPyMockAPIConfigAtHTTPResponseValueFormatTestSuite):

    @property
    def _api_doc_version(self) -> OpenAPIVersion:
        return OpenAPIVersion.V3

    def _set_response(self, api_doc_config: Dict[str, Any]) -> APIConfigWithMethodV3:
        return APIConfigWithMethodV3(
            responses={
                HTTPStatus.OK: HttpConfigV3(
                    content={
                        ContentType.APPLICATION_JSON: HttpConfigV2(
                            schema=ReferenceConfigProperty().deserialize(api_doc_config)
                        ),
                    }
                ),
            },
        )
