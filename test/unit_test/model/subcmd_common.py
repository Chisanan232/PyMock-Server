from typing import List

import pytest

from pymock_server.model.subcmd_common import SysArg


class TestSysArg:

    @pytest.mark.parametrize(
        ("sys_args_value", "expect_data_model"),
        [
            # only one sub-command
            (["pymock.py", "--help"], SysArg(pre_subcmd=None, subcmd="base")),
            (["pymock.py", "-h"], SysArg(pre_subcmd=None, subcmd="base")),
            (["pymock.py", "run"], SysArg(pre_subcmd=SysArg(pre_subcmd=None, subcmd="base"), subcmd="run")),
            (
                ["./test/pymock.py", "run", "-h"],
                SysArg(pre_subcmd=SysArg(pre_subcmd=None, subcmd="base"), subcmd="run"),
            ),
            (
                ["./pymock.py", "run", "-c", "./sample-api.yaml"],
                SysArg(pre_subcmd=SysArg(pre_subcmd=None, subcmd="base"), subcmd="run"),
            ),
            (
                ["./pymock.py", "run", "--app-type", "fastapi"],
                SysArg(pre_subcmd=SysArg(pre_subcmd=None, subcmd="base"), subcmd="run"),
            ),
            # nested sub-command which includes 2 or more sub-commands
            (
                ["./test/pymock.py", "api-server", "run", "-h"],
                SysArg(
                    pre_subcmd=SysArg(pre_subcmd=SysArg(pre_subcmd=None, subcmd="base"), subcmd="api-server"),
                    subcmd="run",
                ),
            ),
            (
                ["./test/pymock.py", "api-server", "run", "-c", "./sample-api.yaml"],
                SysArg(
                    pre_subcmd=SysArg(pre_subcmd=SysArg(pre_subcmd=None, subcmd="base"), subcmd="api-server"),
                    subcmd="run",
                ),
            ),
            (
                ["./test/pymock.py", "api-server", "run", "--app-type", "fastapi"],
                SysArg(
                    pre_subcmd=SysArg(pre_subcmd=SysArg(pre_subcmd=None, subcmd="base"), subcmd="api-server"),
                    subcmd="run",
                ),
            ),
        ],
    )
    def test_parse(self, sys_args_value: List[str], expect_data_model: SysArg):
        result = SysArg.parse(sys_args_value)
        assert result == expect_data_model
