import io
import json
import re
import subprocess
import sys
import threading
from abc import ABC, ABCMeta, abstractmethod
from typing import List

import pytest

from pymock_api.runner import CommandRunner

from .._values import _Bind_Host_And_Port, _Test_Config
from ._spec import MockAPI_Config_Path, run_test


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
    @pytest.fixture(scope="function")
    def runner(self) -> CommandRunner:
        return CommandRunner()

    @property
    @abstractmethod
    def options(self) -> List[str]:
        pass

    def test_command(self, capsys, runner: CommandRunner):
        with Capturing() as output:
            with pytest.raises(SystemExit):
                runner.parse(cmd_args=self.options)
        self.verify_running_output(" ".join(output))

    @abstractmethod
    def verify_running_output(self, cmd_running_result) -> None:
        pass

    @classmethod
    def _should_contains_chars_in_result(self, target: str, expected_char: str) -> None:
        assert re.search(re.escape(expected_char), target, re.IGNORECASE)


class TestHelp(CommandFunctionTestSpec):
    @property
    def options(self) -> List[str]:
        return ["--help"]

    def verify_running_output(self, cmd_running_result) -> None:
        self._should_contains_chars_in_result(cmd_running_result, "mock-api [OPTIONS]")
        self._should_contains_chars_in_result(cmd_running_result, "-h, --help")
        self._should_contains_chars_in_result(cmd_running_result, "-c CONFIG, --config CONFIG")
        self._should_contains_chars_in_result(cmd_running_result, "-b BIND, --bind BIND")
        self._should_contains_chars_in_result(cmd_running_result, "-w WORKERS, --workers WORKERS")
        self._should_contains_chars_in_result(cmd_running_result, "--log-level LOG_LEVEL")


class StreamingOutputCommandFunctionTestSpec(CommandFunctionTestSpec, ABC):

    Server_Running_Entry_Point: str = "pymock_api/runner.py"

    @property
    def command_line(self) -> str:
        cmd_options = " ".join(self.options)
        return f"python3 {self.Server_Running_Entry_Point} {cmd_options}"

    @run_test.with_file
    def test_command(self, runner: CommandRunner) -> None:
        try:
            with Capturing() as mock_server_output:
                self._run_as_thread(target=self.run_mock_api_server)
            self.verify_running_output(" ".join(mock_server_output))
            self.verify_apis()
        finally:
            self._kill_all_server_workers()

    def run_mock_api_server(self) -> None:
        cmd_ps = subprocess.Popen(self.command_line, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in iter(lambda: cmd_ps.stdout.readline(), b""):
            sys.stdout.write(line.decode("utf-8"))
            if re.search(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", line.decode("utf-8")):
                break

    def verify_apis(self) -> None:
        self._curl_and_chk_resp_content(
            api="/test/v1/google", expected_resp_content="google", resp_is_json_format=False
        )
        self._curl_and_chk_resp_content(api="/test/v1/test", expected_resp_content="test", resp_is_json_format=True)
        self._curl_and_chk_resp_content(
            api="/test/v1/youtube", expected_resp_content="youtube", resp_is_json_format=True
        )

    @classmethod
    def _run_as_thread(cls, target) -> None:
        run_cmd_thread = threading.Thread(target=target)
        run_cmd_thread.daemon = True
        run_cmd_thread.run()

    @classmethod
    @abstractmethod
    def _kill_all_server_workers(cls) -> None:
        pass

    @classmethod
    def _curl_and_chk_resp_content(cls, api: str, expected_resp_content: str, resp_is_json_format: bool) -> None:
        curl_google_ps = subprocess.Popen(
            f"curl http://{_Bind_Host_And_Port.value}{api}", shell=True, stdout=subprocess.PIPE
        )
        resp = curl_google_ps.stdout.readlines()[0]
        resp_content = json.loads(resp.decode("utf-8"))["content"] if resp_is_json_format else resp.decode("utf-8")
        assert re.search(re.escape(expected_resp_content), resp_content, re.IGNORECASE)


class TestRunApplicationToMockAPIsWithFlaskAndGunicorn(StreamingOutputCommandFunctionTestSpec):
    @property
    def options(self) -> List[str]:
        return ["--app-type", "flask", "--bind", _Bind_Host_And_Port.value, "--config", MockAPI_Config_Path]

    @classmethod
    def _kill_all_server_workers(cls) -> None:
        subprocess.run("pkill -f gunicorn", shell=True)

    def verify_running_output(self, cmd_running_result) -> None:
        self._should_contains_chars_in_result(cmd_running_result, "Starting gunicorn")
        self._should_contains_chars_in_result(cmd_running_result, f"Listening at: http://{_Bind_Host_And_Port.value}")
