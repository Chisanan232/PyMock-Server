import glob
import os
import pathlib
from typing import List

# _Test_Data: str = "./test/data/check_test/data_model/entire_api/valid/has-base-info_and_tags.yaml"
_Test_Data: List[str] = []


class DeserializeAPIConfigFromYamlTestCaseFactory:

    @classmethod
    def get_test_case(cls) -> List[str]:
        return _Test_Data

    @classmethod
    def load(cls) -> None:
        yaml_dir = os.path.join(
            str(pathlib.Path(__file__).parent.parent.parent.parent.parent),
            "data",
            "check_test",
            "data_model",
            "entire_api",
            "valid",
            "*.yaml",
        )
        for yaml_config_path in glob.glob(yaml_dir):
            _Test_Data.append(yaml_config_path)
