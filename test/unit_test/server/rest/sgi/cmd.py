import re
from abc import ABCMeta, abstractmethod
from typing import Generic, Optional, Type, TypeVar
from unittest.mock import Mock, patch

import pytest

from fake_api_server.model.command.rest_server.cmd_args import SubcmdRunArguments
from fake_api_server.model.subcmd_common import SysArg
from fake_api_server.server.rest.sgi._model import Command, CommandOptions
from fake_api_server.server.rest.sgi.cmd import ASGIServer, BaseSGIServer, WSGIServer
from fake_api_server.server.rest.sgi.cmdoption import (
    ASGICmdOption,
    BaseCommandOption,
    WSGICmdOption,
)

# isort: off
from test._values import (
    SubCommand,
    _Bind_Host_And_Port,
    _Log_Level,
    _Test_Config,
    _Workers_Amount,
)

# isort: on


BaseSGICmdType = TypeVar("BaseSGICmdType", bound=BaseSGIServer)

app_path: str = "application instance path"
mock_parser_arg_obj = SubcmdRunArguments(
    # subparser_name=_Test_SubCommand_Run,
    subparser_structure=SysArg.parse([SubCommand.RestServer, SubCommand.Run]),
    config=_Test_Config,
    app_type="python web library name",
    bind=_Bind_Host_And_Port.value,
    workers=_Workers_Amount.value,
    log_level=_Log_Level.value,
)
mock_cmd_option_obj = CommandOptions(
    bind=_Bind_Host_And_Port.value, workers=_Workers_Amount.value, log_level=_Log_Level.value
)
mock_cmd_obj = Command(entry_point="SGI tool command", app=app_path, options=mock_cmd_option_obj)


@pytest.mark.parametrize(
    ("sgi_server", "app", "expected_err"),
    [
        (WSGIServer, None, ValueError),
        (WSGIServer, "", ValueError),
        (ASGIServer, None, ValueError),
        (ASGIServer, "", ValueError),
    ],
)
def test_invalid_app_path(sgi_server: Type[BaseSGIServer], app: Optional[str], expected_err: Exception):
    with pytest.raises(expected_err) as exc_info:
        sgi_server(app=app)
    assert re.search(r"cannot be None or empty", str(exc_info.value), re.IGNORECASE)


class BaseSGIServerTestSpec(metaclass=ABCMeta):
    @pytest.fixture(scope="function")
    @abstractmethod
    def sgi_cmd(self) -> Generic[BaseSGICmdType]:
        pass

    @patch("fake_api_server.server.rest.sgi.cmd.CommandOptions", return_value=mock_cmd_option_obj)
    @patch("fake_api_server.server.rest.sgi.cmd.Command", return_value=mock_cmd_obj)
    def test_generate(self, mock_command: Mock, mock_command_option: Mock, sgi_cmd: Generic[BaseSGICmdType]):
        command = sgi_cmd.generate(parser_args=mock_parser_arg_obj)

        mock_command.assert_called_once_with(
            entry_point=sgi_cmd.entry_point,
            app=app_path,
            options=mock_cmd_option_obj,
        )
        mock_command_option.assert_called_once_with(
            bind=sgi_cmd.options.bind(address=mock_parser_arg_obj.bind),
            workers=sgi_cmd.options.workers(w=mock_parser_arg_obj.workers),
            log_level=sgi_cmd.options.log_level(level=mock_parser_arg_obj.log_level),
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


class TestWSGIServer(BaseSGIServerTestSpec):
    @pytest.fixture(scope="function")
    def sgi_cmd(self) -> WSGIServer:
        return WSGIServer(app=app_path)

    @property
    def _expected_entry_point(self) -> str:
        return "gunicorn"

    @property
    def _expected_option_type(self) -> Type[WSGICmdOption]:
        return WSGICmdOption


class TestASGIServer(BaseSGIServerTestSpec):
    @pytest.fixture(scope="function")
    def sgi_cmd(self) -> ASGIServer:
        return ASGIServer(app=app_path)

    @property
    def _expected_entry_point(self) -> str:
        return "uvicorn --factory"

    @property
    def _expected_option_type(self) -> Type[ASGICmdOption]:
        return ASGICmdOption
