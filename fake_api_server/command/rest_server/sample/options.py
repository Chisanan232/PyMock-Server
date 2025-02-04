from typing import List, Optional

from fake_api_server.command._base.options import MetaCommandOption
from fake_api_server.command.rest_server.option import BaseSubCommandRestServer
from fake_api_server.command.subcommand import SubCommandLine
from fake_api_server.model.subcmd_common import SubParserAttr


class SubCommandSampleOption(BaseSubCommandRestServer):
    sub_parser: SubParserAttr = SubParserAttr(
        name=SubCommandLine.Sample,
        help="Quickly display or generate a sample configuration helps to use this tool.",
    )


BaseSubCmdSampleOption: type = MetaCommandOption("BaseSubCmdSampleOption", (SubCommandSampleOption,), {})


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
