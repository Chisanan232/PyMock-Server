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
from typing import Any, List, Optional

from pymock_server.__pkg_info__ import __version__
from pymock_server.model.subcmd_common import SubCommandAttr, SubParserAttr

from ._base_options import (
    CommandLineOptions,
    CommandOption,
    MetaCommandOption,
    SubCommandInterface,
)
from .rest_server.option import BaseSubCommandRestServer
from .subcommand import SubCommandLine, SubCommandSection


def get_all_subcommands() -> List[str]:
    return list(set(SubCommandInterface.get()))


def make_options() -> List["CommandOption"]:
    """Initial and generate all options for parser to use and organize.

    Returns:
        list: A list object of **CommandOption** objects.

    """
    mock_api_cmd_options: List["CommandOption"] = []
    for option_cls in CommandLineOptions.get():
        option = option_cls()
        if not option.cli_option:
            raise ValueError(f"The object {option.__class__}'s attribute *cli_option* cannot be None or empty value.")
        mock_api_cmd_options.append(option.copy())
    return mock_api_cmd_options


class BaseSubCommand(CommandOption):
    sub_cmd: SubCommandAttr = SubCommandAttr(
        title=SubCommandSection.Base,
        dest=SubCommandLine.Base,
        description="",
        help="",
    )


class SubCommandRunOption(BaseSubCommandRestServer):
    sub_parser: SubParserAttr = SubParserAttr(
        name=SubCommandLine.Run,
        help="Set up APIs with configuration and run a web application to mock them.",
    )
    option_value_type: type = str


class SubCommandAddOption(BaseSubCommandRestServer):
    sub_parser: SubParserAttr = SubParserAttr(
        name=SubCommandLine.Add,
        help="Something processing about configuration, i.e., generate a sample configuration or validate configuration"
        " content.",
    )


class SubCommandCheckOption(BaseSubCommandRestServer):
    sub_parser: SubParserAttr = SubParserAttr(
        name=SubCommandLine.Check,
        help="Check the validity of *PyMock-API* configuration.",
    )


class SubCommandGetOption(BaseSubCommandRestServer):
    sub_parser: SubParserAttr = SubParserAttr(
        name=SubCommandLine.Get,
        help="Do some comprehensive inspection for configuration.",
    )


class SubCommandSampleOption(BaseSubCommandRestServer):
    sub_parser: SubParserAttr = SubParserAttr(
        name=SubCommandLine.Sample,
        help="Quickly display or generate a sample configuration helps to use this tool.",
    )


class SubCommandPullOption(BaseSubCommandRestServer):
    sub_parser: SubParserAttr = SubParserAttr(
        name=SubCommandLine.Pull,
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
