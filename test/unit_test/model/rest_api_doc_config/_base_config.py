import logging
import re
from abc import ABC, ABCMeta, abstractmethod
from collections import namedtuple
from typing import List, Optional, Type, Union

import pytest

from pymock_server.model.api_config.apis._property import BaseProperty
from pymock_server.model.api_config.format import Format
from pymock_server.model.api_config.value import FormatStrategy, ValueFormat
from pymock_server.model.api_config.variable import Size, Variable
from pymock_server.model.rest_api_doc_config._js_handlers import ApiDocValueFormat

# isort: off

from ._test_case import DeserializeV2OpenAPIConfigTestCaseFactory

# isort: on

from pymock_server.model import OpenAPIVersion
from pymock_server.model.api_config import _Config
from pymock_server.model.rest_api_doc_config._base import (
    Transferable,
    set_openapi_version,
)
from pymock_server.model.rest_api_doc_config._base_model_adapter import (
    BasePropertyDetailAdapter,
    BaseRequestParameterAdapter,
)
from pymock_server.model.rest_api_doc_config._model_adapter import (
    FormatAdapter,
    PropertyDetailAdapter,
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
                # 0
                {"type": "integer"},
                {"name": "", "required": True, "type": "int"},
            ),
            (
                # 1
                {"type": "number"},
                {"name": "", "required": True, "type": "int"},
            ),
            (
                # 2
                {"type": "boolean"},
                {"name": "", "required": True, "type": "bool"},
            ),
            (
                # 3
                {"type": "array", "items": {"type": "integer"}},
                {
                    "name": "",
                    "required": True,
                    "type": "list",
                    "items": [{"name": "", "required": True, "type": "int"}],
                },
            ),
            (
                # 4
                {"type": "array", "items": {"$ref": "#/components/schemas/FooResponse"}},
                {
                    "name": "",
                    "required": True,
                    "type": "list",
                    "items": [
                        {
                            "name": "id",
                            "required": True,
                            "type": "int",
                            "format": {
                                "strategy": "by_data_type",
                                "size": {"max": 9223372036854775807, "min": -9223372036854775808},
                            },
                        },
                        {"name": "name", "required": True, "type": "str"},
                        {"name": "value1", "required": True, "type": "str"},
                        {"name": "value2", "required": True, "type": "str"},
                    ],
                },
            ),
            (
                # 5
                {"type": "file"},
                {"name": "", "required": True, "type": "file"},
            ),
            # For object strategy with format
            (
                # 6
                {"type": "integer", "format": "int64"},
                {
                    "name": "",
                    "required": True,
                    "type": "int",
                    "format": {
                        "strategy": "by_data_type",
                        "size": {"max": 9223372036854775807, "min": -9223372036854775808},
                    },
                },
            ),
            (
                # 7
                {"type": "string", "enum": ["TYPE_1", "TYPE_2"]},
                {
                    "name": "",
                    "required": True,
                    "type": "str",
                    "format": {"strategy": "from_enums", "enums": ["TYPE_1", "TYPE_2"]},
                },
            ),
            (
                # 8
                {"type": "string", "format": "uri"},
                {
                    "name": "",
                    "required": True,
                    "type": "str",
                    "format": {
                        "strategy": "customize",
                        "customize": "uri_value",
                        "variables": [{"name": "uri_value", "value_format": "uri"}],
                    },
                },
            ),
            # # Special data
            (
                # 9
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
                    "items": [{"name": "additionalKey", "required": True, "type": "str"}],
                },
            ),
            (
                # 10
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
                    "items": [
                        {
                            "name": "",
                            "required": True,
                            "type": "str",
                            "format": {"strategy": "from_enums", "enums": ["TYPE_1", "TYPE_2"]},
                        },
                    ],
                },
            ),
            (
                # 11
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
                    "items": [
                        {
                            "name": "id",
                            "required": True,
                            "type": "int",
                            "format": {
                                "strategy": "by_data_type",
                                "size": {"max": 9223372036854775807, "min": -9223372036854775808},
                            },
                        },
                        {"name": "name", "required": False, "type": "str"},
                        {"name": "value1", "required": False, "type": "str"},
                        {"name": "value2", "required": False, "type": "str"},
                    ],
                },
            ),
            (
                # 12
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
                    "items": [
                        {
                            "name": "id",
                            "required": True,
                            "type": "int",
                            "format": {
                                "strategy": "by_data_type",
                                "size": {"max": 9223372036854775807, "min": -9223372036854775808},
                            },
                        },
                        {"name": "name", "required": False, "type": "str"},
                        {
                            "name": "data",
                            "required": False,
                            "type": "list",
                            "items": [
                                {
                                    "name": "id",
                                    "required": True,
                                    "type": "int",
                                    "format": {
                                        "strategy": "by_data_type",
                                        "size": {"max": 9223372036854775807, "min": -9223372036854775808},
                                    },
                                },
                                {"name": "value", "required": True, "type": "str"},
                                {
                                    "name": "url",
                                    "required": True,
                                    "type": "str",
                                    "format": {
                                        "strategy": "customize",
                                        "customize": "uri_value",
                                        "variables": [{"name": "uri_value", "value_format": "uri"}],
                                    },
                                },
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
                                            "items": [
                                                {"name": "domain", "required": True, "type": "str"},
                                                {"name": "needAuth", "required": True, "type": "bool"},
                                            ],
                                        },
                                        {
                                            "name": "detailInfo",
                                            "required": True,
                                            "type": "dict",
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
                # 13
                {
                    "$ref": "#/components/schemas/NestedFooResponse",
                },
                [
                    {
                        "name": "id",
                        "required": True,
                        "type": "int",
                        "format": {
                            "strategy": "by_data_type",
                            "size": {"max": 9223372036854775807, "min": -9223372036854775808},
                        },
                    },
                    {"name": "name", "required": False, "type": "str"},
                    {
                        "name": "data",
                        "required": False,
                        "type": "list",
                        "items": [
                            {
                                "name": "id",
                                "required": True,
                                "type": "int",
                                "format": {
                                    "strategy": "by_data_type",
                                    "size": {"max": 9223372036854775807, "min": -9223372036854775808},
                                },
                            },
                            {"name": "value", "required": True, "type": "str"},
                            {
                                "name": "url",
                                "required": True,
                                "type": "str",
                                "format": {
                                    "strategy": "customize",
                                    "customize": "uri_value",
                                    "variables": [{"name": "uri_value", "value_format": "uri"}],
                                },
                            },
                            {
                                "name": "urlProperties",
                                "required": False,
                                "type": "dict",
                                "items": [
                                    {
                                        "name": "homePage",
                                        "required": True,
                                        "type": "dict",
                                        "items": [
                                            {"name": "domain", "required": True, "type": "str"},
                                            {"name": "needAuth", "required": True, "type": "bool"},
                                        ],
                                    },
                                    {
                                        "name": "detailInfo",
                                        "required": True,
                                        "type": "dict",
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
        self, under_test: BaseReferencialConfig, test_response_data: dict, expected_value: Union[dict, list]
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
        logger.info(f"resp: {resp}")
        logger.info(f"expected_value: {expected_value}")
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
    def _verify_req_parameter(self, openapi_doc_data: dict, parameters: List[BaseRequestParameterAdapter]) -> None:
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
        logger.debug(f"should_check_name: {should_check_name}")

        data_details = response_data.data
        assert data_details is not None and isinstance(data_details, list)
        for d in data_details:
            if should_check_name:
                assert d.name
                assert d.value_type
            assert d.required is not None
            if d.format:
                assert isinstance(d.format, FormatAdapter)
                if not d.format.is_none():
                    assert d.value_type not in ("list", "dict")
            if d.value_type in ("list", "dict"):
                assert d.items is not None
                for item in d.items:
                    assert item.name
                    assert item.value_type
                    assert item.required is not None

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


def _adapter_config(
    required: bool,
    value_type: str,
    name: Optional[str] = None,
    format: Optional[FormatAdapter] = None,
    items: Optional[List[dict]] = None,
) -> dict:
    return {
        "name": name,
        "required": required,
        "value_type": value_type,
        "format": format,
        "items": items,
    }


ExpectModelProps = namedtuple("ExpectModelProps", ("name", "required", "value_type", "format", "items"))


class _BasePropertyDetailAdapterTestSuite(metaclass=ABCMeta):
    @abstractmethod
    @pytest.fixture(scope="function")
    def adapter_model_obj(self) -> Type[BasePropertyDetailAdapter]:
        pass

    @abstractmethod
    @pytest.fixture(scope="function")
    def pymock_model(self) -> BaseProperty:
        pass

    @pytest.mark.parametrize(
        ("under_test_data", "expect"),
        [
            (
                _adapter_config(name="param", required=True, value_type="str"),
                ExpectModelProps(name="param", required=True, value_type="str", format=None, items=None),
            ),
            (
                _adapter_config(name="param", required=False, value_type="int"),
                ExpectModelProps(name="param", required=False, value_type="int", format=None, items=None),
            ),
            (
                _adapter_config(name="param", required=False, value_type="list"),
                ExpectModelProps(name="param", required=False, value_type="list", format=None, items=None),
            ),
            (
                _adapter_config(
                    name="param",
                    required=True,
                    value_type="str",
                    format=FormatAdapter(formatter=ApiDocValueFormat.Int32),
                ),
                ExpectModelProps(
                    name="param",
                    required=True,
                    value_type="str",
                    format=Format(
                        strategy=FormatStrategy.BY_DATA_TYPE,
                        size=Size(max_value=9223372036854775807, min_value=-9223372036854775808),
                    ),
                    items=None,
                ),
            ),
            (
                _adapter_config(
                    name="param", required=True, value_type="str", format=FormatAdapter(enum=["TYPE_1", "TYPE_2"])
                ),
                ExpectModelProps(
                    name="param",
                    required=True,
                    value_type="str",
                    format=Format(strategy=FormatStrategy.FROM_ENUMS, enums=["TYPE_1", "TYPE_2"]),
                    items=None,
                ),
            ),
            (
                _adapter_config(
                    name="param",
                    required=True,
                    value_type="str",
                    format=FormatAdapter(formatter=ApiDocValueFormat.DateTime),
                ),
                ExpectModelProps(
                    name="param",
                    required=True,
                    value_type="str",
                    format=Format(
                        strategy=FormatStrategy.CUSTOMIZE,
                        customize="datetime_value",
                        variables=[Variable(name="datetime_value", value_format=ValueFormat.DateTime)],
                    ),
                    items=None,
                ),
            ),
            (
                _adapter_config(
                    name="array_param",
                    required=True,
                    value_type="list",
                    format=None,
                    items=[
                        _adapter_config(
                            required=True,
                            value_type="str",
                            format=FormatAdapter(formatter=ApiDocValueFormat.DateTime),
                        ),
                    ],
                ),
                ExpectModelProps(
                    name="array_param",
                    required=True,
                    value_type="list",
                    format=None,
                    items=[
                        ExpectModelProps(
                            name="",
                            required=True,
                            value_type="str",
                            format=Format(
                                strategy=FormatStrategy.CUSTOMIZE,
                                customize="datetime_value",
                                variables=[Variable(name="datetime_value", value_format=ValueFormat.DateTime)],
                            ),
                            items=None,
                        ),
                    ],
                ),
            ),
            (
                _adapter_config(
                    name="array_param",
                    required=True,
                    value_type="list",
                    format=None,
                    items=[
                        _adapter_config(
                            name="id",
                            required=True,
                            value_type="str",
                            format=FormatAdapter(formatter=ApiDocValueFormat.Int64),
                        ),
                        _adapter_config(
                            name="date",
                            required=True,
                            value_type="str",
                            format=FormatAdapter(formatter=ApiDocValueFormat.DateTime),
                        ),
                    ],
                ),
                ExpectModelProps(
                    name="array_param",
                    required=True,
                    value_type="list",
                    format=None,
                    items=[
                        ExpectModelProps(
                            name="id",
                            required=True,
                            value_type="str",
                            format=Format(
                                strategy=FormatStrategy.BY_DATA_TYPE,
                                size=Size(
                                    max_value=9223372036854775807,
                                    min_value=-9223372036854775808,
                                ),
                            ),
                            items=None,
                        ),
                        ExpectModelProps(
                            name="date",
                            required=True,
                            value_type="str",
                            format=Format(
                                strategy=FormatStrategy.CUSTOMIZE,
                                customize="datetime_value",
                                variables=[Variable(name="datetime_value", value_format=ValueFormat.DateTime)],
                            ),
                            items=None,
                        ),
                    ],
                ),
            ),
        ],
    )
    def test_convert_flow(
        self, adapter_model_obj, pymock_model: BaseProperty, under_test_data: dict, expect: ExpectModelProps
    ):
        adapter_model = adapter_model_obj(**under_test_data)

        serialized_data = adapter_model.serialize()
        pymock_model_has_data = pymock_model.deserialize(serialized_data)

        self._verify_data_model_props(pymock_model=pymock_model_has_data, expect=expect)

    def _verify_data_model_props(self, pymock_model: BaseProperty, expect: ExpectModelProps) -> None:
        assert pymock_model is not None
        if expect.name:
            assert pymock_model.name == expect.name
        assert pymock_model.required == expect.required
        assert pymock_model.value_type == expect.value_type
        assert pymock_model.value_format == expect.format
        if expect.items:
            assert pymock_model.items
            assert len(pymock_model.items) == len(expect.items)
            # check details of items
            for pm, e in zip(pymock_model.items, expect.items):
                self._verify_data_model_props(pymock_model=pm, expect=e)
