import json
from abc import ABCMeta, abstractmethod
from typing import Type
from unittest.mock import patch

from yaml import dump

try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper  # type: ignore

import pytest

from pymock_api.command.get.component import (
    APIInfoDisplayChain,
    DisplayAsJsonFormat,
    DisplayAsTextFormat,
    DisplayAsYamlFormat,
    SubCmdGetComponent,
    _BaseDisplayFormat,
)
from pymock_api.model import APIConfig
from pymock_api.model.api_config import MockAPI
from pymock_api.model.cmd_args import SubcmdGetArguments
from pymock_api.model.enums import Format

from ...._values import _Test_HTTP_Method, _Test_URL, _TestConfig


class TestSubCmdGetComponent:
    @pytest.fixture(scope="class")
    def component(self) -> SubCmdGetComponent:
        return SubCmdGetComponent()

    @pytest.mark.parametrize(
        ("display_as_format", "expected_object", "expected_exit_code"),
        [
            (Format.TEXT, DisplayAsTextFormat, 0),
            (Format.YAML, DisplayAsYamlFormat, 0),
            (Format.JSON, DisplayAsJsonFormat, 0),
        ],
    )
    def test_component_with_valid_format(
        self,
        display_as_format: Format,
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


class TestAPIInfoDisplayChain:
    @pytest.fixture(scope="function")
    def chain(self) -> APIInfoDisplayChain:
        return APIInfoDisplayChain()

    def test__get_display_members(self, chain: APIInfoDisplayChain):
        displays = chain._get_display_members()
        assert isinstance(displays, dict)
        assert len(displays) == 3

    def test_next(self, chain: APIInfoDisplayChain):
        assert (
            chain.current_display.__class__.__name__ == chain.displays[chain.current_display.format].__class__.__name__
        )
        next_display = chain.next()
        assert next_display.__class__.__name__ == chain.displays[next_display.format].__class__.__name__
        assert (
            chain.current_display.__class__.__name__ == chain.displays[chain.current_display.format].__class__.__name__
        )

    @pytest.mark.parametrize(
        ("ut_format", "expected_instance"),
        [
            (Format.TEXT, DisplayAsTextFormat),
            (Format.YAML, DisplayAsYamlFormat),
            (Format.JSON, DisplayAsJsonFormat),
        ],
    )
    def test_dispatch_with_valid_format(
        self, ut_format: Format, expected_instance: Type[_BaseDisplayFormat], chain: APIInfoDisplayChain
    ):
        display_as_format = chain.dispatch(format=ut_format)
        assert isinstance(display_as_format, expected_instance)

    def test_dispatch_with_invalid_format(self, chain: APIInfoDisplayChain):
        with pytest.raises(SystemExit) as exc_info:
            chain.dispatch(format="invalid format")
        assert str(exc_info.value) == "1"

    def test_show(self, chain: APIInfoDisplayChain):
        pass


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
        return Format.YAML

    @property
    def _expected_format_value(self) -> str:
        return dump(data=_TestConfig.Mock_API, Dumper=Dumper)


class TestDisplayAsJsonFormat(DisplayFormatTestSpec):
    @pytest.fixture(scope="class")
    def formatter(self) -> DisplayAsJsonFormat:
        return DisplayAsJsonFormat()

    @property
    def _expected_format(self) -> str:
        return Format.JSON

    @property
    def _expected_format_value(self) -> str:
        return json.dumps(_TestConfig.Mock_API, indent=4)
