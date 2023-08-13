import glob
import json
import os
import pathlib
import re
from abc import ABCMeta, abstractmethod
from typing import List, Tuple

import pytest

from pymock_api.model.api_config import APIConfig
from pymock_api.model.api_config import APIParameter as PyMockAPIParameter
from pymock_api.model.api_config import MockAPI, _Config
from pymock_api.model.swagger_config import (
    API,
    APIParameter,
    SwaggerConfig,
    Transferable,
    convert_js_type,
    set_component_definition,
)


@pytest.mark.parametrize(
    ("js_type", "py_type"),
    [
        ("string", "str"),
        ("integer", "int"),
        ("boolean", "bool"),
        ("array", "list"),
    ],
)
def test_convert_js_type(js_type: str, py_type: str):
    assert convert_js_type(js_type) == py_type


def test_fail_convert_js_type():
    with pytest.raises(TypeError) as exc_info:
        convert_js_type("JS type which does not support to convert")
    assert "cannot parse JS type" in str(exc_info.value)


SWAGGER_API_DOC_JSON: List[tuple] = []
SWAGGER_ONE_API_JSON: List[tuple] = []
SWAGGER_API_PARAMETERS_JSON: List[tuple] = []
SWAGGER_API_PARAMETERS_JSON_FOR_API: List[Tuple[dict, dict]] = []
SWAGGER_API_PARAMETERS_LIST_JSON_FOR_API: List[Tuple[dict, dict]] = []


def _get_all_swagger_api_doc() -> None:
    json_dir = os.path.join(
        str(pathlib.Path(__file__).parent.parent.parent),
        "data",
        "deserialize_swagger_config_test",
        "entire_config",
        "*.json",
    )
    global SWAGGER_API_DOC_JSON
    for json_config_path in glob.glob(json_dir):
        with open(json_config_path, "r", encoding="utf-8") as file_stream:
            swagger_api_docs = json.loads(file_stream.read())
            SWAGGER_API_DOC_JSON.append(swagger_api_docs)
            apis: dict = swagger_api_docs["paths"]
            for api_path, api_props in apis.items():
                for api_detail in api_props.values():
                    SWAGGER_ONE_API_JSON.append((api_detail, swagger_api_docs))
                    SWAGGER_API_PARAMETERS_LIST_JSON_FOR_API.append((api_detail["parameters"], swagger_api_docs))
                    for param in api_detail["parameters"]:
                        if param.get("schema", {}).get("$ref", None) is None:
                            SWAGGER_API_PARAMETERS_JSON.append(param)
                        else:
                            SWAGGER_API_PARAMETERS_JSON_FOR_API.append((param, swagger_api_docs))


_get_all_swagger_api_doc()


class _SwaggerDataModelTestSuite(metaclass=ABCMeta):
    @pytest.fixture(scope="function")
    @abstractmethod
    def data_model(self) -> Transferable:
        pass

    @pytest.mark.parametrize("swagger_api_doc_data", [])
    def test_deserialize(self, swagger_api_doc_data: dict, data_model: Transferable):
        self._initial(data=data_model)
        deserialized_data = data_model.deserialize(data=swagger_api_doc_data)
        assert deserialized_data
        self._verify_result(data=deserialized_data, og_data=swagger_api_doc_data)

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


class TestAPIParameters(_SwaggerDataModelTestSuite):
    @pytest.fixture(scope="function")
    def data_model(self) -> APIParameter:
        return APIParameter()

    @pytest.mark.parametrize("swagger_api_doc_data", SWAGGER_API_PARAMETERS_JSON)
    def test_deserialize(self, swagger_api_doc_data: dict, data_model: Transferable):
        super().test_deserialize(swagger_api_doc_data, data_model)

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

    def test_parse_schema_with_invalid_value(self, data_model: APIParameter):
        invalid_values = {}
        with pytest.raises(ValueError) as exc_info:
            data_model.parse_schema(invalid_values, accept_no_schema=False)
        assert re.search(r".{0,64}doesn't have key 'schema'.{0,64}", str(exc_info.value), re.IGNORECASE)


class TestAPI(_SwaggerDataModelTestSuite):
    @pytest.fixture(scope="function")
    def data_model(self) -> API:
        return API()

    @pytest.mark.parametrize(("swagger_api_doc_data", "entire_swagger_config"), SWAGGER_ONE_API_JSON)
    def test_deserialize(self, swagger_api_doc_data: dict, entire_swagger_config: dict, data_model: Transferable):
        set_component_definition(data=entire_swagger_config, key="definitions")
        super().test_deserialize(swagger_api_doc_data, data_model)

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
        data_model.response = {}
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

    @pytest.mark.parametrize(
        ("swagger_api_doc_data", "entire_swagger_config"), SWAGGER_API_PARAMETERS_LIST_JSON_FOR_API
    )
    def test__process_api_params(self, swagger_api_doc_data: List[dict], entire_swagger_config: dict, data_model: API):
        # Pro-process
        set_component_definition(data=entire_swagger_config, key="definitions")

        # Run target function
        parameters = data_model._process_api_params(swagger_api_doc_data)

        # Verify
        assert parameters and isinstance(parameters, list)
        assert len(parameters) == len(swagger_api_doc_data)
        type_checksum = list(map(lambda p: isinstance(p, APIParameter), parameters))
        assert False not in type_checksum

    @pytest.mark.parametrize(("swagger_api_doc_data", "entire_swagger_config"), SWAGGER_API_PARAMETERS_JSON_FOR_API)
    def test__process_has_ref_parameters_with_valid_value(
        self, swagger_api_doc_data: dict, entire_swagger_config: dict, data_model: API
    ):
        # Pro-process
        set_component_definition(data=entire_swagger_config, key="definitions")

        # Run target function
        parameters = data_model._process_has_ref_parameters(swagger_api_doc_data)

        # Verify
        assert parameters and isinstance(parameters, list)
        assert len(parameters) == len(entire_swagger_config["definitions"]["UpdateFooRequest"]["properties"].keys())
        type_checksum = list(map(lambda p: isinstance(p, dict), parameters))
        assert False not in type_checksum

    @pytest.mark.parametrize("swagger_api_doc_data", SWAGGER_API_PARAMETERS_JSON)
    def test__process_has_ref_parameters_with_invalid_value(self, swagger_api_doc_data: dict, data_model: API):
        with pytest.raises(ValueError) as exc_info:
            # Run target function
            data_model._process_has_ref_parameters(swagger_api_doc_data)

        # Verify
        assert re.search(r".{1,64}no ref.{1,64}", str(exc_info.value), re.IGNORECASE)


class TestSwaggerConfig(_SwaggerDataModelTestSuite):
    @pytest.fixture(scope="function")
    def data_model(self) -> SwaggerConfig:
        return SwaggerConfig()

    @pytest.mark.parametrize("swagger_api_doc_data", SWAGGER_API_DOC_JSON)
    def test_deserialize(self, swagger_api_doc_data: dict, data_model: Transferable):
        set_component_definition(data=swagger_api_doc_data, key="definitions")
        super().test_deserialize(swagger_api_doc_data, data_model)

    def _initial(self, data: SwaggerConfig) -> None:
        data.paths = []

    def _verify_result(self, data: SwaggerConfig, og_data: dict) -> None:
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

    def _given_props(self, data_model: SwaggerConfig) -> None:
        params = APIParameter()
        params.name = "arg1"
        params.required = False
        params.value_type = "string"
        params.default = "default_value_pytest"

        api = API()
        api.path = "/test/v1/foo-home"
        api.http_method = "POST"
        api.parameters = [params]
        api.response = {}

        data_model.paths = [api]

    def _verify_api_config_model(self, under_test: APIConfig, data_from: SwaggerConfig) -> None:
        assert len(under_test.apis.apis.keys()) == len(data_from.paths)
        for api_path, api_details in under_test.apis.apis.items():
            expect_apis = list(
                filter(lambda a: api_path == f'{a.http_method}_{a.path[1:].replace("/", "_")}', data_from.paths)
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
            assert api_details.http.response.value == json.dumps(expect_api.response)

    @pytest.mark.parametrize(
        ("base_url", "api_path"),
        [
            ("/api/v1/test", "api/v1/test/foo-home"),
            ("api/v1/test", "/api/v1/test/foo-home"),
            ("/api/v1/test", "/api/v1/test/foo-home"),
            ("api/v1/test", "api/v1/test/foo-home"),
        ],
    )
    def test__align_url_format(self, base_url: str, api_path: str, data_model: SwaggerConfig):
        api = API()
        api.path = api_path
        base_url = data_model._align_url_format(base_url, api)
        assert re.search(r"/.{1,32}/.{1,32}/.{1,32}", base_url)
        assert re.search(r"/.{1,32}/.{1,32}/.{1,32}/.{1,32}", api.path)
