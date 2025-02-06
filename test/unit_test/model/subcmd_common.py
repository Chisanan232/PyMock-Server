from typing import List

import pytest

from fake_api_server.command.subcommand import SubCommandLine
from fake_api_server.model.subcmd_common import SysArg


class TestSysArg:

    @pytest.mark.parametrize(
        ("sys_args_value", "expect_data_model"),
        [
            # only one sub-command
            (["pyfake.py", "--help"], SysArg(pre_subcmd=None, subcmd=SubCommandLine.Base)),
            (["pyfake.py", "-h"], SysArg(pre_subcmd=None, subcmd=SubCommandLine.Base)),
            (
                ["pyfake.py", "run"],
                SysArg(pre_subcmd=SysArg(pre_subcmd=None, subcmd=SubCommandLine.Base), subcmd=SubCommandLine.Run),
            ),
            (
                ["./test/pyfake.py", "run", "-h"],
                SysArg(pre_subcmd=SysArg(pre_subcmd=None, subcmd=SubCommandLine.Base), subcmd=SubCommandLine.Run),
            ),
            (
                ["./pyfake.py", "run", "-c", "./sample-api.yaml"],
                SysArg(pre_subcmd=SysArg(pre_subcmd=None, subcmd=SubCommandLine.Base), subcmd=SubCommandLine.Run),
            ),
            (
                ["./pyfake.py", "run", "--app-type", "fastapi"],
                SysArg(pre_subcmd=SysArg(pre_subcmd=None, subcmd=SubCommandLine.Base), subcmd=SubCommandLine.Run),
            ),
            # nested sub-command which includes 2 or more sub-commands
            (
                ["./test/pyfake.py", "rest-server", "run", "-h"],
                SysArg(
                    pre_subcmd=SysArg(
                        pre_subcmd=SysArg(pre_subcmd=None, subcmd=SubCommandLine.Base), subcmd=SubCommandLine.RestServer
                    ),
                    subcmd=SubCommandLine.Run,
                ),
            ),
            (
                ["./test/pyfake.py", "rest-server", "run", "-c", "./sample-api.yaml"],
                SysArg(
                    pre_subcmd=SysArg(
                        pre_subcmd=SysArg(pre_subcmd=None, subcmd=SubCommandLine.Base), subcmd=SubCommandLine.RestServer
                    ),
                    subcmd=SubCommandLine.Run,
                ),
            ),
            (
                ["./test/pyfake.py", "rest-server", "run", "--app-type", "fastapi"],
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
