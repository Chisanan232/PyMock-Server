import re
from unittest.mock import MagicMock, Mock, patch

import pytest

from pymock_server.command._parser import MockAPICommandParser
from pymock_server.exceptions import NotFoundCommandLine


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

    def test_prop_subcommand(self, parser: MockAPICommandParser):
        with patch("sys.argv", ["rest-server", "invalid"]):
            with pytest.raises(NotFoundCommandLine) as exc_info:
                parser.subcommand
            re.search(
                r"Cannot map.{0, 64}subcommand line.{0, 64}" + re.escape("invalid"), str(exc_info.value), re.IGNORECASE
            )
