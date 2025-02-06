import re
from unittest.mock import MagicMock, Mock, patch

import pytest

from fake_api_server.command._parser import FakeAPIServerCommandParser
from fake_api_server.exceptions import NotFoundCommandLine


class TestFakeAPIServerCommandParser:
    @pytest.fixture(scope="function")
    def parser(self) -> FakeAPIServerCommandParser:
        return FakeAPIServerCommandParser()

    @patch("argparse.ArgumentParser")
    def test_parse_when_not_have_parser(self, mock_argparser_obj: Mock, parser: FakeAPIServerCommandParser):
        mock_argparser_obj.add_argument = MagicMock()

        fake_api_server_parser = parser.parse()

        assert fake_api_server_parser is parser.parser
        mock_argparser_obj.assert_called_once()

    def test_prop_subcommand(self, parser: FakeAPIServerCommandParser):
        with patch("sys.argv", ["rest-server", "invalid"]):
            with pytest.raises(NotFoundCommandLine) as exc_info:
                parser.subcommand
            re.search(
                r"Cannot map.{0, 64}subcommand line.{0, 64}" + re.escape("invalid"), str(exc_info.value), re.IGNORECASE
            )
