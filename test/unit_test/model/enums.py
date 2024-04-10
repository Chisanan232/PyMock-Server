import re
from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Any, Type

import pytest

from pymock_api.model.enums import (
    ConfigLoadingOrder,
    OpenAPIVersion,
    ResponseStrategy,
    set_loading_function,
)
from pymock_api.model.openapi._base import (
    _YamlSchema,
    ensure_get_schema_parser_factory,
    set_component_definition,
)
from pymock_api.model.openapi._schema_parser import OpenAPIV3SchemaParser


def test_set_loading_function():
    with pytest.raises(KeyError) as exc_info:
        set_loading_function(data_model_key="data_model", invalid_arg="any value")
    assert re.search(
        r"The arguments only have \*apis\*, \*file\* and \*apply\*.{0,64}", str(exc_info.value), re.IGNORECASE
    )


class EnumTestSuite(metaclass=ABCMeta):
    @pytest.fixture(scope="function")
    @abstractmethod
    def enum_obj(self) -> Type[Enum]:
        pass

    def test_to_enum(self, value: Any, enum_obj: Type[Enum]):
        result = enum_obj.to_enum(value)
        assert isinstance(result, enum_obj)


class TestResponseStrategy(EnumTestSuite):
    @pytest.fixture(scope="function")
    def enum_obj(self) -> Type[ResponseStrategy]:
        return ResponseStrategy

    @pytest.mark.parametrize(
        "value",
        [
            ResponseStrategy.STRING,
            ResponseStrategy.FILE,
            "string",
            "object",
        ],
    )
    def test_to_enum(self, value: Any, enum_obj: Type[ResponseStrategy]):
        super().test_to_enum(value, enum_obj)

    @pytest.mark.parametrize(
        ("ut_enum", "expected_type"),
        [
            (ResponseStrategy.STRING, str),
            (ResponseStrategy.FILE, str),
            (ResponseStrategy.OBJECT, dict),
        ],
    )
    def test_generate_empty_response(self, ut_enum: ResponseStrategy, expected_type: type):
        empty_resp = ut_enum.generate_empty_response()
        assert isinstance(empty_resp, expected_type)

    @pytest.mark.parametrize(
        ("ut_enum", "expected_type"),
        [
            (ResponseStrategy.STRING, str),
            (ResponseStrategy.FILE, str),
            (ResponseStrategy.OBJECT, dict),
        ],
    )
    def test_generate_response_from_reference(self, ut_enum: ResponseStrategy, expected_type: type):
        resp = ut_enum.generate_response_from_reference({"response reference data": {}})
        assert isinstance(resp, expected_type)

    @pytest.mark.parametrize(
        ("ut_enum", "test_response_data", "expected_value"),
        [
            # # General data
            (ResponseStrategy.STRING, {"type": "string"}, "random string value"),
            (ResponseStrategy.FILE, {"type": "string"}, "random string value"),
            (
                ResponseStrategy.OBJECT,
                {"type": "string"},
                {"name": "", "required": True, "type": "str", "format": None, "items": None},
            ),
            # # Each different type as general data
            # For string strategy (the process details of string and file are the same, so it only test one of them)
            (ResponseStrategy.STRING, {"type": "integer"}, "random integer value"),
            (ResponseStrategy.STRING, {"type": "number"}, "random integer value"),
            (ResponseStrategy.STRING, {"type": "boolean"}, "random boolean value"),
            (
                ResponseStrategy.STRING,
                {"type": "array", "items": {"$ref": "#/components/schemas/FooResponse"}},
                [
                    {
                        "id": "random integer value",
                        "name": "random string value",
                        "value1": "random string value",
                        "value2": "random string value",
                    }
                ],
            ),
            (ResponseStrategy.STRING, {"type": "file"}, "random file output stream"),
            (ResponseStrategy.STRING, {"type": "object"}, "random object value"),
            # For object strategy
            (
                ResponseStrategy.OBJECT,
                {"type": "integer"},
                {"name": "", "required": True, "type": "int", "format": None, "items": None},
            ),
            (
                ResponseStrategy.OBJECT,
                {"type": "number"},
                {"name": "", "required": True, "type": "int", "format": None, "items": None},
            ),
            (
                ResponseStrategy.OBJECT,
                {"type": "boolean"},
                {"name": "", "required": True, "type": "bool", "format": None, "items": None},
            ),
            (
                ResponseStrategy.OBJECT,
                {"type": "array", "items": {"$ref": "#/components/schemas/FooResponse"}},
                {
                    "name": "",
                    "required": True,
                    "type": "list",
                    "format": None,
                    "items": [
                        {"name": "id", "required": True, "type": "int"},
                        {"name": "name", "required": True, "type": "str"},
                        {"name": "value1", "required": True, "type": "str"},
                        {"name": "value2", "required": True, "type": "str"},
                    ],
                },
            ),
            (
                ResponseStrategy.OBJECT,
                {"type": "file"},
                {"name": "", "required": True, "type": "file", "format": None, "items": None},
            ),
            (
                ResponseStrategy.OBJECT,
                {"type": "object"},
                {"name": "", "required": True, "type": "dict", "format": None, "items": None},
            ),
            # # Special data
            # (
            #     ResponseStrategy.STRING,
            #     {
            #         "type": "object",
            #         "additionalProperties": {
            #             "type": "array",
            #             "items": {"type": "string", "enum": ["IP_HOLDER", "PARTNER"]},
            #         },
            #     },
            #     [
            #         {
            #             "id": "random integer value",
            #             "name": "random string value",
            #             "value1": "random string value",
            #             "value2": "random string value",
            #         }
            #     ],
            # ),
        ],
    )
    def test_generate_response_from_data(
        self, ut_enum: ResponseStrategy, test_response_data: dict, expected_value: str
    ):
        # Pre-process
        if test_response_data["type"] == "array":
            set_component_definition(
                OpenAPIV3SchemaParser(
                    data={
                        "components": {
                            "schemas": {
                                "FooResponse": {
                                    "type": "object",
                                    "required": ["id"],
                                    "properties": {
                                        "id": {"type": "integer", "format": "int64"},
                                        "name": {"type": "string"},
                                        "value1": {"type": "string"},
                                        "value2": {"type": "string"},
                                    },
                                    "title": "FooResponse",
                                },
                            },
                        },
                    }
                )
            )

        # Run target
        resp = ut_enum.generate_response_from_data(
            resp_prop_data=test_response_data,
            get_schema_parser_factory=ensure_get_schema_parser_factory,
            # has_ref_callback=_YamlSchema.has_ref,
            get_ref_callback=_YamlSchema.get_schema_ref,
        )

        # Verify
        assert resp
        assert resp == expected_value


class TestConfigLoadingOrder(EnumTestSuite):
    @pytest.fixture(scope="function")
    def enum_obj(self) -> Type[ConfigLoadingOrder]:
        return ConfigLoadingOrder

    @pytest.mark.parametrize(
        "value",
        [
            ConfigLoadingOrder.APIs,
            ConfigLoadingOrder.APPLY,
            "apis",
            "file",
        ],
    )
    def test_to_enum(self, value: Any, enum_obj: Type[ConfigLoadingOrder]):
        super().test_to_enum(value, enum_obj)


class TestOpenAPIVersion(EnumTestSuite):
    @pytest.fixture(scope="function")
    def enum_obj(self) -> Type[OpenAPIVersion]:
        return OpenAPIVersion

    @pytest.mark.parametrize(
        "value",
        [
            OpenAPIVersion.V2,
            OpenAPIVersion.V3,
            "OpenAPI V2",
            "OpenAPI V3",
            "2.0",
            "2.0.0",
            "2.0.4",
            "2.3.7",
            "3.0",
            "3.0.0",
            "3.0.9",
            "3.1.0",
        ],
    )
    def test_to_enum(self, value: Any, enum_obj: Type[OpenAPIVersion]):
        super().test_to_enum(value, enum_obj)

    @pytest.mark.parametrize("value", ["1.0.0", "4.0.0", "invalid value"])
    def test_invalid_enum(self, enum_obj: Type[OpenAPIVersion], value: str):
        with pytest.raises(NotImplementedError) as exc_info:
            enum_obj.to_enum(value)
        assert re.search(re.escape(value), str(exc_info.value)) is not None
