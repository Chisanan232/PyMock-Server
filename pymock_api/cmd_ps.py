import copy
import os
import re
from argparse import ArgumentParser, Namespace
from typing import List, Optional, Tuple, Type

from ._utils import YAML, import_web_lib
from .cmd import MockAPICommandParser, SubCommand
from .exceptions import InvalidAppType, NoValidWebLibrary
from .model import (
    ParserArguments,
    SubcmdConfigArguments,
    SubcmdRunArguments,
    deserialize_args,
)
from .model._sample import Sample_Config_Value
from .server import BaseSGIServer, setup_asgi, setup_wsgi

_COMMAND_CHAIN: List[Type["BaseCommandProcessor"]] = []


def dispatch_command_processor() -> "BaseCommandProcessor":
    cmd_chain = make_command_chain()
    return cmd_chain[0].distribute()


def run_command_chain(args: ParserArguments) -> None:
    cmd_chain = make_command_chain()
    cmd_chain[0].process(args)


def make_command_chain() -> List["BaseCommandProcessor"]:
    existed_subcmd: List[str] = []
    mock_api_cmd: List["BaseCommandProcessor"] = []
    for cmd_cls in _COMMAND_CHAIN:
        cmd = cmd_cls()
        if cmd.responsible_subcommand in existed_subcmd:
            raise ValueError(f"The subcommand *{cmd.responsible_subcommand}* has been used. Please use other naming.")
        existed_subcmd.append(cmd.responsible_subcommand)
        mock_api_cmd.append(cmd.copy())
    return mock_api_cmd


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
        _COMMAND_CHAIN.append(new_class)
        return new_class


class BaseCommandProcessor:
    responsible_subcommand: str = None

    def __init__(self):
        self.mock_api_parser = MockAPICommandParser()
        self._current_index = 0

    @property
    def _next(self) -> "BaseCommandProcessor":
        if self._current_index == len(_COMMAND_CHAIN):
            raise StopIteration
        cmd = _COMMAND_CHAIN[self._current_index]
        self._current_index += 1
        return cmd()

    def distribute(self, args: ParserArguments = None, cmd_index: int = 0) -> "BaseCommandProcessor":
        if self._is_responsible(subcmd=self.mock_api_parser.subcommand, args=args):
            return self
        else:
            self._current_index = cmd_index
            return self._next.distribute(args=args, cmd_index=self._current_index)

    def process(self, args: ParserArguments, cmd_index: int = 0) -> None:
        self.distribute(args=args, cmd_index=cmd_index)._run(args)

    def parse(
        self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None, cmd_index: int = 0
    ) -> ParserArguments:
        return self.distribute(cmd_index=cmd_index)._parse_process(parser=parser, cmd_args=cmd_args)

    def _parse_process(self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None) -> ParserArguments:
        raise NotImplementedError

    def copy(self) -> "BaseCommandProcessor":
        return copy.copy(self)

    def _is_responsible(self, subcmd: str = None, args: ParserArguments = None) -> bool:
        if args:
            return args.subparser_name == self.responsible_subcommand
        return subcmd == self.responsible_subcommand

    def _run(self, args: ParserArguments) -> None:
        raise NotImplementedError

    def _parse_cmd_arguments(self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None) -> Namespace:
        return parser.parse_args(cmd_args)


BaseCommandProcessor = MetaCommand("BaseCommandProcessor", (BaseCommandProcessor,), {})


class NoSubCmd(BaseCommandProcessor):
    responsible_subcommand: str = None

    def _parse_process(self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None) -> ParserArguments:
        return self._parse_cmd_arguments(parser, cmd_args)

    def _run(self, args: ParserArguments) -> None:
        pass


class SubCmdRun(BaseCommandProcessor):
    responsible_subcommand = SubCommand.Run

    def __init__(self):
        super().__init__()
        self._server_gateway: BaseSGIServer = None

    def _parse_process(self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None) -> SubcmdRunArguments:
        return deserialize_args.subcmd_run(self._parse_cmd_arguments(parser, cmd_args))

    def _run(self, args: SubcmdRunArguments) -> None:
        self._process_option(args)
        self._server_gateway.run(args)

    def _process_option(self, parser_options: SubcmdRunArguments) -> None:
        # Note: It's possible that it should separate the functions to be multiple objects to implement and manage the
        # behaviors of command line with different options.
        # Handle *config*
        os.environ["MockAPI_Config"] = parser_options.config

        # Handle *app-type*
        self._initial_server_gateway(lib=parser_options.app_type)

    def _initial_server_gateway(self, lib: str) -> None:
        if re.search(r"auto", lib, re.IGNORECASE):
            web_lib = import_web_lib.auto_ready()
            if not web_lib:
                raise NoValidWebLibrary
            self._initial_server_gateway(lib=web_lib)
        elif re.search(r"flask", lib, re.IGNORECASE):
            self._server_gateway = setup_wsgi()
        elif re.search(r"fastapi", lib, re.IGNORECASE):
            self._server_gateway = setup_asgi()
        else:
            raise InvalidAppType


class SubCmdConfig(BaseCommandProcessor):
    responsible_subcommand = SubCommand.Config

    def _parse_process(self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None) -> SubcmdConfigArguments:
        return deserialize_args.subcmd_config(self._parse_cmd_arguments(parser, cmd_args))

    def _run(self, args: SubcmdConfigArguments) -> None:
        yaml: YAML = None
        sample_data: str = None
        if args.print_sample or args.generate_sample:
            yaml = YAML()
            sample_data = yaml.serialize(config=Sample_Config_Value)
        if args.print_sample:
            print(f"It will write below content into file {args.sample_output_path}:")
            print(f"{sample_data}")
        if args.generate_sample:
            yaml.write(path=args.sample_output_path, config=sample_data)
