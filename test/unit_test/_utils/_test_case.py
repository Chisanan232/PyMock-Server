import glob
import os
import pathlib
from typing import List

RESPONSE_JSON_PATHS: List[str] = []


def _get_all_swagger_config() -> None:
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
