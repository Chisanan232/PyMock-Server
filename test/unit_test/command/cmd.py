import argparse
import re
from typing import Optional
from unittest.mock import MagicMock, Mock, patch

import pytest

from pymock_api.command.cmd import BaseCmdOption, MockAPICommandParser, make_options


def test_make_options():
    options = make_options()
    assert options


class TestMockAPICommandParser:
    @pytest.fixture(scope="function")
    def parser(self) -> MockAPICommandParser:
        return MockAPICommandParser()

    @patch("argparse.ArgumentParser")
    def test_parse_when_not_have_parser(self, mock_argparser_obj: Mock, parser: MockAPICommandParser):
        mock_argparser_obj.add_argument = MagicMock()

        mock_api_parser = parser.parse()

        assert mock_api_parser is parser.parser
        mock_argparser_obj.assert_called_once()


class TestCommandOption:
    @pytest.fixture(scope="function")
    def one_option(self) -> BaseCmdOption:
        class FakeOneOption(BaseCmdOption):
            cli_option: str = "--one-fake"
            help_description: str = "Fake option for test"

        return FakeOneOption()

    @pytest.fixture(scope="function")
    def option(self) -> BaseCmdOption:
        class FakeOption(BaseCmdOption):
            cli_option: str = "-f,--fake"
            help_description: str = "Fake option for test"

        return FakeOption()

    def test_instantiate_object_without_cli_option(self):
        class FakeNothingOption(BaseCmdOption):
            cli_option: str = ""
            help_description: str = ""

        with pytest.raises(ValueError) as exc_info:
            make_options()
        assert re.search(r"\*cli_option\* cannot be None or empty value", str(exc_info), re.IGNORECASE)

        # Remove the invalid option object of the list to let test could be run finely.
        from pymock_api.command.cmd import COMMAND_OPTIONS

        COMMAND_OPTIONS.pop(-1)

    def test_cli_option_name_with_one(self, one_option: BaseCmdOption):
        assert one_option.cli_option_name == ("--one-fake",)

    def test_cli_option_name_with_multiple(self, option: BaseCmdOption):
        assert option.cli_option_name == ("-f", "--fake")

    @pytest.mark.parametrize(
        ("help_descr", "default_value", "option_values"),
        [
            ["Message for PyTest", None, None],
            ["Message for PyTest", "default value", None],
            ["Message for PyTest", None, ["Valid Options"]],
            ["Message for PyTest", "default value", ["Valid Options"]],
        ],
    )
    def test_help_description_content(
        self,
        option: BaseCmdOption,
        help_descr: Optional[str],
        default_value: Optional[str],
        option_values: Optional[str],
    ):
        self._given_default_and_options(
            option, help_descr=help_descr, default_value=default_value, option_values=option_values
        )
        self._should_be_satisfied_help_format(option)

    @pytest.mark.parametrize(
        ("help_descr", "default_value", "option_values", "expected_error"),
        [
            [None, "Any value includes None", "Any value includes None", ValueError],
            ["Message for PyTest", None, "Invalid Options", TypeError],
        ],
    )
    def test_help_description_content_with_invalid_options(
        self,
        option: BaseCmdOption,
        help_descr: Optional[str],
        default_value: Optional[str],
        option_values: Optional[str],
        expected_error: Exception,
    ):
        self._given_default_and_options(
            option, help_descr=help_descr, default_value=default_value, option_values=option_values
        )
        self._should_raise_exception(option, expected_error)

    @patch.object(argparse.ArgumentParser, "add_argument")
    def test_add_option(self, mock_argparser: Mock, option: BaseCmdOption):
        mock_argparser.add_argument = MagicMock()
        option.help_description = "Message for PyTest"
        option.add_option(mock_argparser)
        mock_argparser.add_argument.assert_called_once()

    @patch.object(argparse.ArgumentParser, "add_argument")
    def test_bad_add_option(self, mock_argparser: Mock, option: BaseCmdOption):
        mock_argparser.add_argument = MagicMock()
        mock_argparser.add_argument.side_effect = argparse.ArgumentError(None, "Error for PyTest")
        option.help_description = "Message for PyTest"
        with pytest.raises(argparse.ArgumentError) as exc_info:
            option.add_option(mock_argparser)
        mock_argparser.add_argument.assert_called_once()
        assert str(exc_info.value) == "Error for PyTest"

    @patch("copy.copy")
    def test_copy(self, mock_copy: Mock, option: BaseCmdOption):
        option.copy()
        mock_copy.assert_called_once_with(option)

    def _given_default_and_options(
        self,
        option: BaseCmdOption,
        help_descr: Optional[str],
        default_value: Optional[str],
        option_values: Optional[str],
    ) -> None:
        option.help_description = help_descr
        option.default_value = default_value
        setattr(option, "_options", option_values)

    def _should_be_satisfied_help_format(self, option) -> None:
        chk_chars = re.search(
            re.escape(option.help_description) + r"?(.\[default:.{0,256}\]){0,1}?(.\[options:.{0,256}\]){0,1}",
            option.help_description_content,
            re.IGNORECASE,
        )
        assert chk_chars

    def _should_raise_exception(self, option: BaseCmdOption, expected_error: Exception) -> None:
        help_desc = None
        with pytest.raises(expected_error):
            help_desc = option.help_description_content
        assert help_desc is None
