import re
from abc import ABC, ABCMeta, abstractmethod
from typing import List, Type, Union

import pytest

from pymock_api.model.enums import OpenAPIVersion, ResponseStrategy
from pymock_api.model.openapi._base import set_openapi_version
from pymock_api.model.openapi._tmp_data_model import (
    BaseTmpDataModel,
    BaseTmpRefDataModel,
    PropertyDetail,
    RequestParameter,
    ResponseProperty,
    TmpAPIDtailConfigV2,
    TmpAPIDtailConfigV3,
    TmpConfigReferenceModel,
    TmpHttpConfigV2,
    TmpHttpConfigV3,
    TmpReferenceConfigPropertyModel,
    TmpRequestParameterModel,
    TmpRequestSchemaModel,
    _BaseTmpAPIDtailConfig,
)
from pymock_api.model.openapi.base_config import set_component_definition
from pymock_api.model.openapi.content_type import ContentType

from ...model.openapi._test_case import (
    DeserializeV2OpenAPIConfigTestCaseFactory,
    DeserializeV3OpenAPIConfigTestCaseFactory,
)

DeserializeV2OpenAPIConfigTestCaseFactory.load()
DESERIALIZE_V2_OPENAPI_DOC_TEST_CASE = DeserializeV2OpenAPIConfigTestCaseFactory.get_test_case()
GENERATE_RESPONSE_CONFIG_FROM_V2_OPENAPI_CONFIG_TEST_CASE = DESERIALIZE_V2_OPENAPI_DOC_TEST_CASE.each_api_http_response

PARSE_V2_OPENAPI_ENTIRE_APIS_TEST_CASE = DESERIALIZE_V2_OPENAPI_DOC_TEST_CASE.each_apis

PARSE_FAIL_V2_OPENAPI_REQUEST_PARAMETERS_NO_REFERENCE_INFO_TEST_CASE = (
    DESERIALIZE_V2_OPENAPI_DOC_TEST_CASE.reference_api_http_request_parameters
)
PARSE_V2_OPENAPI_REQUEST_PARAMETERS_WITH_REFERENCE_INFO_TEST_CASE = (
    DESERIALIZE_V2_OPENAPI_DOC_TEST_CASE.general_api_http_request_parameters
)
PARSE_V2_OPENAPI_RESPONSES_TEST_CASE = DESERIALIZE_V2_OPENAPI_DOC_TEST_CASE.entire_api_http_response

DeserializeV3OpenAPIConfigTestCaseFactory.load()
V3_OPENAPI_API_DOC_CONFIG_TEST_CASE = DeserializeV3OpenAPIConfigTestCaseFactory.get_test_case()
DESERIALIZE_V3_OPENAPI_ENTIRE_CONFIG_TEST_CASE = V3_OPENAPI_API_DOC_CONFIG_TEST_CASE.entire_config
PARSE_V3_OPENAPI_ENTIRE_APIS_TEST_CASE = V3_OPENAPI_API_DOC_CONFIG_TEST_CASE.each_apis
PARSE_V3_OPENAPI_RESPONSES_TEST_CASE = V3_OPENAPI_API_DOC_CONFIG_TEST_CASE.entire_api_http_response


class BaseTmpDataModelTestSuite(metaclass=ABCMeta):

    @pytest.fixture(scope="function")
    @abstractmethod
    def under_test(self) -> BaseTmpDataModel:
        pass

    @pytest.mark.parametrize(
        ("api_response_detail", "entire_config"), GENERATE_RESPONSE_CONFIG_FROM_V2_OPENAPI_CONFIG_TEST_CASE
    )
    def test_generate_response(
        self,
        under_test: BaseTmpRefDataModel,
        api_response_detail: TmpReferenceConfigPropertyModel,
        entire_config: dict,
    ):
        # Pre-process
        set_component_definition(entire_config.get("definitions", {}))

        # Run target function under test
        response_prop_data = under_test._generate_response(
            init_response=ResponseProperty(),
            property_value=api_response_detail,
        )

        # Verify
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
        self, under_test: BaseTmpRefDataModel, test_response_data: dict, expected_value: str
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
        test_response_data_model = TmpReferenceConfigPropertyModel.deserialize(test_response_data)

        # Run target
        resp = under_test._generate_response_from_data(
            init_response=ResponseProperty.initial_response_data(),
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


class BaseTmpRefDataModelTestSuite(BaseTmpDataModelTestSuite):

    @pytest.fixture(scope="function")
    @abstractmethod
    def under_test(self) -> BaseTmpRefDataModel:
        pass

    @pytest.mark.parametrize(("under_test", "expect_result"), [])
    @abstractmethod
    def test_has_ref(self, under_test: BaseTmpRefDataModel, expect_result: str):
        assert under_test.has_ref() == expect_result

    @pytest.mark.parametrize(("under_test", "expect_result"), [])
    @abstractmethod
    def test_get_ref(self, under_test: BaseTmpRefDataModel, expect_result: str):
        assert under_test.get_ref() == expect_result

    def test_get_schema_ref_with_not_exist_ref(self, under_test: BaseTmpRefDataModel):
        with pytest.raises(ValueError) as exc_info:
            under_test.get_schema_ref()
        assert re.search(r"no ref", str(exc_info.value), re.IGNORECASE)

    @pytest.mark.parametrize(
        ("ut_response_config", "expect_result"),
        [
            (
                [PropertyDetail(name="THIS_IS_EMPTY", required=True, value_type=None, format=None, items=None)],
                [PropertyDetail(name="", required=True, value_type=None, format=None, is_empty=True, items=None)],
            ),
            (
                [
                    PropertyDetail(
                        name="sample_list",
                        required=True,
                        value_type="list",
                        format=None,
                        items=[
                            PropertyDetail(
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
                    PropertyDetail(
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
                    PropertyDetail(
                        name="sample_list",
                        required=True,
                        value_type="list",
                        format=None,
                        items=[
                            PropertyDetail(
                                name="sample_nested_list",
                                required=True,
                                value_type="list",
                                format=None,
                                items=[
                                    PropertyDetail(
                                        name="sample_nested_list",
                                        required=True,
                                        value_type="list",
                                        format=None,
                                        items=[
                                            PropertyDetail(
                                                name="", required=True, value_type="str", format=None, items=None
                                            ),
                                        ],
                                    ),
                                    PropertyDetail(
                                        name="sample_nested_dict",
                                        required=True,
                                        value_type="dict",
                                        format=None,
                                        items=[
                                            PropertyDetail(
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
                    PropertyDetail(
                        name="sample_list",
                        required=True,
                        value_type="list",
                        format=None,
                        items=[
                            PropertyDetail(
                                name="sample_nested_list",
                                required=True,
                                value_type="list",
                                format=None,
                                items=[
                                    PropertyDetail(
                                        name="sample_nested_list",
                                        required=True,
                                        value_type="list",
                                        format=None,
                                        items=[
                                            PropertyDetail(
                                                name="", required=True, value_type="str", format=None, items=None
                                            ),
                                        ],
                                    ),
                                    PropertyDetail(
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
        under_test: BaseTmpRefDataModel,
        ut_response_config: List[PropertyDetail],
        expect_result: List[PropertyDetail],
    ):
        new_response_config = under_test._process_empty_body_response(response_columns_setting=ut_response_config)
        assert new_response_config == expect_result


class TestTmpResponsePropertyModel(BaseTmpRefDataModelTestSuite):

    @pytest.fixture(scope="function")
    def under_test(self) -> TmpReferenceConfigPropertyModel:
        return TmpReferenceConfigPropertyModel()

    @pytest.mark.parametrize(
        ("under_test", "expect_result"),
        [
            (TmpReferenceConfigPropertyModel(ref=None), ""),
            (TmpReferenceConfigPropertyModel(ref=""), ""),
            (TmpReferenceConfigPropertyModel(ref="reference value"), "ref"),
            (TmpReferenceConfigPropertyModel(additionalProperties=TmpReferenceConfigPropertyModel(ref=None)), ""),
            (TmpReferenceConfigPropertyModel(additionalProperties=TmpReferenceConfigPropertyModel(ref="")), ""),
            (
                TmpReferenceConfigPropertyModel(
                    additionalProperties=TmpReferenceConfigPropertyModel(ref="reference value")
                ),
                "additionalProperties",
            ),
        ],
    )
    def test_has_ref(self, under_test: BaseTmpRefDataModel, expect_result: str):
        super().test_has_ref(under_test, expect_result)

    @pytest.mark.parametrize(
        ("under_test", "expect_result"),
        [
            (TmpReferenceConfigPropertyModel(ref="reference value"), "reference value"),
            (
                TmpReferenceConfigPropertyModel(
                    additionalProperties=TmpReferenceConfigPropertyModel(ref="reference value")
                ),
                "reference value",
            ),
        ],
    )
    def test_get_ref(self, under_test: BaseTmpRefDataModel, expect_result: str):
        super().test_get_ref(under_test, expect_result)

    @pytest.mark.parametrize(
        ("under_test", "expect_result"),
        [
            (TmpReferenceConfigPropertyModel(), True),
            (TmpReferenceConfigPropertyModel(value_type=None), True),
            (TmpReferenceConfigPropertyModel(ref=None), True),
            (TmpReferenceConfigPropertyModel(value_type=""), True),
            (TmpReferenceConfigPropertyModel(ref=""), True),
            (TmpReferenceConfigPropertyModel(value_type="data type", ref=""), False),
            (TmpReferenceConfigPropertyModel(value_type=None, ref="reference value"), False),
        ],
    )
    def test_is_empty(self, under_test: TmpReferenceConfigPropertyModel, expect_result: str):
        assert under_test.is_empty() == expect_result


class TestTmpRequestParameterModel(BaseTmpRefDataModelTestSuite):

    @pytest.fixture(scope="function")
    def under_test(self) -> TmpRequestParameterModel:
        return TmpRequestParameterModel()

    @pytest.mark.parametrize(
        ("under_test", "expect_result"),
        [
            (TmpRequestParameterModel(schema=None), ""),
            (TmpRequestParameterModel(schema=TmpRequestSchemaModel(ref=None)), ""),
            (TmpRequestParameterModel(schema=TmpRequestSchemaModel(ref="")), ""),
            (TmpRequestParameterModel(schema=TmpRequestSchemaModel(ref="reference value")), "schema"),
        ],
    )
    def test_has_ref(self, under_test: BaseTmpRefDataModel, expect_result: str):
        super().test_has_ref(under_test, expect_result)

    @pytest.mark.parametrize(
        ("under_test", "expect_result"),
        [
            (TmpRequestParameterModel(schema=TmpRequestSchemaModel(ref="reference value")), "reference value"),
        ],
    )
    def test_get_ref(self, under_test: BaseTmpRefDataModel, expect_result: str):
        super().test_get_ref(under_test, expect_result)

    @pytest.mark.parametrize(
        ("openapi_doc_data", "entire_openapi_config"), PARSE_V2_OPENAPI_REQUEST_PARAMETERS_WITH_REFERENCE_INFO_TEST_CASE
    )
    def test_process_has_ref_request_parameters_with_valid_value(
        self, under_test: TmpRequestParameterModel, openapi_doc_data: dict, entire_openapi_config: dict
    ):
        # Pre-process
        set_component_definition(entire_openapi_config.get("definitions", {}))

        # Run target function
        openapi_doc_data_model = under_test.deserialize(openapi_doc_data)
        parameters = openapi_doc_data_model.process_has_ref_request_parameters()

        # Verify
        assert parameters and isinstance(parameters, list)
        assert len(parameters) == len(entire_openapi_config["definitions"]["UpdateFooRequest"]["properties"].keys())
        type_checksum = list(map(lambda p: isinstance(p, RequestParameter), parameters))
        assert False not in type_checksum

    @pytest.mark.parametrize("openapi_doc_data", PARSE_FAIL_V2_OPENAPI_REQUEST_PARAMETERS_NO_REFERENCE_INFO_TEST_CASE)
    def test_process_has_ref_request_parameters_with_invalid_value(
        self, under_test: TmpRequestParameterModel, openapi_doc_data: dict
    ):
        with pytest.raises(ValueError) as exc_info:
            # Run target function
            openapi_doc_data_model = under_test.deserialize(openapi_doc_data)
            openapi_doc_data_model.process_has_ref_request_parameters()

        # Verify
        assert re.search(r".{1,64}no ref.{1,64}", str(exc_info.value), re.IGNORECASE)


class TestTmpResponseRefModel(BaseTmpDataModelTestSuite):

    @pytest.fixture(scope="function")
    def under_test(self) -> TmpConfigReferenceModel:
        return TmpConfigReferenceModel()

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
                TmpConfigReferenceModel(value_type="object"),
                # {"type": "object"},
                ResponseProperty(
                    data=[PropertyDetail(name="THIS_IS_EMPTY", required=False, value_type=None, format=None, items=[])],
                ),
                # {
                #     "strategy": ResponseStrategy.OBJECT,
                #     "data": [{"name": "THIS_IS_EMPTY", "required": False, "type": None, "format": None, "items": []}],
                # },
            ),
        ],
    )
    def test__process_reference_object_with_empty_body_response(
        self, strategy: ResponseStrategy, test_response_data: TmpConfigReferenceModel, expected_value: ResponseProperty
    ):
        response_config = test_response_data.process_reference_object(
            init_response=ResponseProperty.initial_response_data(),
        )
        assert response_config == expected_value


class BaseTmpAPIDetailConfigTestSuite(BaseTmpDataModelTestSuite, ABC):

    @pytest.mark.parametrize(
        ("openapi_doc_data", "entire_openapi_config", "doc_version", "schema_key", "api_data_model"),
        [],
    )
    @abstractmethod
    def test_process_api_parameters(
        self,
        under_test: _BaseTmpAPIDtailConfig,
        openapi_doc_data: dict,
        entire_openapi_config: dict,
        doc_version: OpenAPIVersion,
        schema_key: str,
        api_data_model: _BaseTmpAPIDtailConfig,
    ):
        print(f"[DEBUG in test__process_api_params] ")
        # Pre-process
        set_openapi_version(doc_version)
        set_component_definition(entire_openapi_config.get(schema_key, {}))

        under_test = under_test.deserialize(openapi_doc_data)

        # Run target function
        parameters = under_test.process_api_parameters(http_method="HTTP method")

        # Verify
        self._verify_req_parameter(openapi_doc_data, parameters)

        # Finally
        set_openapi_version(OpenAPIVersion.V3)

    @abstractmethod
    def _verify_req_parameter(self, openapi_doc_data: dict, parameters: List[RequestParameter]) -> None:
        pass

    @pytest.mark.parametrize(("api_detail", "entire_config"), [])
    def test_process_responses(self, under_test: _BaseTmpAPIDtailConfig, api_detail: dict, entire_config: dict):
        # Pre-process
        set_openapi_version(self._api_doc_version)
        set_component_definition(entire_config.get(self._common_objects_yaml_schema, {}))

        # Run target function under test
        print(f"[DEBUG in test] api_detail: {api_detail}")
        # parser_instance = parser(parser=OpenAPIV2PathSchemaParser(data=api_detail))
        under_test = under_test.deserialize(api_detail)
        response_data = under_test.process_responses()
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
    def _deserialize_as_response_model(self, resp_200: dict) -> TmpHttpConfigV2:
        pass

    @property
    @abstractmethod
    def _common_objects_yaml_schema(self) -> str:
        pass

    @property
    @abstractmethod
    def _api_doc_version(self) -> OpenAPIVersion:
        pass


class TestTmpAPIDetailConfigV2(BaseTmpAPIDetailConfigTestSuite):

    @pytest.fixture(scope="function")
    def under_test(self) -> TmpAPIDtailConfigV2:
        return TmpAPIDtailConfigV2()

    @pytest.mark.parametrize(
        ("openapi_doc_data", "entire_openapi_config", "doc_version", "schema_key", "api_data_model"),
        PARSE_V2_OPENAPI_ENTIRE_APIS_TEST_CASE,
    )
    def test_process_api_parameters(
        self,
        under_test: TmpAPIDtailConfigV2,
        openapi_doc_data: dict,
        entire_openapi_config: dict,
        doc_version: OpenAPIVersion,
        schema_key: str,
        api_data_model: TmpAPIDtailConfigV2,
    ):
        super().test_process_api_parameters(
            under_test=under_test,
            openapi_doc_data=openapi_doc_data,
            entire_openapi_config=entire_openapi_config,
            doc_version=doc_version,
            schema_key=schema_key,
            api_data_model=api_data_model,
        )

    def _verify_req_parameter(self, openapi_doc_data: dict, parameters: List[RequestParameter]) -> None:
        assert parameters and isinstance(parameters, list)
        assert len(parameters) == len(openapi_doc_data["parameters"])
        type_checksum = list(map(lambda p: isinstance(p, RequestParameter), parameters))
        assert False not in type_checksum

    @pytest.mark.parametrize(("api_detail", "entire_config"), PARSE_V2_OPENAPI_RESPONSES_TEST_CASE)
    def test_process_responses(self, under_test: _BaseTmpAPIDtailConfig, api_detail: dict, entire_config: dict):
        super().test_process_responses(
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

    def _deserialize_as_response_model(self, resp_200: dict) -> TmpHttpConfigV2:
        return TmpHttpConfigV2.deserialize(resp_200)


class TestTmpAPIDetailConfigV3(BaseTmpAPIDetailConfigTestSuite):

    @pytest.fixture(scope="function")
    def under_test(self) -> TmpAPIDtailConfigV3:
        return TmpAPIDtailConfigV3()

    @pytest.mark.parametrize(
        ("openapi_doc_data", "entire_openapi_config", "doc_version", "schema_key", "api_data_model"),
        PARSE_V3_OPENAPI_ENTIRE_APIS_TEST_CASE,
    )
    def test_process_api_parameters(
        self,
        under_test: TmpAPIDtailConfigV3,
        openapi_doc_data: dict,
        entire_openapi_config: dict,
        doc_version: OpenAPIVersion,
        schema_key: str,
        api_data_model: TmpAPIDtailConfigV3,
    ):
        super().test_process_api_parameters(
            under_test=under_test,
            openapi_doc_data=openapi_doc_data,
            entire_openapi_config=entire_openapi_config,
            doc_version=doc_version,
            schema_key=schema_key,
            api_data_model=api_data_model,
        )

    def _verify_req_parameter(self, openapi_doc_data: dict, parameters: List[RequestParameter]) -> None:
        assert isinstance(parameters, list)
        print(f"[DEBUG in test] openapi_doc_data: {openapi_doc_data}")
        if parameters:
            if "requestBody" in openapi_doc_data.keys():
                request_body = openapi_doc_data.get("requestBody", {})
                data_format = list(filter(lambda b: b in request_body["content"].keys(), ["application/json", "*/*"]))
                assert len(data_format) == 1
                req_body_model = TmpRequestParameterModel().deserialize(request_body["content"][data_format[0]])
                assert len(parameters) == len(req_body_model.get_schema_ref().properties.keys())
            elif "parameters" in openapi_doc_data.keys():
                all_params = []
                for param in openapi_doc_data["parameters"]:
                    req_body_model = TmpRequestParameterModel().deserialize(param)
                    if req_body_model.has_ref():
                        all_params.extend(list(req_body_model.get_schema_ref().properties.keys()))
                    else:
                        all_params.append(param)
                assert len(parameters) == len(all_params)
            else:
                raise ValueError("")
            type_checksum = list(map(lambda p: isinstance(p, RequestParameter), parameters))
            assert False not in type_checksum

    @pytest.mark.parametrize(("api_detail", "entire_config"), PARSE_V3_OPENAPI_RESPONSES_TEST_CASE)
    def test_process_responses(self, under_test: _BaseTmpAPIDtailConfig, api_detail: dict, entire_config: dict):
        super().test_process_responses(
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

    def _deserialize_as_response_model(self, resp_200: dict) -> TmpHttpConfigV2:
        v3_http_config = TmpHttpConfigV3.deserialize(resp_200)
        resp_format: List[ContentType] = list(
            filter(
                lambda ct: v3_http_config.exist_setting(content_type=ct) is not None,
                ContentType,
            )
        )
        print(f"[DEBUG] has content, resp_format: {resp_format}")
        status_200_response_setting = v3_http_config.get_setting(content_type=resp_format[0])
        return status_200_response_setting


class TestPropertyDetail:

    @pytest.mark.parametrize(
        ("strategy", "expected_type"),
        [
            (ResponseStrategy.OBJECT, PropertyDetail),
        ],
    )
    def test_generate_empty_response(self, strategy: ResponseStrategy, expected_type: Union[type, Type]):
        empty_resp = PropertyDetail.generate_empty_response()
        assert isinstance(empty_resp, expected_type)
