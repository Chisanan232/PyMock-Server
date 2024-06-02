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
from pymock_api.model.openapi._base import ensure_get_schema_parser_factory
from pymock_api.model.openapi._schema_parser import (
    OpenAPIV2SchemaParser,
    OpenAPIV3SchemaParser,
    set_component_definition,
)

from ..model.openapi._test_case import DeserializeV2OpenAPIConfigTestCaseFactory

DeserializeV2OpenAPIConfigTestCaseFactory.load()
DESERIALIZE_V2_OPENAPI_DOC_TEST_CASE = DeserializeV2OpenAPIConfigTestCaseFactory.get_test_case()
GENERATE_RESPONSE_CONFIG_FROM_V2_OPENAPI_CONFIG_TEST_CASE = (
    DESERIALIZE_V2_OPENAPI_DOC_TEST_CASE.each_api_http_response_with_strategy
)


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
        ("strategy", "api_response_detail", "entire_config"), GENERATE_RESPONSE_CONFIG_FROM_V2_OPENAPI_CONFIG_TEST_CASE
    )
    def test_generate_response(self, strategy: ResponseStrategy, api_response_detail: dict, entire_config: dict):
        # Pre-process
        set_component_definition(OpenAPIV2SchemaParser(data=entire_config))

        # Run target function under test
        response_prop_data = strategy._generate_response(
            init_response={},
            property_value=api_response_detail,
            get_schema_parser_factory=ensure_get_schema_parser_factory,
        )

        # Verify
        if strategy is ResponseStrategy.OBJECT:
            assert response_prop_data and isinstance(response_prop_data, dict)
            for resp_k, resp_v in response_prop_data.items():
                assert resp_k in ["name", "required", "type", "format", "items", "FIXME"]
        else:
            assert response_prop_data and isinstance(response_prop_data, (str, list))
            if response_prop_data and isinstance(response_prop_data, str):
                assert response_prop_data in [
                    "random string value",
                    "random integer value",
                    "random boolean value",
                    "random file output stream",
                    "FIXME: Handle the reference",
                ]
            else:
                for item in response_prop_data:
                    for item_value in item.values():
                        assert item_value in ["random string value", "random integer value", "random boolean value"]

    @pytest.mark.parametrize(
        ("ut_enum", "expected_type"),
        [
            (ResponseStrategy.STRING, str),
            (ResponseStrategy.FILE, str),
            (ResponseStrategy.OBJECT, dict),
        ],
    )
    def test_generate_empty_response(self, ut_enum: ResponseStrategy, expected_type: type):
        empty_resp = ut_enum._generate_empty_response()
        assert isinstance(empty_resp, expected_type)

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
            (ResponseStrategy.STRING, {"type": "array", "items": {"type": "integer"}}, ["random integer value"]),
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
                {"type": "array", "items": {"type": "integer"}},
                {
                    "name": "",
                    "required": True,
                    "type": "list",
                    "format": None,
                    "items": [{"name": "", "required": True, "type": "int", "format": None, "items": None}],
                },
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
            # # Special data
            (
                ResponseStrategy.STRING,
                {
                    "type": "object",
                    "additionalProperties": {
                        "type": "string",
                    },
                },
                {"additionalKey": "random string value"},
            ),
            (
                ResponseStrategy.STRING,
                {
                    "type": "object",
                    "additionalProperties": {
                        "type": "array",
                        "items": {"type": "string", "enum": ["TYPE_1", "TYPE_2"]},
                    },
                },
                {"additionalKey": ["random string value"]},
            ),
            (
                ResponseStrategy.STRING,
                {
                    "type": "object",
                    "additionalProperties": {
                        "$ref": "#/components/schemas/FooResponse",
                    },
                },
                {
                    "additionalKey": {
                        "id": "random integer value",
                        "name": "random string value",
                        "value1": "random string value",
                        "value2": "random string value",
                    },
                },
            ),
            (
                ResponseStrategy.OBJECT,
                {
                    "type": "object",
                    "additionalProperties": {
                        "type": "string",
                    },
                },
                {
                    "name": "",
                    "required": True,
                    "type": "dict",
                    "format": None,
                    "items": [
                        {"name": "additionalKey", "required": True, "type": "str", "format": None, "items": None}
                    ],
                },
            ),
            (
                ResponseStrategy.OBJECT,
                {
                    "type": "object",
                    "additionalProperties": {
                        "type": "array",
                        "items": {"type": "string", "enum": ["TYPE_1", "TYPE_2"]},
                    },
                },
                {
                    "name": "",
                    "required": True,
                    "type": "list",
                    "format": None,
                    "items": [
                        {"name": "", "required": True, "type": "str", "format": None, "items": None},
                    ],
                },
            ),
            (
                ResponseStrategy.OBJECT,
                {
                    "type": "object",
                    "additionalProperties": {
                        "$ref": "#/components/schemas/FooResponse",
                    },
                },
                {
                    "name": "additionalKey",
                    "required": True,
                    "type": "dict",
                    "format": None,
                    "items": [
                        {"name": "id", "required": True, "type": "int", "format": None, "items": None},
                        {"name": "name", "required": False, "type": "str", "format": None, "items": None},
                        {"name": "value1", "required": False, "type": "str", "format": None, "items": None},
                        {"name": "value2", "required": False, "type": "str", "format": None, "items": None},
                    ],
                },
            ),
            # # Special data about nested config
            (
                ResponseStrategy.STRING,
                {
                    "type": "object",
                    "additionalProperties": {
                        "$ref": "#/components/schemas/NestedFooResponse",
                    },
                },
                {
                    "additionalKey": {
                        "id": "random integer value",
                        "name": "random string value",
                        "data": [
                            {
                                "id": "random integer value",
                                "value": "random string value",
                                "url": "random string value",
                                "urlProperties": {
                                    "homePage": {
                                        "domain": "random string value",
                                        "needAuth": "random boolean value",
                                    },
                                    "detailInfo": {
                                        "domain": "random string value",
                                        "needAuth": "random boolean value",
                                    },
                                },
                            },
                        ],
                    }
                },
            ),
            (
                ResponseStrategy.STRING,
                {
                    "$ref": "#/components/schemas/NestedFooResponse",
                },
                {
                    "id": "random integer value",
                    "name": "random string value",
                    "data": [
                        {
                            "id": "random integer value",
                            "value": "random string value",
                            "url": "random string value",
                            "urlProperties": {
                                "homePage": {
                                    "domain": "random string value",
                                    "needAuth": "random boolean value",
                                },
                                "detailInfo": {
                                    "domain": "random string value",
                                    "needAuth": "random boolean value",
                                },
                            },
                        },
                    ],
                },
            ),
            (
                ResponseStrategy.OBJECT,
                {
                    "type": "object",
                    "additionalProperties": {
                        "$ref": "#/components/schemas/NestedFooResponse",
                    },
                },
                {
                    "name": "additionalKey",
                    "required": True,
                    "type": "dict",
                    "format": None,
                    "items": [
                        {"name": "id", "required": True, "type": "int", "format": None, "items": None},
                        {"name": "name", "required": False, "type": "str", "format": None, "items": None},
                        {
                            "name": "data",
                            "required": False,
                            "format": None,
                            "type": "list",
                            "items": [
                                {"name": "id", "required": True, "type": "int"},
                                {"name": "value", "required": True, "type": "str"},
                                {"name": "url", "required": True, "type": "str"},
                                {
                                    "name": "urlProperties",
                                    "required": False,
                                    "format": None,
                                    "type": "dict",
                                    "items": [
                                        {
                                            "name": "homePage",
                                            "required": True,
                                            "type": "dict",
                                            "format": None,
                                            "items": [
                                                {"name": "domain", "required": True, "type": "str"},
                                                {"name": "needAuth", "required": True, "type": "bool"},
                                            ],
                                        },
                                        {
                                            "name": "detailInfo",
                                            "required": True,
                                            "type": "dict",
                                            "format": None,
                                            "items": [
                                                {"name": "domain", "required": True, "type": "str"},
                                                {"name": "needAuth", "required": True, "type": "bool"},
                                            ],
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                },
            ),
            (
                ResponseStrategy.OBJECT,
                {
                    "$ref": "#/components/schemas/NestedFooResponse",
                },
                [
                    {"name": "id", "required": True, "type": "int", "format": None, "items": None},
                    {"name": "name", "required": False, "type": "str", "format": None, "items": None},
                    {
                        "name": "data",
                        "required": False,
                        "format": None,
                        "type": "list",
                        "items": [
                            {"name": "id", "required": True, "type": "int"},
                            {"name": "value", "required": True, "type": "str"},
                            {"name": "url", "required": True, "type": "str"},
                            {
                                "name": "urlProperties",
                                "required": False,
                                "format": None,
                                "type": "dict",
                                "items": [
                                    {
                                        "name": "homePage",
                                        "required": True,
                                        "type": "dict",
                                        "format": None,
                                        "items": [
                                            {"name": "domain", "required": True, "type": "str"},
                                            {"name": "needAuth", "required": True, "type": "bool"},
                                        ],
                                    },
                                    {
                                        "name": "detailInfo",
                                        "required": True,
                                        "type": "dict",
                                        "format": None,
                                        "items": [
                                            {"name": "domain", "required": True, "type": "str"},
                                            {"name": "needAuth", "required": True, "type": "bool"},
                                        ],
                                    },
                                ],
                            },
                        ],
                    },
                ],
            ),
        ],
    )
    def test_generate_response_from_data(
        self, ut_enum: ResponseStrategy, test_response_data: dict, expected_value: str
    ):
        # Pre-process
        if test_response_data.get("type", "array") == "array":
            set_component_definition(
                OpenAPIV3SchemaParser(
                    data={
                        "components": {
                            "schemas": {
                                # For general test
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
                                # For special case test about nested detail data
                                "NestedFooResponse": {
                                    "type": "object",
                                    "required": ["id"],
                                    "properties": {
                                        "id": {"type": "integer", "format": "int64"},
                                        "name": {"type": "string"},
                                        "data": {
                                            "type": "array",
                                            "items": {"$ref": "#/components/schemas/FooDetailResponse"},
                                        },
                                    },
                                },
                                "FooDetailResponse": {
                                    "type": "object",
                                    "required": ["id"],
                                    "properties": {
                                        "id": {"type": "integer", "format": "int64"},
                                        "value": {"type": "string"},
                                        "url": {"type": "string", "format": "uri"},
                                        "urlProperties": {"$ref": "#/components/schemas/UrlProperties"},
                                    },
                                },
                                "UrlProperties": {
                                    "type": "object",
                                    "required": ["homePage", "detailInfo"],
                                    "properties": {
                                        "homePage": {"$ref": "#/components/schemas/DomainProperty"},
                                        "detailInfo": {"$ref": "#/components/schemas/DomainProperty"},
                                    },
                                },
                                "DomainProperty": {
                                    "type": "object",
                                    "required": ["homePage", "needAuth"],
                                    "properties": {
                                        "domain": {"type": "string"},
                                        "needAuth": {"type": "boolean"},
                                    },
                                },
                            },
                        },
                    }
                )
            )

        # Run target
        resp = ut_enum._generate_response_from_data(
            init_response=ut_enum.initial_response_data(),
            resp_prop_data=test_response_data,
            get_schema_parser_factory=ensure_get_schema_parser_factory,
        )

        # Verify
        print(f"resp: {resp}")
        assert resp
        assert resp == expected_value

    @pytest.mark.parametrize(
        ("ut_enum", "test_response_data", "expected_value"),
        [
            (
                ResponseStrategy.STRING,
                {"type": "object"},
                {"strategy": ResponseStrategy.STRING, "data": {"THIS_IS_EMPTY": "empty value"}},
            ),
            (
                ResponseStrategy.OBJECT,
                {"type": "object"},
                {
                    "strategy": ResponseStrategy.OBJECT,
                    "data": [{"name": "THIS_IS_EMPTY", "required": False, "type": None, "format": None, "items": []}],
                },
            ),
        ],
    )
    def test__process_reference_object_with_empty_body_response(
        self, ut_enum: ResponseStrategy, test_response_data: dict, expected_value: str
    ):
        response_config = ut_enum._process_reference_object(
            init_response=ut_enum.initial_response_data(),
            response_schema_ref=test_response_data,
            get_schema_parser_factory=ensure_get_schema_parser_factory,
        )
        assert response_config == expected_value

    @pytest.mark.parametrize(
        ("ut_enum", "ut_response_config", "expect_result"),
        [
            (
                ResponseStrategy.OBJECT,
                [{"name": "THIS_IS_EMPTY", "required": True, "type": None, "format": None, "items": None}],
                [{"name": "", "required": True, "type": None, "format": None, "is_empty": True, "items": None}],
            ),
            (
                ResponseStrategy.OBJECT,
                [
                    {
                        "name": "sample_list",
                        "required": True,
                        "type": "list",
                        "format": None,
                        "items": [
                            {"name": "THIS_IS_EMPTY", "required": True, "type": None, "format": None, "items": None}
                        ],
                    },
                ],
                [
                    {
                        "name": "sample_list",
                        "required": True,
                        "type": "list",
                        "format": None,
                        "is_empty": True,
                        "items": [],
                    },
                ],
            ),
            (
                ResponseStrategy.OBJECT,
                [
                    {
                        "name": "sample_list",
                        "required": True,
                        "type": "list",
                        "format": None,
                        "items": [
                            {
                                "name": "sample_nested_list",
                                "required": True,
                                "type": "list",
                                "format": None,
                                "items": [{"name": "", "required": True, "type": "str", "format": None, "items": None}],
                            },
                            {
                                "name": "sample_nested_dict",
                                "required": True,
                                "type": "dict",
                                "format": None,
                                "items": [
                                    {
                                        "name": "THIS_IS_EMPTY",
                                        "required": True,
                                        "type": None,
                                        "format": None,
                                        "items": None,
                                    }
                                ],
                            },
                        ],
                    }
                ],
                [
                    {
                        "name": "sample_list",
                        "required": True,
                        "type": "list",
                        "format": None,
                        "items": [
                            {
                                "name": "sample_nested_list",
                                "required": True,
                                "type": "list",
                                "format": None,
                                "items": [{"name": "", "required": True, "type": "str", "format": None, "items": None}],
                            },
                            {
                                "name": "sample_nested_dict",
                                "required": True,
                                "type": "dict",
                                "format": None,
                                "is_empty": True,
                                "items": [],
                            },
                        ],
                    }
                ],
            ),
        ],
    )
    def test__process_empty_body_response(
        self, ut_enum: ResponseStrategy, ut_response_config: dict, expect_result: dict
    ):
        new_response_config = ut_enum._process_empty_body_response(response_columns_setting=ut_response_config)
        assert new_response_config == expect_result


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
