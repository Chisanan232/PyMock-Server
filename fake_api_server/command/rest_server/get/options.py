from typing import List, Optional

from fake_api_server.command._base.options import MetaCommandOption
from fake_api_server.command.rest_server.option import BaseSubCommandRestServer
from fake_api_server.command.subcommand import SubCommandLine
from fake_api_server.model.subcmd_common import SubParserAttr


class SubCommandGetOption(BaseSubCommandRestServer):
    sub_parser: SubParserAttr = SubParserAttr(
        name=SubCommandLine.Get,
        help="Do some comprehensive inspection for configuration.",
    )


BaseSubCmdGetOption: type = MetaCommandOption("BaseSubCmdGetOption", (SubCommandGetOption,), {})


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
