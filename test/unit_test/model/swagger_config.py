import glob
import json
import os
import pathlib
from abc import ABCMeta, abstractmethod
from typing import List, Optional

import pytest

from pymock_api.model.swagger_config import (
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


def _get_all_swagger_api_doc() -> None:
    json_dir = os.path.join(
        str(pathlib.Path(__file__).parent.parent.parent), "data", "inspect_test", "api_response", "*.json"
    )
    global SWAGGER_API_DOC_JSON
    for json_config_path in glob.glob(json_dir):
        with open(json_config_path, "r", encoding="utf-8") as file_stream:
            SWAGGER_API_DOC_JSON.append(json.loads(file_stream.read()))


_get_all_swagger_api_doc()


class _SwaggerDataModelTestSuite(metaclass=ABCMeta):
    @pytest.fixture(scope="function")
    @abstractmethod
    def data_model(self) -> BaseSwaggerDataModel:
        pass

    @pytest.mark.parametrize("swagger_api_doc_data", SWAGGER_API_DOC_JSON)
    def test_deserialize(self, swagger_api_doc_data: dict, data_model: BaseSwaggerDataModel):
        self._initial(data=data_model)
        deserialized_data = data_model.deserialize(data=swagger_api_doc_data)
        assert deserialized_data
        self._verify_result(data=deserialized_data, og_data=swagger_api_doc_data)

    @abstractmethod
    def _initial(self, data: BaseSwaggerDataModel) -> None:
        pass

    @abstractmethod
    def _verify_result(self, data: BaseSwaggerDataModel, og_data: dict) -> None:
        pass


class TestSwaggerConfig(_SwaggerDataModelTestSuite):
    @pytest.fixture(scope="function")
    def data_model(self) -> SwaggerConfig:
        return SwaggerConfig()

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
                assert api_param.default_value == one_swagger_api_param["schema"]["default"]
