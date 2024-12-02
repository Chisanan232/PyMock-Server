import random
import re
from abc import ABC, ABCMeta, abstractmethod
from typing import List, Optional, Tuple, Union

import pytest

try:
    from http import HTTPMethod, HTTPStatus
except ImportError:
    from http import HTTPStatus
    from pymock_api.model.http import HTTPMethod

from pymock_api import APIConfig as PyMockAPI_APIConfig
from pymock_api.exceptions import CannotParsingAPIDocumentVersion
from pymock_api.model import MockAPI, OpenAPIVersion
from pymock_api.model.api_config import _Config
from pymock_api.model.api_config.apis import ResponseStrategy
from pymock_api.model.api_doc_config._base import Transferable, set_openapi_version
from pymock_api.model.api_doc_config._model_adapter import (
    APIAdapter,
    PropertyDetailAdapter,
    RequestParameterAdapter,
    ResponsePropertyAdapter,
)
from pymock_api.model.api_doc_config.base_config import (
    BaseAPIDocConfig,
    BaseReferencialConfig,
    _BaseAPIConfigWithMethod,
    set_component_definition,
)
from pymock_api.model.api_doc_config.config import (
    APIConfig,
    APIConfigWithMethodV2,
    APIConfigWithMethodV3,
    HttpConfigV2,
    HttpConfigV3,
    OpenAPIDocumentConfig,
    ReferenceConfig,
    ReferenceConfigProperty,
    RequestParameter,
    RequestSchema,
    SwaggerAPIDocumentConfig,
    get_api_doc_version,
)
from pymock_api.model.api_doc_config.content_type import ContentType

from ...model.api_doc_config._test_case import (
    DeserializeV2OpenAPIConfigTestCaseFactory,
    DeserializeV3OpenAPIConfigTestCaseFactory,
)

DeserializeV2OpenAPIConfigTestCaseFactory.load()
DESERIALIZE_V2_OPENAPI_DOC_TEST_CASE = DeserializeV2OpenAPIConfigTestCaseFactory.get_test_case()
DESERIALIZE_V2_OPENAPI_ENTIRE_CONFIG_TEST_CASE = DESERIALIZE_V2_OPENAPI_DOC_TEST_CASE.entire_config
DESERIALIZE_V2_OPENAPI_ENTIRE_API_TEST_CASE = DESERIALIZE_V2_OPENAPI_DOC_TEST_CASE.each_apis
DESERIALIZE_V2_OPENAPI_API_REQUEST_PARAMETERS_TEST_CASE = (
    DESERIALIZE_V2_OPENAPI_DOC_TEST_CASE.reference_api_http_request_parameters
)
GENERATE_RESPONSE_CONFIG_FROM_V2_OPENAPI_CONFIG_TEST_CASE = DESERIALIZE_V2_OPENAPI_DOC_TEST_CASE.each_api_http_response
PARSE_V2_OPENAPI_REQUEST_PARAMETERS_WITH_REFERENCE_INFO_TEST_CASE = (
    DESERIALIZE_V2_OPENAPI_DOC_TEST_CASE.general_api_http_request_parameters
)
PARSE_V2_OPENAPI_RESPONSES_TEST_CASE = DESERIALIZE_V2_OPENAPI_DOC_TEST_CASE.entire_api_http_response

DeserializeV3OpenAPIConfigTestCaseFactory.load()
V3_OPENAPI_API_DOC_CONFIG_TEST_CASE = DeserializeV3OpenAPIConfigTestCaseFactory.get_test_case()
DESERIALIZE_V3_OPENAPI_ENTIRE_CONFIG_TEST_CASE = V3_OPENAPI_API_DOC_CONFIG_TEST_CASE.entire_config
PARSE_V3_OPENAPI_RESPONSES_TEST_CASE = V3_OPENAPI_API_DOC_CONFIG_TEST_CASE.entire_api_http_response
DESERIALIZE_V3_OPENAPI_ENTIRE_API_TEST_CASE = V3_OPENAPI_API_DOC_CONFIG_TEST_CASE.each_apis


class BaseAPIDocConfigTestSuite(metaclass=ABCMeta):

    @pytest.fixture(scope="function")
    @abstractmethod
    def under_test(self) -> BaseAPIDocConfig:
        pass

    @pytest.mark.parametrize(
        ("api_response_detail", "entire_config"), GENERATE_RESPONSE_CONFIG_FROM_V2_OPENAPI_CONFIG_TEST_CASE
    )
    def test_generate_response(
        self,
        under_test: BaseReferencialConfig,
        api_response_detail: ReferenceConfigProperty,
        entire_config: dict,
    ):
        # Pre-process
        set_component_definition(entire_config.get("definitions", {}))

        # Run target function under test
        response_prop_data = under_test._generate_response(
            init_response=ResponsePropertyAdapter(),
            property_value=api_response_detail,
        )

        # Verify
        assert response_prop_data and isinstance(response_prop_data, PropertyDetailAdapter)
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
        ("test_response_data", "expected_value"),
        [
            # # # General data
            # For object strategy
            (
                # 1
                {"type": "integer"},
                {"name": "", "required": True, "type": "int"},
            ),
            (
                # 2
                {"type": "number"},
                {"name": "", "required": True, "type": "int"},
            ),
            (
                # 3
                {"type": "boolean"},
                {"name": "", "required": True, "type": "bool"},
            ),
            (
                # 4
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
                {"type": "file"},
                {"name": "", "required": True, "type": "file"},
            ),
            # # Special data
            (
                # 7
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
            (
                # 10
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
        self, under_test: BaseReferencialConfig, test_response_data: dict, expected_value: str
    ):
        # Pre-process
        if test_response_data.get("type", "array") == "array":
            set_component_definition(
                {
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
                }
            )
        test_response_data_model = ReferenceConfigProperty.deserialize(test_response_data)

        # Run target
        resp = under_test._generate_response_from_data(
            init_response=ResponsePropertyAdapter.initial_response_data(),
            resp_prop_data=test_response_data_model,
        )

        # Verify
        print(f"resp: {resp}")
        assert resp
        if isinstance(resp, list):
            resp = [r.serialize() for r in resp]
        else:
            resp = resp.serialize()
        assert resp == expected_value


class BaseReferencialConfigTestSuite(BaseAPIDocConfigTestSuite):

    @pytest.fixture(scope="function")
    @abstractmethod
    def under_test(self) -> BaseReferencialConfig:
        pass

    @pytest.mark.parametrize(("under_test", "expect_result"), [])
    @abstractmethod
    def test_has_ref(self, under_test: BaseReferencialConfig, expect_result: str):
        assert under_test.has_ref() == expect_result

    @pytest.mark.parametrize(("under_test", "expect_result"), [])
    @abstractmethod
    def test_get_ref(self, under_test: BaseReferencialConfig, expect_result: str):
        assert under_test.get_ref() == expect_result

    def test_get_schema_ref_with_not_exist_ref(self, under_test: BaseReferencialConfig):
        with pytest.raises(ValueError) as exc_info:
            under_test.get_schema_ref()
        assert re.search(r"no ref", str(exc_info.value), re.IGNORECASE)

    @pytest.mark.parametrize(
        ("ut_response_config", "expect_result"),
        [
            (
                [PropertyDetailAdapter(name="THIS_IS_EMPTY", required=True, value_type=None, format=None, items=None)],
                [
                    PropertyDetailAdapter(
                        name="", required=True, value_type=None, format=None, is_empty=True, items=None
                    )
                ],
            ),
            (
                [
                    PropertyDetailAdapter(
                        name="sample_list",
                        required=True,
                        value_type="list",
                        format=None,
                        items=[
                            PropertyDetailAdapter(
                                name="THIS_IS_EMPTY",
                                required=True,
                                value_type=None,
                                format=None,
                                items=None,
                            ),
                        ],
                    ),
                ],
                [
                    PropertyDetailAdapter(
                        name="sample_list",
                        required=True,
                        value_type="list",
                        format=None,
                        is_empty=True,
                        items=[],
                    ),
                ],
            ),
            (
                [
                    PropertyDetailAdapter(
                        name="sample_list",
                        required=True,
                        value_type="list",
                        format=None,
                        items=[
                            PropertyDetailAdapter(
                                name="sample_nested_list",
                                required=True,
                                value_type="list",
                                format=None,
                                items=[
                                    PropertyDetailAdapter(
                                        name="sample_nested_list",
                                        required=True,
                                        value_type="list",
                                        format=None,
                                        items=[
                                            PropertyDetailAdapter(
                                                name="", required=True, value_type="str", format=None, items=None
                                            ),
                                        ],
                                    ),
                                    PropertyDetailAdapter(
                                        name="sample_nested_dict",
                                        required=True,
                                        value_type="dict",
                                        format=None,
                                        items=[
                                            PropertyDetailAdapter(
                                                name="THIS_IS_EMPTY",
                                                required=True,
                                                value_type=None,
                                                format=None,
                                                items=None,
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
                [
                    PropertyDetailAdapter(
                        name="sample_list",
                        required=True,
                        value_type="list",
                        format=None,
                        items=[
                            PropertyDetailAdapter(
                                name="sample_nested_list",
                                required=True,
                                value_type="list",
                                format=None,
                                items=[
                                    PropertyDetailAdapter(
                                        name="sample_nested_list",
                                        required=True,
                                        value_type="list",
                                        format=None,
                                        items=[
                                            PropertyDetailAdapter(
                                                name="", required=True, value_type="str", format=None, items=None
                                            ),
                                        ],
                                    ),
                                    PropertyDetailAdapter(
                                        name="sample_nested_dict",
                                        required=True,
                                        value_type="dict",
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
        under_test: BaseReferencialConfig,
        ut_response_config: List[PropertyDetailAdapter],
        expect_result: List[PropertyDetailAdapter],
    ):
        new_response_config = under_test._process_empty_body_response(response_columns_setting=ut_response_config)
        assert new_response_config == expect_result


class TestReferenceConfigProperty(BaseReferencialConfigTestSuite):

    @pytest.fixture(scope="function")
    def under_test(self) -> ReferenceConfigProperty:
        return ReferenceConfigProperty()

    @pytest.mark.parametrize(
        ("under_test", "expect_result"),
        [
            (ReferenceConfigProperty(ref=None), ""),
            (ReferenceConfigProperty(ref=""), ""),
            (ReferenceConfigProperty(ref="reference value"), "ref"),
            (ReferenceConfigProperty(additionalProperties=ReferenceConfigProperty(ref=None)), ""),
            (ReferenceConfigProperty(additionalProperties=ReferenceConfigProperty(ref="")), ""),
            (
                ReferenceConfigProperty(additionalProperties=ReferenceConfigProperty(ref="reference value")),
                "additionalProperties",
            ),
        ],
    )
    def test_has_ref(self, under_test: BaseReferencialConfig, expect_result: str):
        super().test_has_ref(under_test, expect_result)

    @pytest.mark.parametrize(
        ("under_test", "expect_result"),
        [
            (ReferenceConfigProperty(ref="reference value"), "reference value"),
            (
                ReferenceConfigProperty(additionalProperties=ReferenceConfigProperty(ref="reference value")),
                "reference value",
            ),
        ],
    )
    def test_get_ref(self, under_test: BaseReferencialConfig, expect_result: str):
        super().test_get_ref(under_test, expect_result)

    @pytest.mark.parametrize(
        ("under_test", "expect_result"),
        [
            (ReferenceConfigProperty(), True),
            (ReferenceConfigProperty(value_type=None), True),
            (ReferenceConfigProperty(ref=None), True),
            (ReferenceConfigProperty(value_type=""), True),
            (ReferenceConfigProperty(ref=""), True),
            (ReferenceConfigProperty(value_type="data type", ref=""), False),
            (ReferenceConfigProperty(value_type=None, ref="reference value"), False),
        ],
    )
    def test_is_empty(self, under_test: ReferenceConfigProperty, expect_result: str):
        assert under_test.is_empty() == expect_result


class TestRequestParameter(BaseReferencialConfigTestSuite):

    @pytest.fixture(scope="function")
    def under_test(self) -> RequestParameter:
        return RequestParameter()

    def test_converting_with_invalid_items(self, under_test: RequestParameter):
        with pytest.raises(ValueError):
            under_test.deserialize(data={"items": ["invalid data type"]})

    @pytest.mark.parametrize(
        ("under_test", "expect_result"),
        [
            (RequestParameter(schema=None), ""),
            (RequestParameter(schema=RequestSchema(ref=None)), ""),
            (RequestParameter(schema=RequestSchema(ref="")), ""),
            (RequestParameter(schema=RequestSchema(ref="reference value")), "schema"),
        ],
    )
    def test_has_ref(self, under_test: BaseReferencialConfig, expect_result: str):
        super().test_has_ref(under_test, expect_result)

    @pytest.mark.parametrize(
        ("under_test", "expect_result"),
        [
            (RequestParameter(schema=RequestSchema(ref="reference value")), "reference value"),
        ],
    )
    def test_get_ref(self, under_test: BaseReferencialConfig, expect_result: str):
        super().test_get_ref(under_test, expect_result)

    @pytest.mark.parametrize(
        ("openapi_doc_data", "entire_openapi_config"), PARSE_V2_OPENAPI_REQUEST_PARAMETERS_WITH_REFERENCE_INFO_TEST_CASE
    )
    def test_process_has_ref_request_parameters_with_valid_value(
        self, under_test: RequestParameter, openapi_doc_data: dict, entire_openapi_config: dict
    ):
        # Pre-process
        set_component_definition(entire_openapi_config.get("definitions", {}))

        # Run target function
        openapi_doc_data_model = under_test.deserialize(openapi_doc_data)
        parameters = openapi_doc_data_model.process_has_ref_request_parameters()

        # Verify
        assert parameters and isinstance(parameters, list)
        assert len(parameters) == len(entire_openapi_config["definitions"]["UpdateFooRequest"]["properties"].keys())
        type_checksum = list(map(lambda p: isinstance(p, RequestParameterAdapter), parameters))
        assert False not in type_checksum

    @pytest.mark.parametrize("openapi_doc_data", DESERIALIZE_V2_OPENAPI_API_REQUEST_PARAMETERS_TEST_CASE)
    def test_process_has_ref_request_parameters_with_invalid_value(
        self, under_test: RequestParameter, openapi_doc_data: dict
    ):
        with pytest.raises(ValueError) as exc_info:
            # Run target function
            openapi_doc_data_model = under_test.deserialize(openapi_doc_data)
            openapi_doc_data_model.process_has_ref_request_parameters()

        # Verify
        assert re.search(r".{1,64}no ref.{1,64}", str(exc_info.value), re.IGNORECASE)


class TestReferenceConfig(BaseAPIDocConfigTestSuite):

    @pytest.fixture(scope="function")
    def under_test(self) -> ReferenceConfig:
        return ReferenceConfig()

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
                ReferenceConfig(value_type="object"),
                # {"type": "object"},
                ResponsePropertyAdapter(
                    data=[
                        PropertyDetailAdapter(
                            name="THIS_IS_EMPTY", required=False, value_type=None, format=None, items=[]
                        )
                    ],
                ),
                # {
                #     "strategy": ResponseStrategy.OBJECT,
                #     "data": [{"name": "THIS_IS_EMPTY", "required": False, "type": None, "format": None, "items": []}],
                # },
            ),
        ],
    )
    def test__process_reference_object_with_empty_body_response(
        self,
        strategy: ResponseStrategy,
        test_response_data: ReferenceConfig,
        expected_value: ResponsePropertyAdapter,
    ):
        response_config = test_response_data.process_reference_object(
            init_response=ResponsePropertyAdapter.initial_response_data(),
        )
        assert response_config == expected_value


class BaseAPIConfigWithMethodTestSuite(BaseAPIDocConfigTestSuite, ABC):

    @pytest.mark.parametrize(
        ("openapi_doc_data", "entire_openapi_config", "doc_version", "schema_key", "api_data_model"),
        [],
    )
    @abstractmethod
    def test_to_request_adapter(
        self,
        under_test: _BaseAPIConfigWithMethod,
        openapi_doc_data: dict,
        entire_openapi_config: dict,
        doc_version: OpenAPIVersion,
        schema_key: str,
        api_data_model: _BaseAPIConfigWithMethod,
    ):
        print(f"[DEBUG in test__process_api_params] ")
        # Pre-process
        set_openapi_version(doc_version)
        set_component_definition(entire_openapi_config.get(schema_key, {}))

        under_test = under_test.deserialize(openapi_doc_data)

        # Run target function
        parameters = under_test.to_request_adapter(http_method="HTTP method")

        # Verify
        self._verify_req_parameter(openapi_doc_data, parameters)

        # Finally
        set_openapi_version(OpenAPIVersion.V3)

    @abstractmethod
    def _verify_req_parameter(self, openapi_doc_data: dict, parameters: List[RequestParameterAdapter]) -> None:
        pass

    @pytest.mark.parametrize(("api_detail", "entire_config"), [])
    def test_to_responses_adapter(self, under_test: _BaseAPIConfigWithMethod, api_detail: dict, entire_config: dict):
        # Pre-process
        set_openapi_version(self._api_doc_version)
        set_component_definition(entire_config.get(self._common_objects_yaml_schema, {}))

        # Run target function under test
        print(f"[DEBUG in test] api_detail: {api_detail}")
        # parser_instance = parser(parser=OpenAPIV2PathSchemaParser(data=api_detail))
        under_test = under_test.deserialize(api_detail)
        response_data = under_test.to_responses_adapter()
        print(f"[DEBUG in test] response_data: {response_data}")

        # Verify
        resp_200 = api_detail["responses"]["200"]
        resp_200_model = self._deserialize_as_response_model(resp_200)
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

    @abstractmethod
    def _deserialize_as_response_model(self, resp_200: dict) -> HttpConfigV2:
        pass

    @property
    @abstractmethod
    def _common_objects_yaml_schema(self) -> str:
        pass

    @property
    @abstractmethod
    def _api_doc_version(self) -> OpenAPIVersion:
        pass


class TestHttpConfigV3:

    @pytest.fixture(scope="function")
    def data_model(self) -> HttpConfigV3:
        return HttpConfigV3()

    @pytest.mark.parametrize(
        ("given_content_type", "find_content_type", "expect_result"),
        [
            (ContentType.APPLICATION_JSON, ContentType.APPLICATION_JSON, ContentType.APPLICATION_JSON),
            (
                ContentType.APPLICATION_OCTET_STREAM,
                ContentType.APPLICATION_OCTET_STREAM,
                ContentType.APPLICATION_OCTET_STREAM,
            ),
            (ContentType.ALL, ContentType.ALL, ContentType.ALL),
            (ContentType.APPLICATION_OCTET_STREAM, ContentType.APPLICATION_JSON, None),
            (ContentType.APPLICATION_JSON, ContentType.ALL, None),
            (ContentType.ALL, ContentType.APPLICATION_OCTET_STREAM, None),
        ],
    )
    def test_exist_setting(
        self,
        data_model: HttpConfigV3,
        given_content_type: ContentType,
        find_content_type: ContentType,
        expect_result: Optional[ContentType],
    ):
        # given
        data_model.content = {given_content_type: HttpConfigV2()}

        # when
        exist_content_type = data_model.exist_setting(content_type=find_content_type)

        # should
        assert exist_content_type == expect_result

    @pytest.mark.parametrize(
        "content_type", [ContentType.APPLICATION_JSON, ContentType.APPLICATION_OCTET_STREAM, ContentType.ALL]
    )
    def test_get_setting(self, data_model: HttpConfigV3, content_type: ContentType):
        # given
        content_type_setting = HttpConfigV2()
        data_model.content = {content_type: content_type_setting}

        # when
        exist_content_type_setting = data_model.get_setting(content_type=content_type)

        # should
        assert exist_content_type_setting == content_type_setting

    @pytest.mark.parametrize(
        "content_type", [ContentType.APPLICATION_JSON, ContentType.APPLICATION_OCTET_STREAM, ContentType.ALL]
    )
    def test_get_setting_with_invalid_content_type(self, data_model: HttpConfigV3, content_type: ContentType):
        # given
        data_model.content = {content_type: HttpConfigV2()}

        # when
        not_exist_content_type = random.choice(list(filter(lambda t: t is not content_type, ContentType)))
        with pytest.raises(ValueError) as exc_info:
            data_model.get_setting(content_type=not_exist_content_type)

        # should
        assert re.search(r"cannot find.{0,64}content type.{0,64}", str(exc_info.value), re.IGNORECASE)


class TestAPIConfigWithMethodV2(BaseAPIConfigWithMethodTestSuite):

    @pytest.fixture(scope="function")
    def under_test(self) -> APIConfigWithMethodV2:
        return APIConfigWithMethodV2()

    @pytest.mark.parametrize(
        ("openapi_doc_data", "entire_openapi_config", "doc_version", "schema_key", "api_data_model"),
        DESERIALIZE_V2_OPENAPI_ENTIRE_API_TEST_CASE,
    )
    def test_to_request_adapter(
        self,
        under_test: APIConfigWithMethodV2,
        openapi_doc_data: dict,
        entire_openapi_config: dict,
        doc_version: OpenAPIVersion,
        schema_key: str,
        api_data_model: APIConfigWithMethodV2,
    ):
        super().test_to_request_adapter(
            under_test=under_test,
            openapi_doc_data=openapi_doc_data,
            entire_openapi_config=entire_openapi_config,
            doc_version=doc_version,
            schema_key=schema_key,
            api_data_model=api_data_model,
        )

    def _verify_req_parameter(self, openapi_doc_data: dict, parameters: List[RequestParameterAdapter]) -> None:
        assert parameters and isinstance(parameters, list)
        assert len(parameters) == len(openapi_doc_data["parameters"])
        type_checksum = list(map(lambda p: isinstance(p, RequestParameterAdapter), parameters))
        assert False not in type_checksum

    @pytest.mark.parametrize(("api_detail", "entire_config"), PARSE_V2_OPENAPI_RESPONSES_TEST_CASE)
    def test_to_responses_adapter(self, under_test: _BaseAPIConfigWithMethod, api_detail: dict, entire_config: dict):
        super().test_to_responses_adapter(
            under_test=under_test,
            api_detail=api_detail,
            entire_config=entire_config,
        )

    @property
    def _api_doc_version(self) -> OpenAPIVersion:
        return OpenAPIVersion.V2

    @property
    def _common_objects_yaml_schema(self) -> str:
        return "definitions"

    def _deserialize_as_response_model(self, resp_200: dict) -> HttpConfigV2:
        return HttpConfigV2.deserialize(resp_200)


class TestAPIConfigWithMethodV3(BaseAPIConfigWithMethodTestSuite):

    @pytest.fixture(scope="function")
    def under_test(self) -> APIConfigWithMethodV3:
        return APIConfigWithMethodV3()

    @pytest.mark.parametrize(
        ("openapi_doc_data", "entire_openapi_config", "doc_version", "schema_key", "api_data_model"),
        DESERIALIZE_V3_OPENAPI_ENTIRE_API_TEST_CASE,
    )
    def test_to_request_adapter(
        self,
        under_test: APIConfigWithMethodV3,
        openapi_doc_data: dict,
        entire_openapi_config: dict,
        doc_version: OpenAPIVersion,
        schema_key: str,
        api_data_model: APIConfigWithMethodV3,
    ):
        super().test_to_request_adapter(
            under_test=under_test,
            openapi_doc_data=openapi_doc_data,
            entire_openapi_config=entire_openapi_config,
            doc_version=doc_version,
            schema_key=schema_key,
            api_data_model=api_data_model,
        )

    def _verify_req_parameter(self, openapi_doc_data: dict, parameters: List[RequestParameterAdapter]) -> None:
        assert isinstance(parameters, list)
        print(f"[DEBUG in test] openapi_doc_data: {openapi_doc_data}")
        if parameters:
            if "requestBody" in openapi_doc_data.keys():
                request_body = openapi_doc_data.get("requestBody", {})
                data_format = list(filter(lambda b: b in request_body["content"].keys(), ["application/json", "*/*"]))
                assert len(data_format) == 1
                req_body_model = RequestParameter().deserialize(request_body["content"][data_format[0]])
                assert len(parameters) == len(req_body_model.get_schema_ref().properties.keys())
            elif "parameters" in openapi_doc_data.keys():
                all_params = []
                for param in openapi_doc_data["parameters"]:
                    req_body_model = RequestParameter().deserialize(param)
                    if req_body_model.has_ref():
                        all_params.extend(list(req_body_model.get_schema_ref().properties.keys()))
                    else:
                        all_params.append(param)
                assert len(parameters) == len(all_params)
            else:
                raise ValueError("")
            type_checksum = list(map(lambda p: isinstance(p, RequestParameterAdapter), parameters))
            assert False not in type_checksum

    @pytest.mark.parametrize(("api_detail", "entire_config"), PARSE_V3_OPENAPI_RESPONSES_TEST_CASE)
    def test_to_responses_adapter(self, under_test: _BaseAPIConfigWithMethod, api_detail: dict, entire_config: dict):
        super().test_to_responses_adapter(
            under_test=under_test,
            api_detail=api_detail,
            entire_config=entire_config,
        )

    @property
    def _api_doc_version(self) -> OpenAPIVersion:
        return OpenAPIVersion.V3

    @property
    def _common_objects_yaml_schema(self) -> str:
        return "components"

    def _deserialize_as_response_model(self, resp_200: dict) -> HttpConfigV2:
        v3_http_config = HttpConfigV3.deserialize(resp_200)
        resp_format: List[ContentType] = list(
            filter(
                lambda ct: v3_http_config.exist_setting(content_type=ct) is not None,
                ContentType,
            )
        )
        print(f"[DEBUG] has content, resp_format: {resp_format}")
        status_200_response_setting = v3_http_config.get_setting(content_type=resp_format[0])
        return status_200_response_setting


class _OpenAPIDocumentDataModelTestSuite(metaclass=ABCMeta):
    @pytest.fixture(scope="function")
    @abstractmethod
    def data_model(self) -> Transferable:
        pass

    @pytest.mark.parametrize("openapi_doc_data", [])
    def test_deserialize(self, openapi_doc_data: Union[dict, BaseAPIDocConfig], data_model: Transferable):
        self._initial(data=data_model)
        deserialized_data = data_model.deserialize(data=openapi_doc_data)
        assert deserialized_data
        self._verify_result(data=deserialized_data, og_data=openapi_doc_data)

    def test_to_api_config(self, data_model: Transferable):
        self._given_props(data_model)
        new_data_model = data_model.to_api_config()
        self._verify_api_config_model(under_test=new_data_model, data_from=data_model)

    @abstractmethod
    def _initial(self, data: Transferable) -> None:
        pass

    @abstractmethod
    def _verify_result(self, data: Transferable, og_data: Union[dict, BaseAPIDocConfig]) -> None:
        pass

    @abstractmethod
    def _given_props(self, data_model: Transferable) -> None:
        pass

    @abstractmethod
    def _verify_api_config_model(self, under_test: _Config, data_from: Transferable) -> None:
        pass


class TestAPIAdapter(_OpenAPIDocumentDataModelTestSuite):
    @pytest.fixture(scope="function")
    def data_model(self) -> APIAdapter:
        return APIAdapter()

    @pytest.mark.parametrize(
        ("openapi_doc_data", "entire_openapi_config", "doc_version", "schema_key", "api_data_model"),
        DESERIALIZE_V2_OPENAPI_ENTIRE_API_TEST_CASE + DESERIALIZE_V3_OPENAPI_ENTIRE_API_TEST_CASE,
    )
    def test_deserialize(
        self,
        data_model: Transferable,
        openapi_doc_data: dict,
        entire_openapi_config: dict,
        doc_version: OpenAPIVersion,
        schema_key: str,
        api_data_model: _BaseAPIConfigWithMethod,
    ):
        # Previous process
        set_openapi_version(doc_version)
        set_component_definition(entire_openapi_config.get(schema_key, {}))

        # Run test
        openapi_doc_data = api_data_model.deserialize(openapi_doc_data)
        super().test_deserialize(openapi_doc_data, data_model)

        # Finally
        set_openapi_version(OpenAPIVersion.V3)

    def _initial(self, data: APIAdapter) -> None:
        data.path = ""
        data.http_method = ""
        data.parameters = []
        data.response = {}

    def _verify_result(self, data: APIAdapter, og_data: _BaseAPIConfigWithMethod) -> None:
        # TODO: Remove this deprecated test criteria if it ensure
        # def _get_api_param(name: str) -> Optional[dict]:
        #     swagger_api_params = og_data["parameters"]
        #     for param in swagger_api_params:
        #         if param["name"] == name:
        #             return param
        #     return None

        assert data is not None
        assert data.path == ""
        assert data.http_method == ""

        # param: List[TmpRequestParameterModel] = list(filter(lambda e: e.has_ref(), og_data.parameters))
        # if param is not None:
        #     print(f"[DEBUG in test] param: {param}")
        #     assert len(data.parameters) == len(param[0].get_schema_ref().properties)
        # else:
        if isinstance(og_data, APIConfigWithMethodV3):
            request_body = og_data.request_body
            has_ref_params: List[RequestParameter] = (
                list(filter(lambda p: p.has_ref(), og_data.parameters)) if og_data.parameters else None
            )
            if request_body:
                req_param_format: List[ContentType] = list(
                    filter(
                        lambda ct: request_body.exist_setting(content_type=ct) is not None,
                        ContentType,
                    )
                )
                print(f"[DEBUG] has content, req_param_format: {req_param_format}")
                req_param_setting = request_body.get_setting(content_type=req_param_format[0])
                req_param_data_model = req_param_setting.get_schema_ref()
                assert len(data.parameters) == len(req_param_data_model.properties)
            elif has_ref_params:
                all_params = []
                for param in has_ref_params:
                    all_params.extend(list(param.get_schema_ref().properties.keys()))
                assert len(data.parameters) == len(all_params)
            else:
                assert len(data.parameters) == len(og_data.parameters)
        else:
            assert len(data.parameters) == len(og_data.parameters)
        # TODO: Remove this deprecated test criteria if it ensure
        # for api_param in data.parameters:
        #     one_swagger_api_param = _get_api_param(api_param.name)
        #     assert one_swagger_api_param is not None
        #     assert api_param.required == one_swagger_api_param["required"]
        #     if api_param.has_schema(one_swagger_api_param):
        #         assert api_param.value_type == convert_js_type(one_swagger_api_param["schema"]["type"])
        #         assert api_param.default == one_swagger_api_param["schema"].get("default", None)
        #     else:
        #         assert api_param.value_type == convert_js_type(one_swagger_api_param["type"])
        #         assert api_param.default == one_swagger_api_param.get("default", None)

    def _given_props(self, data_model: APIAdapter) -> None:
        params = RequestParameterAdapter()
        params.name = "arg1"
        params.required = False
        params.value_type = "string"
        params.default = "default_value_pytest"

        data_model.path = "/test/v1/foo-home"
        data_model.http_method = "POST"
        data_model.parameters = [params]
        data_model.response = ResponsePropertyAdapter(
            data=[
                PropertyDetailAdapter(name="key1", value_type="str", required=True),
            ],
        )
        data_model.tags = ["first tag", "second tag"]

    def _verify_api_config_model(self, under_test: MockAPI, data_from: APIAdapter) -> None:
        assert under_test.url == data_from.path
        assert under_test.http.request.method == data_from.http_method
        assert len(under_test.http.request.parameters) == len(data_from.parameters)
        for p in under_test.http.request.parameters:
            api_param_in_data_from = list(filter(lambda _p: _p.name == p.name, data_from.parameters))
            assert len(api_param_in_data_from) == 1
            param_data_from = api_param_in_data_from[0]
            assert p.name == param_data_from.name
            assert p.required == param_data_from.required
            assert p.value_type == param_data_from.value_type
            assert p.default == param_data_from.default
            assert p.value_format is None
        assert under_test.tag == data_from.tags[0]
        assert under_test.http.response.value == ""
        assert len(under_test.http.response.properties) == 1
        assert under_test.http.response.properties[0].serialize() == data_from.response.data[0].serialize()


class TestSwaggerAPIDocumentConfig(_OpenAPIDocumentDataModelTestSuite):
    @pytest.fixture(scope="function")
    def data_model(self) -> SwaggerAPIDocumentConfig:
        return SwaggerAPIDocumentConfig()

    @pytest.mark.parametrize("openapi_doc_data", DESERIALIZE_V2_OPENAPI_ENTIRE_CONFIG_TEST_CASE)
    def test_deserialize(self, openapi_doc_data: dict, data_model: Transferable):
        set_component_definition(openapi_doc_data.get("definitions", {}))
        super().test_deserialize(openapi_doc_data, data_model)

    def _initial(self, data: OpenAPIDocumentConfig) -> None:
        data.paths = {}

    def _verify_result(self, data: OpenAPIDocumentConfig, og_data: dict) -> None:
        # TODO: Remove this deprecated test criteria if it ensure
        # def _get_api_param(name: str) -> Optional[dict]:
        #     swagger_api_params = og_data["paths"][api.path][api.http_method]["parameters"]
        #     for param in swagger_api_params:
        #         if param["name"] == name:
        #             return param
        #     return None

        path_with_method_number = [len(v.keys()) for v in og_data["paths"].values()]
        data_model_apis = [len(v) for v in data.paths.values()]
        assert sum(data_model_apis) == sum(path_with_method_number)
        for path, api_config in data.paths.items():
            apis = api_config.to_adapter(path)
            for api in apis:
                assert api.path in og_data["paths"].keys()
                assert api.http_method.lower() in og_data["paths"][api.path].keys()

                assert len(api.parameters) == len(og_data["paths"][api.path][api.http_method.lower()]["parameters"])
                # TODO: Remove this deprecated test criteria if it ensure
                # for api_param in api.parameters:
                #     one_swagger_api_param = _get_api_param(api_param.name)
                #     assert one_swagger_api_param is not None
                #     assert api_param.required == one_swagger_api_param["required"]
                #     assert api_param.value_type == convert_js_type(one_swagger_api_param["schema"]["type"])
                #     assert api_param.default == one_swagger_api_param["schema"]["default"]

    def _given_props(self, data_model: OpenAPIDocumentConfig) -> None:
        params = RequestParameter()
        params.name = "arg1"
        params.required = False
        params.value_type = "str"
        params.default = "default_value_pytest"

        api_with_one_method = APIConfigWithMethodV2()
        api_with_one_method.parameters = [params]
        api_with_one_method.responses = {
            HTTPStatus.OK: HttpConfigV2(
                schema=ReferenceConfigProperty(
                    value_type="str",
                )
            )
        }

        apis = APIConfig()
        apis.api = {HTTPMethod.POST: api_with_one_method}

        data_model.paths = {"/test/v1/foo-home": apis}

    def _verify_api_config_model(self, under_test: PyMockAPI_APIConfig, data_from: OpenAPIDocumentConfig) -> None:
        assert len(under_test.apis.apis.keys()) == len(data_from.paths)
        for api_path, api_details in under_test.apis.apis.items():
            print(f"[DEBUG in test] api_path: {api_path}")
            # Find the mapping expect API config

            def _find_path(_http_method: HTTPMethod) -> bool:
                return api_path == f'{_http_method.name.lower()}{path.replace("/", "_")}'

            expect_api_setting: Optional[Tuple[str, HTTPMethod, _BaseAPIConfigWithMethod]] = None
            for path, api_config in data_from.paths.items():
                expect_apis = list(filter(lambda _http_method: _find_path(_http_method), api_config.api.keys()))
                if len(expect_apis):
                    # (path, HTTP method, API config)
                    expect_api_setting = (path, expect_apis[0], api_config.api[expect_apis[0]])
                    break

            assert expect_api_setting
            expect_path = expect_api_setting[0]
            expect_http_method = expect_api_setting[1]
            expect_api_config = expect_api_setting[2]

            assert api_details.url == expect_path
            assert api_details.http.request.method == expect_http_method.value
            for api_param in api_details.http.request.parameters:
                api_param_in_data_from = list(
                    filter(lambda _p: _p.name == api_param.name, expect_api_config.parameters)
                )
                assert len(api_param_in_data_from) == 1
                param_data_from = api_param_in_data_from[0]
                assert param_data_from is not None
                assert api_param.required == param_data_from.required
                assert api_param.value_type == param_data_from.value_type
                assert api_param.default == param_data_from.default
            assert HTTPStatus.OK in expect_api_config.responses.keys()
            response = expect_api_config.responses[HTTPStatus.OK]
            assert isinstance(response, HttpConfigV2)
            assert api_details.http.response.properties == []

    @pytest.mark.parametrize(
        "path",
        [
            # base path
            "/api/v1/test",
            "api/v1/test",
            # API path
            "api/v1/test/foo-home",
            "/api/v1/test/foo-home",
        ],
    )
    def test__align_url_format(self, path: str, data_model: OpenAPIDocumentConfig):
        handled_url = OpenAPIDocumentConfig()._align_url_format(path=path)
        assert re.search(r"/.{1,32}/.{1,32}/.{1,32}", handled_url)


class TestOpenAPIDocumentConfig(_OpenAPIDocumentDataModelTestSuite):
    @pytest.fixture(scope="function")
    def data_model(self) -> OpenAPIDocumentConfig:
        return OpenAPIDocumentConfig()

    @pytest.mark.parametrize("openapi_doc_data", DESERIALIZE_V3_OPENAPI_ENTIRE_CONFIG_TEST_CASE)
    def test_deserialize(self, openapi_doc_data: dict, data_model: Transferable):
        """
        modify the test data at this test
        """
        set_component_definition(openapi_doc_data.get("components", {}))
        super().test_deserialize(openapi_doc_data, data_model)

    def _initial(self, data: OpenAPIDocumentConfig) -> None:
        data.paths = {}

    def _verify_result(self, data: OpenAPIDocumentConfig, og_data: dict) -> None:
        path_with_method_number = [len(v.keys()) for v in og_data["paths"].values()]
        data_model_apis = [len(v) for v in data.paths.values()]
        assert sum(data_model_apis) == sum(path_with_method_number)
        for api_path, api_config in data.paths.items():
            assert api_path in og_data["paths"].keys()
            apis = api_config.to_adapter(api_path)
            for api in apis:
                assert api.http_method.lower() in og_data["paths"][api.path].keys()

                api_http_details = og_data["paths"][api.path][api.http_method.lower()]
                if api.http_method.upper() == "GET":
                    expected_parameters = 0
                    api_req_params_data_model = list(
                        map(lambda e: RequestParameter().deserialize(e), api_http_details.get("parameters", []))
                    )
                    for param in api_req_params_data_model:
                        if param.has_ref():
                            expected_parameters += len(param.get_schema_ref().properties.keys())
                        else:
                            expected_parameters += 1
                    assert len(api.parameters) == expected_parameters
                else:
                    request_body = api_http_details.get("requestBody", {})
                    if request_body:
                        data_format = list(
                            filter(lambda b: b in request_body["content"].keys(), ["application/json", "*/*"])
                        )
                        assert len(data_format) == 1
                        req_body_model = RequestParameter().deserialize(request_body["content"][data_format[0]])
                        assert len(api.parameters) == len(req_body_model.get_schema_ref().properties.keys())
                    else:
                        expected_parameters = 0
                        api_req_params_data_model = list(
                            map(lambda e: RequestParameter().deserialize(e), api_http_details["parameters"])
                        )
                        for param in api_req_params_data_model:
                            if param.has_ref():
                                expected_parameters += len(param.get_schema_ref().properties.keys())
                            else:
                                expected_parameters += 1
                        assert len(api.parameters) == expected_parameters

    def _given_props(self, data_model: OpenAPIDocumentConfig) -> None:
        params = RequestParameter()
        params.name = "arg1"
        params.required = False
        params.value_type = "str"
        params.default = "default_value_pytest"

        api_with_one_method = APIConfigWithMethodV2()
        api_with_one_method.parameters = [params]
        api_with_one_method.responses = {
            HTTPStatus.OK: HttpConfigV2(
                schema=ReferenceConfigProperty(
                    value_type="str",
                )
            )
        }

        apis = APIConfig()
        apis.api = {HTTPMethod.POST: api_with_one_method}

        data_model.paths = {"/test/v1/foo-home": apis}

    def _verify_api_config_model(self, under_test: PyMockAPI_APIConfig, data_from: OpenAPIDocumentConfig) -> None:
        assert len(under_test.apis.apis.keys()) == len(data_from.paths)
        for api_path, api_details in under_test.apis.apis.items():
            print(f"[DEBUG in test] api_path: {api_path}")
            # Find the mapping expect API config

            def _find_path(_http_method: HTTPMethod) -> bool:
                return api_path == f'{_http_method.name.lower()}{path.replace("/", "_")}'

            expect_api_setting: Optional[Tuple[str, HTTPMethod, _BaseAPIConfigWithMethod]] = None
            for path, api_config in data_from.paths.items():
                expect_apis = list(filter(lambda _http_method: _find_path(_http_method), api_config.api.keys()))
                if len(expect_apis):
                    # (path, HTTP method, API config)
                    expect_api_setting = (path, expect_apis[0], api_config.api[expect_apis[0]])
                    break

            assert expect_api_setting
            expect_path = expect_api_setting[0]
            expect_http_method = expect_api_setting[1]
            expect_api_config = expect_api_setting[2]

            assert api_details.url == expect_path
            assert api_details.http.request.method == expect_http_method.value
            for api_param in api_details.http.request.parameters:
                api_param_in_data_from = list(
                    filter(lambda _p: _p.name == api_param.name, expect_api_config.parameters)
                )
                assert len(api_param_in_data_from) == 1
                param_data_from = api_param_in_data_from[0]
                assert param_data_from is not None
                assert api_param.required == param_data_from.required
                assert api_param.value_type == param_data_from.value_type
                assert api_param.default == param_data_from.default
            assert HTTPStatus.OK in expect_api_config.responses.keys()
            response = expect_api_config.responses[HTTPStatus.OK]
            assert isinstance(response, HttpConfigV2)
            assert api_details.http.response.properties == []

    @pytest.mark.parametrize(
        "path",
        [
            # base path
            "/api/v1/test",
            "api/v1/test",
            # API path
            "api/v1/test/foo-home",
            "/api/v1/test/foo-home",
        ],
    )
    def test__align_url_format(self, path: str, data_model: OpenAPIDocumentConfig):
        handled_url = OpenAPIDocumentConfig()._align_url_format(path=path)
        assert re.search(r"/.{1,32}/.{1,32}/.{1,32}", handled_url)

    def _verify_result_with_openapi_v3(self, data: OpenAPIDocumentConfig, og_data: dict) -> None:
        path_with_method_number = [len(v.keys()) for v in og_data["paths"].values()]
        data_model_apis = [len(v) for v in data.paths.values()]
        assert sum(data_model_apis) == sum(path_with_method_number)
        for api_path, api_config in data.paths.items():
            assert api_path in og_data["paths"].keys()
            apis = api_config.to_adapter(api_path)
            for api in apis:
                assert api.http_method.lower() in og_data["paths"][api.path].keys()

                api_http_details = og_data["paths"][api.path][api.http_method.lower()]
                if api.http_method.upper() == "GET":
                    expected_parameters = 0
                    api_req_params_data_model = list(
                        map(lambda e: RequestParameter().deserialize(e), api_http_details.get("parameters", []))
                    )
                    for param in api_req_params_data_model:
                        if param.has_ref():
                            expected_parameters += len(param.get_schema_ref().properties.keys())
                        else:
                            expected_parameters += 1
                    assert len(api.parameters) == expected_parameters
                else:
                    request_body = api_http_details.get("requestBody", {})
                    if request_body:
                        data_format = list(
                            filter(lambda b: b in request_body["content"].keys(), ["application/json", "*/*"])
                        )
                        assert len(data_format) == 1
                        req_body_model = RequestParameter().deserialize(request_body["content"][data_format[0]])
                        assert len(api.parameters) == len(req_body_model.get_schema_ref().properties.keys())
                    else:
                        expected_parameters = 0
                        api_req_params_data_model = list(
                            map(lambda e: RequestParameter().deserialize(e), api_http_details["parameters"])
                        )
                        for param in api_req_params_data_model:
                            if param.has_ref():
                                expected_parameters += len(param.get_schema_ref().properties.keys())
                            else:
                                expected_parameters += 1
                        assert len(api.parameters) == expected_parameters


def test_get_api_doc_version_with_invalid_version():
    data = {"doesn't have key which could identify which version the API document is.": ""}
    with pytest.raises(CannotParsingAPIDocumentVersion):
        get_api_doc_version(data)
