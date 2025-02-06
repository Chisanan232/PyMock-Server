import argparse
import copy
import re
from collections import namedtuple
from typing import Any, List, Optional, Tuple

from fake_api_server.command.subcommand import SubCommandLine, SubCommandSection
from fake_api_server.model.subcmd_common import (
    SubCmdParser,
    SubCmdParserAction,
    SubCommandAttr,
    SubParserAttr,
)

SUBCOMMAND: List[str] = [SubCommandLine.RestServer.value]
COMMAND_OPTIONS: List["MetaCommandOption"] = []


class SubCommandInterface:
    @staticmethod
    def get() -> List[str]:
        return SUBCOMMAND

    @staticmethod
    def extend(v: List[str]) -> None:
        assert isinstance(v, list)
        global SUBCOMMAND
        SUBCOMMAND.extend(v)


class CommandLineOptions:
    @staticmethod
    def get() -> List["MetaCommandOption"]:
        return COMMAND_OPTIONS

    @staticmethod
    def append(v: "MetaCommandOption") -> None:
        assert isinstance(v, MetaCommandOption)
        global COMMAND_OPTIONS
        COMMAND_OPTIONS.append(v)

    @staticmethod
    def pop(index: int) -> None:
        global COMMAND_OPTIONS
        COMMAND_OPTIONS.pop(index)


_ClsNamingFormat = namedtuple("_ClsNamingFormat", ["ahead", "tail"])
_ClsNamingFormat.ahead = "BaseSubCmd"
_ClsNamingFormat.tail = "Option"


class MetaCommandOption(type):
    """*The metaclass for options of PyFake-API-Server command*

    content ...
    """

    def __new__(cls, name: str, bases: Tuple[type], attrs: dict):
        super_new = super().__new__
        parent = [b for b in bases if isinstance(b, MetaCommandOption)]
        if not parent:
            return super_new(cls, name, bases, attrs)
        parent_is_subcmd = list(
            filter(
                lambda b: re.search(
                    re.escape(_ClsNamingFormat.ahead) + r"\w{1,10}" + re.escape(_ClsNamingFormat.tail), b.__name__
                ),
                bases,
            )
        )
        if parent_is_subcmd:
            SubCommandInterface.extend(
                [
                    b.__name__.replace(_ClsNamingFormat.ahead, "").replace(_ClsNamingFormat.tail, "").lower()
                    for b in bases
                ]
            )
        new_class = super_new(cls, name, bases, attrs)
        CommandLineOptions.append(new_class)
        return new_class


SUBCOMMAND_PARSER: List[SubCmdParser] = []


class CommandOption:
    """
    TODO: finish this docstring

    :param sub_cmd: test content ...
    :type sub_cmd: SubCommandAttr

    :param in_sub_cmd:
    :param sub_parser:

    :param cli_option:
    :type cli_option: str

    :param name:
    :param help_description:
    :param option_value_type:
    :param default_value:
    :param action:
    :param _options:
    """

    sub_cmd: Optional[SubCommandAttr] = None
    in_sub_cmd: SubCommandLine = SubCommandLine.Base
    sub_parser: Optional[SubParserAttr] = None
    cli_option: str
    name: Optional[str] = None
    help_description: str
    option_value_type: Optional[type] = None
    default_value: Optional[Any] = None
    action: Optional[str] = None
    _options: Optional[List[str]] = None

    _subparser: List[SubCmdParserAction] = []
    # _parser_of_subparser: List[SubCmdParser] = []    # Deprecated and use object *SUBCOMMAND_PARSER* to replace it

    @property
    def cli_option_name(self) -> Tuple[str, ...]:
        cli_option_sep_char: list = self.cli_option.split(",")
        if cli_option_sep_char and len(cli_option_sep_char) > 1:
            return tuple(map(lambda o: o.replace(" ", ""), self.cli_option.split(",")))
        return (self.cli_option,)

    @property
    def help_description_content(self) -> str:
        if not self.help_description:
            raise ValueError("An command option must have help description for developers to clear what it does.")
        all_help_desps: List[str] = [self.help_description.splitlines()[0]]

        if self.default_value is not None:
            default_value_str = f"[default: '{self.default_value}']"
            all_help_desps.append(default_value_str)

        if self._options:
            if not isinstance(self._options, list):
                raise TypeError(f"The attribute *{self.__class__.__name__}._options* should be a list type value.")
            all_options_value_str = ",".join([f"'{o}'" for o in self._options])
            all_options_str = f"[options: {all_options_value_str}]"
            all_help_desps.append(all_options_str)

        return " ".join(all_help_desps)

    @property
    def option_args(self) -> dict:
        cmd_option_args = {
            "dest": self.name,
            "help": self.help_description_content,
            "type": self.option_value_type,
            "default": self.default_value,
            "action": self.action or "store",
        }
        cmd_option_args_clone = copy.copy(cmd_option_args)
        for arg_name, arg_val in cmd_option_args.items():
            if not arg_val:
                cmd_option_args_clone.pop(arg_name)
        return cmd_option_args_clone

    def add_option(self, parser: argparse.ArgumentParser) -> None:
        try:
            self._dispatch_parser(parser).add_argument(*self.cli_option_name, **self.option_args)
        except argparse.ArgumentError as ae:
            if re.search(r"conflict", str(ae), re.IGNORECASE):
                return
            raise ae

    def copy(self) -> "CommandOption":
        return copy.copy(self)

    def _dispatch_parser(self, parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
        if self.sub_cmd and self.sub_parser:

            # initial the sub-command line parser collection first if it's empty.
            if self._find_subcmd_parser_action(SubCommandLine.Base) is None:
                sub_cmd: SubCommandAttr = SubCommandAttr(
                    title=SubCommandSection.Base,
                    dest=SubCommandLine.Base,
                    description="",
                    help="",
                )
                self._subparser.append(
                    SubCmdParserAction(
                        subcmd_name=SubCommandLine.Base,
                        subcmd_parser=parser.add_subparsers(
                            title=sub_cmd.title.value,
                            dest=sub_cmd.dest.value,
                            description=sub_cmd.description,
                            help=sub_cmd.help,
                        ),
                    ),
                )

            subcmd_parser_action = self._find_subcmd_parser_action(self.in_sub_cmd)

            def _add_new_subcommand_line() -> None:
                # Add parser first
                _base_subcmd_parser_action = subcmd_parser_action
                if _base_subcmd_parser_action is None:
                    _base_subcmd_parser_action = self._find_subcmd_parser_action(SubCommandLine.Base)
                _parser = _base_subcmd_parser_action.subcmd_parser.add_parser(  # type: ignore[union-attr]
                    name=self.sub_cmd.dest.value, help=self.sub_cmd.help  # type: ignore[union-attr]
                )
                global SUBCOMMAND_PARSER
                SUBCOMMAND_PARSER.append(
                    SubCmdParser(
                        in_subcmd=self.sub_cmd.dest,  # type: ignore[union-attr]
                        parser=_parser,
                        sub_parser=[],
                    )
                )

                # Add sub-command line parser
                assert self.sub_cmd is not None
                self._subparser.append(
                    SubCmdParserAction(
                        subcmd_name=self.in_sub_cmd,
                        subcmd_parser=_parser.add_subparsers(
                            title=self.sub_cmd.title.value,
                            dest=self.sub_cmd.dest.value,
                            description=self.sub_cmd.description,
                            help=self.sub_cmd.help,
                        ),
                    ),
                )

            if self.in_sub_cmd and subcmd_parser_action is None:
                _add_new_subcommand_line()
                subcmd_parser_action = self._find_subcmd_parser_action(self.in_sub_cmd)

            subcmd_parser_model = self._find_subcmd_parser(self.sub_parser.name)
            if subcmd_parser_model is None:
                assert subcmd_parser_action is not None
                parser = subcmd_parser_action.subcmd_parser.add_parser(
                    name=self.sub_parser.name.value, help=self.sub_parser.help
                )
                global SUBCOMMAND_PARSER
                SUBCOMMAND_PARSER.append(
                    SubCmdParser(
                        in_subcmd=self.sub_parser.name,
                        parser=parser,
                        sub_parser=[],
                    )
                )
            else:
                parser = subcmd_parser_model.parser
        return parser

    def _find_subcmd_parser(self, subcmd_name: SubCommandLine) -> Optional[SubCmdParser]:
        mapping_subcmd_parser = list(filter(lambda e: e.find(subcmd_name) is not None, SUBCOMMAND_PARSER))
        return mapping_subcmd_parser[0] if mapping_subcmd_parser else None

    def _find_subcmd_parser_action(self, subcmd_name: SubCommandLine) -> Optional[SubCmdParserAction]:
        mapping_subcmd_parser_action: List[SubCmdParserAction] = list(
            filter(lambda e: e.subcmd_name is subcmd_name, self._subparser)
        )
        return mapping_subcmd_parser_action[0] if mapping_subcmd_parser_action else None
