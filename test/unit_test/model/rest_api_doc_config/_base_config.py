import logging
import re
from abc import ABC, ABCMeta, abstractmethod
from typing import List, Union

import pytest

# isort: off

from ._test_case import DeserializeV2OpenAPIConfigTestCaseFactory

# isort: on

from pymock_server.model import OpenAPIVersion
from pymock_server.model.api_config import _Config
from pymock_server.model.rest_api_doc_config._base import (
    Transferable,
    set_openapi_version,
)
from pymock_server.model.rest_api_doc_config._model_adapter import (
    PropertyDetailAdapter,
    RequestParameterAdapter,
    ResponsePropertyAdapter,
)
from pymock_server.model.rest_api_doc_config.base_config import (
    BaseAPIDocConfig,
    BaseReferencialConfig,
    _BaseAPIConfigWithMethod,
    set_component_definition,
)
from pymock_server.model.rest_api_doc_config.config import (
    HttpConfigV2,
    ReferenceConfigProperty,
)

logger = logging.getLogger(__name__)

DeserializeV2OpenAPIConfigTestCaseFactory.load()
DESERIALIZE_V2_OPENAPI_DOC_TEST_CASE = DeserializeV2OpenAPIConfigTestCaseFactory.get_test_case()
GENERATE_RESPONSE_CONFIG_FROM_V2_OPENAPI_CONFIG_TEST_CASE = DESERIALIZE_V2_OPENAPI_DOC_TEST_CASE.each_api_http_response


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
        assert response_prop_data and isinstance(response_prop_data, (PropertyDetailAdapter, list))

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
        logger.debug(f"resp: {resp}")
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
        logger.debug(f"api_detail: {api_detail}")
        under_test = under_test.deserialize(api_detail)
        response_data = under_test.to_responses_adapter()
        logger.debug(f"response_data: {response_data}")

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
        logger.debug(f"should_check_name: {should_check_name}")

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
