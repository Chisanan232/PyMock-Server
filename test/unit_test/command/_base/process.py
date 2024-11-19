import sys
from abc import ABCMeta, abstractmethod
from argparse import Namespace
from typing import Callable, List, Optional, Type, Union
from unittest.mock import MagicMock, patch

import pytest

from pymock_server.command._base.process import BaseCommandProcessor
from pymock_server.command.process import run_command_chain
from pymock_server.model import ParserArguments
from pymock_server.model.subcmd_common import SysArg


class BaseCommandProcessorTestSpec(metaclass=ABCMeta):
    @pytest.fixture(scope="function")
    @abstractmethod
    def cmd_ps(self) -> BaseCommandProcessor:
        pass

    @pytest.fixture(scope="function")
    def object_under_test(self, cmd_ps: BaseCommandProcessor) -> Callable:
        return cmd_ps.process

    @pytest.fixture(scope="function")
    def entry_point_under_test(self) -> Callable:
        return run_command_chain

    def test_with_command_processor(self, object_under_test: Callable, **kwargs):
        with patch.object(sys, "argv", self._given_command_line()):
            kwargs["cmd_ps"] = object_under_test
            self._test_process(**kwargs)

    @abstractmethod
    def _given_command_line(self) -> List[str]:
        pass

    def test_with_run_entry_point(self, entry_point_under_test: Callable, **kwargs):
        with patch.object(sys, "argv", self._given_command_line()):
            kwargs["cmd_ps"] = entry_point_under_test
            self._test_process(**kwargs)

    @abstractmethod
    def _test_process(self, **kwargs):
        pass

    def test_parse(self, cmd_ps: BaseCommandProcessor):
        args_namespace = self._given_cmd_args_namespace()
        cmd_ps._parse_cmd_arguments = MagicMock(return_value=args_namespace)

        api_parser = MagicMock()
        api_parser.subcommand = self._given_subcmd()
        cmd_ps.mock_api_parser = api_parser

        arguments = cmd_ps.parse(parser=cmd_ps.mock_api_parser.parse(), cmd_args=None)

        assert isinstance(arguments, self._expected_argument_type())

    @abstractmethod
    def _given_cmd_args_namespace(self) -> Namespace:
        pass

    @abstractmethod
    def _given_subcmd(self) -> Optional[SysArg]:
        pass

    @abstractmethod
    def _expected_argument_type(self) -> Type[Union[Namespace, ParserArguments]]:
        pass
