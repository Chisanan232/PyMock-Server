from argparse import Namespace
from typing import Type

import pytest

from pymock_api.model.cmd_args import Deserialize, ParserArguments

from ..._values import (
    _Bind_Host_And_Port,
    _Log_Level,
    _Test_App_Type,
    _Test_Config,
    _Test_SubCommand,
    _Workers_Amount,
)


class TestDeserialize:
    @pytest.fixture(scope="function")
    def deserialize(self) -> Type[Deserialize]:
        return Deserialize

    def test_parser_arguments(self, deserialize: Type[Deserialize]):
        namespace_args = {
            _Test_SubCommand: _Test_SubCommand,
            "config": _Test_Config,
            "app_type": _Test_App_Type,
            "bind": _Bind_Host_And_Port.value,
            "workers": _Workers_Amount.value,
            "log_level": _Log_Level.value,
        }
        namespace = Namespace(**namespace_args)
        arguments = deserialize.parser_arguments(namespace, subcmd=_Test_SubCommand)
        assert isinstance(arguments, ParserArguments)
        assert arguments.subparser_name == _Test_SubCommand
        assert arguments.config == _Test_Config
        assert arguments.app_type == _Test_App_Type
        assert arguments.bind == _Bind_Host_And_Port.value
        assert arguments.workers == _Workers_Amount.value
        assert arguments.log_level == _Log_Level.value
