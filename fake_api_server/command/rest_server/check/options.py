from typing import Optional

from fake_api_server.command._base.options import MetaCommandOption
from fake_api_server.command.rest_server.option import BaseSubCommandRestServer
from fake_api_server.command.subcommand import SubCommandLine
from fake_api_server.model.subcmd_common import SubParserAttr


class SubCommandCheckOption(BaseSubCommandRestServer):
    sub_parser: SubParserAttr = SubParserAttr(
        name=SubCommandLine.Check,
        help="Check the validity of *PyFake-API-Server* configuration.",
    )


BaseSubCmdCheckOption: type = MetaCommandOption("BaseSubCmdCheckOption", (SubCommandCheckOption,), {})


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
