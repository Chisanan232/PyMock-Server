from typing import List

from ..._base_test_case import BaseTestCaseFactory, TestCaseDirPath

RESPONSE_JSON_PATHS: List[str] = []


class APIClientRequestTestCaseFactory(BaseTestCaseFactory):

    @classmethod
    def get_test_case(cls) -> List[str]:
        return RESPONSE_JSON_PATHS

    @classmethod
    def load(cls) -> None:

        def _generate_test_case_callback(file_path: str) -> None:
            one_test_scenario = file_path
            RESPONSE_JSON_PATHS.append(one_test_scenario)

        test_case_dir = TestCaseDirPath.CHECK_TEST
        cls._iterate_files_by_path(
            path=(
                test_case_dir.get_test_source_path(__file__),
                test_case_dir.base_data_path,
                test_case_dir.name,
                "diff_with_swagger",
                "api_response",
                "*.json",
            ),
            generate_test_case_callback=_generate_test_case_callback,
        )
