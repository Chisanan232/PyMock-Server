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
from pymock_server.command.rest_server.add.options import (
    import_option as import_add_options,
)
from pymock_server.command.rest_server.check.options import (
    import_option as import_check_options,
)
from pymock_server.command.rest_server.get.options import (
    import_option as import_get_options,
)

# NOTE: Just for importing the command line options, do nothing in this module
from pymock_server.command.rest_server.run.options import (
    import_option as import_run_options,
)
from pymock_server.model.subcmd_common import SubCommandAttr, SubParserAttr

from ._base_options import (
    CommandLineOptions,
    CommandOption,
    MetaCommandOption,
    SubCommandInterface,
)
from .rest_server.option import BaseSubCommandRestServer
from .subcommand import SubCommandLine, SubCommandSection

# FIXME: Please use more clear and beautiful implementation to apply the command line options
import_run_options()
import_add_options()
import_check_options()
import_get_options()


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
