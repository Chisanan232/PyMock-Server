from test.system_test._base import SubCmdRestServerTestSuite

# isort: off
from test._values import (
    SubCommand,
)

# isort: on


class TestSubCmdRestServerWithoutAnyCmdArgs(SubCmdRestServerTestSuite):
    Terminate_Command_Running_When_Sniff_IP_Info: bool = False

    @property
    def options(self) -> str:
        return ""

    def _verify_running_output(self, cmd_running_result: str) -> None:
        self._should_contains_chars_in_result(
            cmd_running_result, "warn: please operate on this command with one more subcommand line you need"
        )
        self._should_contains_chars_in_result(cmd_running_result, "fake rest-server [-h]")
        self._should_contains_chars_in_result(cmd_running_result, "-h, --help")
        self._should_contains_chars_in_result(cmd_running_result, "API server subcommands:")
        self._should_contains_chars_in_result(cmd_running_result, SubCommand.Pull)
        self._should_contains_chars_in_result(cmd_running_result, SubCommand.Run)
        self._should_contains_chars_in_result(cmd_running_result, SubCommand.Check)
        self._should_contains_chars_in_result(cmd_running_result, SubCommand.Add)
        self._should_contains_chars_in_result(cmd_running_result, SubCommand.Get)
        self._should_contains_chars_in_result(cmd_running_result, SubCommand.Sample)
