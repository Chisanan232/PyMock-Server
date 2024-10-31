from test._base_test_case import BaseTestCaseFactory, TestCaseDirPath
from typing import List

RESPONSE_JSON_PATHS: List[str] = []


class APIClientRequestTestCaseFactory(BaseTestCaseFactory):

    @classmethod
    def test_data_dir(cls) -> TestCaseDirPath:
        return TestCaseDirPath.CHECK_TEST

    @classmethod
    def get_test_case(cls) -> List[str]:
        return RESPONSE_JSON_PATHS

    @classmethod
    def load(cls) -> None:

        def _generate_test_case_callback(file_path: str) -> None:
            one_test_scenario = file_path
            RESPONSE_JSON_PATHS.append(one_test_scenario)

        cls._iterate_files_by_path(
            path=cls.test_data_dir().generate_path_with_base_prefix_path(
                path=(
                    "diff_with_swagger",
                    "openapi_config",
                    "version3",
                    "*.json",
                ),
            ),
            generate_test_case_callback=_generate_test_case_callback,
        )
