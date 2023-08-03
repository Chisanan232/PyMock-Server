import glob
import json
import os
import pathlib
from abc import ABCMeta, abstractmethod
from typing import List, Optional

import pytest

from pymock_api.model.api_config import APIConfig
from pymock_api.model.api_config import APIParameter as PyMockAPIParameter
from pymock_api.model.api_config import MockAPI, _Config
from pymock_api.model.swagger_config import (
    API,
    APIParameter,
    BaseSwaggerDataModel,
    SwaggerConfig,
    convert_js_type,
)


@pytest.mark.parametrize(
    ("js_type", "py_type"),
    [
        ("string", "str"),
        ("integer", "int"),
        ("boolean", "bool"),
    ],
)
def test_convert_js_type(js_type: str, py_type: str):
    assert convert_js_type(js_type) == py_type


def test_fail_convert_js_type():
    with pytest.raises(TypeError) as exc_info:
        convert_js_type("JS type which does not support to convert")
    assert "cannot parse JS type" in str(exc_info.value)


SWAGGER_API_DOC_JSON: List[dict] = []
SWAGGER_ONE_API_JSON: List[dict] = []
SWAGGER_API_PARAMETERS_JSON: List[dict] = []


def _get_all_swagger_api_doc() -> None:
    json_dir = os.path.join(
        str(pathlib.Path(__file__).parent.parent.parent),
        "data",
        "check_test",
        "diff_with_swagger",
        "api_response",
        "*.json",
    )
    global SWAGGER_API_DOC_JSON
    for json_config_path in glob.glob(json_dir):
        with open(json_config_path, "r", encoding="utf-8") as file_stream:
            swagger_api_docs = json.loads(file_stream.read())
            SWAGGER_API_DOC_JSON.append(swagger_api_docs)
            apis: dict = swagger_api_docs["paths"]
            for api_path, api_props in apis.items():
                SWAGGER_ONE_API_JSON.append(api_props)
                for api_detail in api_props.values():
                    for param in api_detail["parameters"]:
                        SWAGGER_API_PARAMETERS_JSON.append(param)


_get_all_swagger_api_doc()


class _SwaggerDataModelTestSuite(metaclass=ABCMeta):
    @pytest.fixture(scope="function")
    @abstractmethod
    def data_model(self) -> BaseSwaggerDataModel:
        pass

    @pytest.mark.parametrize("swagger_api_doc_data", [])
    def test_deserialize(self, swagger_api_doc_data: dict, data_model: BaseSwaggerDataModel):
        self._initial(data=data_model)
        deserialized_data = data_model.deserialize(data=swagger_api_doc_data)
        assert deserialized_data
        self._verify_result(data=deserialized_data, og_data=swagger_api_doc_data)

    def test_to_api_config(self, data_model: BaseSwaggerDataModel):
        self._given_props(data_model)
        new_data_model = data_model.to_api_config()
        self._verify_api_config_model(under_test=new_data_model, data_from=data_model)

    @abstractmethod
    def _initial(self, data: BaseSwaggerDataModel) -> None:
        pass

    @abstractmethod
    def _verify_result(self, data: BaseSwaggerDataModel, og_data: dict) -> None:
        pass

    @abstractmethod
    def _given_props(self, data_model: BaseSwaggerDataModel) -> None:
        pass

    @abstractmethod
    def _verify_api_config_model(self, under_test: _Config, data_from: BaseSwaggerDataModel) -> None:
        pass


class TestAPIParameters(_SwaggerDataModelTestSuite):
    @pytest.fixture(scope="function")
    def data_model(self) -> APIParameter:
        return APIParameter()

    @pytest.mark.parametrize("swagger_api_doc_data", SWAGGER_API_PARAMETERS_JSON)
    def test_deserialize(self, swagger_api_doc_data: dict, data_model: BaseSwaggerDataModel):
        super().test_deserialize(swagger_api_doc_data, data_model)

    def _initial(self, data: APIParameter) -> None:
        data.name = ""
        data.required = False
        data.value_type = ""
        data.default = None

    def _verify_result(self, data: APIParameter, og_data: dict) -> None:
        assert data is not None
        assert data.required == og_data["required"]
        assert data.value_type == convert_js_type(og_data["schema"]["type"])
        assert data.default == og_data["schema"]["default"]

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


class TestAPI(_SwaggerDataModelTestSuite):
    @pytest.fixture(scope="function")
    def data_model(self) -> API:
        return API()

    @pytest.mark.parametrize("swagger_api_doc_data", SWAGGER_ONE_API_JSON)
    def test_deserialize(self, swagger_api_doc_data: dict, data_model: BaseSwaggerDataModel):
        super().test_deserialize(swagger_api_doc_data, data_model)

    def _initial(self, data: API) -> None:
        data.path = ""
        data.http_method = ""
        data.parameters = []
        data.response = {}

    def _verify_result(self, data: API, og_data: dict) -> None:
        def _get_api_param(method: str, name: str) -> Optional[dict]:
            swagger_api_params = og_data[method]["parameters"]
            for param in swagger_api_params:
                if param["name"] == name:
                    return param
            return None

        for og_api_method, og_api_props in og_data.items():
            assert data is not None
            assert data.path == ""
            assert data.http_method == og_api_method
            for api_param in data.parameters:
                one_swagger_api_param = _get_api_param(og_api_method, api_param.name)
                assert one_swagger_api_param is not None
                assert api_param.required == one_swagger_api_param["required"]
                assert api_param.value_type == convert_js_type(one_swagger_api_param["schema"]["type"])
                assert api_param.default == one_swagger_api_param["schema"]["default"]

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


class TestSwaggerConfig(_SwaggerDataModelTestSuite):
    @pytest.fixture(scope="function")
    def data_model(self) -> SwaggerConfig:
        return SwaggerConfig()

    @pytest.mark.parametrize("swagger_api_doc_data", SWAGGER_API_DOC_JSON)
    def test_deserialize(self, swagger_api_doc_data: dict, data_model: BaseSwaggerDataModel):
        super().test_deserialize(swagger_api_doc_data, data_model)

    def _initial(self, data: SwaggerConfig) -> None:
        data.paths = []

    def _verify_result(self, data: SwaggerConfig, og_data: dict) -> None:
        def _get_api_param(name: str) -> Optional[dict]:
            swagger_api_params = og_data["paths"][api.path][api.http_method]["parameters"]
            for param in swagger_api_params:
                if param["name"] == name:
                    return param
            return None

        assert len(data.paths) == len(og_data["paths"].keys())
        for api in data.paths:
            assert api.path in og_data["paths"].keys()
            assert api.http_method in og_data["paths"][api.path].keys()

            for api_param in api.parameters:
                one_swagger_api_param = _get_api_param(api_param.name)
                assert one_swagger_api_param is not None
                assert api_param.required == one_swagger_api_param["required"]
                assert api_param.value_type == convert_js_type(one_swagger_api_param["schema"]["type"])
                assert api_param.default == one_swagger_api_param["schema"]["default"]

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
            expect_apis = list(filter(lambda a: api_path == a.path[1:].replace("/", "_"), data_from.paths))
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
