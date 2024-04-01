from argparse import Namespace
from unittest.mock import Mock, patch

from pymock_api.model import (
    DeserializeParsedArgs,
    deserialize_args,
    deserialize_swagger_api_config,
)

from ..._values import (
    _API_Doc_Source,
    _Base_URL,
    _Bind_Host_And_Port,
    _Generate_Sample,
    _Log_Level,
    _Print_Sample,
    _Sample_File_Path,
    _Swagger_API_Document_URL,
    _Test_App_Type,
    _Test_Config,
    _Test_SubCommand_Add,
    _Test_SubCommand_Check,
    _Test_SubCommand_Get,
    _Test_SubCommand_Pull,
    _Test_SubCommand_Run,
    _Workers_Amount,
)


@patch.object(DeserializeParsedArgs, "subcommand_run")
def test_deserialize_subcommand_run_args(mock_parser_arguments: Mock):
    namespace_args = {
        "subcommand": _Test_SubCommand_Run,
        "config": _Test_Config,
        "app_type": _Test_App_Type,
        "bind": _Bind_Host_And_Port.value,
        "workers": _Workers_Amount.value,
        "log_level": _Log_Level.value,
    }
    namespace = Namespace(**namespace_args)
    deserialize_args.subcmd_run(namespace)
    mock_parser_arguments.assert_called_once_with(namespace)


@patch.object(DeserializeParsedArgs, "subcommand_add")
def test_deserialize_subcommand_add_args(mock_parser_arguments: Mock):
    namespace_args = {
        "subcommand": _Test_SubCommand_Add,
        "generate_sample": _Generate_Sample,
        "print_sample": _Print_Sample,
        "file_path": _Sample_File_Path,
    }
    namespace = Namespace(**namespace_args)
    deserialize_args.subcmd_add(namespace)
    mock_parser_arguments.assert_called_once_with(namespace)


@patch.object(DeserializeParsedArgs, "subcommand_check")
def test_deserialize_subcommand_check_args(mock_parser_arguments: Mock):
    namespace_args = {
        "subcommand": _Test_SubCommand_Check,
        "config_path": _Test_Config,
    }
    namespace = Namespace(**namespace_args)
    deserialize_args.subcmd_check(namespace)
    mock_parser_arguments.assert_called_once_with(namespace)


@patch.object(DeserializeParsedArgs, "subcommand_get")
def test_deserialize_subcommand_get_args(mock_parser_arguments: Mock):
    namespace_args = {
        "subcommand": _Test_SubCommand_Get,
        "config_path": _Test_Config,
        "swagger_doc_url": _Swagger_API_Document_URL,
        "check_api_path": True,
        "check_api_http_method": True,
        "check_api_parameters": True,
    }
    namespace = Namespace(**namespace_args)
    deserialize_args.subcmd_get(namespace)
    mock_parser_arguments.assert_called_once_with(namespace)


@patch.object(DeserializeParsedArgs, "subcommand_pull")
def test_deserialize_subcommand_get_args(mock_parser_arguments: Mock):
    namespace_args = {
        "subcommand": _Test_SubCommand_Pull,
        "source": _API_Doc_Source,
        "base_url": _Base_URL,
        "config_path": _Test_Config,
    }
    namespace = Namespace(**namespace_args)
    deserialize_args.subcmd_pull(namespace)
    mock_parser_arguments.assert_called_once_with(namespace)


def test_deserialize_swagger_api_config():
    with patch("pymock_api.model.OpenAPIDocumentConfig.deserialize") as mock_deserialize_swagger_config_function:
        deserialize_swagger_api_config(data={"some key": "some value"})
        mock_deserialize_swagger_config_function.assert_called_once_with(data={"some key": "some value"})
