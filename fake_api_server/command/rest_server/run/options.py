from typing import List, Optional

from fake_api_server.command._base.options import MetaCommandOption
from fake_api_server.command.rest_server.option import BaseSubCommandRestServer
from fake_api_server.command.subcommand import SubCommandLine
from fake_api_server.model.subcmd_common import SubParserAttr


class SubCommandRunOption(BaseSubCommandRestServer):
    sub_parser: SubParserAttr = SubParserAttr(
        name=SubCommandLine.Run,
        help="Set up APIs with configuration and run a web application to mock them.",
    )
    option_value_type: type = str


BaseSubCmdRunOption: type = MetaCommandOption("BaseSubCmdRunOption", (SubCommandRunOption,), {})


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
    help_description: str = "The configuration of tool PyFake-API-Server."
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


class DaemonizeProcess(BaseSubCmdRunOption):
    cli_option: str = "-D, --daemon"
    name: str = "daemon"
    help_description: str = "Daemonize the process runs API server instance."
    action: str = "store_true"
    default_value: bool = False
    option_value_type: Optional[type] = None


class AccessLogFile(BaseSubCmdRunOption):
    cli_option: str = "--access-log-file"
    name: str = "access_log_file"
    help_description: str = "The file which program would use to write the access log to for record."
    default_value: str = "fake-api-server.log"
