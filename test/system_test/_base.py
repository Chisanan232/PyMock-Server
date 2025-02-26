import re
import subprocess
import sys
import threading
import time
from abc import ABCMeta, abstractmethod

# isort: off
from test._file_utils import yaml_factory
from test._spec import run_test
from test._utils import Capturing

# isort: on


class CommandTestSpec(metaclass=ABCMeta):
    Server_Running_Entry_Point: str = "fake_api_server/runner.py"
    Terminate_Command_Running_When_Sniff_IP_Info: bool = True
    Wait_Time_Before_Verify: int = 0

    @property
    def command_line(self) -> str:
        return f"python3 {self.Server_Running_Entry_Point} {self.options}"

    @property
    @abstractmethod
    def options(self) -> str:
        pass

    @run_test.with_file(yaml_factory)
    def test_command(self) -> None:
        try:
            with Capturing() as mock_server_output:
                self._run_as_thread(target=self._run_command_line)
            time.sleep(self.Wait_Time_Before_Verify)
            self._verify_running_output(" ".join(mock_server_output).replace("\n", "").replace("  ", ""))
        finally:
            self._do_finally()

    def _run_command_line(self) -> None:
        cmd_ps = subprocess.Popen(self.command_line, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self._read_streaming_output(cmd_ps)

    def _read_streaming_output(self, cmd_ps: subprocess.Popen) -> None:
        for line in iter(lambda: cmd_ps.stdout.readline(), b""):  # type: ignore
            sys.stdout.write(line.decode("utf-8"))
            if self.Terminate_Command_Running_When_Sniff_IP_Info and re.search(
                r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", line.decode("utf-8")
            ):
                break

    @abstractmethod
    def _verify_running_output(self, cmd_running_result: str) -> None:
        pass

    @classmethod
    def _run_as_thread(cls, target) -> None:
        run_cmd_thread = threading.Thread(target=target)
        run_cmd_thread.daemon = True
        run_cmd_thread.run()

    def _do_finally(self) -> None:
        pass

    @classmethod
    def _should_contains_chars_in_result(cls, target: str, expected_char, translate: bool = True) -> None:
        if translate:
            assert re.search(re.escape(expected_char), target, re.IGNORECASE)
        else:
            assert re.search(expected_char, target, re.IGNORECASE)

    @classmethod
    def _should_not_contains_chars_in_result(cls, target: str, expected_char, translate: bool = True) -> None:
        print(f"[DEBUG] in _should_not_contains_chars_in_result target: {target}")
        if translate:
            assert not re.search(re.escape(expected_char), target, re.IGNORECASE)
        else:
            assert not re.search(expected_char, target, re.IGNORECASE)
