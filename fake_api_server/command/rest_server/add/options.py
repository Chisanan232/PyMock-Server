from typing import List, Optional

from fake_api_server.command._base.options import MetaCommandOption
from fake_api_server.command.rest_server.option import BaseSubCommandRestServer
from fake_api_server.command.subcommand import SubCommandLine
from fake_api_server.model.subcmd_common import SubParserAttr


class SubCommandAddOption(BaseSubCommandRestServer):
    sub_parser: SubParserAttr = SubParserAttr(
        name=SubCommandLine.Add,
        help="Something processing about configuration, i.e., generate a sample configuration or validate configuration"
        " content.",
    )


BaseSubCmdAddOption: type = MetaCommandOption("BaseSubCmdAddOption", (SubCommandAddOption,), {})


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


class BaseFilePath(BaseSubCmdAddOption):
    cli_option: str = "--base-file-path"
    name: str = "base_file_path"
    help_description: str = (
        "The path which is the basic value of all configuration file paths. In the other "
        "words, it would automatically add the base path in front of all the other file "
        "paths in configuration."
    )


class IncludeTemplateConfig(BaseSubCmdAddOption):
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


class DryRun(BaseSubCmdAddOption):
    cli_option: str = "--dry-run"
    name: str = "dry_run"
    help_description: str = "If it's true, it would run pulling process without saving result configuration."
    action: str = "store_true"
    option_value_type: Optional[type] = None
    default_value: bool = False


class DivideApi(BaseSubCmdAddOption):
    cli_option: str = "--divide-api"
    name: str = "divide_api"
    help_description: str = (
        "If it's true, it would divide the setting values of mocked API section (mocked_apis.apis.<mock API>)."
    )
    action: str = "store_true"
    option_value_type: Optional[type] = None
    default_value: bool = False


class DivideHttp(BaseSubCmdAddOption):
    cli_option: str = "--divide-http"
    name: str = "divide_http"
    help_description: str = (
        "If it's true, it would divide the setting values of HTTP part section (mocked_apis.apis.<mock API>.http)."
    )
    action: str = "store_true"
    option_value_type: Optional[type] = None
    default_value: bool = False


class DivideHttpRequest(BaseSubCmdAddOption):
    cli_option: str = "--divide-http-request"
    name: str = "divide_http_request"
    help_description: str = (
        "If it's true, it would divide the setting values of HTTP request part section "
        "(mocked_apis.apis.<mock API>.http.request)."
    )
    action: str = "store_true"
    option_value_type: Optional[type] = None
    default_value: bool = False


class DivideHttpResponse(BaseSubCmdAddOption):
    cli_option: str = "--divide-http-response"
    name: str = "divide_http_response"
    help_description: str = (
        "If it's true, it would divide the setting values of HTTP response part section "
        "(mocked_apis.apis.<mock API>.http.response)."
    )
    action: str = "store_true"
    option_value_type: Optional[type] = None
    default_value: bool = False
