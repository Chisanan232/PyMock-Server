import io
import re
import sys
from abc import ABCMeta, abstractmethod
from typing import List

import pytest

from pymock_api.runner import CommandRunner


class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = io.StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio  # free up some memory
        sys.stdout = self._stdout


class CommandFunctionTestSpec(metaclass=ABCMeta):
    _Command_Runner: CommandRunner = CommandRunner()

    @pytest.fixture(scope="module", autouse=True)
    def runner(self) -> CommandRunner:
        return self._Command_Runner

    @property
    @abstractmethod
    def options(self) -> List[str]:
        pass

    def test_command(self, runner: CommandRunner):
        with Capturing() as output:
            with pytest.raises(SystemExit):
                runner.parse(cmd_args=self.options)
        self.verify_running_output(" ".join(output))

    @abstractmethod
    def verify_running_output(self, cmd_running_result) -> None:
        pass

    @classmethod
    def _should_contains_chars_in_result(self, target: str, expected_char, translate: bool = True) -> None:
        if translate:
            assert re.search(re.escape(expected_char), target, re.IGNORECASE)
        else:
            assert re.search(expected_char, target, re.IGNORECASE)


class TestHelp(CommandFunctionTestSpec):
    @property
    def options(self) -> List[str]:
        return ["--help"]

    def verify_running_output(self, cmd_running_result) -> None:
        self._should_contains_chars_in_result(cmd_running_result, "mock-api [SUBCOMMAND] [OPTIONS]")
        self._should_contains_chars_in_result(cmd_running_result, "-h, --help")
        self._should_contains_chars_in_result(cmd_running_result, "-v, --version")


class TestSubCommandRunHelp(CommandFunctionTestSpec):
    @property
    def options(self) -> List[str]:
        return ["run", "--help"]

    def verify_running_output(self, cmd_running_result) -> None:
        self._should_contains_chars_in_result(cmd_running_result, "mock-api [SUBCOMMAND] [OPTIONS]")
        self._should_contains_chars_in_result(cmd_running_result, "-h, --help")
        self._should_contains_chars_in_result(cmd_running_result, "-c CONFIG, --config CONFIG")
        self._should_contains_chars_in_result(cmd_running_result, "-b BIND, --bind BIND")
        self._should_contains_chars_in_result(cmd_running_result, "-w WORKERS, --workers WORKERS")
        self._should_contains_chars_in_result(cmd_running_result, "--log-level LOG_LEVEL")


class TestVersion(CommandFunctionTestSpec):
    @property
    def options(self) -> List[str]:
        return ["--version"]

    def verify_running_output(self, cmd_running_result) -> None:
        software_version_format = r".{0,32}([0-9]{1,4}.[0-9]{1,4}.[0-9]{1,4}).{0,8}"
        self._should_contains_chars_in_result(
            cmd_running_result, re.escape("pymock-api") + software_version_format, translate=False
        )
