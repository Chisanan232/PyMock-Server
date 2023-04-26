import json
import os
import re
import subprocess
import sys
import threading
from abc import ABC, ABCMeta, abstractmethod
from typing import Optional

import pytest

from pymock_api._utils.file_opt import YAML
from pymock_api.model._sample import Mocked_APIs, Sample_Config_Value

from .._values import (
    _Base_URL,
    _Bind_Host_And_Port,
    _Google_Home_Value,
    _Test_Home,
    _YouTube_Home_Value,
)
from ._spec import MockAPI_Config_Path, run_test
from .runner import Capturing


class CommandTestSpec(metaclass=ABCMeta):
    Server_Running_Entry_Point: str = "pymock_api/runner.py"
    Terminate_Command_Running_When_Sniff_IP_Info: bool = True

    @property
    def command_line(self) -> str:
        return f"python3 {self.Server_Running_Entry_Point} {self.options}"

    @property
    @abstractmethod
    def options(self) -> str:
        pass

    @run_test.with_file
    def test_command(self) -> None:
        try:
            with Capturing() as mock_server_output:
                self._run_as_thread(target=self._run_command_line)
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


class TestSubCommandRun(CommandTestSpec):
    Terminate_Command_Running_When_Sniff_IP_Info: bool = False

    @property
    def options(self) -> str:
        return "run --help"

    def _verify_running_output(self, cmd_running_result: str) -> None:
        self._should_contains_chars_in_result(cmd_running_result, "mock-api run [-h]")
        self._should_contains_chars_in_result(cmd_running_result, "-h, --help")
        self._should_contains_chars_in_result(cmd_running_result, "--app-type APP_TYPE")
        self._should_contains_chars_in_result(cmd_running_result, "-c CONFIG, --config CONFIG")
        self._should_contains_chars_in_result(cmd_running_result, "-b BIND, --bind BIND")
        self._should_contains_chars_in_result(cmd_running_result, "-w WORKERS, --workers WORKERS")
        self._should_contains_chars_in_result(cmd_running_result, "--log-level LOG_LEVEL")


class TestSubCommandConfig(CommandTestSpec):
    Terminate_Command_Running_When_Sniff_IP_Info: bool = False

    @property
    def options(self) -> str:
        return "config --help"

    def _verify_running_output(self, cmd_running_result: str) -> None:
        self._should_contains_chars_in_result(cmd_running_result, "-h, --help")
        self._should_contains_chars_in_result(cmd_running_result, "-p, --print-sample")
        self._should_contains_chars_in_result(cmd_running_result, "-g, --generate-sample")
        self._should_contains_chars_in_result(cmd_running_result, "-o FILE_PATH, --output FILE_PATH")


class TestShowSampleConfiguration(CommandTestSpec):
    Terminate_Command_Running_When_Sniff_IP_Info: bool = False

    @property
    def options(self) -> str:
        return "config -p"

    def _verify_running_output(self, cmd_running_result: str) -> None:
        for api_name, api_config in Mocked_APIs.items():
            self._should_contains_chars_in_result(cmd_running_result, api_name)
            self._should_contains_chars_in_result(cmd_running_result, api_config["url"])
            if api_name != "base":
                self._should_contains_chars_in_result(cmd_running_result, api_config["http"]["request"]["method"])
                self._should_contains_chars_in_result(cmd_running_result, str(api_config["http"]["response"]["value"]))


class TestGenerateSampleConfiguration(CommandTestSpec):
    Terminate_Command_Running_When_Sniff_IP_Info: bool = False
    _Default_Path: str = "sample-api.yaml"
    _Under_Test_Path: Optional[str] = None

    @property
    def options(self) -> str:
        return f"config -g -o {self._Under_Test_Path}" if self._Under_Test_Path else "config -g"

    @pytest.mark.parametrize("config_path", [None, "output-test-api.yaml"])
    def test_command(self, config_path: str) -> None:
        self._Under_Test_Path = config_path or self._Default_Path

        # Check and clean file
        if os.path.exists(self._Under_Test_Path):
            os.remove(self._Under_Test_Path)

        try:
            super().test_command()
        finally:
            # clean file
            if os.path.exists(self._Under_Test_Path):
                os.remove(self._Under_Test_Path)

    def _verify_running_output(self, cmd_running_result: str) -> None:
        assert self._Under_Test_Path
        assert os.path.exists(self._Under_Test_Path)
        config_data = YAML().read(self._Under_Test_Path)
        assert config_data == Sample_Config_Value


class RunMockApplicationTestSpec(CommandTestSpec, ABC):
    def _verify_running_output(self, cmd_running_result: str) -> None:
        self._verify_apis()

    def _verify_apis(self) -> None:
        self._curl_and_chk_resp_content(
            api=f"{_Base_URL}{_Google_Home_Value['url']}", expected_resp_content="google", resp_is_json_format=False
        )
        self._curl_and_chk_resp_content(
            api=f"{_Base_URL}{_Test_Home['url']}", expected_resp_content="test", resp_is_json_format=True
        )
        self._curl_and_chk_resp_content(
            api=f"{_Base_URL}{_YouTube_Home_Value['url']}", expected_resp_content="youtube", resp_is_json_format=True
        )

    @classmethod
    def _curl_and_chk_resp_content(cls, api: str, expected_resp_content: str, resp_is_json_format: bool) -> None:
        curl_google_ps = subprocess.Popen(
            f"curl http://{_Bind_Host_And_Port.value}{api}", shell=True, stdout=subprocess.PIPE
        )
        assert curl_google_ps.stdout
        resp = curl_google_ps.stdout.readlines()[0]
        resp_content = json.loads(resp.decode("utf-8"))["content"] if resp_is_json_format else resp.decode("utf-8")
        assert re.search(re.escape(expected_resp_content), resp_content, re.IGNORECASE)


class TestRunMockApplicationWithFlask(RunMockApplicationTestSpec):
    @property
    def options(self) -> str:
        return f"run --app-type flask --bind {_Bind_Host_And_Port.value} --config {MockAPI_Config_Path}"

    def _do_finally(self) -> None:
        subprocess.run("pkill -f gunicorn", shell=True)

    def _verify_running_output(self, cmd_running_result: str) -> None:
        self._should_contains_chars_in_result(cmd_running_result, "Starting gunicorn")
        self._should_contains_chars_in_result(cmd_running_result, f"Listening at: http://{_Bind_Host_And_Port.value}")
        super()._verify_running_output(cmd_running_result)


class TestRunMockApplicationWithFastAPI(RunMockApplicationTestSpec):
    @property
    def options(self) -> str:
        return f"run --app-type fastapi --bind {_Bind_Host_And_Port.value} --config {MockAPI_Config_Path}"

    def _do_finally(self) -> None:
        subprocess.run("pkill -f uvicorn", shell=True)

    def _verify_running_output(self, cmd_running_result: str) -> None:
        self._should_contains_chars_in_result(cmd_running_result, "Started server process")
        self._should_contains_chars_in_result(cmd_running_result, "Waiting for application startup")
        self._should_contains_chars_in_result(cmd_running_result, "Application startup complete")
        self._should_contains_chars_in_result(
            cmd_running_result, f"Uvicorn running on http://{_Bind_Host_And_Port.value}"
        )
        super()._verify_running_output(cmd_running_result)


class TestRunMockApplicationWithAuto(RunMockApplicationTestSpec):
    @property
    def options(self) -> str:
        return f"run --app-type auto --bind {_Bind_Host_And_Port.value} --config {MockAPI_Config_Path}"

    def _do_finally(self) -> None:
        subprocess.run("pkill -f uvicorn", shell=True)

    def _verify_running_output(self, cmd_running_result: str) -> None:
        self._should_contains_chars_in_result(cmd_running_result, "Started server process")
        self._should_contains_chars_in_result(cmd_running_result, "Waiting for application startup")
        self._should_contains_chars_in_result(cmd_running_result, "Application startup complete")
        self._should_contains_chars_in_result(
            cmd_running_result, f"Uvicorn running on http://{_Bind_Host_And_Port.value}"
        )
        super()._verify_running_output(cmd_running_result)
