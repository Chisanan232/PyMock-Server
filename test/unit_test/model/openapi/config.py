import re
from abc import ABCMeta, abstractmethod
from http import HTTPMethod, HTTPStatus
from typing import Type, Union

import pytest

from pymock_api import APIConfig
from pymock_api.model import MockAPI
from pymock_api.model.api_config import _Config
from pymock_api.model.enums import OpenAPIVersion
from pymock_api.model.openapi._base import Transferable, set_openapi_version
from pymock_api.model.openapi._parser_factory import (
    BaseOpenAPISchemaParserFactory,
    OpenAPIV2SchemaParserFactory,
    OpenAPIV3SchemaParserFactory,
)
from pymock_api.model.openapi._schema_parser import (
    OpenAPIV2SchemaParser,
    OpenAPIV3SchemaParser,
)
from pymock_api.model.openapi._tmp_data_model import (
    API,
    BaseTmpDataModel,
    PropertyDetail,
    RequestParameter,
    ResponseProperty,
    TmpAPIConfig,
    TmpAPIDtailConfigV2,
    TmpHttpConfigV2,
    TmpReferenceConfigPropertyModel,
    TmpRequestParameterModel,
    set_component_definition,
)
from pymock_api.model.openapi.config import OpenAPIDocumentConfig

from ._test_case import (
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

DeserializeV3OpenAPIConfigTestCaseFactory.load()
V3_OPENAPI_API_DOC_CONFIG_TEST_CASE = DeserializeV3OpenAPIConfigTestCaseFactory.get_test_case()


class _OpenAPIDocumentDataModelTestSuite(metaclass=ABCMeta):
    @pytest.fixture(scope="function")
    @abstractmethod
    def data_model(self) -> Transferable:
        pass

    @pytest.mark.parametrize("openapi_doc_data", [])
    def test_deserialize(self, openapi_doc_data: Union[dict, BaseTmpDataModel], data_model: Transferable):
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
    def _verify_result(self, data: Transferable, og_data: Union[dict, BaseTmpDataModel]) -> None:
        pass

    @abstractmethod
    def _given_props(self, data_model: Transferable) -> None:
        pass

    @abstractmethod
    def _verify_api_config_model(self, under_test: _Config, data_from: Transferable) -> None:
        pass

    @pytest.mark.parametrize(
        ("openapi_version", "expected_parser_factory"),
        [
            (OpenAPIVersion.V3, OpenAPIV3SchemaParserFactory),
        ],
    )
    def test_load_parser_factory_at_instantiate(
        self,
        data_model: Transferable,
        openapi_version: OpenAPIVersion,
        expected_parser_factory: Type[BaseOpenAPISchemaParserFactory],
    ):
        from pymock_api.model.openapi._base import OpenAPI_Document_Version

        assert OpenAPI_Document_Version is openapi_version
        assert isinstance(data_model.schema_parser_factory, expected_parser_factory)

    @pytest.mark.parametrize(
        ("openapi_version", "expected_parser_factory"),
        [
            # Enum type
            (OpenAPIVersion.V2, OpenAPIV2SchemaParserFactory),
            (OpenAPIVersion.V3, OpenAPIV3SchemaParserFactory),
            # str type
            ("2.0", OpenAPIV2SchemaParserFactory),
            ("2.0.6", OpenAPIV2SchemaParserFactory),
            ("3.0.1", OpenAPIV3SchemaParserFactory),
        ],
    )
    def test_reload_parser_factory(
        self,
        data_model: Transferable,
        openapi_version: OpenAPIVersion,
        expected_parser_factory: Type[BaseOpenAPISchemaParserFactory],
    ):
        set_openapi_version(openapi_version)
        data_model.reload_schema_parser_factory()
        assert isinstance(data_model.schema_parser_factory, expected_parser_factory)


class TestAPI(_OpenAPIDocumentDataModelTestSuite):
    @pytest.fixture(scope="function")
    def data_model(self) -> API:
        return API()

    @pytest.mark.parametrize(("openapi_doc_data", "entire_openapi_config"), DESERIALIZE_V2_OPENAPI_ENTIRE_API_TEST_CASE)
    def test_deserialize(self, openapi_doc_data: dict, entire_openapi_config: dict, data_model: Transferable):
        # Previous process
        set_openapi_version(OpenAPIVersion.V2)
        set_component_definition(OpenAPIV2SchemaParser(data=entire_openapi_config))
        data_model.reload_schema_parser_factory()

        # Run test
        openapi_doc_data = TmpAPIDtailConfigV2.deserialize(openapi_doc_data)
        super().test_deserialize(openapi_doc_data, data_model)

        # Finally
        set_openapi_version(OpenAPIVersion.V3)
        data_model.reload_schema_parser_factory()

    def _initial(self, data: API) -> None:
        data.path = ""
        data.http_method = ""
        data.parameters = []
        data.response = {}

    def _verify_result(self, data: API, og_data: TmpAPIDtailConfigV2) -> None:
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

    def _given_props(self, data_model: API) -> None:
        params = RequestParameter()
        params.name = "arg1"
        params.required = False
        params.value_type = "string"
        params.default = "default_value_pytest"

        data_model.path = "/test/v1/foo-home"
        data_model.http_method = "POST"
        data_model.parameters = [params]
        data_model.response = ResponseProperty(
            data=[
                PropertyDetail(name="key1", value_type="str", required=True),
            ],
        )
        data_model.tags = ["first tag", "second tag"]

    def _verify_api_config_model(self, under_test: MockAPI, data_from: API) -> None:
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


class TestOpenAPIDocumentConfig(_OpenAPIDocumentDataModelTestSuite):
    @pytest.fixture(scope="function")
    def data_model(self) -> OpenAPIDocumentConfig:
        return OpenAPIDocumentConfig()

    @pytest.mark.parametrize("openapi_doc_data", DESERIALIZE_V2_OPENAPI_ENTIRE_CONFIG_TEST_CASE)
    def test_deserialize(self, openapi_doc_data: dict, data_model: Transferable):
        set_component_definition(OpenAPIV2SchemaParser(data=openapi_doc_data))
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
            apis = api_config.to_adapter_api(path)
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
        params = TmpRequestParameterModel()
        params.name = "arg1"
        params.required = False
        params.value_type = "str"
        params.default = "default_value_pytest"

        api_with_one_method = TmpAPIDtailConfigV2()
        api_with_one_method.parameters = [params]
        api_with_one_method.responses = {
            HTTPStatus.OK: TmpHttpConfigV2(
                schema=TmpReferenceConfigPropertyModel(
                    value_type="str",
                )
            )
        }

        apis = TmpAPIConfig()
        apis.api = {HTTPMethod.POST: api_with_one_method}

        data_model.paths = {"/test/v1/foo-home": apis}

    def _verify_api_config_model(self, under_test: APIConfig, data_from: OpenAPIDocumentConfig) -> None:
        assert len(under_test.apis.apis.keys()) == len(data_from.paths)
        for api_path, api_details in under_test.apis.apis.items():
            print(f"[DEBUG in test] api_path: {api_path}")
            # Find the mapping expect API config

            def _find_path(_http_method: HTTPMethod) -> bool:
                return api_path == f'{_http_method.name.lower()}{path.replace("/", "_")}'

            expect_api_setting = None
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
            assert api_details.http.request.method == expect_http_method
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
            assert isinstance(response, TmpHttpConfigV2)
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

    @pytest.mark.parametrize(
        ("data", "expected_openapi_version", "expected_parser_factory"),
        [
            ({"swagger": "2.0"}, OpenAPIVersion.V2, OpenAPIV2SchemaParserFactory),
            ({"swagger": "2.6.0"}, OpenAPIVersion.V2, OpenAPIV2SchemaParserFactory),
            ({"swagger": "3.0"}, OpenAPIVersion.V3, OpenAPIV3SchemaParserFactory),
            ({"swagger": "3.1.0"}, OpenAPIVersion.V3, OpenAPIV3SchemaParserFactory),
        ],
    )
    def test__chk_version_and_load_parser(
        self,
        data_model: OpenAPIDocumentConfig,
        data: dict,
        expected_openapi_version: OpenAPIVersion,
        expected_parser_factory: Type[BaseOpenAPISchemaParserFactory],
    ):
        data_model._chk_version_and_load_parser(data)
        from pymock_api.model.openapi._base import OpenAPI_Document_Version

        assert OpenAPI_Document_Version is expected_openapi_version
        assert isinstance(data_model.schema_parser_factory, expected_parser_factory)

    @pytest.mark.parametrize("openapi_doc_data", V3_OPENAPI_API_DOC_CONFIG_TEST_CASE)
    def test_deserialize_with_openapi_v3(self, openapi_doc_data: dict, data_model: OpenAPIDocumentConfig):
        set_component_definition(OpenAPIV3SchemaParser(data=openapi_doc_data))

        self._initial(data=data_model)
        deserialized_data = data_model.deserialize(data=openapi_doc_data)
        assert deserialized_data
        self._verify_result_with_openapi_v3(data=deserialized_data, og_data=openapi_doc_data)

    def _verify_result_with_openapi_v3(self, data: OpenAPIDocumentConfig, og_data: dict) -> None:
        path_with_method_number = [len(v.keys()) for v in og_data["paths"].values()]
        data_model_apis = [len(v) for v in data.paths.values()]
        assert sum(data_model_apis) == sum(path_with_method_number)
        for api_path, api_config in data.paths.items():
            assert api_path in og_data["paths"].keys()
            apis = api_config.to_adapter_api(api_path)
            for api in apis:
                assert api.http_method.lower() in og_data["paths"][api.path].keys()

                api_http_details = og_data["paths"][api.path][api.http_method.lower()]
                if api.http_method.upper() == "GET":
                    expected_parameters = 0
                    api_req_params_data_model = list(
                        map(lambda e: TmpRequestParameterModel().deserialize(e), api_http_details.get("parameters", []))
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
                        req_body_model = TmpRequestParameterModel().deserialize(request_body["content"][data_format[0]])
                        assert len(api.parameters) == len(req_body_model.get_schema_ref().properties.keys())
                    else:
                        expected_parameters = 0
                        api_req_params_data_model = list(
                            map(lambda e: TmpRequestParameterModel().deserialize(e), api_http_details["parameters"])
                        )
                        for param in api_req_params_data_model:
                            if param.has_ref():
                                expected_parameters += len(param.get_schema_ref().properties.keys())
                            else:
                                expected_parameters += 1
                        assert len(api.parameters) == expected_parameters
