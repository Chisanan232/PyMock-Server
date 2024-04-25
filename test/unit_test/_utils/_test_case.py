import glob
import os
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
        json_dir = os.path.join(
            str(pathlib.Path(__file__).parent.parent.parent),
            "data",
            "check_test",
            "diff_with_swagger",
            "api_response",
            "*.json",
        )
        global RESPONSE_JSON_PATHS
        for json_config_path in glob.glob(json_dir):
            one_test_scenario = json_config_path
            RESPONSE_JSON_PATHS.append(one_test_scenario)
