from abc import ABCMeta, abstractmethod
from typing import List, Type, Union

import pytest

from pymock_api.model.enums import ResponseStrategy
from pymock_api.model.openapi._base import ensure_get_schema_parser_factory
from pymock_api.model.openapi._schema_parser import (
    OpenAPIV2SchemaParser,
    OpenAPIV3SchemaParser,
)
from pymock_api.model.openapi._tmp_data_model import (
    BaseTmpDataModel,
    BaseTmpRefDataModel,
    PropertyDetail,
    ResponseProperty,
    TmpResponsePropertyModel,
    TmpResponseRefModel,
    set_component_definition,
)

from ...model.openapi._test_case import DeserializeV2OpenAPIConfigTestCaseFactory

DeserializeV2OpenAPIConfigTestCaseFactory.load()
DESERIALIZE_V2_OPENAPI_DOC_TEST_CASE = DeserializeV2OpenAPIConfigTestCaseFactory.get_test_case()
GENERATE_RESPONSE_CONFIG_FROM_V2_OPENAPI_CONFIG_TEST_CASE = (
    DESERIALIZE_V2_OPENAPI_DOC_TEST_CASE.each_api_http_response_with_strategy
)


class BaseTmpDataModelTestSuite(metaclass=ABCMeta):

    @pytest.fixture(scope="function")
    @abstractmethod
    def under_test(self) -> BaseTmpDataModel:
        pass

    @pytest.mark.parametrize(
        ("strategy", "api_response_detail", "entire_config"), GENERATE_RESPONSE_CONFIG_FROM_V2_OPENAPI_CONFIG_TEST_CASE
    )
    def test_generate_response(
        self,
        under_test: BaseTmpRefDataModel,
        strategy: ResponseStrategy,
        api_response_detail: dict,
        entire_config: dict,
    ):
        # Pre-process
        set_component_definition(OpenAPIV2SchemaParser(data=entire_config))
        tmp_data_model = TmpResponsePropertyModel.deserialize(api_response_detail)

        # Run target function under test
        response_prop_data = under_test._generate_response(
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
        ("strategy", "test_response_data", "expected_value"),
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
        self, under_test: BaseTmpRefDataModel, strategy: ResponseStrategy, test_response_data: dict, expected_value: str
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
        resp = under_test._generate_response_from_data(
            init_response=ResponseProperty.initial_response_data(),
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


class BaseTmpRefDataModelTestSuite(BaseTmpDataModelTestSuite):

    @pytest.fixture(scope="function")
    @abstractmethod
    def under_test(self) -> BaseTmpRefDataModel:
        pass

    #
    # @pytest.mark.parametrize(
    #     ("strategy", "api_response_detail", "entire_config"), GENERATE_RESPONSE_CONFIG_FROM_V2_OPENAPI_CONFIG_TEST_CASE
    # )
    # def test_generate_response(
    #     self,
    #     under_test: BaseTmpRefDataModel,
    #     strategy: ResponseStrategy,
    #     api_response_detail: dict,
    #     entire_config: dict,
    # ):
    #     # Pre-process
    #     set_component_definition(OpenAPIV2SchemaParser(data=entire_config))
    #     tmp_data_model = TmpResponsePropertyModel.deserialize(api_response_detail)
    #
    #     # Run target function under test
    #     response_prop_data = under_test._generate_response(
    #         init_response=ResponseProperty(),
    #         property_value=tmp_data_model,
    #         get_schema_parser_factory=ensure_get_schema_parser_factory,
    #     )
    #
    #     # Verify
    #     assert strategy is ResponseStrategy.OBJECT
    #     assert response_prop_data and isinstance(response_prop_data, PropertyDetail)
    #     # for resp_k, resp_v in response_prop_data.items():
    #     #     assert resp_k in ["name", "required", "type", "format", "items", "FIXME"]
    #     # else:
    #     #     assert response_prop_data and isinstance(response_prop_data, (str, list))
    #     #     if response_prop_data and isinstance(response_prop_data, str):
    #     #         assert response_prop_data in [
    #     #             "random string value",
    #     #             "random integer value",
    #     #             "random boolean value",
    #     #             "random file output stream",
    #     #             "FIXME: Handle the reference",
    #     #         ]
    #     #     else:
    #     #         for item in response_prop_data:
    #     #             for item_value in item.values():
    #     #                 assert item_value in ["random string value", "random integer value", "random boolean value"]
    #
    # @pytest.mark.parametrize(
    #     ("strategy", "expected_type"),
    #     [
    #         # (ResponseStrategy.STRING, str),
    #         # (ResponseStrategy.FILE, str),
    #         (ResponseStrategy.OBJECT, PropertyDetail),
    #     ],
    # )
    # def test_generate_empty_response(
    #     self, under_test: BaseTmpRefDataModel, strategy: ResponseStrategy, expected_type: Union[type, Type]
    # ):
    #     empty_resp = under_test.generate_empty_response()
    #     assert isinstance(empty_resp, expected_type)
    #
    # @pytest.mark.parametrize(
    #     ("strategy", "test_response_data", "expected_value"),
    #     [
    #         # # # General data
    #         # (ResponseStrategy.STRING, {"type": "string"}, "random string value"),
    #         # (ResponseStrategy.FILE, {"type": "string"}, "random string value"),
    #         # (
    #         #     ResponseStrategy.OBJECT,
    #         #     {"type": "string"},
    #         #     {"name": "", "required": True, "type": "str", "format": None, "items": None},
    #         # ),
    #         # # # Each different type as general data
    #         # # For string strategy (the process details of string and file are the same, so it only test one of them)
    #         # (ResponseStrategy.STRING, {"type": "integer"}, "random integer value"),
    #         # (ResponseStrategy.STRING, {"type": "number"}, "random integer value"),
    #         # (ResponseStrategy.STRING, {"type": "boolean"}, "random boolean value"),
    #         # (ResponseStrategy.STRING, {"type": "array", "items": {"type": "integer"}}, ["random integer value"]),
    #         # (
    #         #     ResponseStrategy.STRING,
    #         #     {"type": "array", "items": {"$ref": "#/components/schemas/FooResponse"}},
    #         #     [
    #         #         {
    #         #             "id": "random integer value",
    #         #             "name": "random string value",
    #         #             "value1": "random string value",
    #         #             "value2": "random string value",
    #         #         }
    #         #     ],
    #         # ),
    #         # (ResponseStrategy.STRING, {"type": "file"}, "random file output stream"),
    #         # For object strategy
    #         (
    #             # 1
    #             ResponseStrategy.OBJECT,
    #             {"type": "integer"},
    #             {"name": "", "required": True, "type": "int"},
    #         ),
    #         (
    #             # 2
    #             ResponseStrategy.OBJECT,
    #             {"type": "number"},
    #             {"name": "", "required": True, "type": "int"},
    #         ),
    #         (
    #             # 3
    #             ResponseStrategy.OBJECT,
    #             {"type": "boolean"},
    #             {"name": "", "required": True, "type": "bool"},
    #         ),
    #         (
    #             # 4
    #             ResponseStrategy.OBJECT,
    #             {"type": "array", "items": {"type": "integer"}},
    #             {
    #                 "name": "",
    #                 "required": True,
    #                 "type": "list",
    #                 # "format": None,
    #                 "items": [{"name": "", "required": True, "type": "int"}],
    #             },
    #         ),
    #         (
    #             # 5
    #             ResponseStrategy.OBJECT,
    #             {"type": "array", "items": {"$ref": "#/components/schemas/FooResponse"}},
    #             {
    #                 "name": "",
    #                 "required": True,
    #                 "type": "list",
    #                 # "format": None,
    #                 "items": [
    #                     {"name": "id", "required": True, "type": "int"},
    #                     {"name": "name", "required": True, "type": "str"},
    #                     {"name": "value1", "required": True, "type": "str"},
    #                     {"name": "value2", "required": True, "type": "str"},
    #                 ],
    #             },
    #         ),
    #         (
    #             # 6
    #             ResponseStrategy.OBJECT,
    #             {"type": "file"},
    #             {"name": "", "required": True, "type": "file"},
    #         ),
    #         # # Special data
    #         # (
    #         #     ResponseStrategy.STRING,
    #         #     {
    #         #         "type": "object",
    #         #         "additionalProperties": {
    #         #             "type": "string",
    #         #         },
    #         #     },
    #         #     {"additionalKey": "random string value"},
    #         # ),
    #         # (
    #         #     ResponseStrategy.STRING,
    #         #     {
    #         #         "type": "object",
    #         #         "additionalProperties": {
    #         #             "type": "array",
    #         #             "items": {"type": "string", "enum": ["TYPE_1", "TYPE_2"]},
    #         #         },
    #         #     },
    #         #     {"additionalKey": ["random string value"]},
    #         # ),
    #         # (
    #         #     ResponseStrategy.STRING,
    #         #     {
    #         #         "type": "object",
    #         #         "additionalProperties": {
    #         #             "$ref": "#/components/schemas/FooResponse",
    #         #         },
    #         #     },
    #         #     {
    #         #         "additionalKey": {
    #         #             "id": "random integer value",
    #         #             "name": "random string value",
    #         #             "value1": "random string value",
    #         #             "value2": "random string value",
    #         #         },
    #         #     },
    #         # ),
    #         (
    #             # 7
    #             ResponseStrategy.OBJECT,
    #             {
    #                 "type": "object",
    #                 "additionalProperties": {
    #                     "type": "string",
    #                 },
    #             },
    #             {
    #                 "name": "",
    #                 "required": True,
    #                 "type": "dict",
    #                 # "format": None,
    #                 "items": [{"name": "additionalKey", "required": True, "type": "str"}],
    #             },
    #         ),
    #         (
    #             # 8
    #             ResponseStrategy.OBJECT,
    #             {
    #                 "type": "object",
    #                 "additionalProperties": {
    #                     "type": "array",
    #                     "items": {"type": "string", "enum": ["TYPE_1", "TYPE_2"]},
    #                 },
    #             },
    #             {
    #                 "name": "",
    #                 "required": True,
    #                 "type": "list",
    #                 # "format": None,
    #                 "items": [
    #                     {"name": "", "required": True, "type": "str"},
    #                 ],
    #             },
    #         ),
    #         (
    #             # 9
    #             ResponseStrategy.OBJECT,
    #             {
    #                 "type": "object",
    #                 "additionalProperties": {
    #                     "$ref": "#/components/schemas/FooResponse",
    #                 },
    #             },
    #             {
    #                 "name": "additionalKey",
    #                 "required": True,
    #                 "type": "dict",
    #                 # "format": None,
    #                 "items": [
    #                     {"name": "id", "required": True, "type": "int"},
    #                     {"name": "name", "required": False, "type": "str"},
    #                     {"name": "value1", "required": False, "type": "str"},
    #                     {"name": "value2", "required": False, "type": "str"},
    #                 ],
    #             },
    #         ),
    #         # # Special data about nested config
    #         # (
    #         #     ResponseStrategy.STRING,
    #         #     {
    #         #         "type": "object",
    #         #         "additionalProperties": {
    #         #             "$ref": "#/components/schemas/NestedFooResponse",
    #         #         },
    #         #     },
    #         #     {
    #         #         "additionalKey": {
    #         #             "id": "random integer value",
    #         #             "name": "random string value",
    #         #             "data": [
    #         #                 {
    #         #                     "id": "random integer value",
    #         #                     "value": "random string value",
    #         #                     "url": "random string value",
    #         #                     "urlProperties": {
    #         #                         "homePage": {
    #         #                             "domain": "random string value",
    #         #                             "needAuth": "random boolean value",
    #         #                         },
    #         #                         "detailInfo": {
    #         #                             "domain": "random string value",
    #         #                             "needAuth": "random boolean value",
    #         #                         },
    #         #                     },
    #         #                 },
    #         #             ],
    #         #         }
    #         #     },
    #         # ),
    #         # (
    #         #     ResponseStrategy.STRING,
    #         #     {
    #         #         "$ref": "#/components/schemas/NestedFooResponse",
    #         #     },
    #         #     {
    #         #         "id": "random integer value",
    #         #         "name": "random string value",
    #         #         "data": [
    #         #             {
    #         #                 "id": "random integer value",
    #         #                 "value": "random string value",
    #         #                 "url": "random string value",
    #         #                 "urlProperties": {
    #         #                     "homePage": {
    #         #                         "domain": "random string value",
    #         #                         "needAuth": "random boolean value",
    #         #                     },
    #         #                     "detailInfo": {
    #         #                         "domain": "random string value",
    #         #                         "needAuth": "random boolean value",
    #         #                     },
    #         #                 },
    #         #             },
    #         #         ],
    #         #     },
    #         # ),
    #         (
    #             # 10
    #             ResponseStrategy.OBJECT,
    #             {
    #                 "type": "object",
    #                 "additionalProperties": {
    #                     "$ref": "#/components/schemas/NestedFooResponse",
    #                 },
    #             },
    #             {
    #                 "name": "additionalKey",
    #                 "required": True,
    #                 "type": "dict",
    #                 # "format": None,
    #                 "items": [
    #                     {"name": "id", "required": True, "type": "int"},
    #                     {"name": "name", "required": False, "type": "str"},
    #                     {
    #                         "name": "data",
    #                         "required": False,
    #                         # "format": None,
    #                         "type": "list",
    #                         "items": [
    #                             {"name": "id", "required": True, "type": "int"},
    #                             {"name": "value", "required": True, "type": "str"},
    #                             {"name": "url", "required": True, "type": "str"},
    #                             {
    #                                 "name": "urlProperties",
    #                                 "required": False,
    #                                 # "format": None,
    #                                 "type": "dict",
    #                                 "items": [
    #                                     {
    #                                         "name": "homePage",
    #                                         "required": True,
    #                                         "type": "dict",
    #                                         # "format": None,
    #                                         "items": [
    #                                             {"name": "domain", "required": True, "type": "str"},
    #                                             {"name": "needAuth", "required": True, "type": "bool"},
    #                                         ],
    #                                     },
    #                                     {
    #                                         "name": "detailInfo",
    #                                         "required": True,
    #                                         "type": "dict",
    #                                         # "format": None,
    #                                         "items": [
    #                                             {"name": "domain", "required": True, "type": "str"},
    #                                             {"name": "needAuth", "required": True, "type": "bool"},
    #                                         ],
    #                                     },
    #                                 ],
    #                             },
    #                         ],
    #                     },
    #                 ],
    #             },
    #         ),
    #         (
    #             # 11
    #             ResponseStrategy.OBJECT,
    #             {
    #                 "$ref": "#/components/schemas/NestedFooResponse",
    #             },
    #             [
    #                 {"name": "id", "required": True, "type": "int"},
    #                 {"name": "name", "required": False, "type": "str"},
    #                 {
    #                     "name": "data",
    #                     "required": False,
    #                     # "format": None,
    #                     "type": "list",
    #                     "items": [
    #                         {"name": "id", "required": True, "type": "int"},
    #                         {"name": "value", "required": True, "type": "str"},
    #                         {"name": "url", "required": True, "type": "str"},
    #                         {
    #                             "name": "urlProperties",
    #                             "required": False,
    #                             # "format": None,
    #                             "type": "dict",
    #                             "items": [
    #                                 {
    #                                     "name": "homePage",
    #                                     "required": True,
    #                                     "type": "dict",
    #                                     # "format": None,
    #                                     "items": [
    #                                         {"name": "domain", "required": True, "type": "str"},
    #                                         {"name": "needAuth", "required": True, "type": "bool"},
    #                                     ],
    #                                 },
    #                                 {
    #                                     "name": "detailInfo",
    #                                     "required": True,
    #                                     "type": "dict",
    #                                     # "format": None,
    #                                     "items": [
    #                                         {"name": "domain", "required": True, "type": "str"},
    #                                         {"name": "needAuth", "required": True, "type": "bool"},
    #                                     ],
    #                                 },
    #                             ],
    #                         },
    #                     ],
    #                 },
    #             ],
    #         ),
    #     ],
    # )
    # def test_generate_response_from_data(
    #     self, under_test: BaseTmpRefDataModel, strategy: ResponseStrategy, test_response_data: dict, expected_value: str
    # ):
    #     # Pre-process
    #     if test_response_data.get("type", "array") == "array":
    #         set_component_definition(
    #             OpenAPIV3SchemaParser(
    #                 data={
    #                     "components": {
    #                         "schemas": {
    #                             # For general test
    #                             "FooResponse": {
    #                                 "type": "object",
    #                                 "required": ["id"],
    #                                 "properties": {
    #                                     "id": {"type": "integer", "format": "int64"},
    #                                     "name": {"type": "string"},
    #                                     "value1": {"type": "string"},
    #                                     "value2": {"type": "string"},
    #                                 },
    #                                 "title": "FooResponse",
    #                             },
    #                             # For special case test about nested detail data
    #                             "NestedFooResponse": {
    #                                 "type": "object",
    #                                 "required": ["id"],
    #                                 "properties": {
    #                                     "id": {"type": "integer", "format": "int64"},
    #                                     "name": {"type": "string"},
    #                                     "data": {
    #                                         "type": "array",
    #                                         "items": {"$ref": "#/components/schemas/FooDetailResponse"},
    #                                     },
    #                                 },
    #                             },
    #                             "FooDetailResponse": {
    #                                 "type": "object",
    #                                 "required": ["id"],
    #                                 "properties": {
    #                                     "id": {"type": "integer", "format": "int64"},
    #                                     "value": {"type": "string"},
    #                                     "url": {"type": "string", "format": "uri"},
    #                                     "urlProperties": {"$ref": "#/components/schemas/UrlProperties"},
    #                                 },
    #                             },
    #                             "UrlProperties": {
    #                                 "type": "object",
    #                                 "required": ["homePage", "detailInfo"],
    #                                 "properties": {
    #                                     "homePage": {"$ref": "#/components/schemas/DomainProperty"},
    #                                     "detailInfo": {"$ref": "#/components/schemas/DomainProperty"},
    #                                 },
    #                             },
    #                             "DomainProperty": {
    #                                 "type": "object",
    #                                 "required": ["homePage", "needAuth"],
    #                                 "properties": {
    #                                     "domain": {"type": "string"},
    #                                     "needAuth": {"type": "boolean"},
    #                                 },
    #                             },
    #                         },
    #                     },
    #                 }
    #             )
    #         )
    #     test_response_data_model = TmpResponsePropertyModel.deserialize(test_response_data)
    #
    #     # Run target
    #     resp = under_test._generate_response_from_data(
    #         init_response=ResponseProperty.initial_response_data(),
    #         resp_prop_data=test_response_data_model,
    #         get_schema_parser_factory=ensure_get_schema_parser_factory,
    #     )
    #
    #     # Verify
    #     print(f"resp: {resp}")
    #     assert resp
    #     if isinstance(resp, list):
    #         resp = [r.serialize() for r in resp]
    #     else:
    #         resp = resp.serialize()
    #     assert resp == expected_value

    @pytest.mark.parametrize(("under_test", "expect_result"), [])
    @abstractmethod
    def test_has_ref(self, under_test: BaseTmpRefDataModel, expect_result: str):
        assert under_test.has_ref() == expect_result

    @pytest.mark.parametrize(("under_test", "expect_result"), [])
    @abstractmethod
    def test_get_ref(self, under_test: BaseTmpRefDataModel, expect_result: str):
        assert under_test.get_ref() == expect_result

    @pytest.mark.parametrize(
        ("strategy", "ut_response_data", "expect_result"),
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
        self, under_test: BaseTmpRefDataModel, strategy: ResponseStrategy, ut_response_data: dict, expect_result: dict
    ):
        ut_response = under_test._process_empty_body_response_by_string_strategy(
            response_columns_setting=ut_response_data
        )
        assert ut_response == expect_result

    @pytest.mark.parametrize(
        ("strategy", "ut_response_config", "expect_result"),
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
        self,
        under_test: BaseTmpRefDataModel,
        strategy: ResponseStrategy,
        ut_response_config: List[PropertyDetail],
        expect_result: List[PropertyDetail],
    ):
        new_response_config = under_test._process_empty_body_response(response_columns_setting=ut_response_config)
        assert new_response_config == expect_result


class TestTmpResponsePropertyModel(BaseTmpRefDataModelTestSuite):

    @pytest.fixture(scope="function")
    def under_test(self) -> TmpResponsePropertyModel:
        return TmpResponsePropertyModel()

    @pytest.mark.parametrize(
        ("under_test", "expect_result"),
        [
            (TmpResponsePropertyModel(ref=None), ""),
            (TmpResponsePropertyModel(ref=""), ""),
            (TmpResponsePropertyModel(ref="reference value"), "ref"),
            (TmpResponsePropertyModel(additionalProperties=TmpResponsePropertyModel(ref=None)), ""),
            (TmpResponsePropertyModel(additionalProperties=TmpResponsePropertyModel(ref="")), ""),
            (
                TmpResponsePropertyModel(additionalProperties=TmpResponsePropertyModel(ref="reference value")),
                "additionalProperties",
            ),
        ],
    )
    def test_has_ref(self, under_test: BaseTmpRefDataModel, expect_result: str):
        super().test_has_ref(under_test, expect_result)

    @pytest.mark.parametrize(
        ("under_test", "expect_result"),
        [
            (TmpResponsePropertyModel(ref="reference value"), "reference value"),
            (
                TmpResponsePropertyModel(additionalProperties=TmpResponsePropertyModel(ref="reference value")),
                "reference value",
            ),
        ],
    )
    def test_get_ref(self, under_test: BaseTmpRefDataModel, expect_result: str):
        super().test_get_ref(under_test, expect_result)

    @pytest.mark.parametrize(
        ("under_test", "expect_result"),
        [
            (TmpResponsePropertyModel(), True),
            (TmpResponsePropertyModel(value_type=None), True),
            (TmpResponsePropertyModel(ref=None), True),
            (TmpResponsePropertyModel(value_type=""), True),
            (TmpResponsePropertyModel(ref=""), True),
            (TmpResponsePropertyModel(value_type="data type", ref=""), False),
            (TmpResponsePropertyModel(value_type=None, ref="reference value"), False),
        ],
    )
    def test_is_empty(self, under_test: TmpResponsePropertyModel, expect_result: str):
        assert under_test.is_empty() == expect_result


class TestTmpResponseRefModel(BaseTmpDataModelTestSuite):

    @pytest.fixture(scope="function")
    def under_test(self) -> TmpResponseRefModel:
        return TmpResponseRefModel()

    @pytest.mark.parametrize(
        ("strategy", "test_response_data", "expected_value"),
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
        self, strategy: ResponseStrategy, test_response_data: TmpResponseRefModel, expected_value: ResponseProperty
    ):
        response_config = test_response_data.process_reference_object(
            init_response=ResponseProperty.initial_response_data(),
            # response_schema_ref=test_response_data,
            get_schema_parser_factory=ensure_get_schema_parser_factory,
        )
        assert response_config == expected_value


class TestPropertyDetail:

    @pytest.mark.parametrize(
        ("strategy", "expected_type"),
        [
            # (ResponseStrategy.STRING, str),
            # (ResponseStrategy.FILE, str),
            (ResponseStrategy.OBJECT, PropertyDetail),
        ],
    )
    def test_generate_empty_response(self, strategy: ResponseStrategy, expected_type: Union[type, Type]):
        empty_resp = PropertyDetail.generate_empty_response()
        assert isinstance(empty_resp, expected_type)
