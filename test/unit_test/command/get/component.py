from abc import ABCMeta, abstractmethod
from typing import Optional
from unittest.mock import patch

from yaml import dump

try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper  # type: ignore

import pytest

from pymock_api.command.get.component import (
    DisplayAsTextFormat,
    DisplayAsYamlFormat,
    SubCmdGetComponent,
    _BaseDisplayFormat,
)
from pymock_api.model.api_config import APIConfig, MockAPI
from pymock_api.model.cmd_args import SubcmdGetArguments

from ...._values import _Test_HTTP_Method, _Test_URL, _TestConfig


class TestSubCmdGetComponent:
    @pytest.fixture(scope="class")
    def component(self) -> SubCmdGetComponent:
        return SubCmdGetComponent()

    @pytest.mark.parametrize(
        ("display_as_format", "expected_object", "expected_exit_code"),
        [
            ("text", DisplayAsTextFormat, 0),
            ("yaml", DisplayAsYamlFormat, 0),
            ("json", None, 0),
        ],
    )
    def test_component_with_valid_format(
        self,
        display_as_format: str,
        expected_object: _BaseDisplayFormat,
        expected_exit_code: int,
        component: SubCmdGetComponent,
    ):
        with patch("pymock_api.command.get.component.load_config") as mock_load_config:
            mock_load_config.return_value = APIConfig().deserialize(data=_TestConfig.API_Config)
            with patch.object(expected_object, "display") as mock_formatter_display:
                with pytest.raises(SystemExit) as exc_info:
                    subcmd_get_args = SubcmdGetArguments(
                        subparser_name="get",
                        config_path="config path",
                        show_detail=True,
                        show_as_format=display_as_format,
                        api_path=_Test_URL,
                        http_method=_Test_HTTP_Method,
                    )
                    component.process(subcmd_get_args)

                assert str(exc_info.value) == str(expected_exit_code)
                mock_formatter_display.assert_called_once_with(MockAPI().deserialize(data=_TestConfig.Mock_API))

    def test_component_with_invalid_format(self, component: SubCmdGetComponent):
        with patch("pymock_api.command.get.component.load_config") as mock_load_config:
            mock_load_config.return_value = APIConfig().deserialize(data=_TestConfig.API_Config)
            with pytest.raises(SystemExit) as exc_info:
                subcmd_get_args = SubcmdGetArguments(
                    subparser_name="get",
                    config_path="config path",
                    show_detail=True,
                    show_as_format="invalid format",
                    api_path=_Test_URL,
                    http_method=_Test_HTTP_Method,
                )
                component.process(subcmd_get_args)

            assert str(exc_info.value) == "1"


class DisplayFormatTestSpec(metaclass=ABCMeta):
    @pytest.fixture(scope="class")
    @abstractmethod
    def formatter(self) -> _BaseDisplayFormat:
        pass

    def test_format(self, formatter: _BaseDisplayFormat):
        assert formatter.format == self._expected_format

    @property
    @abstractmethod
    def _expected_format(self) -> str:
        pass

    def test_display(self, formatter: _BaseDisplayFormat):
        with patch("builtins.print") as mock_print:
            formatter.display(self._given_mock_api())
            mock_print(self._expected_format_value)

    def _given_mock_api(self) -> MockAPI:
        return MockAPI().deserialize(_TestConfig.Mock_API)

    @property
    @abstractmethod
    def _expected_format_value(self) -> str:
        pass


class TestDisplayAsYamlFormat(DisplayFormatTestSpec):
    @pytest.fixture(scope="class")
    def formatter(self) -> DisplayAsYamlFormat:
        return DisplayAsYamlFormat()

    @property
    def _expected_format(self) -> str:
        return "yaml"

    @property
    def _expected_format_value(self) -> str:
        return dump(data=_TestConfig.Mock_API, Dumper=Dumper)
