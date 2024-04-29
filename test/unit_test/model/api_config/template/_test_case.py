from typing import List

from ....._base_test_case import BaseTestCaseFactory, TestCaseDirPath

# _Test_Data: str = "./test/data/check_test/data_model/entire_api/valid/has-base-info_and_tags.yaml"
_Test_Data: List[str] = []


class DeserializeAPIConfigFromYamlTestCaseFactory(BaseTestCaseFactory):

    @classmethod
    def test_data_dir(cls) -> TestCaseDirPath:
        return TestCaseDirPath.CHECK_TEST

    @classmethod
    def get_test_case(cls) -> List[str]:
        return _Test_Data

    @classmethod
    def load(cls) -> None:

        def _generate_test_case_callback(file_path: str) -> None:
            _Test_Data.append(file_path)

        cls._iterate_files_by_path(
            path=cls.test_data_dir().generate_path_with_base_prefix_path(
                path=(
                    "data_model",
                    "entire_api",
                    "valid",
                    "*.yaml",
                ),
            ),
            generate_test_case_callback=_generate_test_case_callback,
        )
