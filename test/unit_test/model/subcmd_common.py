from typing import List

import pytest

from pymock_server.command.subcommand import SubCommandLine
from pymock_server.model.subcmd_common import SysArg


class TestSysArg:

    @pytest.mark.parametrize(
        ("sys_args_value", "expect_data_model"),
        [
            # only one sub-command
            (["pymock.py", "--help"], SysArg(pre_subcmd=None, subcmd=SubCommandLine.Base)),
            (["pymock.py", "-h"], SysArg(pre_subcmd=None, subcmd=SubCommandLine.Base)),
            (
                ["pymock.py", "run"],
                SysArg(pre_subcmd=SysArg(pre_subcmd=None, subcmd=SubCommandLine.Base), subcmd=SubCommandLine.Run),
            ),
            (
                ["./test/pymock.py", "run", "-h"],
                SysArg(pre_subcmd=SysArg(pre_subcmd=None, subcmd=SubCommandLine.Base), subcmd=SubCommandLine.Run),
            ),
            (
                ["./pymock.py", "run", "-c", "./sample-api.yaml"],
                SysArg(pre_subcmd=SysArg(pre_subcmd=None, subcmd=SubCommandLine.Base), subcmd=SubCommandLine.Run),
            ),
            (
                ["./pymock.py", "run", "--app-type", "fastapi"],
                SysArg(pre_subcmd=SysArg(pre_subcmd=None, subcmd=SubCommandLine.Base), subcmd=SubCommandLine.Run),
            ),
            # nested sub-command which includes 2 or more sub-commands
            (
                ["./test/pymock.py", "rest-server", "run", "-h"],
                SysArg(
                    pre_subcmd=SysArg(
                        pre_subcmd=SysArg(pre_subcmd=None, subcmd=SubCommandLine.Base), subcmd=SubCommandLine.RestServer
                    ),
                    subcmd=SubCommandLine.Run,
                ),
            ),
            (
                ["./test/pymock.py", "rest-server", "run", "-c", "./sample-api.yaml"],
                SysArg(
                    pre_subcmd=SysArg(
                        pre_subcmd=SysArg(pre_subcmd=None, subcmd=SubCommandLine.Base), subcmd=SubCommandLine.RestServer
                    ),
                    subcmd=SubCommandLine.Run,
                ),
            ),
            (
                ["./test/pymock.py", "rest-server", "run", "--app-type", "fastapi"],
                SysArg(
                    pre_subcmd=SysArg(
                        pre_subcmd=SysArg(pre_subcmd=None, subcmd=SubCommandLine.Base), subcmd=SubCommandLine.RestServer
                    ),
                    subcmd=SubCommandLine.Run,
                ),
            ),
        ],
    )
    def test_parse(self, sys_args_value: List[str], expect_data_model: SysArg):
        result = SysArg.parse(sys_args_value)
        assert result == expect_data_model
