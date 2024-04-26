import pathlib
from typing import List

from ....._base_test_case import BaseTestCaseFactory

# _Test_Data: str = "./test/data/check_test/data_model/entire_api/valid/has-base-info_and_tags.yaml"
_Test_Data: List[str] = []


class DeserializeAPIConfigFromYamlTestCaseFactory(BaseTestCaseFactory):

    @classmethod
    def get_test_case(cls) -> List[str]:
        return _Test_Data

    @classmethod
    def load(cls) -> None:

        def _generate_test_case_callback(file_path: str) -> None:
            _Test_Data.append(file_path)

        cls._iterate_files_by_path(
            path=(
                str(pathlib.Path(__file__).parent.parent.parent.parent.parent),
                "data",
                "check_test",
                "data_model",
                "entire_api",
                "valid",
                "*.yaml",
            ),
            generate_test_case_callback=_generate_test_case_callback,
        )
