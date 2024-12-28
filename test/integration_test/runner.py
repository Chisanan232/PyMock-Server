import re
import sys
from abc import ABCMeta, abstractmethod
from typing import List
from unittest.mock import patch

import pytest

from pymock_server._utils.importing import SUPPORT_SGI_SERVER, SUPPORT_WEB_FRAMEWORK
from pymock_server.command.subcommand import SubCommandLine
from pymock_server.runner import CommandRunner

# isort: off
from test._sut import get_runner
from test._utils import Capturing

# isort: on


class CommandFunctionTestSpec(metaclass=ABCMeta):
    @pytest.fixture(scope="function")
    def runner(self) -> CommandRunner:
        return get_runner()

    @property
    @abstractmethod
    def options(self) -> str:
        pass

    def test_command(self, runner: CommandRunner):
        with Capturing() as output:
            with pytest.raises(SystemExit):
                runner.parse(cmd_args=self.options.split())
        self.verify_running_output(" ".join(output))

    @abstractmethod
    def verify_running_output(self, cmd_running_result: str) -> None:
        pass

    @classmethod
    def _should_contains_chars_in_result(cls, target: str, expected_char, translate: bool = True) -> None:
        if translate:
            assert re.search(re.escape(expected_char), target, re.IGNORECASE)
        else:
            assert re.search(expected_char, target, re.IGNORECASE)


class TestCmdMock(CommandFunctionTestSpec):
    @property
    def options(self) -> str:
        return ""

    def test_command(self, runner: CommandRunner):
        with Capturing() as output:
            with pytest.raises(SystemExit):
                with patch.object(sys, "argv", [""]):
                    args = runner.parse(cmd_args=self.options.split())
                    runner.run(cmd_args=args)
        self.verify_running_output(" ".join(output))

    def verify_running_output(self, cmd_running_result: str) -> None:
        self._should_contains_chars_in_result(cmd_running_result, "mock [SUBCOMMAND] [OPTIONS]")
        self._should_contains_chars_in_result(cmd_running_result, "-h, --help")
        self._should_contains_chars_in_result(cmd_running_result, "-v, --version")
        self._should_contains_chars_in_result(cmd_running_result, "subcommands:")
        self._should_contains_chars_in_result(cmd_running_result, SubCommandLine.RestServer.value)


class TestHelp(CommandFunctionTestSpec):
    @property
    def options(self) -> str:
        return "--help"

    def verify_running_output(self, cmd_running_result: str) -> None:
        self._should_contains_chars_in_result(cmd_running_result, "mock [SUBCOMMAND] [OPTIONS]")
        self._should_contains_chars_in_result(cmd_running_result, "-h, --help")
        self._should_contains_chars_in_result(cmd_running_result, "-v, --version")
        self._should_contains_chars_in_result(cmd_running_result, "subcommands:")
        self._should_contains_chars_in_result(cmd_running_result, SubCommandLine.RestServer.value)


class TestVersion(CommandFunctionTestSpec):
    @property
    def options(self) -> str:
        return "--version"

    def verify_running_output(self, cmd_running_result: str) -> None:
        assert "PyMock-Server" in cmd_running_result
        assert "Web server" in cmd_running_result
        assert "Server gateway interface" in cmd_running_result
        software_version_format = r".{0,32}([0-9]{1,4}.[0-9]{1,4}.[0-9]{1,4}).{0,8}"
        all_py_pkg: List[str] = ["pymock-server"]
        all_py_pkg.extend(SUPPORT_WEB_FRAMEWORK)
        all_py_pkg.extend(SUPPORT_SGI_SERVER)
        for py_pkg in all_py_pkg:
            self._should_contains_chars_in_result(
                cmd_running_result, re.escape(py_pkg) + software_version_format, translate=False
            )


class TestSubCmdRestServer(CommandFunctionTestSpec):
    @property
    def options(self) -> str:
        return "rest-server"

    def test_command(self, runner: CommandRunner):
        with Capturing() as output:
            with pytest.raises(SystemExit):
                with patch.object(sys, "argv", ["rest-server"]):
                    args = runner.parse(cmd_args=self.options.split())
                    runner.run(cmd_args=args)
        self.verify_running_output(" ".join(output))

    def verify_running_output(self, cmd_running_result: str) -> None:
        self._should_contains_chars_in_result(cmd_running_result, "mock [SUBCOMMAND] [OPTIONS]")
        self._should_contains_chars_in_result(cmd_running_result, "-h, --help")
        self._should_contains_chars_in_result(cmd_running_result, "API server subcommands:")
        self._should_contains_chars_in_result(cmd_running_result, SubCommandLine.Pull.value)
        self._should_contains_chars_in_result(cmd_running_result, SubCommandLine.Run.value)
        self._should_contains_chars_in_result(cmd_running_result, SubCommandLine.Check.value)
        self._should_contains_chars_in_result(cmd_running_result, SubCommandLine.Add.value)
        self._should_contains_chars_in_result(cmd_running_result, SubCommandLine.Get.value)
        self._should_contains_chars_in_result(cmd_running_result, SubCommandLine.Sample.value)


class TestSubCmdRestServerHelp(CommandFunctionTestSpec):
    @property
    def options(self) -> str:
        return "rest-server --help"

    def verify_running_output(self, cmd_running_result: str) -> None:
        self._should_contains_chars_in_result(cmd_running_result, "mock [SUBCOMMAND] [OPTIONS]")
        self._should_contains_chars_in_result(cmd_running_result, "-h, --help")
        self._should_contains_chars_in_result(cmd_running_result, "API server subcommands:")
        self._should_contains_chars_in_result(cmd_running_result, SubCommandLine.Pull.value)
        self._should_contains_chars_in_result(cmd_running_result, SubCommandLine.Run.value)
        self._should_contains_chars_in_result(cmd_running_result, SubCommandLine.Check.value)
        self._should_contains_chars_in_result(cmd_running_result, SubCommandLine.Add.value)
        self._should_contains_chars_in_result(cmd_running_result, SubCommandLine.Get.value)
        self._should_contains_chars_in_result(cmd_running_result, SubCommandLine.Sample.value)
