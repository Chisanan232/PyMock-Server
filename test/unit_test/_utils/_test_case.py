import pathlib
from typing import List

from ..._base_test_case import BaseTestCaseFactory

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

        cls._iterate_files_by_path(
            path=(
                str(pathlib.Path(__file__).parent.parent.parent),
                "data",
                "check_test",
                "diff_with_swagger",
                "api_response",
                "*.json",
            ),
            generate_test_case_callback=_generate_test_case_callback,
        )
