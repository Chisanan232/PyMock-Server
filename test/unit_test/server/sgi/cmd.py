from abc import ABCMeta, abstractmethod
from typing import Generic, Type, TypeVar
from unittest.mock import Mock, patch

import pytest

from pymock_api.server.sgi._model import Command, CommandOptions, ParserArguments
from pymock_api.server.sgi.cmd import BaseSGICmd, WSGICmd
from pymock_api.server.sgi.cmdoption import BaseCommandOption, WSGICmdOption

from ...._values import _Bind_Host_And_Port, _Log_Level, _Workers_Amount

BaseSGICmdType = TypeVar("BaseSGICmdType", bound=BaseSGICmd)

mock_parser_arg = Mock(
    ParserArguments(bind=_Bind_Host_And_Port.value, workers=_Workers_Amount.value, log_level=_Log_Level.value)
)
mock_cmd_option_obj = Mock(
    CommandOptions(bind=_Bind_Host_And_Port.value, workers=_Workers_Amount.value, log_level=_Log_Level.value)
)
mock_cmd_obj = Mock(Command(entry_point="gunicorn", options=mock_cmd_option_obj))


class BaseSGICmdTestSpec(metaclass=ABCMeta):
    @pytest.fixture(scope="function")
    @abstractmethod
    def sgi_cmd(self) -> Generic[BaseSGICmdType]:
        pass

    @patch("pymock_api.server.sgi.cmd.CommandOptions", return_value=mock_cmd_option_obj)
    @patch("pymock_api.server.sgi.cmd.Command", return_value=mock_cmd_obj)
    def test_generate(self, mock_command: Mock, mock_command_option: Mock, sgi_cmd: Generic[BaseSGICmdType]):
        command = sgi_cmd.generate(parser_args=mock_parser_arg)

        mock_command.assert_called_once_with(
            entry_point=sgi_cmd.entry_point,
            options=mock_cmd_option_obj,
        )
        mock_command_option.assert_called_once_with(
            bind=sgi_cmd.options.bind(address=mock_parser_arg.bind),
            workers=sgi_cmd.options.workers(w=mock_parser_arg.workers),
            log_level=sgi_cmd.options.log_level(level=mock_parser_arg.log_level),
        )
        assert isinstance(command, Command)

    def test_entry_point(self, sgi_cmd: Generic[BaseSGICmdType]):
        assert sgi_cmd.entry_point == self._expected_entry_point

    @property
    @abstractmethod
    def _expected_entry_point(self) -> str:
        pass

    def test_options(self, sgi_cmd: Generic[BaseSGICmdType]):
        assert isinstance(sgi_cmd.options, self._expected_option_type)

    @property
    @abstractmethod
    def _expected_option_type(self) -> Type[BaseCommandOption]:
        pass


class TestWSGICmd(BaseSGICmdTestSpec):
    @pytest.fixture(scope="function")
    def sgi_cmd(self) -> WSGICmd:
        return WSGICmd()

    @property
    def _expected_entry_point(self) -> str:
        return "gunicorn"

    @property
    def _expected_option_type(self) -> Type[WSGICmdOption]:
        return WSGICmdOption
