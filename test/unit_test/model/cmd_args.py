from argparse import Namespace
from typing import Type

import pytest

from pymock_api.model.cmd_args import (
    DeserializeParsedArgs,
    SubcmdCheckArguments,
    SubcmdConfigArguments,
    SubcmdRunArguments,
)

from ..._values import (
    _Bind_Host_And_Port,
    _Generate_Sample,
    _Log_Level,
    _Print_Sample,
    _Sample_File_Path,
    _Test_App_Type,
    _Test_Config,
    _Test_SubCommand_Check,
    _Test_SubCommand_Config,
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
