from argparse import Namespace
from typing import Type

import pytest

from pymock_api.model.cmd_args import (
    DeserializeParsedArgs,
    SubcmdCheckArguments,
    SubcmdConfigArguments,
    SubcmdInspectArguments,
    SubcmdRunArguments,
)

from ..._values import (
    _Bind_Host_And_Port,
    _Generate_Sample,
    _Log_Level,
    _Print_Sample,
    _Sample_File_Path,
    _Swagger_API_Document_URL,
    _Test_App_Type,
    _Test_Config,
    _Test_SubCommand_Check,
    _Test_SubCommand_Config,
    _Test_SubCommand_Inspect,
    _Test_SubCommand_Run,
    _Workers_Amount,
)


class TestDeserialize:
    @pytest.fixture(scope="function")
    def deserialize(self) -> Type[DeserializeParsedArgs]:
        return DeserializeParsedArgs

    def test_parser_subcommand_run_arguments(self, deserialize: Type[DeserializeParsedArgs]):
        namespace_args = {
            "subcommand": _Test_SubCommand_Run,
            "config": _Test_Config,
            "app_type": _Test_App_Type,
            "bind": _Bind_Host_And_Port.value,
            "workers": _Workers_Amount.value,
            "log_level": _Log_Level.value,
        }
        namespace = Namespace(**namespace_args)
        arguments = deserialize.subcommand_run(namespace)
        assert isinstance(arguments, SubcmdRunArguments)
        assert arguments.subparser_name == _Test_SubCommand_Run
        assert arguments.config == _Test_Config
        assert arguments.app_type == _Test_App_Type
        assert arguments.bind == _Bind_Host_And_Port.value
        assert arguments.workers == _Workers_Amount.value
        assert arguments.log_level == _Log_Level.value

    def test_parser_subcommand_config_arguments(self, deserialize: Type[DeserializeParsedArgs]):
        namespace_args = {
            "subcommand": _Test_SubCommand_Config,
            "generate_sample": _Generate_Sample,
            "print_sample": _Print_Sample,
            "file_path": _Sample_File_Path,
        }
        namespace = Namespace(**namespace_args)
        arguments = deserialize.subcommand_config(namespace)
        assert isinstance(arguments, SubcmdConfigArguments)
        assert arguments.subparser_name == _Test_SubCommand_Config
        assert arguments.generate_sample == _Generate_Sample
        assert arguments.print_sample == _Print_Sample
        assert arguments.sample_output_path == _Sample_File_Path

    def test_parser_subcommand_check_arguments(self, deserialize: Type[DeserializeParsedArgs]):
        namespace_args = {
            "subcommand": _Test_SubCommand_Check,
            "config_path": _Test_Config,
        }
        namespace = Namespace(**namespace_args)
        arguments = deserialize.subcommand_check(namespace)
        assert isinstance(arguments, SubcmdCheckArguments)
        assert arguments.subparser_name == _Test_SubCommand_Check
        assert arguments.config_path == _Test_Config

    @pytest.mark.parametrize(
        (
            "entire_check",
            "check_api_path",
            "check_http_method",
            "check_api_parameters",
            "expected_check_api_path",
            "expected_check_http_method",
            "expected_check_api_parameters",
        ),
        [
            (True, True, True, True, True, True, True),
            (True, False, True, True, True, True, True),
            (True, True, False, False, True, True, True),
            (True, False, False, False, True, True, True),
            (False, True, False, True, True, False, True),
            (False, False, False, True, False, False, True),
        ],
    )
    def test_parser_subcommand_inspect_arguments(
        self,
        entire_check: bool,
        check_api_path: bool,
        check_http_method: bool,
        check_api_parameters: bool,
        expected_check_api_path: bool,
        expected_check_http_method: bool,
        expected_check_api_parameters: bool,
        deserialize: Type[DeserializeParsedArgs],
    ):
        namespace_args = {
            "subcommand": _Test_SubCommand_Inspect,
            "config_path": _Test_Config,
            "swagger_doc_url": _Swagger_API_Document_URL,
            "check_entire_api": entire_check,
            "check_api_path": check_api_path,
            "check_api_http_method": check_http_method,
            "check_api_parameters": check_api_parameters,
        }
        namespace = Namespace(**namespace_args)
        arguments = deserialize.subcommand_inspect(namespace)
        assert isinstance(arguments, SubcmdInspectArguments)
        assert arguments.subparser_name == _Test_SubCommand_Inspect
        assert arguments.config_path == _Test_Config
        assert arguments.swagger_doc_url == _Swagger_API_Document_URL
        assert arguments.check_api_path is expected_check_api_path
        assert arguments.check_api_http_method is expected_check_http_method
        assert arguments.check_api_parameters is expected_check_api_parameters
