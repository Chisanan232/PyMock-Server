import glob
import os
from typing import List

from ..._base_test_case import BaseTestCaseFactory, TestCaseDirPath

# [(under_test_path, expected_path)]
DIVIDING_YAML_PATHS: List[tuple] = []

# [config_path]
OPENAPI_DOCUMENT_CONFIG_PATHS: List[str] = []


class LoadApiConfigWithDividingConfigTestCaseFactory(BaseTestCaseFactory):

    @classmethod
    def test_data_dir(cls) -> TestCaseDirPath:
        return TestCaseDirPath.DIVIDE_TEST_LOAD

    @classmethod
    def get_test_case(cls) -> List[tuple]:
        return DIVIDING_YAML_PATHS

    @classmethod
    def load(cls) -> None:
        def _get_path(scenario_folder: str = "", yaml_file_naming: str = "") -> tuple:
            return cls.test_data_dir().generate_path_with_base_prefix_path(
                path=(
                    scenario_folder,
                    yaml_file_naming,
                ),
            )

        def _generate_dir_paths(folder_path: str) -> tuple:
            yaml_dir = _get_path(scenario_folder=folder_path, yaml_file_naming="api.yaml")
            expected_yaml_dir = _get_path(scenario_folder=folder_path, yaml_file_naming="_expected_api.yaml")
            return yaml_dir, expected_yaml_dir

        def _generate_test_case_callback(pair_files: tuple) -> None:
            yaml_config_path = pair_files[0]
            expected_yaml_config_path = pair_files[1]
            one_test_scenario = (yaml_config_path, expected_yaml_config_path)
            DIVIDING_YAML_PATHS.append(one_test_scenario)

        cls._iterate_files_by_directory(
            path=_get_path(),
            generate_dir_paths=_generate_dir_paths,
            generate_test_case_callback=_generate_test_case_callback,
        )


class DeserializeOpenAPIConfigTestCaseFactory(BaseTestCaseFactory):

    @classmethod
    def test_data_dir(cls) -> TestCaseDirPath:
        return TestCaseDirPath.DESERIALIZE_OPENAPI_CONFIG_TEST

    @classmethod
    def get_test_case(cls) -> List[str]:
        return OPENAPI_DOCUMENT_CONFIG_PATHS

    @classmethod
    def load(cls) -> None:
        def _get_path(config_type_dir: str) -> str:
            _path = cls.test_data_dir().generate_path_with_base_prefix_path(
                path=(
                    config_type_dir,
                    "*.json",
                ),
            )
            return str(os.path.join(*_path))

        openapi_v2_dir = _get_path(config_type_dir="different_version")
        openapi_v3_dir = _get_path(config_type_dir="entire_config")
        for openapi_dir in [openapi_v2_dir, openapi_v3_dir]:
            global OPENAPI_DOCUMENT_CONFIG_PATHS
            for openapi_config_path in glob.glob(openapi_dir):
                OPENAPI_DOCUMENT_CONFIG_PATHS.append(openapi_config_path)
