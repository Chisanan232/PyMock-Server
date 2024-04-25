import glob
import os
import pathlib
from typing import List

from ..._base_test_case import BaseTestCaseFactory

# [(under_test_path, expected_path)]
DIVIDING_YAML_PATHS: List[tuple] = []

# [config_path]
OPENAPI_DOCUMENT_CONFIG_PATHS: List[str] = []


class LoadApiConfigWithDividingConfigTestCaseFactory(BaseTestCaseFactory):

    @classmethod
    def get_test_case(cls) -> List[tuple]:
        return DIVIDING_YAML_PATHS

    @classmethod
    def load(cls) -> None:
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


class DeserializeOpenAPIConfigTestCaseFactory(BaseTestCaseFactory):

    @classmethod
    def get_test_case(cls) -> List[str]:
        return OPENAPI_DOCUMENT_CONFIG_PATHS

    @classmethod
    def load(cls) -> None:
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
