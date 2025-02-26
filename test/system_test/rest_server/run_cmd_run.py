import json
import os
import re
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable

# isort: off
from test._file_utils import MockAPI_Config_Yaml_Path
from test._values import (
    _Base_URL,
    _Bind_Host_And_Port,
    _Google_Home_Value,
    _Test_Home,
    _YouTube_Home_Value,
    _Access_Log_File,
)
from test.system_test.rest_server._base import SubCmdRestServerTestSuite

# isort: on


class TestSubCommandRun(SubCmdRestServerTestSuite):
    Terminate_Command_Running_When_Sniff_IP_Info: bool = False

    @property
    def options(self) -> str:
        return "run --help"

    def _verify_running_output(self, cmd_running_result: str) -> None:
        self._should_contains_chars_in_result(cmd_running_result, "fake rest-server run [-h]")
        self._should_contains_chars_in_result(cmd_running_result, "-h, --help")
        self._should_contains_chars_in_result(cmd_running_result, "--app-type APP_TYPE")
        self._should_contains_chars_in_result(cmd_running_result, "-c CONFIG, --config CONFIG")
        self._should_contains_chars_in_result(cmd_running_result, "-b BIND, --bind BIND")
        self._should_contains_chars_in_result(cmd_running_result, "-w WORKERS, --workers WORKERS")
        self._should_contains_chars_in_result(cmd_running_result, "--log-level LOG_LEVEL")


class RunFakeServerTestSpec(SubCmdRestServerTestSuite, ABC):
    def _verify_running_output(self, cmd_running_result: str) -> None:
        self._verify_apis()

    def _verify_apis(self) -> None:
        self._curl_and_chk_resp_content(
            api=f"{_Base_URL}{_Google_Home_Value['url']}",
            http_method=_Google_Home_Value["http"]["request"]["method"],
            expected_resp_content="google",
            resp_is_json_format=False,
        )
        self._curl_and_chk_resp_content(
            api=f"{_Base_URL}{_Test_Home['url']}",
            http_method=_Test_Home["http"]["request"]["method"],
            expected_resp_content="test",
            resp_is_json_format=True,
        )
        self._curl_and_chk_resp_content(
            api=f"{_Base_URL}{_YouTube_Home_Value['url']}",
            http_method=_YouTube_Home_Value["http"]["request"]["method"],
            expected_resp_content="youtube",
            resp_is_json_format=True,
        )

    @classmethod
    def _curl_and_chk_resp_content(
        cls, api: str, http_method: str, expected_resp_content: str, resp_is_json_format: bool
    ) -> None:
        if http_method.upper() == "GET":
            api_path = f"http://{_Bind_Host_And_Port.value}{api}\?param1\=any_format\&single_iterable_param\=test"
            option_data = ""
        else:
            api_path = f"http://{_Bind_Host_And_Port.value}{api}"
            option_data = '-d \'{"param1": "any_format", "iterable_param": ["test_value"]}\''
        curl_cmd_with_options = f"curl {api_path} \
              -X {http_method.upper()} \
              {option_data} \
              -H 'Content-Type: application/json'"
        curl_google_ps = subprocess.Popen(
            curl_cmd_with_options,
            shell=True,
            stdout=subprocess.PIPE,
        )
        assert curl_google_ps.stdout
        resp = curl_google_ps.stdout.readlines()[0]
        resp_content = json.loads(resp.decode("utf-8"))["content"] if resp_is_json_format else resp.decode("utf-8")
        assert re.search(re.escape(expected_resp_content), resp_content, re.IGNORECASE)

    @abstractmethod
    def _check_server_running_access_log(self, cmd_running_result: str, contains: bool) -> None:
        pass


class FlaskTestSuite(RunFakeServerTestSpec, ABC):
    def _do_finally(self) -> None:
        subprocess.run("pkill -f gunicorn", shell=True)

    def _check_server_running_access_log(self, cmd_running_result: str, contains: bool) -> None:
        check_callback: Callable[[str, str], None] = (
            self._should_contains_chars_in_result if contains else self._should_not_contains_chars_in_result
        )
        check_callback(cmd_running_result, "Starting gunicorn")
        check_callback(cmd_running_result, f"Listening at: http://{_Bind_Host_And_Port.value}")


class FastAPITestSuite(RunFakeServerTestSpec, ABC):
    def _do_finally(self) -> None:
        subprocess.run("pkill -f uvicorn", shell=True)

    def _check_server_running_access_log(self, cmd_running_result: str, contains: bool) -> None:
        check_callback: Callable[[str, str], None] = (
            self._should_contains_chars_in_result if contains else self._should_not_contains_chars_in_result
        )
        check_callback(cmd_running_result, "Started server process")
        check_callback(cmd_running_result, "Waiting for application startup")
        check_callback(cmd_running_result, "Application startup complete")
        check_callback(cmd_running_result, f"Uvicorn running on http://{_Bind_Host_And_Port.value}")


class TestWithFlask(FlaskTestSuite):
    @property
    def options(self) -> str:
        return f"run --app-type flask --bind {_Bind_Host_And_Port.value} --config {MockAPI_Config_Yaml_Path}"

    def _verify_running_output(self, cmd_running_result: str) -> None:
        self._check_server_running_access_log(cmd_running_result, contains=True)
        super()._verify_running_output(cmd_running_result)


class TestWithFastAPI(FastAPITestSuite):
    @property
    def options(self) -> str:
        return f"run --app-type fastapi --bind {_Bind_Host_And_Port.value} --config {MockAPI_Config_Yaml_Path}"

    def _verify_running_output(self, cmd_running_result: str) -> None:
        self._check_server_running_access_log(cmd_running_result, contains=True)
        super()._verify_running_output(cmd_running_result)


class TestWithAuto(FastAPITestSuite):
    @property
    def options(self) -> str:
        return f"run --app-type auto --bind {_Bind_Host_And_Port.value} --config {MockAPI_Config_Yaml_Path}"

    def _verify_running_output(self, cmd_running_result: str) -> None:
        self._check_server_running_access_log(cmd_running_result, contains=True)
        super()._verify_running_output(cmd_running_result)


class RunFakeServerAsDaemonTestSpec(RunFakeServerTestSpec, ABC):
    Wait_Time_Before_Verify: int = 2

    def _do_finally(self) -> None:
        with open(_Access_Log_File.value, "r") as file:
            content = file.read()
            print(f"[DEBUG] Server access log: {content}")
        os.remove(_Access_Log_File.value)
        super()._do_finally()

    def _verify_running_output(self, cmd_running_result: str) -> None:
        self._check_server_running_access_log(cmd_running_result, contains=False)
        assert Path(_Access_Log_File.value).exists()
        with open(_Access_Log_File.value, "r") as file:
            log_file_content = file.read()
        super()._verify_running_output(log_file_content)


class TestWithFlaskAsDaemon(RunFakeServerAsDaemonTestSpec, FlaskTestSuite):
    @property
    def options(self) -> str:
        return f"run --app-type flask --bind {_Bind_Host_And_Port.value} --config {MockAPI_Config_Yaml_Path} --config {MockAPI_Config_Yaml_Path} --access-log-file {_Access_Log_File.value} --daemon"


class TestWithFastAPIAsDaemon(RunFakeServerAsDaemonTestSpec, FastAPITestSuite):
    @property
    def options(self) -> str:
        return f"run --app-type fastapi --bind {_Bind_Host_And_Port.value} --config {MockAPI_Config_Yaml_Path} --config {MockAPI_Config_Yaml_Path} --access-log-file {_Access_Log_File.value} --daemon"


class TestWithAutoAsDaemon(RunFakeServerAsDaemonTestSpec, FastAPITestSuite):
    @property
    def options(self) -> str:
        return f"run --app-type auto --bind {_Bind_Host_And_Port.value} --config {MockAPI_Config_Yaml_Path} --access-log-file {_Access_Log_File.value} --daemon"
