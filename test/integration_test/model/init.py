import glob
import json
import os
import pathlib
from typing import Dict, List

import pytest

from pymock_api import APIConfig
from pymock_api.model import deserialize_swagger_api_config, load_config

from ..._file_utils import MockAPI_Config_Yaml_Path, yaml_factory
from ..._spec import run_test

# [(under_test_path, expected_path)]
DIVIDING_YAML_PATHS: List[tuple] = []

# [config_path]
OPENAPI_DOCUMENT_CONFIG_PATHS: List[str] = []


def _get_all_yaml_for_dividing() -> None:
    def _get_path(scenario_folder: str = "", yaml_file_naming: str = "") -> str:
        _path = (
            str(pathlib.Path(__file__).parent.parent.parent),
            "data",
            "divide_test_load",
            scenario_folder,
            yaml_file_naming,
        )
        return os.path.join(*_path)

    different_scenarios_data_folder = os.listdir(_get_path())
    for f in different_scenarios_data_folder:
        yaml_dir = _get_path(scenario_folder=f, yaml_file_naming="api.yaml")
        expected_yaml_dir = _get_path(scenario_folder=f, yaml_file_naming="_expected_api.yaml")
        global DIVIDING_YAML_PATHS
        for yaml_config_path, expected_yaml_config_path in zip(glob.glob(yaml_dir), glob.glob(expected_yaml_dir)):
            one_test_scenario = (yaml_config_path, expected_yaml_config_path)
            DIVIDING_YAML_PATHS.append(one_test_scenario)


def _get_all_openapi_config_path() -> None:
    def _get_path(config_type_dir: str) -> str:
        _path = (
            str(pathlib.Path(__file__).parent.parent.parent),
            "data",
            "deserialize_openapi_config_test",
            config_type_dir,
            "*.json",
        )
        return os.path.join(*_path)

    openapi_v2_dir = _get_path(config_type_dir="different_version")
    openapi_v3_dir = _get_path(config_type_dir="entire_config")
    for openapi_dir in [openapi_v2_dir, openapi_v3_dir]:
        global OPENAPI_DOCUMENT_CONFIG_PATHS
        for openapi_config_path in glob.glob(openapi_dir):
            OPENAPI_DOCUMENT_CONFIG_PATHS.append(openapi_config_path)


_get_all_yaml_for_dividing()
_get_all_openapi_config_path()


class TestInitFunctions:
    @property
    def not_exist_file_path(self) -> str:
        return "./file_not_exist.yaml"

    @run_test.with_file(yaml_factory)
    def test_load_config(self):
        # Run target function
        loaded_data = load_config(path=MockAPI_Config_Yaml_Path)

        # Verify result
        assert isinstance(loaded_data, APIConfig) and len(loaded_data) != 0, ""
        return "./file_not_exist.yaml"

    @run_test.with_file(yaml_factory)
    def test_load_config_with_not_exist_file(self):
        with pytest.raises(FileNotFoundError) as exc_info:
            # Run target function to test
            load_config(path=self.not_exist_file_path)
            # Verify result
            expected_err_msg = f"The target configuration file {self.not_exist_file_path} doesn't exist."
            assert str(exc_info) == expected_err_msg, f"The error message should be same as '{expected_err_msg}'."

    @pytest.mark.parametrize(("yaml_config_path", "expected_yaml_config_path"), DIVIDING_YAML_PATHS)
    def test_load_config_with_dividing_feature(self, yaml_config_path: str, expected_yaml_config_path: str):
        # Run utility function loads configuration to get config data
        dividing_config = load_config(yaml_config_path)
        expected_config = load_config(expected_yaml_config_path)

        # Verify detail values
        assert dividing_config is not None
        assert expected_config is not None

        # Check basic info
        assert dividing_config.name == expected_config.name
        assert dividing_config.description == expected_config.description

        # Check section
        assert dividing_config.apis is not None
        assert expected_config.apis is not None

        # Check section *base*
        if "no-base" not in yaml_config_path:
            assert dividing_config.apis.base is not None
            assert expected_config.apis.base is not None
            assert dividing_config.apis.base.serialize() == expected_config.apis.base.serialize()

        # Check section *apis*
        assert dividing_config.apis.apis is not None
        assert expected_config.apis.apis is not None
        expected_config_apis = expected_config.apis.apis
        # Compare the key of all mocked APIs
        assert dividing_config.apis.apis.keys() == expected_config.apis.apis.keys()
        # Compare the details of each mocked API
        for api_name, api_config in dividing_config.apis.apis.items():
            expected_api_config = expected_config_apis[api_name]
            assert api_config is not None
            assert expected_api_config is not None
            # Check URL
            assert api_config.url == expected_api_config.url
            # Check HTTP request
            assert api_config.http is not None
            assert expected_api_config.http is not None
            assert api_config.http.request is not None
            assert expected_api_config.http.request is not None
            assert api_config.http.request.serialize() == expected_api_config.http.request.serialize()
            # Check HTTP response
            assert api_config.http.response is not None
            assert expected_api_config.http.response is not None
            assert api_config.http.response.serialize() == expected_api_config.http.response.serialize()

    @pytest.mark.parametrize("openapi_config_path", OPENAPI_DOCUMENT_CONFIG_PATHS)
    def test_deserialize_swagger_api_config_with_openapi_config(self, openapi_config_path: str):
        # Pre-process
        with open(openapi_config_path, "r", encoding="utf-8") as io_stream:
            openapi_config_json = json.load(io_stream)

        # Run target
        openapi_config = deserialize_swagger_api_config(data=openapi_config_json)

        # Verify
        assert openapi_config is not None
        assert len(openapi_config.paths) != 0

        total_apis_cnt = 0
        paths: Dict[str, dict] = openapi_config_json["paths"]
        for p in paths.keys():
            total_apis_cnt += len(paths[p].keys())
        assert len(openapi_config.paths) == total_apis_cnt
