import re
from abc import ABCMeta, abstractmethod
from decimal import Decimal
from enum import Enum
from typing import Any, List, Optional, Type, Union

import pytest

from pymock_api._utils.random import DigitRange, ValueSize
from pymock_api.model.enums import (
    ConfigLoadingOrder,
    FormatStrategy,
    OpenAPIVersion,
    ResponseStrategy,
    ValueFormat,
    set_loading_function,
)
from pymock_api.model.openapi._base import ensure_get_schema_parser_factory
from pymock_api.model.openapi._schema_parser import (
    OpenAPIV2SchemaParser,
    OpenAPIV3SchemaParser,
    set_component_definition,
)
from pymock_api.model.openapi._tmp_data_model import (
    PropertyDetail,
    ResponseProperty,
    TmpResponsePropertyModel,
    TmpResponseRefModel,
)

from ..._test_utils import Verify
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
        tmp_data_model = TmpResponsePropertyModel.deserialize(api_response_detail)

        # Run target function under test
        response_prop_data = strategy._generate_response(
            init_response=ResponseProperty(),
            property_value=tmp_data_model,
            get_schema_parser_factory=ensure_get_schema_parser_factory,
        )

        # Verify
        assert strategy is ResponseStrategy.OBJECT
        assert response_prop_data and isinstance(response_prop_data, PropertyDetail)
        # for resp_k, resp_v in response_prop_data.items():
        #     assert resp_k in ["name", "required", "type", "format", "items", "FIXME"]
        # else:
        #     assert response_prop_data and isinstance(response_prop_data, (str, list))
        #     if response_prop_data and isinstance(response_prop_data, str):
        #         assert response_prop_data in [
        #             "random string value",
        #             "random integer value",
        #             "random boolean value",
        #             "random file output stream",
        #             "FIXME: Handle the reference",
        #         ]
        #     else:
        #         for item in response_prop_data:
        #             for item_value in item.values():
        #                 assert item_value in ["random string value", "random integer value", "random boolean value"]

    @pytest.mark.parametrize(
        ("ut_enum", "expected_type"),
        [
            # (ResponseStrategy.STRING, str),
            # (ResponseStrategy.FILE, str),
            (ResponseStrategy.OBJECT, PropertyDetail),
        ],
    )
    def test_generate_empty_response(self, ut_enum: ResponseStrategy, expected_type: Union[type, Type]):
        empty_resp = ut_enum._generate_empty_response()
        assert isinstance(empty_resp, expected_type)

    @pytest.mark.parametrize(
        ("ut_enum", "test_response_data", "expected_value"),
        [
            # # # General data
            # (ResponseStrategy.STRING, {"type": "string"}, "random string value"),
            # (ResponseStrategy.FILE, {"type": "string"}, "random string value"),
            # (
            #     ResponseStrategy.OBJECT,
            #     {"type": "string"},
            #     {"name": "", "required": True, "type": "str", "format": None, "items": None},
            # ),
            # # # Each different type as general data
            # # For string strategy (the process details of string and file are the same, so it only test one of them)
            # (ResponseStrategy.STRING, {"type": "integer"}, "random integer value"),
            # (ResponseStrategy.STRING, {"type": "number"}, "random integer value"),
            # (ResponseStrategy.STRING, {"type": "boolean"}, "random boolean value"),
            # (ResponseStrategy.STRING, {"type": "array", "items": {"type": "integer"}}, ["random integer value"]),
            # (
            #     ResponseStrategy.STRING,
            #     {"type": "array", "items": {"$ref": "#/components/schemas/FooResponse"}},
            #     [
            #         {
            #             "id": "random integer value",
            #             "name": "random string value",
            #             "value1": "random string value",
            #             "value2": "random string value",
            #         }
            #     ],
            # ),
            # (ResponseStrategy.STRING, {"type": "file"}, "random file output stream"),
            # For object strategy
            (
                # 1
                ResponseStrategy.OBJECT,
                {"type": "integer"},
                {"name": "", "required": True, "type": "int"},
            ),
            (
                # 2
                ResponseStrategy.OBJECT,
                {"type": "number"},
                {"name": "", "required": True, "type": "int"},
            ),
            (
                # 3
                ResponseStrategy.OBJECT,
                {"type": "boolean"},
                {"name": "", "required": True, "type": "bool"},
            ),
            (
                # 4
                ResponseStrategy.OBJECT,
                {"type": "array", "items": {"type": "integer"}},
                {
                    "name": "",
                    "required": True,
                    "type": "list",
                    # "format": None,
                    "items": [{"name": "", "required": True, "type": "int"}],
                },
            ),
            (
                # 5
                ResponseStrategy.OBJECT,
                {"type": "array", "items": {"$ref": "#/components/schemas/FooResponse"}},
                {
                    "name": "",
                    "required": True,
                    "type": "list",
                    # "format": None,
                    "items": [
                        {"name": "id", "required": True, "type": "int"},
                        {"name": "name", "required": True, "type": "str"},
                        {"name": "value1", "required": True, "type": "str"},
                        {"name": "value2", "required": True, "type": "str"},
                    ],
                },
            ),
            (
                # 6
                ResponseStrategy.OBJECT,
                {"type": "file"},
                {"name": "", "required": True, "type": "file"},
            ),
            # # Special data
            # (
            #     ResponseStrategy.STRING,
            #     {
            #         "type": "object",
            #         "additionalProperties": {
            #             "type": "string",
            #         },
            #     },
            #     {"additionalKey": "random string value"},
            # ),
            # (
            #     ResponseStrategy.STRING,
            #     {
            #         "type": "object",
            #         "additionalProperties": {
            #             "type": "array",
            #             "items": {"type": "string", "enum": ["TYPE_1", "TYPE_2"]},
            #         },
            #     },
            #     {"additionalKey": ["random string value"]},
            # ),
            # (
            #     ResponseStrategy.STRING,
            #     {
            #         "type": "object",
            #         "additionalProperties": {
            #             "$ref": "#/components/schemas/FooResponse",
            #         },
            #     },
            #     {
            #         "additionalKey": {
            #             "id": "random integer value",
            #             "name": "random string value",
            #             "value1": "random string value",
            #             "value2": "random string value",
            #         },
            #     },
            # ),
            (
                # 7
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
                    # "format": None,
                    "items": [{"name": "additionalKey", "required": True, "type": "str"}],
                },
            ),
            (
                # 8
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
                    # "format": None,
                    "items": [
                        {"name": "", "required": True, "type": "str"},
                    ],
                },
            ),
            (
                # 9
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
                    # "format": None,
                    "items": [
                        {"name": "id", "required": True, "type": "int"},
                        {"name": "name", "required": False, "type": "str"},
                        {"name": "value1", "required": False, "type": "str"},
                        {"name": "value2", "required": False, "type": "str"},
                    ],
                },
            ),
            # # Special data about nested config
            # (
            #     ResponseStrategy.STRING,
            #     {
            #         "type": "object",
            #         "additionalProperties": {
            #             "$ref": "#/components/schemas/NestedFooResponse",
            #         },
            #     },
            #     {
            #         "additionalKey": {
            #             "id": "random integer value",
            #             "name": "random string value",
            #             "data": [
            #                 {
            #                     "id": "random integer value",
            #                     "value": "random string value",
            #                     "url": "random string value",
            #                     "urlProperties": {
            #                         "homePage": {
            #                             "domain": "random string value",
            #                             "needAuth": "random boolean value",
            #                         },
            #                         "detailInfo": {
            #                             "domain": "random string value",
            #                             "needAuth": "random boolean value",
            #                         },
            #                     },
            #                 },
            #             ],
            #         }
            #     },
            # ),
            # (
            #     ResponseStrategy.STRING,
            #     {
            #         "$ref": "#/components/schemas/NestedFooResponse",
            #     },
            #     {
            #         "id": "random integer value",
            #         "name": "random string value",
            #         "data": [
            #             {
            #                 "id": "random integer value",
            #                 "value": "random string value",
            #                 "url": "random string value",
            #                 "urlProperties": {
            #                     "homePage": {
            #                         "domain": "random string value",
            #                         "needAuth": "random boolean value",
            #                     },
            #                     "detailInfo": {
            #                         "domain": "random string value",
            #                         "needAuth": "random boolean value",
            #                     },
            #                 },
            #             },
            #         ],
            #     },
            # ),
            (
                # 10
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
                    # "format": None,
                    "items": [
                        {"name": "id", "required": True, "type": "int"},
                        {"name": "name", "required": False, "type": "str"},
                        {
                            "name": "data",
                            "required": False,
                            # "format": None,
                            "type": "list",
                            "items": [
                                {"name": "id", "required": True, "type": "int"},
                                {"name": "value", "required": True, "type": "str"},
                                {"name": "url", "required": True, "type": "str"},
                                {
                                    "name": "urlProperties",
                                    "required": False,
                                    # "format": None,
                                    "type": "dict",
                                    "items": [
                                        {
                                            "name": "homePage",
                                            "required": True,
                                            "type": "dict",
                                            # "format": None,
                                            "items": [
                                                {"name": "domain", "required": True, "type": "str"},
                                                {"name": "needAuth", "required": True, "type": "bool"},
                                            ],
                                        },
                                        {
                                            "name": "detailInfo",
                                            "required": True,
                                            "type": "dict",
                                            # "format": None,
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
                # 11
                ResponseStrategy.OBJECT,
                {
                    "$ref": "#/components/schemas/NestedFooResponse",
                },
                [
                    {"name": "id", "required": True, "type": "int"},
                    {"name": "name", "required": False, "type": "str"},
                    {
                        "name": "data",
                        "required": False,
                        # "format": None,
                        "type": "list",
                        "items": [
                            {"name": "id", "required": True, "type": "int"},
                            {"name": "value", "required": True, "type": "str"},
                            {"name": "url", "required": True, "type": "str"},
                            {
                                "name": "urlProperties",
                                "required": False,
                                # "format": None,
                                "type": "dict",
                                "items": [
                                    {
                                        "name": "homePage",
                                        "required": True,
                                        "type": "dict",
                                        # "format": None,
                                        "items": [
                                            {"name": "domain", "required": True, "type": "str"},
                                            {"name": "needAuth", "required": True, "type": "bool"},
                                        ],
                                    },
                                    {
                                        "name": "detailInfo",
                                        "required": True,
                                        "type": "dict",
                                        # "format": None,
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
        test_response_data_model = TmpResponsePropertyModel.deserialize(test_response_data)

        # Run target
        resp = ut_enum._generate_response_from_data(
            init_response=ut_enum.initial_response_data(),
            resp_prop_data=test_response_data_model,
            get_schema_parser_factory=ensure_get_schema_parser_factory,
        )

        # Verify
        print(f"resp: {resp}")
        assert resp
        if isinstance(resp, list):
            resp = [r.serialize() for r in resp]
        else:
            resp = resp.serialize()
        assert resp == expected_value

    @pytest.mark.parametrize(
        ("ut_enum", "test_response_data", "expected_value"),
        [
            # (
            #     ResponseStrategy.STRING,
            #     {"type": "object"},
            #     {"strategy": ResponseStrategy.STRING, "data": {"THIS_IS_EMPTY": "empty value"}},
            # ),
            (
                ResponseStrategy.OBJECT,
                TmpResponseRefModel(value_type="object"),
                # {"type": "object"},
                ResponseProperty(
                    data=[PropertyDetail(name="THIS_IS_EMPTY", required=False, type=None, format=None, items=[])],
                ),
                # {
                #     "strategy": ResponseStrategy.OBJECT,
                #     "data": [{"name": "THIS_IS_EMPTY", "required": False, "type": None, "format": None, "items": []}],
                # },
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
        ("ut_enum", "ut_response_data", "expect_result"),
        [
            (ResponseStrategy.STRING, {"THIS_IS_EMPTY": "empty value"}, {}),
            (
                ResponseStrategy.STRING,
                {"key1": "value1", "sample_dict": {"THIS_IS_EMPTY": "empty value"}},
                {"key1": "value1", "sample_dict": {}},
            ),
            (
                ResponseStrategy.STRING,
                {"key1": "value1", "sample_list": ["empty value"]},
                {"key1": "value1", "sample_list": ["empty value"]},
            ),
            (
                ResponseStrategy.STRING,
                {"key1": "value1", "sample_list": [{"THIS_IS_EMPTY": "empty value"}]},
                {"key1": "value1", "sample_list": []},
            ),
            (
                ResponseStrategy.STRING,
                {"key1": "value1", "sample_dict": {"inner_list": [{"THIS_IS_EMPTY": "empty value"}]}},
                {"key1": "value1", "sample_dict": {"inner_list": []}},
            ),
            (
                ResponseStrategy.STRING,
                {
                    "key1": "value1",
                    "sample_list": [{"inner_dict": "inner_value", "inner_dict2": {"THIS_IS_EMPTY": "empty value"}}],
                },
                {"key1": "value1", "sample_list": [{"inner_dict": "inner_value", "inner_dict2": {}}]},
            ),
            (
                ResponseStrategy.STRING,
                {
                    "key1": "value1",
                    "sample_list": [
                        {
                            "inner_dict": "inner_value",
                            "inner_dict2": {"THIS_IS_EMPTY": "empty value"},
                            "inner_list": ["empty value"],
                        }
                    ],
                },
                {
                    "key1": "value1",
                    "sample_list": [{"inner_dict": "inner_value", "inner_dict2": {}, "inner_list": ["empty value"]}],
                },
            ),
        ],
    )
    def test__process_empty_body_response_by_string_strategy(
        self, ut_enum: ResponseStrategy, ut_response_data: dict, expect_result: dict
    ):
        ut_response = ut_enum._process_empty_body_response_by_string_strategy(response_columns_setting=ut_response_data)
        assert ut_response == expect_result

    @pytest.mark.parametrize(
        ("ut_enum", "ut_response_config", "expect_result"),
        [
            (
                ResponseStrategy.OBJECT,
                [PropertyDetail(name="THIS_IS_EMPTY", required=True, type=None, format=None, items=None)],
                [PropertyDetail(name="", required=True, type=None, format=None, is_empty=True, items=None)],
            ),
            (
                ResponseStrategy.OBJECT,
                [
                    PropertyDetail(
                        name="sample_list",
                        required=True,
                        type="list",
                        format=None,
                        items=[
                            PropertyDetail(
                                name="THIS_IS_EMPTY",
                                required=True,
                                type=None,
                                format=None,
                                items=None,
                            ),
                        ],
                    ),
                ],
                [
                    PropertyDetail(
                        name="sample_list",
                        required=True,
                        type="list",
                        format=None,
                        is_empty=True,
                        items=[],
                    ),
                ],
            ),
            (
                ResponseStrategy.OBJECT,
                [
                    PropertyDetail(
                        name="sample_list",
                        required=True,
                        type="list",
                        format=None,
                        items=[
                            PropertyDetail(
                                name="sample_nested_list",
                                required=True,
                                type="list",
                                format=None,
                                items=[
                                    PropertyDetail(
                                        name="sample_nested_list",
                                        required=True,
                                        type="list",
                                        format=None,
                                        items=[
                                            PropertyDetail(name="", required=True, type="str", format=None, items=None),
                                        ],
                                    ),
                                    PropertyDetail(
                                        name="sample_nested_dict",
                                        required=True,
                                        type="dict",
                                        format=None,
                                        items=[
                                            PropertyDetail(
                                                name="THIS_IS_EMPTY", required=True, type=None, format=None, items=None
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
                [
                    PropertyDetail(
                        name="sample_list",
                        required=True,
                        type="list",
                        format=None,
                        items=[
                            PropertyDetail(
                                name="sample_nested_list",
                                required=True,
                                type="list",
                                format=None,
                                items=[
                                    PropertyDetail(
                                        name="sample_nested_list",
                                        required=True,
                                        type="list",
                                        format=None,
                                        items=[
                                            PropertyDetail(name="", required=True, type="str", format=None, items=None),
                                        ],
                                    ),
                                    PropertyDetail(
                                        name="sample_nested_dict",
                                        required=True,
                                        type="dict",
                                        format=None,
                                        is_empty=True,
                                        items=[],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )
    def test__process_empty_body_response(
        self, ut_enum: ResponseStrategy, ut_response_config: List[PropertyDetail], expect_result: List[PropertyDetail]
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


class TestValueFormat(EnumTestSuite):
    @pytest.fixture(scope="function")
    def enum_obj(self) -> Type[ValueFormat]:
        return ValueFormat

    @pytest.mark.parametrize(
        "value",
        [
            ValueFormat.String,
            ValueFormat.Integer,
            ValueFormat.BigDecimal,
            ValueFormat.Boolean,
            ValueFormat.Enum,
            "str",
            "int",
            "big_decimal",
            "bool",
            "enum",
            str,
            int,
            float,
            bool,
        ],
    )
    def test_to_enum(self, value: Any, enum_obj: Type[ValueFormat]):
        super().test_to_enum(value, enum_obj)

    @pytest.mark.parametrize("invalid_data_type", [list, tuple, set, dict])
    def test_to_enum_error(self, enum_obj: Type[ValueFormat], invalid_data_type: object):
        with pytest.raises(ValueError) as exc_info:
            enum_obj.to_enum(invalid_data_type)
        assert re.search(r"doesn't support " + re.escape(str(invalid_data_type)), str(exc_info.value)) is not None

    @pytest.mark.parametrize(
        ("formatter", "enums", "expect_type"),
        [
            (ValueFormat.String, [], str),
            (ValueFormat.Integer, [], int),
            (ValueFormat.BigDecimal, [], Decimal),
            (ValueFormat.Boolean, [], bool),
            (ValueFormat.Enum, ["ENUM_1", "ENUM_2", "ENUM_3"], str),
        ],
    )
    def test_generate_value(self, formatter: ValueFormat, enums: List[str], expect_type: object):
        value = formatter.generate_value(enums=enums)
        assert value is not None
        assert isinstance(value, expect_type)
        if enums:
            assert value in enums

    @pytest.mark.parametrize(
        ("formatter", "size", "expect_type"),
        [
            (ValueFormat.String, ValueSize(max=3, min=0), str),
            (ValueFormat.String, ValueSize(max=8, min=5), str),
        ],
    )
    def test_generate_string_value(self, formatter: ValueFormat, size: ValueSize, expect_type: object):
        value = formatter.generate_value(size=size)
        assert value is not None
        assert isinstance(value, expect_type)
        assert size.min <= len(value) <= size.max

    @pytest.mark.parametrize(
        ("formatter", "digit_range", "expect_type", "expect_range"),
        [
            (ValueFormat.Integer, DigitRange(integer=1, decimal=0), int, ValueSize(min=-9, max=9)),
            (ValueFormat.Integer, DigitRange(integer=3, decimal=0), int, ValueSize(min=-999, max=999)),
            (ValueFormat.Integer, DigitRange(integer=1, decimal=2), int, ValueSize(min=-9, max=9)),
            (ValueFormat.BigDecimal, DigitRange(integer=1, decimal=0), Decimal, ValueSize(min=-9, max=9)),
            (ValueFormat.BigDecimal, DigitRange(integer=3, decimal=0), Decimal, ValueSize(min=-999, max=999)),
            (ValueFormat.BigDecimal, DigitRange(integer=3, decimal=2), Decimal, ValueSize(min=-999.99, max=999.99)),
            (ValueFormat.BigDecimal, DigitRange(integer=0, decimal=3), Decimal, ValueSize(min=-0.999, max=0.999)),
        ],
    )
    def test_generate_numerical_value(
        self, formatter: ValueFormat, digit_range: DigitRange, expect_type: object, expect_range: ValueSize
    ):
        value = formatter.generate_value(digit=digit_range)
        assert value is not None
        assert isinstance(value, expect_type)
        Verify.numerical_value_should_be_in_range(value=value, expect_range=expect_range)

    @pytest.mark.parametrize(
        ("formatter", "invalid_enums", "invalid_size", "invalid_digit", "expect_err_msg"),
        [
            (ValueFormat.String, None, None, None, r"must not be empty"),
            (ValueFormat.String, None, ValueSize(max=0, min=0), None, r"must be greater than 0"),
            (ValueFormat.String, None, ValueSize(max=-1, min=0), None, r"must be greater than 0"),
            (ValueFormat.String, None, ValueSize(max=3, min=-1), None, r"must be greater or equal to 0"),
            (ValueFormat.Integer, None, None, None, r"must not be empty"),
            (ValueFormat.Integer, None, None, DigitRange(integer=-2, decimal=0), r"must be greater than 0"),
            (ValueFormat.BigDecimal, None, None, None, r"must not be empty"),
            (ValueFormat.BigDecimal, None, None, DigitRange(integer=-2, decimal=0), r"must be greater or equal to 0"),
            (ValueFormat.BigDecimal, None, None, DigitRange(integer=1, decimal=-3), r"must be greater or equal to 0"),
            (ValueFormat.Enum, None, None, None, r"must not be empty"),
            (ValueFormat.Enum, [], None, None, r"must not be empty"),
            (ValueFormat.Enum, [123], None, None, r"must be string"),
        ],
    )
    def test_failure_generate_value(
        self,
        formatter: ValueFormat,
        invalid_enums: Optional[List[str]],
        invalid_size: Optional[ValueSize],
        invalid_digit: Optional[DigitRange],
        expect_err_msg: str,
    ):
        with pytest.raises(AssertionError) as exc_info:
            formatter.generate_value(enums=invalid_enums, size=invalid_size, digit=invalid_digit)
        assert re.search(expect_err_msg, str(exc_info.value), re.IGNORECASE)

    @pytest.mark.parametrize(
        ("formatter", "enums", "size", "digit_range", "expect_regex"),
        [
            (
                ValueFormat.String,
                [],
                ValueSize(max=3, min=0),
                None,
                r"[@\-_!#$%^&+*()\[\]<>?=/\\|`'\"}{~:;,.\w\s]{0,3}",
            ),
            (
                ValueFormat.String,
                [],
                ValueSize(max=128, min=5),
                None,
                r"[@\-_!#$%^&+*()\[\]<>?=/\\|`'\"}{~:;,.\w\s]{5,128}",
            ),
            (ValueFormat.Integer, [], None, DigitRange(integer=3, decimal=0), r"\d{1,3}"),
            (ValueFormat.Integer, [], None, DigitRange(integer=3, decimal=2), r"\d{1,3}"),
            (ValueFormat.Integer, [], None, DigitRange(integer=10, decimal=2), r"\d{1,10}"),
            (ValueFormat.BigDecimal, [], None, DigitRange(integer=4, decimal=0), r"\d{1,4}\.?\d{0,0}"),
            (ValueFormat.BigDecimal, [], None, DigitRange(integer=4, decimal=2), r"\d{1,4}\.?\d{0,2}"),
            (ValueFormat.BigDecimal, [], None, DigitRange(integer=10, decimal=3), r"\d{1,10}\.?\d{0,3}"),
            (ValueFormat.Enum, ["ENUM_1", "ENUM_2", "ENUM_3"], None, None, r"(ENUM_1|ENUM_2|ENUM_3)"),
        ],
    )
    def test_generate_regex(
        self,
        formatter: ValueFormat,
        enums: List[str],
        size: Optional[ValueSize],
        digit_range: Optional[DigitRange],
        expect_regex: str,
    ):
        regex = formatter.generate_regex(enums=enums, size=size, digit=digit_range)
        assert regex == expect_regex

    @pytest.mark.parametrize(
        ("formatter", "invalid_enums", "invalid_size", "invalid_digit", "expect_err_msg"),
        [
            (ValueFormat.String, None, None, None, r"must not be empty"),
            (ValueFormat.String, None, ValueSize(max=0, min=0), None, r"must be greater than 0"),
            (ValueFormat.String, None, ValueSize(max=-1, min=0), None, r"must be greater than 0"),
            (ValueFormat.String, None, ValueSize(max=3, min=-1), None, r"must be greater or equal to 0"),
            (ValueFormat.Integer, None, None, None, r"must not be empty"),
            (ValueFormat.Integer, None, None, DigitRange(integer=-2, decimal=0), r"must be greater than 0"),
            (ValueFormat.BigDecimal, None, None, None, r"must not be empty"),
            (ValueFormat.BigDecimal, None, None, DigitRange(integer=-2, decimal=0), r"must be greater or equal to 0"),
            (ValueFormat.BigDecimal, None, None, DigitRange(integer=1, decimal=-3), r"must be greater or equal to 0"),
            (ValueFormat.Enum, None, None, None, r"must not be empty"),
            (ValueFormat.Enum, [], None, None, r"must not be empty"),
            (ValueFormat.Enum, [123], None, None, r"must be string"),
        ],
    )
    def test_failure_generate_regex(
        self,
        formatter: ValueFormat,
        invalid_enums: Optional[List[str]],
        invalid_size: Optional[ValueSize],
        invalid_digit: Optional[DigitRange],
        expect_err_msg: str,
    ):
        with pytest.raises(AssertionError) as exc_info:
            formatter.generate_regex(enums=invalid_enums, size=invalid_size, digit=invalid_digit)
        assert re.search(expect_err_msg, str(exc_info.value), re.IGNORECASE)


class TestFormatStrategy(EnumTestSuite):
    @pytest.fixture(scope="function")
    def enum_obj(self) -> Type[FormatStrategy]:
        return FormatStrategy

    @pytest.mark.parametrize(
        "value",
        [
            FormatStrategy.BY_DATA_TYPE,
            FormatStrategy.FROM_ENUMS,
            FormatStrategy.CUSTOMIZE,
            FormatStrategy.FROM_TEMPLATE,
            "by_data_type",
            "from_enums",
            "customize",
            "from_template",
        ],
    )
    def test_to_enum(self, value: Union[str, FormatStrategy], enum_obj: Type[FormatStrategy]):
        super().test_to_enum(value, enum_obj)

    @pytest.mark.parametrize(
        ("format_strategy", "data_type", "expect_value"),
        [
            (FormatStrategy.BY_DATA_TYPE, str, ValueFormat.String),
            (FormatStrategy.BY_DATA_TYPE, int, ValueFormat.Integer),
            (FormatStrategy.BY_DATA_TYPE, float, ValueFormat.BigDecimal),
            (FormatStrategy.BY_DATA_TYPE, "big_decimal", ValueFormat.BigDecimal),
            (FormatStrategy.BY_DATA_TYPE, bool, ValueFormat.Boolean),
            (FormatStrategy.BY_DATA_TYPE, "enum", ValueFormat.Enum),
        ],
    )
    def test_to_value_format(
        self, format_strategy: FormatStrategy, data_type: Union[str, object], expect_value: ValueFormat
    ):
        assert format_strategy.to_value_format(data_type=data_type) == expect_value

    @pytest.mark.parametrize(
        "format_strategy",
        [
            FormatStrategy.CUSTOMIZE,
            FormatStrategy.FROM_TEMPLATE,
        ],
    )
    def test_failure_to_value_format(self, format_strategy: FormatStrategy):
        with pytest.raises(RuntimeError):
            format_strategy.to_value_format(data_type="any data type")

    @pytest.mark.parametrize(
        ("strategy", "data_type", "enums", "expect_type"),
        [
            (FormatStrategy.BY_DATA_TYPE, str, [], str),
            (FormatStrategy.BY_DATA_TYPE, int, [], int),
            (FormatStrategy.BY_DATA_TYPE, "big_decimal", [], Decimal),
            (FormatStrategy.BY_DATA_TYPE, bool, [], bool),
            (FormatStrategy.FROM_ENUMS, str, ["ENUM_1", "ENUM_2", "ENUM_3"], str),
        ],
    )
    def test_generate_not_customize_value(
        self, strategy: FormatStrategy, data_type: Union[None, str, object], enums: List[str], expect_type: type
    ):
        value = strategy.generate_not_customize_value(data_type=data_type, enums=enums)
        assert value is not None
        assert isinstance(value, expect_type)
        if enums:
            assert value in enums

    @pytest.mark.parametrize(
        ("strategy", "data_type", "size", "expect_type"),
        [
            (FormatStrategy.BY_DATA_TYPE, str, ValueSize(max=5, min=2), str),
            (FormatStrategy.BY_DATA_TYPE, str, ValueSize(max=128, min=10), str),
        ],
    )
    def test_generate_string_value(
        self, strategy: FormatStrategy, data_type: Union[None, str, object], size: ValueSize, expect_type: type
    ):
        value = strategy.generate_not_customize_value(data_type=data_type, size=size)
        assert value is not None
        assert isinstance(value, expect_type)
        assert size.min <= len(value) <= size.max

    @pytest.mark.parametrize(
        ("strategy", "data_type", "digit_range", "expect_type", "expect_range"),
        [
            (FormatStrategy.BY_DATA_TYPE, int, DigitRange(integer=1, decimal=0), int, ValueSize(min=-9, max=9)),
            (FormatStrategy.BY_DATA_TYPE, int, DigitRange(integer=3, decimal=0), int, ValueSize(min=-999, max=999)),
            (FormatStrategy.BY_DATA_TYPE, int, DigitRange(integer=1, decimal=2), int, ValueSize(min=-9, max=9)),
            (FormatStrategy.BY_DATA_TYPE, float, DigitRange(integer=1, decimal=0), Decimal, ValueSize(min=-9, max=9)),
            (
                FormatStrategy.BY_DATA_TYPE,
                float,
                DigitRange(integer=3, decimal=0),
                Decimal,
                ValueSize(min=-999, max=999),
            ),
            (
                FormatStrategy.BY_DATA_TYPE,
                float,
                DigitRange(integer=3, decimal=2),
                Decimal,
                ValueSize(min=-999.99, max=999.99),
            ),
            (
                FormatStrategy.BY_DATA_TYPE,
                float,
                DigitRange(integer=0, decimal=3),
                Decimal,
                ValueSize(min=-0.999, max=0.999),
            ),
            (
                FormatStrategy.BY_DATA_TYPE,
                "big_decimal",
                DigitRange(integer=1, decimal=0),
                Decimal,
                ValueSize(min=-9, max=9),
            ),
            (
                FormatStrategy.BY_DATA_TYPE,
                "big_decimal",
                DigitRange(integer=3, decimal=0),
                Decimal,
                ValueSize(min=-999, max=999),
            ),
            (
                FormatStrategy.BY_DATA_TYPE,
                "big_decimal",
                DigitRange(integer=3, decimal=2),
                Decimal,
                ValueSize(min=-999.99, max=999.99),
            ),
            (
                FormatStrategy.BY_DATA_TYPE,
                "big_decimal",
                DigitRange(integer=0, decimal=3),
                Decimal,
                ValueSize(min=-0.999, max=0.999),
            ),
        ],
    )
    def test_generate_numerical_value(
        self,
        strategy: FormatStrategy,
        data_type: Union[None, str, object],
        digit_range: DigitRange,
        expect_type: object,
        expect_range: ValueSize,
    ):
        value = strategy.generate_not_customize_value(data_type=data_type, digit=digit_range)
        assert value is not None
        assert isinstance(value, expect_type)
        Verify.numerical_value_should_be_in_range(value=value, expect_range=expect_range)

    @pytest.mark.parametrize("strategy", [FormatStrategy.CUSTOMIZE])
    def test_failure_generate_not_customize_value(self, strategy: FormatStrategy):
        with pytest.raises(ValueError):
            assert strategy.generate_not_customize_value()
