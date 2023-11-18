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

SUBCOMMAND: List[str] = []
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


class MockAPICommandParser:
    """*The parser of PyMock-API command line*

    Handling the command line about options includes what options PyMock-API could use and what values of entry command
    line.
    """

    def __init__(self):
        self._prog = "pymock-api"
        self._usage = "mock-api" if self.is_running_subcmd else "mock-api [SUBCOMMAND] [OPTIONS]"
        self._description = """
        A Python tool for mocking APIs by set up an application easily. PyMock-API bases on Python web framework to set
        up application, i.e., you could select using *flask* to set up application to mock APIs.
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
    def subcommand(self) -> Optional[str]:
        return sys.argv[1] if self.is_running_subcmd else None

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


class CommandOption:
    sub_cmd: Optional[SubCommandAttr] = None
    sub_parser: Optional[SubParserAttr] = None
    cli_option: str
    name: Optional[str] = None
    help_description: str
    option_value_type: Optional[type] = None
    default_value: Optional[Any] = None
    action: Optional[str] = None
    _options: Optional[List[str]] = None

    _subparser: List[argparse._SubParsersAction] = []
    _parser_of_subparser: Dict[str, argparse.ArgumentParser] = {}

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
            if not self._subparser:
                self._subparser.append(
                    parser.add_subparsers(
                        title=self.sub_cmd.title,
                        dest=self.sub_cmd.dest,
                        description=self.sub_cmd.description,
                        help=self.sub_cmd.help,
                    )
                )
            if self.sub_parser.name not in self._parser_of_subparser.keys():
                self._parser_of_subparser[self.sub_parser.name] = self._subparser[0].add_parser(
                    name=self.sub_parser.name, help=self.sub_parser.help
                )
            parser = self._parser_of_subparser[self.sub_parser.name]
        return parser


@dataclass
class SubCommand:
    Base: str = "subcommand"
    Run: str = "run"
    Add: str = "add"
    Check: str = "check"
    Get: str = "get"
    Sample: str = "sample"
    Pull: str = "pull"


class BaseSubCommand(CommandOption):
    sub_cmd: SubCommandAttr = SubCommandAttr(
        title="Subcommands",
        dest=SubCommand.Base,
        description="",
        help="",
    )


class SubCommandRunOption(BaseSubCommand):
    sub_parser: SubParserAttr = SubParserAttr(
        name=SubCommand.Run,
        help="Set up APIs with configuration and run a web application to mock them.",
    )
    option_value_type: type = str


class SubCommandAddOption(BaseSubCommand):
    sub_parser: SubParserAttr = SubParserAttr(
        name=SubCommand.Add,
        help="Something processing about configuration, i.e., generate a sample configuration or validate configuration"
        " content.",
    )


class SubCommandCheckOption(BaseSubCommand):
    sub_parser: SubParserAttr = SubParserAttr(
        name=SubCommand.Check,
        help="Check the validity of *PyMock-API* configuration.",
    )


class SubCommandGetOption(BaseSubCommand):
    sub_parser: SubParserAttr = SubParserAttr(
        name=SubCommand.Get,
        help="Do some comprehensive inspection for configuration.",
    )


class SubCommandSampleOption(BaseSubCommand):
    sub_parser: SubParserAttr = SubParserAttr(
        name=SubCommand.Sample,
        help="Quickly display or generate a sample configuration helps to use this tool.",
    )


class SubCommandPullOption(BaseSubCommand):
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
    cli_option: str = "--api-config-path"
    name: str = "api_config_path"
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
