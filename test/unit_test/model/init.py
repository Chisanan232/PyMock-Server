from argparse import Namespace
from unittest.mock import Mock, patch

from pymock_api.model import DeserializeParsedArgs, deserialize_subcommand_run_args

from ..._values import (
    _Bind_Host_And_Port,
    _Log_Level,
    _Test_App_Type,
    _Test_Config,
    _Test_SubCommand,
    _Workers_Amount,
)


@patch.object(DeserializeParsedArgs, "subcommand_run")
def test_deserialize_parser_args(mock_parser_arguments: Mock):
    namespace_args = {
        "subcommand": _Test_SubCommand,
        "config": _Test_Config,
        "app_type": _Test_App_Type,
        "bind": _Bind_Host_And_Port.value,
        "workers": _Workers_Amount.value,
        "log_level": _Log_Level.value,
    }
    namespace = Namespace(**namespace_args)
    deserialize_subcommand_run_args(namespace)
    mock_parser_arguments.assert_called_once_with(namespace)
