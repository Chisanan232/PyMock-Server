import sys
from argparse import Namespace
from typing import Callable, List, Optional, Type
from unittest.mock import Mock, patch

import pytest

from fake_api_server._utils.file import Format
from fake_api_server.command.rest_server.get.process import SubCmdGet
from fake_api_server.command.subcommand import SubCommandLine
from fake_api_server.model import SubcmdGetArguments
from fake_api_server.model.subcmd_common import SysArg

# isort: off

from test._values import (
    SubCommand,
    _Cmd_Arg_API_Path,
    _Cmd_Arg_HTTP_Method,
    _Show_Detail_As_Format,
    _Test_Config,
)
from test.unit_test.command._base.process import BaseCommandProcessorTestSpec
from ._test_case import SubCmdGetTestCaseFactory

# isort: on

# With valid configuration
SubCmdGetTestCaseFactory.load(get_api_path="/foo-home", is_valid_config=True, exit_code=0)
SubCmdGetTestCaseFactory.load(get_api_path="/not-exist-api", is_valid_config=True, exit_code=1)

# With invalid configuration
SubCmdGetTestCaseFactory.load(get_api_path="/foo-home", is_valid_config=False, acceptable_error=True, exit_code=0)
SubCmdGetTestCaseFactory.load(get_api_path="/foo-home", is_valid_config=False, acceptable_error=False, exit_code=1)
SubCmdGetTestCaseFactory.load(get_api_path="/not-exist-api", is_valid_config=False, acceptable_error=True, exit_code=1)
SubCmdGetTestCaseFactory.load(get_api_path="/not-exist-api", is_valid_config=False, acceptable_error=False, exit_code=1)

SUBCMD_GET_TEST_CASE = SubCmdGetTestCaseFactory.get_test_case()


class TestSubCmdGet(BaseCommandProcessorTestSpec):
    @pytest.fixture(scope="function")
    def cmd_ps(self) -> SubCmdGet:
        return SubCmdGet()

    @pytest.mark.parametrize(
        ("yaml_config_path", "get_api_path", "expected_exit_code"),
        SUBCMD_GET_TEST_CASE,
    )
    def test_with_command_processor(
        self, yaml_config_path: str, get_api_path: str, expected_exit_code: int, object_under_test: Callable, **kwargs
    ):
        kwargs = {
            "yaml_config_path": yaml_config_path,
            "get_api_path": get_api_path,
            "expected_exit_code": expected_exit_code,
            "cmd_ps": object_under_test,
        }
        self._test_process(**kwargs)

    @pytest.mark.parametrize(
        ("yaml_config_path", "get_api_path", "expected_exit_code"),
        SUBCMD_GET_TEST_CASE,
    )
    def test_with_run_entry_point(
        self,
        yaml_config_path: str,
        get_api_path: str,
        expected_exit_code: int,
        entry_point_under_test: Callable,
        **kwargs,
    ):
        kwargs = {
            "yaml_config_path": yaml_config_path,
            "get_api_path": get_api_path,
            "expected_exit_code": expected_exit_code,
            "cmd_ps": entry_point_under_test,
        }
        self._test_process(**kwargs)

    def _test_process(self, yaml_config_path: str, get_api_path: str, expected_exit_code: int, cmd_ps: Callable):
        mock_parser_arg = self._given_parser_args(config_path=yaml_config_path, get_api_path=get_api_path)
        cmd_parser = Mock()
        with patch.object(sys, "argv", self._given_command_line()):
            with pytest.raises(SystemExit) as exc_info:
                cmd_ps(cmd_parser, mock_parser_arg)
        assert str(expected_exit_code) == str(exc_info.value)

    def _given_command_line(self) -> List[str]:
        return ["rest-server", "get"]

    def _given_parser_args(
        self, config_path: Optional[str] = None, get_api_path: str = _Cmd_Arg_API_Path
    ) -> SubcmdGetArguments:
        return SubcmdGetArguments(
            subparser_structure=SysArg.parse([SubCommand.RestServer, SubCommand.Get]),
            config_path=(config_path or _Test_Config),
            show_detail=True,
            show_as_format=Format[_Show_Detail_As_Format.upper()],
            api_path=get_api_path,
            http_method=_Cmd_Arg_HTTP_Method,
        )

    def _given_cmd_args_namespace(self) -> Namespace:
        args_namespace = Namespace()
        args_namespace.subcommand = SubCommand.RestServer
        setattr(args_namespace, SubCommand.RestServer, SubCommand.Get)
        args_namespace.config_path = _Test_Config
        args_namespace.show_detail = True
        args_namespace.show_as_format = _Show_Detail_As_Format
        args_namespace.api_path = _Cmd_Arg_API_Path
        args_namespace.http_method = _Cmd_Arg_HTTP_Method
        return args_namespace

    def _given_subcmd(self) -> Optional[SysArg]:
        return SysArg(
            pre_subcmd=SysArg(pre_subcmd=SysArg(subcmd=SubCommandLine.Base), subcmd=SubCommandLine.RestServer),
            subcmd=SubCommandLine.Get,
        )

    def _expected_argument_type(self) -> Type[SubcmdGetArguments]:
        return SubcmdGetArguments
