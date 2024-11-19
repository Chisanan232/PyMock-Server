from unittest.mock import MagicMock, Mock, patch

import pytest

from pymock_server.command._parser import MockAPICommandParser


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
