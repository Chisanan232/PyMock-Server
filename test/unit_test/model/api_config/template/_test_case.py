from typing import List

from ....._base_test_case import BaseTestCaseFactory, TestCaseDirPath

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

        test_case_dir = TestCaseDirPath.CHECK_TEST
        cls._iterate_files_by_path(
            path=(
                test_case_dir.get_test_source_path(__file__),
                test_case_dir.base_data_path,
                test_case_dir.name,
                "data_model",
                "entire_api",
                "valid",
                "*.yaml",
            ),
            generate_test_case_callback=_generate_test_case_callback,
        )
