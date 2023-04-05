import copy
import os
import re
from argparse import ArgumentParser
from typing import List, Tuple, Type

from ._utils import YAML
from .cmd import MockAPICommandParser, SubCommand
from .model import ParserArguments, SubcmdConfigArguments, SubcmdRunArguments
from .model._sample import Sample_Config_Value
from .server import BaseSGIServer, setup_asgi, setup_wsgi

_COMMAND_CHAIN: List[Type["BaseCommandProcessor"]] = []


def run_command_chain(args: ParserArguments) -> None:
    cmd_chain = make_command_chain()
    cmd_chain[0].receive(args)


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
        self._current_index = 0

    @property
    def next(self) -> "BaseCommandProcessor":
        if self._current_index == len(_COMMAND_CHAIN):
            raise StopIteration
        cmd = _COMMAND_CHAIN[self._current_index]
        self._current_index += 1
        return cmd()

    def receive(self, args: ParserArguments, cmd_index: int = 0) -> None:
        if self.is_responsible(args):
            self.run(args)
        else:
            self._current_index = cmd_index
            self.dispatch_to_next(args)

    def is_responsible(self, args: ParserArguments) -> bool:
        return args.subparser_name == self.responsible_subcommand

    def run(self, args: ParserArguments) -> None:
        raise NotImplementedError

    def dispatch_to_next(self, args: ParserArguments) -> None:
        self.next.receive(args, cmd_index=self._current_index)

    def copy(self) -> "BaseCommandProcessor":
        return copy.copy(self)


BaseCommandProcessor = MetaCommand("BaseCommandProcessor", (BaseCommandProcessor,), {})


class NoSubCmd(BaseCommandProcessor):

    responsible_subcommand: str = None

    def run(self, args: ParserArguments) -> None:
        pass


class SubCmdRun(BaseCommandProcessor):

    responsible_subcommand = SubCommand.Run

    def __init__(self):
        super().__init__()
        self.mock_api_parser = MockAPICommandParser()
        self.cmd_parser: ArgumentParser = self.mock_api_parser.parse()
        self._server_gateway: BaseSGIServer = None

    def run(self, args: SubcmdRunArguments) -> None:
        self._process_option(args)
        self._server_gateway.run(args)

    def _process_option(self, parser_options: SubcmdRunArguments) -> None:
        # Note: It's possible that it should separate the functions to be multiple objects to implement and manage the
        # behaviors of command line with different options.
        # Handle *config*
        os.environ["MockAPI_Config"] = parser_options.config

        # Handle *app-type*
        if re.search(r"flask", parser_options.app_type, re.IGNORECASE):
            self._server_gateway = setup_wsgi()
        elif re.search(r"fastapi", parser_options.app_type, re.IGNORECASE):
            self._server_gateway = setup_asgi()
        else:
            raise ValueError("Invalid value at argument *app-type*. It only supports 'flask' or 'fastapi' currently.")


class SubCmdConfig(BaseCommandProcessor):

    responsible_subcommand = SubCommand.Config

    def run(self, args: SubcmdConfigArguments) -> None:
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
