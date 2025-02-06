import glob
import os
import pathlib
import sys
from argparse import Namespace
from typing import Callable, List, Optional, Type, Union
from unittest.mock import Mock, patch

import pytest

# isort: off

from test._values import SubCommand, _Test_Config
from test.unit_test.command._base.process import BaseCommandProcessorTestSpec

# isort: on

from fake_api_server.command.rest_server.check.process import SubCmdCheck
from fake_api_server.command.subcommand import SubCommandLine
from fake_api_server.model import SubcmdCheckArguments
from fake_api_server.model.subcmd_common import SysArg

YAML_PATHS_WITH_EX_CODE: List[tuple] = []


def _get_all_yaml(config_type: str, exit_code: Union[str, int]) -> None:
    yaml_dir = os.path.join(
        str(pathlib.Path(__file__).parent.parent.parent.parent.parent),
        "data",
        "check_test",
        "config",
        config_type,
        "*.yaml",
    )
    for yaml_config_path in glob.glob(yaml_dir):
        expected_exit_code = exit_code if isinstance(exit_code, str) and exit_code.isdigit() else str(exit_code)
        for stop_if_fail in (False, True):
            one_test_scenario = (yaml_config_path, stop_if_fail, expected_exit_code)
            global YAML_PATHS_WITH_EX_CODE
            YAML_PATHS_WITH_EX_CODE.append(one_test_scenario)


def _expected_err_msg(file: str) -> str:
    file = file.split("/")[-1] if "/" in file else file
    file_name: List[str] = file.split("-")
    config_key = file_name[0].replace("no_", "").replace(".yaml", "").replace("_", ".").replace("api.name", API_NAME)
    return f"Configuration *{config_key}* content"


_get_all_yaml(config_type="valid", exit_code=0)
_get_all_yaml(config_type="invalid", exit_code=1)

API_NAME: str = "google_home"


class TestSubCmdCheck(BaseCommandProcessorTestSpec):
    @pytest.fixture(scope="function")
    def cmd_ps(self) -> SubCmdCheck:
        return SubCmdCheck()

    @pytest.mark.parametrize(
        ("config_path", "stop_if_fail", "expected_exit_code"),
        YAML_PATHS_WITH_EX_CODE,
    )
    def test_with_command_processor(
        self, config_path: str, stop_if_fail: bool, expected_exit_code: str, object_under_test: Callable
    ):
        kwargs = {
            "config_path": config_path,
            "stop_if_fail": stop_if_fail,
            "expected_exit_code": expected_exit_code,
            "cmd_ps": object_under_test,
        }
        self._test_process(**kwargs)

    @pytest.mark.parametrize(
        ("config_path", "stop_if_fail", "expected_exit_code"),
        YAML_PATHS_WITH_EX_CODE,
    )
    def test_with_run_entry_point(
        self, config_path: str, stop_if_fail: bool, expected_exit_code: str, entry_point_under_test: Callable
    ):
        kwargs = {
            "config_path": config_path,
            "stop_if_fail": stop_if_fail,
            "expected_exit_code": expected_exit_code,
            "cmd_ps": entry_point_under_test,
        }
        self._test_process(**kwargs)

    def _test_process(self, config_path: str, stop_if_fail: bool, expected_exit_code: str, cmd_ps: Callable):
        mock_parser_arg = self._given_parser_args(config_path=config_path, stop_if_fail=stop_if_fail)
        cmd_parser = Mock()
        with patch.object(sys, "argv", self._given_command_line()):
            with pytest.raises(SystemExit) as exc_info:
                cmd_ps(cmd_parser, mock_parser_arg)
        assert expected_exit_code in str(exc_info.value)
        # TODO: Add one more checking of the error message content with function *_expected_err_msg*

    def _given_command_line(self) -> List[str]:
        return ["rest-server", "check"]

    def _given_parser_args(
        self, config_path: str, stop_if_fail: bool, swagger_doc_url: str = None
    ) -> SubcmdCheckArguments:
        return SubcmdCheckArguments(
            subparser_structure=SysArg.parse([SubCommand.RestServer, SubCommand.Check]),
            config_path=(config_path or _Test_Config),
            swagger_doc_url=swagger_doc_url,
            stop_if_fail=stop_if_fail,
            check_api_path=True,
            check_api_parameters=True,
            check_api_http_method=True,
        )

    def _given_cmd_args_namespace(self) -> Namespace:
        args_namespace = Namespace()
        args_namespace.subcommand = SubCommand.RestServer
        setattr(args_namespace, SubCommand.RestServer, SubCommand.Check)
        args_namespace.config_path = _Test_Config
        args_namespace.swagger_doc_url = "http://127.0.0.1:8080/docs"
        args_namespace.stop_if_fail = True
        args_namespace.check_api_path = True
        args_namespace.check_api_http_method = True
        args_namespace.check_api_parameters = True
        return args_namespace

    def _given_subcmd(self) -> Optional[SysArg]:
        return SysArg(
            pre_subcmd=SysArg(pre_subcmd=SysArg(subcmd=SubCommandLine.Base), subcmd=SubCommandLine.RestServer),
            subcmd=SubCommandLine.Check,
        )

    def _expected_argument_type(self) -> Type[SubcmdCheckArguments]:
        return SubcmdCheckArguments
