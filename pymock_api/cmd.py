"""*The command attributes of PyMock-API*

This module processes the features about command to let *PyMock-API* could be used and run through command line. In
briefly, It has below major features:

* Parser of *PyMock-API* command line
  Handling parsing the arguments of command line.

* Options of *PyMock-API* command
  Handling all the details of command options, i.e., what the option format should be used in command line, the help
  description of what this option does, etc.

"""

import argparse
import copy
import re
import sys
from collections import namedtuple
from typing import Dict, List, Optional, Tuple, Type

from .__pkg_info__ import __version__

SUBCOMMAND: List[str] = []
COMMAND_OPTIONS: List[Type["CommandOption"]] = []


def get_all_subcommands() -> List[str]:
    return list(set(SUBCOMMAND))


def make_options() -> List["CommandOption"]:
    """Initial and generate all options for parser to use and organize.

    Returns:
        list: A list object of **CommandOption** objects.

    """
    mock_api_cmd_options: List["CommandOption"] = []
    for option_cls in COMMAND_OPTIONS:
        option = option_cls()
        mock_api_cmd_options.append(option.copy())
    return mock_api_cmd_options


class MockAPICommandParser:
    """*The parser of PyMock-API command line*

    Handling the command line about options includes what options PyMock-API could use and what values of entry command
    line.
    """

    def __init__(self):
        self._prog = "pymock-api"
        self._usage = "mock-api" if self.is_running_subcmd else "mock-api [SUBCOMMAND] [OPTIONS]"
        self._description = "Mock APIs"
        self._parser_args: Dict[str, str] = {
            "prog": self._prog,
            "usage": self._usage,
            "description": self._description,
        }

        self._parser = None

        self._command_options: List["CommandOption"] = make_options()

    @property
    def parser(self) -> argparse.ArgumentParser:
        return self._parser

    @property
    def subcommand(self) -> Optional[str]:
        if self.is_running_subcmd:
            return sys.argv[1]
        return None

    @property
    def is_running_subcmd(self) -> bool:
        return True in [arg in get_all_subcommands() for arg in sys.argv]

    def parse(self) -> argparse.ArgumentParser:
        """Initial and parse the arguments of current running command line.

        Returns:
            A parser object which is *argparse.ArgumentParser* type.

        """
        if not self.parser:
            self._parser = argparse.ArgumentParser(**self._parser_args)

        for option in self._command_options:
            option.add_option(parser=self.parser)

        return self.parser


SubCommand: str = "subcommand"
SubParserAttr = namedtuple("SubParserAttr", ["title", "dest", "description", "help"])


class MetaCommandOption(type):
    """*The metaclass for options of PyMock-API command*

    content ...
    """

    def __new__(cls, name: str, bases: Tuple[type], attrs: dict):
        super_new = super().__new__
        parent = [b for b in bases if isinstance(b, MetaCommandOption)]
        is_subcommand = re.search(r"'cli_option': '" + re.escape(SubCommand) + "'", str(attrs), re.IGNORECASE)
        if not parent or is_subcommand:
            return super_new(cls, name, bases, attrs)
        parent_is_subcmd = list(filter(lambda b: re.search(r"SubCommand\w{1,10}Option", b.__name__), bases))
        if parent_is_subcmd:
            SUBCOMMAND.extend([b.__name__.replace("SubCommand", "").replace("Option", "").lower() for b in bases])
        new_class = super_new(cls, name, bases, attrs)
        COMMAND_OPTIONS.append(new_class)
        return new_class


class CommandOption:

    sub_cmd: SubParserAttr = None
    cli_option: str = None
    name: str = None
    help_description: str = None
    option_value_type: type = None
    default_value: type = None
    action: str = None
    _options: List[str] = None

    _cmd_subparser: Dict[str, argparse._ArgumentGroup] = {}

    def __init__(self):
        if not self.cli_option:
            raise ValueError(f"The object {self.__class__}'s attribute *cli_option* cannot be None or empty value.")

    @property
    def cli_option_name(self) -> Tuple[str]:
        cli_option_sep_char: list = self.cli_option.split(",")
        if cli_option_sep_char and len(cli_option_sep_char) > 1:
            return tuple(map(lambda o: o.replace(" ", ""), self.cli_option.split(",")))
        return (self.cli_option,)

    @property
    def help_description_content(self) -> str:
        if not self.help_description:
            raise ValueError("An command option must have help description for developers to clear what it does.")
        all_help_desps: List[str] = [self.help_description.splitlines()[0]]

        if self.default_value:
            default_value_str = f"[default: '{self.default_value}']"
            all_help_desps.append(default_value_str)

        if self._options:
            if not isinstance(self._options, list):
                raise TypeError(f"The attribute *{self.__class__.__name__}._options* should be a list type value.")
            all_options_value_str = ",".join([f"'{o}'" for o in self._options])
            all_options_str = f"[options: {all_options_value_str}]"
            all_help_desps.append(all_options_str)

        return " ".join(all_help_desps)

    def add_option(self, parser: argparse.ArgumentParser) -> None:
        cmd_option_args = {
            "dest": self.name,
            "help": self.help_description_content,
            "type": self.option_value_type or str,
            "default": self.default_value,
            "action": self.action or "store",
        }
        if self.sub_cmd:
            if self.sub_cmd.dest not in self._cmd_subparser.keys():
                cmd_subparser = parser.add_subparsers(
                    title=self.sub_cmd.title,
                    dest=self.sub_cmd.dest,
                    description=self.sub_cmd.description,
                    help=self.sub_cmd.help,
                )
                self._cmd_subparser[self.sub_cmd.dest] = cmd_subparser.add_parser(self.sub_cmd.dest)
            self._cmd_subparser[self.sub_cmd.dest].add_argument(*self.cli_option_name, **cmd_option_args)
        else:
            parser.add_argument(*self.cli_option_name, **cmd_option_args)

    def copy(self) -> "CommandOption":
        return copy.copy(self)


CommandOption = MetaCommandOption("CommandOption", (CommandOption,), {})


class Version(CommandOption):

    cli_option: str = "-v, --version"
    name: str = "version"
    help_description: str = "The version info of PyMock-API."
    default_value: type = argparse.SUPPRESS
    action: str = "version"
    _version_output: str = "%(prog)s (version " + __version__ + ")\n"

    def add_option(self, parser: argparse.ArgumentParser) -> None:
        # TODO: Should get relation tools or library's version, e.g., flask, gunicorn, etc.
        cmd_option_args = {
            "dest": self.name,
            "help": self.help_description,
            "default": self.default_value,
            "action": self.action or "store",
            "version": self._version_output,
        }
        parser.add_argument(*self.cli_option_name, **cmd_option_args)


class SubCommandRunOption(CommandOption):

    sub_cmd: SubParserAttr = SubParserAttr(
        title="Running an application",
        dest="run",
        description="",
        help="Set up APIs and start to run an application.",
    )
    cli_option: str = SubCommand


class WebAppType(SubCommandRunOption):

    cli_option: str = "--app-type"
    name: str = "app_type"
    help_description: str = "Which Python web framework it should use to set up web server for mocking APIs."
    default_value: str = "flask"
    _options: List[str] = ["flask"]


class Config(SubCommandRunOption):

    cli_option: str = "-c, --config"
    name: str = "config"
    help_description: str = "The configuration of tool PyMock-API."
    default_value: str = "api.yaml"


class Bind(SubCommandRunOption):

    cli_option: str = "-b, --bind"
    name: str = "bind"
    help_description: str = "The socket to bind."
    default_value: str = "127.0.0.1:9672"


class Workers(SubCommandRunOption):

    cli_option: str = "-w, --workers"
    name: str = "workers"
    help_description: str = "The workers amount."
    default_value: int = 1


class LegLevel(SubCommandRunOption):

    cli_option: str = "--log-level"
    name: str = "log_level"
    help_description: str = "The log level."
    default_value: str = "info"
    _options: List[str] = ["critical", "error", "warning", "info", "debug", "trace"]
