import copy
import logging
import sys
from argparse import ArgumentParser, Namespace
from typing import List, Optional, Tuple, Type, Union

from ..log import init_logger_config
from ..model import (
    ParserArguments,
    SubcmdAddArguments,
    SubcmdCheckArguments,
    SubcmdGetArguments,
    SubcmdPullArguments,
    SubcmdRunArguments,
    SubcmdSampleArguments,
    deserialize_args,
)
from .add import SubCmdAddComponent
from .check import SubCmdCheckComponent
from .component import BaseSubCmdComponent, NoSubCmdComponent
from .get import SubCmdGetComponent
from .options import MockAPICommandParser, SubCommand, SysArg
from .pull.component import SubCmdPullComponent
from .rest_server import SubCmdRestServerComponent
from .run import SubCmdRunComponent
from .sample.component import SubCmdSampleComponent

logger = logging.getLogger(__name__)

_COMMAND_CHAIN: List[Type["CommandProcessor"]] = []


def dispatch_command_processor() -> "CommandProcessor":
    cmd_chain = make_command_chain()
    assert len(cmd_chain) > 0, "It's impossible that command line processors list is empty."
    return cmd_chain[0].distribute()


def run_command_chain(parser: ArgumentParser, args: ParserArguments) -> None:
    cmd_chain = make_command_chain()
    assert len(cmd_chain) > 0, "It's impossible that command line processors list is empty."
    cmd_chain[0].process(parser=parser, args=args)


def make_command_chain() -> List["CommandProcessor"]:
    existed_subcmd: List[Optional[SysArg]] = []
    mock_api_cmd: List["CommandProcessor"] = []
    for cmd_cls in _COMMAND_CHAIN:
        cmd = cmd_cls()
        if cmd.responsible_subcommand in existed_subcmd:
            raise ValueError(f"The subcommand *{cmd.responsible_subcommand}* has been used. Please use other naming.")
        existed_subcmd.append(getattr(cmd, "responsible_subcommand"))
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
        _COMMAND_CHAIN.append(new_class)  # type: ignore
        return new_class


class CommandProcessor:
    responsible_subcommand: Optional[SysArg] = None
    deserialize_args: deserialize_args = deserialize_args()

    def __init__(self):
        self.mock_api_parser = MockAPICommandParser()
        self._current_index = 0

    @property
    def _next(self) -> "CommandProcessor":
        if self._current_index == len(_COMMAND_CHAIN):
            raise StopIteration("It cannot find the component which is responsible of this sub-command line.")
        cmd = _COMMAND_CHAIN[self._current_index]
        self._current_index += 1
        return cmd()

    @property
    def _subcmd_component(self) -> BaseSubCmdComponent:
        raise NotImplementedError

    def distribute(
        self, args: Optional[Union[Namespace, ParserArguments]] = None, cmd_index: int = 0
    ) -> "CommandProcessor":
        if self._is_responsible(subcmd=self.mock_api_parser.subcommand, args=args):
            return self
        else:
            self._current_index = cmd_index
            return self._next.distribute(args=args, cmd_index=self._current_index)

    def process(self, parser: ArgumentParser, args: ParserArguments, cmd_index: int = 0) -> None:
        self.distribute(args=args, cmd_index=cmd_index)._run(parser=parser, args=args)

    def parse(
        self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None, cmd_index: int = 0
    ) -> ParserArguments:
        return self.distribute(cmd_index=cmd_index)._parse_process(parser=parser, cmd_args=cmd_args)

    def _parse_process(self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None) -> ParserArguments:
        raise NotImplementedError

    def copy(self) -> "CommandProcessor":
        return copy.copy(self)

    def _is_responsible(
        self, subcmd: Optional[SysArg] = None, args: Optional[Union[Namespace, ParserArguments]] = None
    ) -> bool:
        if args:
            subcmd_key = args.subparser_structure.subcmd if isinstance(args, ParserArguments) else args.subcommand
            return subcmd_key == (self.responsible_subcommand.subcmd if self.responsible_subcommand else None)
        return (subcmd == self.responsible_subcommand) or (
            subcmd is None and self.responsible_subcommand == SysArg(subcmd="base")
        )

    def _run(self, parser: ArgumentParser, args: ParserArguments) -> None:
        init_logger_config()
        self._subcmd_component.process(parser=parser, args=args)

    def _parse_cmd_arguments(self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None) -> Namespace:
        return parser.parse_args(cmd_args)


BaseCommandProcessor: type = MetaCommand("BaseCommandProcessor", (CommandProcessor,), {})


class NoSubCmd(BaseCommandProcessor):
    responsible_subcommand: SysArg = SysArg(subcmd="base")

    @property
    def _subcmd_component(self) -> NoSubCmdComponent:
        return NoSubCmdComponent()

    def _parse_process(self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None) -> ParserArguments:
        return self._parse_cmd_arguments(parser, cmd_args)


class SubCmdRestServer(BaseCommandProcessor):
    responsible_subcommand: SysArg = SysArg(pre_subcmd=SysArg(subcmd="base"), subcmd=SubCommand.RestServer)

    @property
    def _subcmd_component(self) -> SubCmdRestServerComponent:
        return SubCmdRestServerComponent()

    def _parse_process(self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None) -> ParserArguments:
        return self._parse_cmd_arguments(parser, cmd_args)


class SubCmdRun(BaseCommandProcessor):
    responsible_subcommand: SysArg = SysArg(
        pre_subcmd=SysArg(pre_subcmd=SysArg(subcmd="base"), subcmd=SubCommand.RestServer), subcmd=SubCommand.Run
    )

    @property
    def _subcmd_component(self) -> SubCmdRunComponent:
        return SubCmdRunComponent()

    def _parse_process(self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None) -> SubcmdRunArguments:
        return deserialize_args.subcmd_run(self._parse_cmd_arguments(parser, cmd_args))


class SubCmdAdd(BaseCommandProcessor):
    responsible_subcommand: SysArg = SysArg(
        pre_subcmd=SysArg(pre_subcmd=SysArg(subcmd="base"), subcmd=SubCommand.RestServer), subcmd=SubCommand.Add
    )

    @property
    def _subcmd_component(self) -> SubCmdAddComponent:
        return SubCmdAddComponent()

    def _parse_process(self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None) -> SubcmdAddArguments:
        return deserialize_args.subcmd_add(self._parse_cmd_arguments(parser, cmd_args))


class SubCmdCheck(BaseCommandProcessor):
    responsible_subcommand: SysArg = SysArg(
        pre_subcmd=SysArg(pre_subcmd=SysArg(subcmd="base"), subcmd=SubCommand.RestServer), subcmd=SubCommand.Check
    )

    @property
    def _subcmd_component(self) -> SubCmdCheckComponent:
        return SubCmdCheckComponent()

    def _parse_process(self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None) -> SubcmdCheckArguments:
        return deserialize_args.subcmd_check(self._parse_cmd_arguments(parser, cmd_args))


class SubCmdGet(BaseCommandProcessor):
    responsible_subcommand: SysArg = SysArg(
        pre_subcmd=SysArg(pre_subcmd=SysArg(subcmd="base"), subcmd=SubCommand.RestServer), subcmd=SubCommand.Get
    )

    @property
    def _subcmd_component(self) -> SubCmdGetComponent:
        return SubCmdGetComponent()

    def _parse_process(self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None) -> SubcmdGetArguments:
        return deserialize_args.subcmd_get(self._parse_cmd_arguments(parser, cmd_args))


class SubCmdSample(BaseCommandProcessor):
    responsible_subcommand: SysArg = SysArg(
        pre_subcmd=SysArg(pre_subcmd=SysArg(subcmd="base"), subcmd=SubCommand.RestServer), subcmd=SubCommand.Sample
    )

    @property
    def _subcmd_component(self) -> SubCmdSampleComponent:
        return SubCmdSampleComponent()

    def _parse_process(self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None) -> SubcmdSampleArguments:
        cmd_options = self._parse_cmd_arguments(parser, cmd_args)
        try:
            return deserialize_args.subcmd_sample(cmd_options)
        except KeyError:
            logger.error(f"❌  Invalid value of option *--sample-config-type*: {cmd_options.sample_config_type}.")
            sys.exit(1)


class SubCmdPull(BaseCommandProcessor):
    responsible_subcommand: SysArg = SysArg(
        pre_subcmd=SysArg(pre_subcmd=SysArg(subcmd="base"), subcmd=SubCommand.RestServer), subcmd=SubCommand.Pull
    )

    @property
    def _subcmd_component(self) -> SubCmdPullComponent:
        return SubCmdPullComponent()

    def _parse_process(self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None) -> SubcmdPullArguments:
        return deserialize_args.subcmd_pull(self._parse_cmd_arguments(parser, cmd_args))
