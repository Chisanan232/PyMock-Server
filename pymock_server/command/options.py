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
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from ..__pkg_info__ import __version__


@dataclass
class SubCommand:
    Base: str = "subcommand"
    RestServer: str = "rest-server"
    Run: str = "run"
    Add: str = "add"
    Check: str = "check"
    Get: str = "get"
    Sample: str = "sample"
    Pull: str = "pull"


SUBCOMMAND: List[str] = [SubCommand.RestServer]
COMMAND_OPTIONS: List["MetaCommandOption"] = []


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
        if not option.cli_option:
            raise ValueError(f"The object {option.__class__}'s attribute *cli_option* cannot be None or empty value.")
        mock_api_cmd_options.append(option.copy())
    return mock_api_cmd_options


@dataclass
class SysArg:
    subcmd: str
    pre_subcmd: Optional["SysArg"] = None

    @staticmethod
    def parse(args: List[str]) -> "SysArg":
        if not args:
            return SysArg(subcmd="base")

        no_pyfile_subcmds = list(filter(lambda a: not re.search(r".{1,1024}.py", a), args))
        subcmds = []
        for subcmd_or_options in no_pyfile_subcmds:
            search_subcmd = re.search(r"-.{1,256}", subcmd_or_options)
            if search_subcmd and len(search_subcmd.group(0)) == len(subcmd_or_options):
                break
            subcmds.append(subcmd_or_options)

        if len(subcmds) == 0:
            return SysArg(subcmd="base")
        elif len(subcmds) == 1:
            return SysArg(
                pre_subcmd=SysArg(
                    pre_subcmd=None,
                    subcmd="base",
                ),
                subcmd=subcmds[0],
            )
        else:
            return SysArg(
                pre_subcmd=SysArg.parse(subcmds[:-1]),
                subcmd=subcmds[-1],
            )


class MockAPICommandParser:
    """*The parser of PyMock-API command line*

    Handling the command line about options includes what options PyMock-API could use and what values of entry command
    line.
    """

    def __init__(self):
        self._prog = "pymock-api"
        self._usage = "mock" if self.is_running_subcmd else "mock [SUBCOMMAND] [OPTIONS]"
        self._description = """
        A Python tool for mocking APIs by set up an application easily. PyMock-API bases on Python framework to set
        up application, i.e., for REST API, you could select using *flask* to set up application to mock APIs.
        """
        self._parser_args: Dict[str, Any] = {
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
    def subcommand(self) -> Optional[SysArg]:
        return SysArg.parse(sys.argv) if self.is_running_subcmd else None

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


SubCommandAttr = namedtuple("SubCommandAttr", ["title", "dest", "description", "help"])
SubParserAttr = namedtuple("SubParserAttr", ["name", "help"])

_ClsNamingFormat = namedtuple("_ClsNamingFormat", ["ahead", "tail"])
_ClsNamingFormat.ahead = "BaseSubCmd"
_ClsNamingFormat.tail = "Option"


class MetaCommandOption(type):
    """*The metaclass for options of PyMock-API command*

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
            SUBCOMMAND.extend(
                [
                    b.__name__.replace(_ClsNamingFormat.ahead, "").replace(_ClsNamingFormat.tail, "").lower()
                    for b in bases
                ]
            )
        new_class = super_new(cls, name, bases, attrs)
        COMMAND_OPTIONS.append(new_class)
        return new_class


@dataclass
class SubCmdParserAction:
    subcmd_name: str
    subcmd_parser: argparse._SubParsersAction


@dataclass
class SubCmdParser:
    in_subcmd: str
    parser: argparse.ArgumentParser
    sub_parser: List["SubCmdParser"]

    def find(self, subcmd: str) -> Optional[argparse.ArgumentParser]:
        if subcmd == self.in_subcmd:
            return self.parser
        else:
            if self.sub_parser:
                all_subcmd_parser = list(map(lambda sp: sp.find(subcmd), self.sub_parser))
                exist_subcmd_parser = list(filter(lambda sp: sp is not None, all_subcmd_parser))
                if exist_subcmd_parser:
                    return exist_subcmd_parser[0]
                return None
            else:
                return None


SUBCOMMAND_PARSER: List[SubCmdParser] = []


@dataclass
class SubCommandSection:
    Base: str = "subcommands"
    ApiServer: str = "API server subcommands"


class CommandOption:
    sub_cmd: Optional[SubCommandAttr] = None
    in_sub_cmd: str = SubCommand.Base
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
            if self._find_subcmd_parser_action(SubCommand.Base) is None:
                sub_cmd: SubCommandAttr = SubCommandAttr(
                    title=SubCommandSection.Base,
                    dest=SubCommand.Base,
                    description="",
                    help="",
                )
                self._subparser.append(
                    SubCmdParserAction(
                        subcmd_name=SubCommand.Base,
                        subcmd_parser=parser.add_subparsers(
                            title=sub_cmd.title,
                            dest=sub_cmd.dest,
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
                    _base_subcmd_parser_action = self._find_subcmd_parser_action(SubCommand.Base)
                _parser = _base_subcmd_parser_action.subcmd_parser.add_parser(  # type: ignore[union-attr]
                    name=self.sub_cmd.dest, help=self.sub_cmd.help  # type: ignore[union-attr]
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
                self._subparser.append(
                    SubCmdParserAction(
                        subcmd_name=self.in_sub_cmd,
                        subcmd_parser=_parser.add_subparsers(
                            title=self.sub_cmd.title,  # type: ignore[union-attr]
                            dest=self.sub_cmd.dest,  # type: ignore[union-attr]
                            description=self.sub_cmd.description,  # type: ignore[union-attr]
                            help=self.sub_cmd.help,  # type: ignore[union-attr]
                        ),
                    ),
                )

            if self.in_sub_cmd and subcmd_parser_action is None:
                _add_new_subcommand_line()
                subcmd_parser_action = self._find_subcmd_parser_action(self.in_sub_cmd)

            subcmd_parser_model = self._find_subcmd_parser(self.sub_parser.name)
            if subcmd_parser_model is None:
                parser = subcmd_parser_action.subcmd_parser.add_parser(  # type: ignore[union-attr]
                    name=self.sub_parser.name, help=self.sub_parser.help
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

    def _find_subcmd_parser(self, subcmd_name: str) -> Optional[SubCmdParser]:
        mapping_subcmd_parser = list(filter(lambda e: e.find(subcmd_name) is not None, SUBCOMMAND_PARSER))
        return mapping_subcmd_parser[0] if mapping_subcmd_parser else None

    def _find_subcmd_parser_action(self, subcmd_name: str = "") -> Optional[SubCmdParserAction]:
        mapping_subcmd_parser_action = list(
            filter(lambda e: e.subcmd_name == (subcmd_name if subcmd_name else self.in_sub_cmd), self._subparser)
        )
        return mapping_subcmd_parser_action[0] if mapping_subcmd_parser_action else None


class BaseSubCommand(CommandOption):
    sub_cmd: SubCommandAttr = SubCommandAttr(
        title=SubCommandSection.Base,
        dest=SubCommand.Base,
        description="",
        help="",
    )


class BaseSubCommandRestServer(CommandOption):
    sub_cmd: SubCommandAttr = SubCommandAttr(
        title=SubCommandSection.ApiServer,
        dest=SubCommand.RestServer,
        description="Some operations for mocking REST API server.",
        help="Set up an application to mock HTTP server which adopts REST API to communicate between client and server.",
    )
    in_sub_cmd = SubCommand.RestServer


class SubCommandRunOption(BaseSubCommandRestServer):
    sub_parser: SubParserAttr = SubParserAttr(
        name=SubCommand.Run,
        help="Set up APIs with configuration and run a web application to mock them.",
    )
    option_value_type: type = str


class SubCommandAddOption(BaseSubCommandRestServer):
    sub_parser: SubParserAttr = SubParserAttr(
        name=SubCommand.Add,
        help="Something processing about configuration, i.e., generate a sample configuration or validate configuration"
        " content.",
    )


class SubCommandCheckOption(BaseSubCommandRestServer):
    sub_parser: SubParserAttr = SubParserAttr(
        name=SubCommand.Check,
        help="Check the validity of *PyMock-API* configuration.",
    )


class SubCommandGetOption(BaseSubCommandRestServer):
    sub_parser: SubParserAttr = SubParserAttr(
        name=SubCommand.Get,
        help="Do some comprehensive inspection for configuration.",
    )


class SubCommandSampleOption(BaseSubCommandRestServer):
    sub_parser: SubParserAttr = SubParserAttr(
        name=SubCommand.Sample,
        help="Quickly display or generate a sample configuration helps to use this tool.",
    )


class SubCommandPullOption(BaseSubCommandRestServer):
    sub_parser: SubParserAttr = SubParserAttr(
        name=SubCommand.Pull,
        help="Pull the API details from one specific source, e.g., Swagger API documentation.",
    )


BaseCmdOption: type = MetaCommandOption("BaseCmdOption", (CommandOption,), {})
BaseSubCmdRunOption: type = MetaCommandOption("BaseSubCmdRunOption", (SubCommandRunOption,), {})
BaseSubCmdAddOption: type = MetaCommandOption("BaseSubCmdAddOption", (SubCommandAddOption,), {})
BaseSubCmdCheckOption: type = MetaCommandOption("BaseSubCmdCheckOption", (SubCommandCheckOption,), {})
BaseSubCmdGetOption: type = MetaCommandOption("BaseSubCmdGetOption", (SubCommandGetOption,), {})
BaseSubCmdSampleOption: type = MetaCommandOption("BaseSubCmdSampleOption", (SubCommandSampleOption,), {})
BaseSubCmdPullOption: type = MetaCommandOption("BaseSubCmdPullOption", (SubCommandPullOption,), {})


class Version(BaseCmdOption):
    cli_option: str = "-v, --version"
    name: str = "version"
    help_description: str = "The version info of PyMock-API."
    default_value: Any = argparse.SUPPRESS
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


class WebAppType(BaseSubCmdRunOption):
    """
    Which Python web framework it should use to set up web server for mocking APIs.

    Option values:
        * *auto*: it would automatically scan which Python web library it could use to initial and set up server gateway in current runtime environment.
        * *flask*: Use Python web framework Flask (https://palletsprojects.com/p/flask/) to set up web application.
        * *fastapi*: Use Python web framework FastAPI (https://fastapi.tiangolo.com/) to set up web application.
    """

    cli_option: str = "--app-type"
    name: str = "app_type"
    help_description: str = "Which Python web framework it should use to set up web server for mocking APIs."
    default_value: str = "auto"
    _options: List[str] = ["auto", "flask", "fastapi"]


class Config(BaseSubCmdRunOption):
    cli_option: str = "-c, --config"
    name: str = "config"
    help_description: str = "The configuration of tool PyMock-API."
    default_value: str = "api.yaml"


class Bind(BaseSubCmdRunOption):
    cli_option: str = "-b, --bind"
    name: str = "bind"
    help_description: str = "The socket to bind."
    default_value: str = "127.0.0.1:9672"


class Workers(BaseSubCmdRunOption):
    cli_option: str = "-w, --workers"
    name: str = "workers"
    help_description: str = "The workers amount."
    default_value: int = 1


class LegLevel(BaseSubCmdRunOption):
    cli_option: str = "--log-level"
    name: str = "log_level"
    help_description: str = "The log level."
    default_value: str = "info"
    _options: List[str] = ["critical", "error", "warning", "info", "debug", "trace"]


class PrintSample(BaseSubCmdSampleOption):
    cli_option: str = "-p, --print-sample"
    name: str = "print_sample"
    help_description: str = "Print the sample configuration content."
    action: str = "store_true"
    option_value_type: Optional[type] = None
    default_value: bool = False


class GenerateSample(BaseSubCmdSampleOption):
    cli_option: str = "-g, --generate-sample"
    name: str = "generate_sample"
    help_description: str = "Create a sample configuration file."
    action: str = "store_true"
    option_value_type: Optional[type] = None
    default_value: bool = False


class Output(BaseSubCmdSampleOption):
    cli_option: str = "-o, --output"
    name: str = "file_path"
    help_description: str = (
        "Save the sample configuration to this path. In generally, this option would be used with"
        " option *-g* (aka *--generate-sample*)."
    )
    option_value_type: type = str
    default_value: str = "sample-api.yaml"


class DemoSampleType(BaseSubCmdSampleOption):
    cli_option: str = "-t, --sample-config-type"
    name: str = "sample_config_type"
    help_description: str = "Which configuration type (the type means the response way) you want to demonstrate."
    option_value_type: type = str
    default_value: str = "all"
    _options: List[str] = ["all", "response_as_str", "response_as_json", "response_with_file"]


class APIConfigPath(BaseSubCmdAddOption):
    cli_option: str = "--config-path"
    name: str = "config_path"
    help_description: str = "The configuration file path."
    option_value_type: type = str
    default_value: str = "api.yaml"


class AddAPIPath(BaseSubCmdAddOption):
    cli_option: str = "--api-path"
    name: str = "api_path"
    help_description: str = "Set URL path of one specific API."
    option_value_type: type = str


class AddHTTPMethod(BaseSubCmdAddOption):
    cli_option: str = "--http-method"
    name: str = "http_method"
    help_description: str = "Set HTTP method of one specific API."
    option_value_type: type = str
    default_value: str = "GET"


class AddParameters(BaseSubCmdAddOption):
    cli_option: str = "--parameters"
    name: str = "parameters"
    help_description: str = "Set HTTP request parameter(s) of one specific API."
    action: str = "append"
    option_value_type: type = str
    default_value: str = ""


class AddResponseStrategy(BaseSubCmdAddOption):
    cli_option: str = "--response-strategy"
    name: str = "response_strategy"
    help_description: str = "Set HTTP response strategy of one specific API."
    option_value_type: type = str
    _options: List[str] = ["string", "file", "object"]


class AddResponse(BaseSubCmdAddOption):
    cli_option: str = "--response-value"
    name: str = "response_value"
    help_description: str = "Set HTTP response value of one specific API."
    action: str = "append"
    option_value_type: type = str
    default_value: str = "OK."


class AddBaseFilePath(BaseSubCmdAddOption):
    cli_option: str = "--base-file-path"
    name: str = "base_file_path"
    help_description: str = (
        "The path which is the basic value of all configuration file paths. In the other "
        "words, it would automatically add the base path in front of all the other file "
        "paths in configuration."
    )


class AddIncludeTemplateConfig(BaseSubCmdAddOption):
    cli_option: str = "--include-template-config"
    name: str = "include_template_config"
    help_description: str = "If it's true, it would also configure *template* section setting in result configuration."
    action: str = "store_true"
    option_value_type: Optional[type] = None
    default_value: bool = False


class AddBaseURL(BaseSubCmdAddOption):
    cli_option: str = "--base-url"
    name: str = "base_url"
    help_description: str = "The base URL which must be the part of path all the APIs begin with."


class AddTag(BaseSubCmdAddOption):
    cli_option: str = "--tag"
    name: str = "tag"
    help_description: str = "Set tag at the new mock API."


class AddDryRun(BaseSubCmdAddOption):
    cli_option: str = "--dry-run"
    name: str = "dry_run"
    help_description: str = "If it's true, it would run pulling process without saving result configuration."
    action: str = "store_true"
    option_value_type: Optional[type] = None
    default_value: bool = False


class AddDivideApi(BaseSubCmdAddOption):
    cli_option: str = "--divide-api"
    name: str = "divide_api"
    help_description: str = (
        "If it's true, it would divide the setting values of mocked API section " "(mocked_apis.apis.<mock API>)."
    )
    action: str = "store_true"
    option_value_type: Optional[type] = None
    default_value: bool = False


class AddDivideHttp(BaseSubCmdAddOption):
    cli_option: str = "--divide-http"
    name: str = "divide_http"
    help_description: str = (
        "If it's true, it would divide the setting values of HTTP part section " "(mocked_apis.apis.<mock API>.http)."
    )
    action: str = "store_true"
    option_value_type: Optional[type] = None
    default_value: bool = False


class AddDivideHttpRequest(BaseSubCmdAddOption):
    cli_option: str = "--divide-http-request"
    name: str = "divide_http_request"
    help_description: str = (
        "If it's true, it would divide the setting values of HTTP request part section "
        "(mocked_apis.apis.<mock API>.http.request)."
    )
    action: str = "store_true"
    option_value_type: Optional[type] = None
    default_value: bool = False


class AddDivideHttpResponse(BaseSubCmdAddOption):
    cli_option: str = "--divide-http-response"
    name: str = "divide_http_response"
    help_description: str = (
        "If it's true, it would divide the setting values of HTTP response part section "
        "(mocked_apis.apis.<mock API>.http.response)."
    )
    action: str = "store_true"
    option_value_type: Optional[type] = None
    default_value: bool = False


class ConfigPath(BaseSubCmdCheckOption):
    cli_option: str = "-p, --config-path"
    name: str = "config_path"
    help_description: str = "The file path of configuration."
    default_value: str = "api.yaml"


class StopCheckIfFail(BaseSubCmdCheckOption):
    cli_option: str = "--stop-if-fail"
    name: str = "stop_if_fail"
    help_description: str = "Stop program if it gets any fail in checking."
    action: str = "store_true"
    option_value_type: Optional[type] = None
    default_value: bool = False


class SwaggerDocURL(BaseSubCmdCheckOption):
    cli_option: str = "-s, --swagger-doc-url"
    name: str = "swagger_doc_url"
    help_description: str = "The URL path of swagger style API document."


class CheckEntireAPI(BaseSubCmdCheckOption):
    cli_option: str = "--check-entire-api"
    name: str = "check_entire_api"
    help_description: str = "Do the inspection of all properties of each API."
    action: str = "store_true"
    option_value_type: Optional[type] = None
    default_value: bool = False


class CheckAPIPath(BaseSubCmdCheckOption):
    cli_option: str = "--check-api-path"
    name: str = "check_api_path"
    help_description: str = "Do the inspection of property API path."
    action: str = "store_true"
    option_value_type: Optional[type] = None
    default_value: bool = False


class CheckAPIHTTPMethod(BaseSubCmdCheckOption):
    cli_option: str = "--check-api-http-method"
    name: str = "check_api_http_method"
    help_description: str = "Do the inspection of property allowable HTTP method of one specific API."
    action: str = "store_true"
    option_value_type: Optional[type] = None
    default_value: bool = False


class CheckAPIParameter(BaseSubCmdCheckOption):
    cli_option: str = "--check-api-parameters"
    name: str = "check_api_parameters"
    help_description: str = "Do the inspection of property API parameters."
    action: str = "store_true"
    option_value_type: Optional[type] = None
    default_value: bool = False


class UnderCheckConfigPath(BaseSubCmdGetOption):
    cli_option: str = "-p, --config-path"
    name: str = "config_path"
    help_description: str = "The file path of configuration."
    default_value: str = "api.yaml"


class GetAPIShowDetail(BaseSubCmdGetOption):
    cli_option: str = "-s, --show-detail"
    name: str = "show_detail"
    help_description: str = "Show the API details."
    action: str = "store_true"
    option_value_type: Optional[type] = None
    default_value: bool = False


class GetAPIShowDetailAsFormat(BaseSubCmdGetOption):
    cli_option: str = "-f, --show-as-format"
    name: str = "show_as_format"
    help_description: str = "Show the API details as one specific format."
    option_value_type: type = str
    default_value: str = "text"
    _options: List[str] = ["text", "json", "yaml"]


class GetAPIPath(BaseSubCmdGetOption):
    cli_option: str = "-a, --api-path"
    name: str = "api_path"
    help_description: str = "Get the API info by API path."


class GetWithHTTPMethod(BaseSubCmdGetOption):
    cli_option: str = "-m, --http-method"
    name: str = "http_method"
    help_description: str = (
        "This is an option for searching condition which cannot be used individually. Add "
        "condition of HTTP method to get the API info."
    )


class Source(BaseSubCmdPullOption):
    cli_option: str = "-s, --source"
    name: str = "source"
    help_description: str = "The source where keeps API details as documentation."
    default_value: str = ""


class SourceFile(BaseSubCmdPullOption):
    cli_option: str = "-f, --source-file"
    name: str = "source_file"
    help_description: str = "The source file which is the OpenAPI documentation configuration."
    default_value: str = ""


class PullRequestWithHttps(BaseSubCmdPullOption):
    cli_option: str = "--request-with-https"
    name: str = "request_with_https"
    help_description: str = (
        "If it's true, it would send the HTTP request over TLS to get the Swagger API documentation configuration."
    )
    action: str = "store_true"
    option_value_type: Optional[type] = None
    default_value: bool = False


class PullToConfigPath(BaseSubCmdPullOption):
    cli_option: str = "-c, --config-path"
    name: str = "config_path"
    help_description: str = (
        "The file path where program will write the deserialization result configuration of API documentation, e.g., "
        "Swagger API documentation to it."
    )


class PullBaseURL(BaseSubCmdPullOption):
    cli_option: str = "--base-url"
    name: str = "base_url"
    help_description: str = "The base URL which must be the part of path all the APIs begin with."


class PullBaseFilePath(BaseSubCmdPullOption):
    cli_option: str = "--base-file-path"
    name: str = "base_file_path"
    help_description: str = (
        "The path which is the basic value of all configuration file paths. In the other "
        "words, it would automatically add the base path in front of all the other file "
        "paths in configuration."
    )


class PullIncludeTemplateConfig(BaseSubCmdPullOption):
    cli_option: str = "--include-template-config"
    name: str = "include_template_config"
    help_description: str = "If it's true, it would also configure *template* section setting in result configuration."
    action: str = "store_true"
    option_value_type: Optional[type] = None
    default_value: bool = False


class PullDryRun(BaseSubCmdPullOption):
    cli_option: str = "--dry-run"
    name: str = "dry_run"
    help_description: str = "If it's true, it would run pulling process without saving result configuration."
    action: str = "store_true"
    option_value_type: Optional[type] = None
    default_value: bool = False


class PullDivideApi(BaseSubCmdPullOption):
    cli_option: str = "--divide-api"
    name: str = "divide_api"
    help_description: str = (
        "If it's true, it would divide the setting values of mocked API section " "(mocked_apis.apis.<mock API>)."
    )
    action: str = "store_true"
    option_value_type: Optional[type] = None
    default_value: bool = False


class PullDivideHttp(BaseSubCmdPullOption):
    cli_option: str = "--divide-http"
    name: str = "divide_http"
    help_description: str = (
        "If it's true, it would divide the setting values of HTTP part section " "(mocked_apis.apis.<mock API>.http)."
    )
    action: str = "store_true"
    option_value_type: Optional[type] = None
    default_value: bool = False


class PullDivideHttpRequest(BaseSubCmdPullOption):
    cli_option: str = "--divide-http-request"
    name: str = "divide_http_request"
    help_description: str = (
        "If it's true, it would divide the setting values of HTTP request part section "
        "(mocked_apis.apis.<mock API>.http.request)."
    )
    action: str = "store_true"
    option_value_type: Optional[type] = None
    default_value: bool = False


class PullDivideHttpResponse(BaseSubCmdPullOption):
    cli_option: str = "--divide-http-response"
    name: str = "divide_http_response"
    help_description: str = (
        "If it's true, it would divide the setting values of HTTP response part section "
        "(mocked_apis.apis.<mock API>.http.response)."
    )
    action: str = "store_true"
    option_value_type: Optional[type] = None
    default_value: bool = False
