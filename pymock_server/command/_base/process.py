import copy
from argparse import ArgumentParser, Namespace
from typing import List, Optional, Tuple, Type

from pymock_server.command._parser import MockAPICommandParser
from pymock_server.command.subcommand import SubCommandLine
from pymock_server.log import init_logger_config
from pymock_server.model import ParserArguments, deserialize_args
from pymock_server.model.subcmd_common import SysArg

from .component import BaseSubCmdComponent

_COMMAND_CHAIN: List[Type["CommandProcessor"]] = []


class CommandProcessChain:
    @staticmethod
    def get() -> List[Type["CommandProcessor"]]:
        return _COMMAND_CHAIN

    @staticmethod
    def get_element(index: int) -> Type["CommandProcessor"]:
        return _COMMAND_CHAIN[index]

    @staticmethod
    def append(v: Type["CommandProcessor"]) -> None:
        assert issubclass(v, CommandProcessor)
        global _COMMAND_CHAIN
        return _COMMAND_CHAIN.append(v)

    @staticmethod
    def pop(index: int) -> None:
        global _COMMAND_CHAIN
        _COMMAND_CHAIN.pop(index)


class MetaCommand(type):
    """*The metaclass for options of PyMock-API command*

    content ...
    """

    def __new__(cls, name: str, bases: Tuple[type], attrs: dict):
        super_new = super().__new__
        parent = [b for b in bases if isinstance(b, MetaCommand)]
        if not parent:
            return super_new(cls, name, bases, attrs)
        new_class = super_new(cls, name, bases, attrs)
        CommandProcessChain.append(new_class)  # type: ignore
        return new_class


class CommandProcessor:
    responsible_subcommand: Optional[SysArg] = None
    deserialize_args: deserialize_args = deserialize_args()

    def __init__(self):
        self.mock_api_parser = MockAPICommandParser()
        self._current_index = 0

    @property
    def _next(self) -> "CommandProcessor":
        if self._current_index == len(CommandProcessChain.get()):
            raise StopIteration("It cannot find the component which is responsible of this sub-command line.")
        cmd = CommandProcessChain.get_element(self._current_index)
        self._current_index += 1
        return cmd()

    @property
    def _subcmd_component(self) -> BaseSubCmdComponent:
        raise NotImplementedError

    def distribute(self, cmd_index: int = 0) -> "CommandProcessor":
        if self._is_responsible(subcmd=self.mock_api_parser.subcommand):
            return self
        else:
            self._current_index = cmd_index
            return self._next.distribute(cmd_index=self._current_index)

    def process(self, parser: ArgumentParser, args: ParserArguments, cmd_index: int = 0) -> None:
        self.distribute(cmd_index=cmd_index)._run(parser=parser, args=args)

    def parse(
        self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None, cmd_index: int = 0
    ) -> ParserArguments:
        return self.distribute(cmd_index=cmd_index)._parse_process(parser=parser, cmd_args=cmd_args)

    def _parse_process(self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None) -> ParserArguments:
        raise NotImplementedError

    def copy(self) -> "CommandProcessor":
        return copy.copy(self)

    def _is_responsible(self, subcmd: Optional[SysArg] = None) -> bool:
        return (subcmd == self.responsible_subcommand) or (
            subcmd is None and self.responsible_subcommand == SysArg(subcmd=SubCommandLine.Base)
        )

    def _run(self, parser: ArgumentParser, args: ParserArguments) -> None:
        init_logger_config()
        self._subcmd_component.process(parser=parser, args=args)

    def _parse_cmd_arguments(self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None) -> Namespace:
        return parser.parse_args(cmd_args)


BaseCommandProcessor: type = MetaCommand("BaseCommandProcessor", (CommandProcessor,), {})