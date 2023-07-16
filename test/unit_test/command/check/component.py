import glob
import json
import os
import pathlib
import re
from typing import List, Union
from unittest.mock import MagicMock, patch

import pytest

from pymock_api.command.check.component import (
    SubCmdCheckComponent,
    SwaggerDiffChecking,
    ValidityChecking,
)
from pymock_api.model import (
    ParserArguments,
    SubcmdAddArguments,
    SubcmdCheckArguments,
    SubcmdInspectArguments,
    SubcmdRunArguments,
    deserialize_swagger_api_config,
    load_config,
)

from ...._values import (
    _Bind_Host_And_Port,
    _Generate_Sample,
    _Log_Level,
    _Print_Sample,
    _Sample_File_Path,
    _Swagger_API_Document_URL,
    _Test_Config,
    _Test_SubCommand_Check,
    _Workers_Amount,
)


def _given_parser_args(
    subcommand: str = None,
    app_type: str = None,
    config_path: str = None,
    swagger_doc_url: str = None,
    stop_if_fail: bool = True,
) -> Union[SubcmdRunArguments, SubcmdAddArguments, SubcmdCheckArguments, SubcmdInspectArguments, ParserArguments]:
    if subcommand == "run":
        return SubcmdRunArguments(
            subparser_name=subcommand,
            app_type=app_type,
            config=_Test_Config,
            bind=_Bind_Host_And_Port.value,
            workers=_Workers_Amount.value,
            log_level=_Log_Level.value,
        )
    elif subcommand == "config":
        return SubcmdAddArguments(
            subparser_name=subcommand,
            print_sample=_Print_Sample,
            generate_sample=_Generate_Sample,
            sample_output_path=_Sample_File_Path,
        )
    elif subcommand == "check":
        return SubcmdCheckArguments(
            subparser_name=subcommand,
            config_path=(config_path or _Test_Config),
            swagger_doc_url=swagger_doc_url,
            stop_if_fail=stop_if_fail,
            check_api_path=True,
            check_api_parameters=True,
            check_api_http_method=True,
        )
    elif subcommand == "inspect":
        return SubcmdInspectArguments(
            subparser_name=subcommand,
            config_path=(config_path or _Test_Config),
        )
    else:
        return ParserArguments(
            subparser_name=None,
        )


RESPONSE_JSON_PATHS_WITH_EX_CODE: List[tuple] = []
RESPONSE_JSON_PATHS: List[str] = []


def _get_all_json(has_base_info: bool, config_type: str, exit_code: Union[str, int]) -> None:
    file_naming = "has-base-info" if has_base_info else "no-base-info"
    json_dir = os.path.join(
        str(pathlib.Path(__file__).parent.parent.parent.parent),
        "data",
        "check_test",
        "diff_with_swagger",
        "api_response",
        f"{file_naming}*.json",
    )
    global RESPONSE_JSON_PATHS_WITH_EX_CODE
    for json_config_path in glob.glob(json_dir):
        yaml_file_format = "*.yaml" if config_type == "invalid" else f"{file_naming}*.yaml"
        yaml_dir = os.path.join(
            str(pathlib.Path(__file__).parent.parent.parent.parent),
            "data",
            "check_test",
            "diff_with_swagger",
            "config",
            config_type,
            yaml_file_format,
        )
        expected_exit_code = exit_code if isinstance(exit_code, str) and exit_code.isdigit() else str(exit_code)
        for yaml_config_path in glob.glob(yaml_dir):
            for stop_if_fail in (True, False):
                one_test_scenario = (json_config_path, yaml_config_path, stop_if_fail, expected_exit_code)
                RESPONSE_JSON_PATHS_WITH_EX_CODE.append(one_test_scenario)


def _get_all_swagger_config() -> None:
    json_dir = os.path.join(
        str(pathlib.Path(__file__).parent.parent.parent.parent),
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


_get_all_json(has_base_info=False, config_type="valid", exit_code=0)
_get_all_json(has_base_info=True, config_type="valid", exit_code=0)
_get_all_json(has_base_info=False, config_type="invalid", exit_code=1)

_get_all_swagger_config()


class TestSubCmdCheckComponent:
    @pytest.fixture(scope="class")
    def subcmd(self) -> SubCmdCheckComponent:
        return SubCmdCheckComponent()

    @pytest.mark.parametrize(
        ("api_resp_path", "dummy_yaml_path", "stop_if_fail", "expected_exit_code"),
        RESPONSE_JSON_PATHS_WITH_EX_CODE,
    )
    def test_with_command_processor_of_diff_swagger(
        self,
        api_resp_path: str,
        dummy_yaml_path: str,
        stop_if_fail: bool,
        expected_exit_code: str,
        subcmd: SubCmdCheckComponent,
    ):
        kwargs = {
            "api_resp_path": api_resp_path,
            "dummy_yaml_path": dummy_yaml_path,
            "stop_if_fail": stop_if_fail,
            "expected_exit_code": expected_exit_code,
            "subcmd": subcmd,
        }
        self._test_process_of_diff_swagger(**kwargs)

    def _test_process_of_diff_swagger(
        self,
        api_resp_path: str,
        dummy_yaml_path: str,
        expected_exit_code: str,
        subcmd: SubCmdCheckComponent,
        stop_if_fail: bool,
    ):
        mock_parser_arg = _given_parser_args(
            subcommand=_Test_SubCommand_Check, swagger_doc_url=_Swagger_API_Document_URL, stop_if_fail=stop_if_fail
        )
        with patch("pymock_api.command.check.component.load_config") as mock_load_config:
            mock_load_config.return_value = load_config(dummy_yaml_path)
            with patch.object(SwaggerDiffChecking, "_get_swagger_config") as mock_get_swagger_config:
                with open(api_resp_path, "r", encoding="utf-8") as file_stream:
                    mock_get_swagger_config.return_value = deserialize_swagger_api_config(
                        json.loads(file_stream.read())
                    )

                with pytest.raises(SystemExit) as exc_info:
                    subcmd.process(mock_parser_arg)
                assert expected_exit_code in str(exc_info.value)


class TestValidityChecking:
    @pytest.fixture(scope="class")
    def checking(self) -> ValidityChecking:
        return ValidityChecking()

    def test__setting_should_be_valid(self, checking: ValidityChecking):
        test_callback = MagicMock()
        checking._setting_should_be_valid(
            config_key="key", config_value="value", criteria=["value"], valid_callback=test_callback
        )
        test_callback.assert_called_once_with("key", "value", ["value"])

    def test__setting_should_be_valid_with_invalid_type_criteria(self, checking: ValidityChecking):
        with pytest.raises(TypeError) as exc_info:
            checking._setting_should_be_valid(
                config_key="any key", config_value="any value", criteria="invalid type value"
            )
        assert re.search(r"only accept 'list'", str(exc_info.value), re.IGNORECASE)


class TestSwaggerDiffChecking:
    @pytest.fixture(scope="class")
    def checking(self) -> SwaggerDiffChecking:
        return SwaggerDiffChecking()

    @pytest.mark.parametrize("swagger_config_response", RESPONSE_JSON_PATHS)
    def test__get_swagger_config(self, swagger_config_response: str, checking: SwaggerDiffChecking):
        with patch("pymock_api.command.check.component.URLLibHTTPClient.request") as mock_api_client_request:
            with open(swagger_config_response, "r", encoding="utf-8") as file_stream:
                mock_api_client_request.return_value = json.loads(file_stream.read())

            checking._get_swagger_config(_Swagger_API_Document_URL)
            mock_api_client_request.assert_called_once_with(method="GET", url=_Swagger_API_Document_URL)
