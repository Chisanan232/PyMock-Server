import os
from test._base_test_case import BaseTestCaseFactory, TestCaseDirPath
from typing import List

# [("swagger_config", "dry_run", "expected_config")]
PULL_YAML_PATHS_WITH_CONFIG: List[tuple] = []


class SubCmdPullTestCaseFactory(BaseTestCaseFactory):

    @classmethod
    def test_data_dir(cls) -> TestCaseDirPath:
        return TestCaseDirPath.PULL_TEST

    @classmethod
    def get_test_case(cls) -> List[tuple]:
        return PULL_YAML_PATHS_WITH_CONFIG

    @classmethod
    def load(cls) -> None:
        def _get_path(data_type: tuple, file_extension: str) -> str:
            path = cls.test_data_dir().generate_path_with_base_prefix_path(
                path=(
                    *data_type,
                    f"*.{file_extension}",
                ),
            )
            return str(os.path.join(*path))

        def _generate_test_case_callback(pair_paths: tuple) -> None:
            yaml_config_path = pair_paths[0]
            json_path = pair_paths[1]
            for dry_run_scenario in (True, False):
                one_test_scenario = (json_path, dry_run_scenario, yaml_config_path)
                PULL_YAML_PATHS_WITH_CONFIG.append(one_test_scenario)

        from_v2_config_yaml_path = _get_path(("config", "from_v2_openapi"), "yaml")
        from_v3_config_yaml_path = _get_path(("config", "from_v3_openapi"), "yaml")
        v2_openapi_doc_json_path = _get_path(("openapi_doc", "version2"), "json")
        v3_openapi_doc_json_path = _get_path(("openapi_doc", "version3"), "json")

        cls._iterate_files_by_paths(
            paths=(from_v2_config_yaml_path, v2_openapi_doc_json_path),
            generate_test_case_callback=_generate_test_case_callback,
            sort=True,
        )

        cls._iterate_files_by_paths(
            paths=(from_v3_config_yaml_path, v3_openapi_doc_json_path),
            generate_test_case_callback=_generate_test_case_callback,
            sort=True,
        )
