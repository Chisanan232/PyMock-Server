import re
from abc import ABCMeta, abstractmethod
from typing import Type

import pytest

from pymock_api import APIConfig
from pymock_api.model import MockAPI
from pymock_api.model.api_config import _Config
from pymock_api.model.api_config.apis import APIParameter as PyMockAPIParameter
from pymock_api.model.enums import OpenAPIVersion, ResponseStrategy
from pymock_api.model.openapi._base import Transferable, set_openapi_version
from pymock_api.model.openapi._parser_factory import (
    BaseOpenAPISchemaParserFactory,
    OpenAPIV2SchemaParserFactory,
    OpenAPIV3SchemaParserFactory,
)
from pymock_api.model.openapi._schema_parser import (
    OpenAPIV2SchemaParser,
    OpenAPIV3SchemaParser,
    _ReferenceObjectParser,
    set_component_definition,
)
from pymock_api.model.openapi.config import (
    API,
    APIParameter,
    OpenAPIDocumentConfig,
    convert_js_type,
)

from ._test_case import (
    OPENAPI_API_DOC_JSON,
    OPENAPI_API_PARAMETERS_JSON,
    OPENAPI_ONE_API_JSON,
    DeserializeV2OpenAPIConfigTestCaseFactory,
    DeserializeV3OpenAPIConfigTestCaseFactory,
)

DeserializeV2OpenAPIConfigTestCaseFactory.load()

DeserializeV3OpenAPIConfigTestCaseFactory.load()
V3_OPENAPI_API_DOC_CONFIG_TEST_CASE = DeserializeV3OpenAPIConfigTestCaseFactory.get_test_case()


class _OpenAPIDocumentDataModelTestSuite(metaclass=ABCMeta):
    @pytest.fixture(scope="function")
    @abstractmethod
    def data_model(self) -> Transferable:
        pass

    @pytest.mark.parametrize("openapi_doc_data", [])
    def test_deserialize(self, openapi_doc_data: dict, data_model: Transferable):
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
    def _verify_result(self, data: Transferable, og_data: dict) -> None:
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


class TestAPIParameters(_OpenAPIDocumentDataModelTestSuite):
    @pytest.fixture(scope="function")
    def data_model(self) -> APIParameter:
        return APIParameter()

    @pytest.mark.parametrize("openapi_doc_data", OPENAPI_API_PARAMETERS_JSON)
    def test_deserialize(self, openapi_doc_data: dict, data_model: Transferable):
        super().test_deserialize(openapi_doc_data, data_model)

    def _initial(self, data: APIParameter) -> None:
        data.name = ""
        data.required = False
        data.value_type = ""
        data.default = None

    def _verify_result(self, data: APIParameter, og_data: dict) -> None:
        assert data is not None
        assert data.required == og_data["required"]
        if "schema" in og_data.keys():
            assert data.value_type == convert_js_type(og_data["schema"]["type"])
            assert data.default == og_data["schema"]["default"]
        else:
            assert data.value_type == convert_js_type(og_data["type"])
            assert data.default == og_data.get("default", None)

    def _given_props(self, data_model: APIParameter) -> None:
        data_model.name = "arg1"
        data_model.required = False
        data_model.value_type = "string"
        data_model.default = "default_value_pytest"

    def _verify_api_config_model(self, under_test: PyMockAPIParameter, data_from: APIParameter) -> None:
        assert under_test.name == data_from.name
        assert under_test.required == data_from.required
        assert under_test.value_type == data_from.value_type
        assert under_test.default == data_from.default
        assert under_test.value_format is None


class TestAPI(_OpenAPIDocumentDataModelTestSuite):
    @pytest.fixture(scope="function")
    def data_model(self) -> API:
        return API()

    @pytest.mark.parametrize(("openapi_doc_data", "entire_openapi_config"), OPENAPI_ONE_API_JSON)
    def test_deserialize(self, openapi_doc_data: dict, entire_openapi_config: dict, data_model: Transferable):
        # Previous process
        set_openapi_version(OpenAPIVersion.V2)
        set_component_definition(OpenAPIV2SchemaParser(data=entire_openapi_config))
        data_model.reload_schema_parser_factory()

        # Run test
        super().test_deserialize(openapi_doc_data, data_model)

        # Finally
        set_openapi_version(OpenAPIVersion.V3)
        data_model.reload_schema_parser_factory()

    def test_invalid_deserialize(self, data_model: API):
        data_model.process_response_strategy = None
        with pytest.raises(ValueError) as exc_info:
            data_model.deserialize(data={})
        assert re.search(r".{0,32}strategy.{0,32}", str(exc_info.value), re.IGNORECASE)

    def _initial(self, data: API) -> None:
        data.path = ""
        data.http_method = ""
        data.parameters = []
        data.response = {}

    def _verify_result(self, data: API, og_data: dict) -> None:
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
        assert len(data.parameters) == len(og_data["parameters"])
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
        params = APIParameter()
        params.name = "arg1"
        params.required = False
        params.value_type = "string"
        params.default = "default_value_pytest"

        data_model.path = "/test/v1/foo-home"
        data_model.http_method = "POST"
        data_model.parameters = [params]
        data_model.response = {"strategy": ResponseStrategy.STRING, "data": "OK"}
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


class TestOpenAPIDocumentConfig(_OpenAPIDocumentDataModelTestSuite):
    @pytest.fixture(scope="function")
    def data_model(self) -> OpenAPIDocumentConfig:
        return OpenAPIDocumentConfig()

    @pytest.mark.parametrize("openapi_doc_data", OPENAPI_API_DOC_JSON)
    def test_deserialize(self, openapi_doc_data: dict, data_model: Transferable):
        set_component_definition(OpenAPIV2SchemaParser(data=openapi_doc_data))
        super().test_deserialize(openapi_doc_data, data_model)

    def _initial(self, data: OpenAPIDocumentConfig) -> None:
        data.paths = []

    def _verify_result(self, data: OpenAPIDocumentConfig, og_data: dict) -> None:
        # TODO: Remove this deprecated test criteria if it ensure
        # def _get_api_param(name: str) -> Optional[dict]:
        #     swagger_api_params = og_data["paths"][api.path][api.http_method]["parameters"]
        #     for param in swagger_api_params:
        #         if param["name"] == name:
        #             return param
        #     return None

        path_with_method_number = [len(v.keys()) for v in og_data["paths"].values()]
        assert len(data.paths) == sum(path_with_method_number)
        for api in data.paths:
            assert api.path in og_data["paths"].keys()
            assert api.http_method in og_data["paths"][api.path].keys()

            assert len(api.parameters) == len(og_data["paths"][api.path][api.http_method]["parameters"])
            # TODO: Remove this deprecated test criteria if it ensure
            # for api_param in api.parameters:
            #     one_swagger_api_param = _get_api_param(api_param.name)
            #     assert one_swagger_api_param is not None
            #     assert api_param.required == one_swagger_api_param["required"]
            #     assert api_param.value_type == convert_js_type(one_swagger_api_param["schema"]["type"])
            #     assert api_param.default == one_swagger_api_param["schema"]["default"]

    def _given_props(self, data_model: OpenAPIDocumentConfig) -> None:
        params = APIParameter()
        params.name = "arg1"
        params.required = False
        params.value_type = "string"
        params.default = "default_value_pytest"

        api = API()
        api.path = "/test/v1/foo-home"
        api.http_method = "POST"
        api.parameters = [params]
        api.response = {"strategy": ResponseStrategy.STRING, "data": "OK"}

        data_model.paths = [api]

    def _verify_api_config_model(self, under_test: APIConfig, data_from: OpenAPIDocumentConfig) -> None:
        assert len(under_test.apis.apis.keys()) == len(data_from.paths)
        for api_path, api_details in under_test.apis.apis.items():
            expect_apis = list(
                filter(
                    lambda a: api_path == f'{a.http_method}_{a.path[1:].replace("/", "_")}',
                    data_from.paths,
                )
            )
            assert expect_apis
            expect_api = expect_apis[0]

            assert api_details.url == expect_api.path
            assert api_details.http.request.method == expect_api.http_method
            for api_param in api_details.http.request.parameters:
                api_param_in_data_from = list(filter(lambda _p: _p.name == api_param.name, expect_api.parameters))
                assert len(api_param_in_data_from) == 1
                param_data_from = api_param_in_data_from[0]
                assert param_data_from is not None
                assert api_param.required == param_data_from.required
                assert api_param.value_type == param_data_from.value_type
                assert api_param.default == param_data_from.default
            assert api_details.http.response.strategy == expect_api.response["strategy"]
            assert api_details.http.response.value == expect_api.response["data"]

    @pytest.mark.parametrize(
        ("base_url", "api_path"),
        [
            ("/api/v1/test", "api/v1/test/foo-home"),
            ("api/v1/test", "/api/v1/test/foo-home"),
            ("/api/v1/test", "/api/v1/test/foo-home"),
            ("api/v1/test", "api/v1/test/foo-home"),
        ],
    )
    def test__align_url_format(self, base_url: str, api_path: str, data_model: OpenAPIDocumentConfig):
        api = API()
        api.path = api_path
        base_url = data_model._align_url_format(base_url, api)
        assert re.search(r"/.{1,32}/.{1,32}/.{1,32}", base_url)
        assert re.search(r"/.{1,32}/.{1,32}/.{1,32}/.{1,32}", api.path)

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
        assert len(data.paths) == sum(path_with_method_number)
        for api in data.paths:
            assert api.path in og_data["paths"].keys()
            assert api.http_method in og_data["paths"][api.path].keys()

            api_http_details = og_data["paths"][api.path][api.http_method]
            if api.http_method.upper() == "GET":
                expected_parameters = 0
                for param in api_http_details.get("parameters", []):
                    if _ReferenceObjectParser.has_ref(param):
                        expected_parameters += len(_ReferenceObjectParser.get_schema_ref(param)["properties"].keys())
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
                    assert len(api.parameters) == len(
                        _ReferenceObjectParser.get_schema_ref(request_body["content"][data_format[0]])[
                            "properties"
                        ].keys()
                    )
                else:
                    expected_parameters = 0
                    for param in api_http_details["parameters"]:
                        if _ReferenceObjectParser.has_ref(param):
                            expected_parameters += len(
                                _ReferenceObjectParser.get_schema_ref(param)["properties"].keys()
                            )
                        else:
                            expected_parameters += 1
                    assert len(api.parameters) == expected_parameters
