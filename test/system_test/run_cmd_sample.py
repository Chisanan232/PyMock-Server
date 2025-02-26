import os
from typing import Optional

import pytest

from fake_api_server._utils.file.operation import YAML
from fake_api_server.model.api_config.apis import ResponseStrategy
from fake_api_server.model.command.rest_server._sample import (
    Mocked_APIs,
    Sample_Config_Value,
)

# isort: off
from ._base import SubCmdRestServerTestSuite

# isort: on


class TestSubCommandSample(SubCmdRestServerTestSuite):
    Terminate_Command_Running_When_Sniff_IP_Info: bool = False

    @property
    def options(self) -> str:
        return "sample --help"

    def _verify_running_output(self, cmd_running_result: str) -> None:
        self._should_contains_chars_in_result(cmd_running_result, "-h, --help")
        self._should_contains_chars_in_result(cmd_running_result, "-p, --print-sample")
        self._should_contains_chars_in_result(cmd_running_result, "-g, --generate-sample")
        self._should_contains_chars_in_result(cmd_running_result, "-o FILE_PATH, --output FILE_PATH")


class TestShowSampleConfiguration(SubCmdRestServerTestSuite):
    Terminate_Command_Running_When_Sniff_IP_Info: bool = False

    @property
    def options(self) -> str:
        return "sample -p"

    def _verify_running_output(self, cmd_running_result: str) -> None:
        for api_name, api_config in Mocked_APIs["apis"].items():
            self._should_contains_chars_in_result(cmd_running_result, api_name)
            self._should_contains_chars_in_result(cmd_running_result, api_config["url"])
            if api_name != "base":
                self._should_contains_chars_in_result(cmd_running_result, api_config["http"]["request"]["method"])
                api_response_config = api_config["http"]["response"]
                resp_value = api_response_config.get("value", None)
                if resp_value:
                    assert api_response_config["strategy"] in (
                        ResponseStrategy.STRING.value,
                        ResponseStrategy.FILE.value,
                    )
                    self._should_contains_chars_in_result(cmd_running_result, str(resp_value))
                else:
                    assert api_response_config["strategy"] == ResponseStrategy.OBJECT.value
                    assert api_response_config["properties"]


class TestGenerateSampleConfiguration(SubCmdRestServerTestSuite):
    Terminate_Command_Running_When_Sniff_IP_Info: bool = False
    _Default_Path: str = "sample-api.yaml"
    _Under_Test_Path: Optional[str] = None

    @property
    def options(self) -> str:
        return f"sample -g -o {self._Under_Test_Path}" if self._Under_Test_Path else "config -g"

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
