from argparse import Namespace
from collections import namedtuple
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
    _Test_SubCommand_Add,
    _Test_SubCommand_Check,
    _Test_SubCommand_Inspect,
    _Test_SubCommand_Run,
    _Workers_Amount,
)

check_attrs = namedtuple("check_attrs", ("entire_check", "api_path", "http_method", "api_parameters"))
expected_check_attrs = namedtuple("expected_check_attrs", ("entire_check", "api_path", "http_method", "api_parameters"))


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
            "subcommand": _Test_SubCommand_Add,
            "generate_sample": _Generate_Sample,
            "print_sample": _Print_Sample,
            "file_path": _Sample_File_Path,
        }
        namespace = Namespace(**namespace_args)
        arguments = deserialize.subcommand_config(namespace)
        assert isinstance(arguments, SubcmdConfigArguments)
        assert arguments.subparser_name == _Test_SubCommand_Add
        assert arguments.generate_sample == _Generate_Sample
        assert arguments.print_sample == _Print_Sample
        assert arguments.sample_output_path == _Sample_File_Path

    @pytest.mark.parametrize(
        (
            "stop_if_fail",
            "under_test_check_props",
            "expected_check_props",
        ),
        [
            (
                True,
                check_attrs(entire_check=True, api_path=True, http_method=True, api_parameters=True),
                expected_check_attrs(entire_check=True, api_path=True, http_method=True, api_parameters=True),
            ),
            (
                False,
                check_attrs(entire_check=True, api_path=False, http_method=True, api_parameters=True),
                expected_check_attrs(entire_check=True, api_path=True, http_method=True, api_parameters=True),
            ),
            (
                True,
                check_attrs(entire_check=True, api_path=False, http_method=False, api_parameters=True),
                expected_check_attrs(entire_check=True, api_path=True, http_method=True, api_parameters=True),
            ),
            (
                True,
                check_attrs(entire_check=True, api_path=False, http_method=False, api_parameters=False),
                expected_check_attrs(entire_check=True, api_path=True, http_method=True, api_parameters=True),
            ),
            (
                False,
                check_attrs(entire_check=False, api_path=True, http_method=False, api_parameters=True),
                expected_check_attrs(entire_check=False, api_path=True, http_method=False, api_parameters=True),
            ),
            (
                False,
                check_attrs(entire_check=False, api_path=True, http_method=False, api_parameters=False),
                expected_check_attrs(entire_check=False, api_path=True, http_method=False, api_parameters=False),
            ),
        ],
    )
    def test_parser_subcommand_check_arguments(
        self,
        stop_if_fail: bool,
        under_test_check_props: check_attrs,
        expected_check_props: expected_check_attrs,
        deserialize: Type[DeserializeParsedArgs],
    ):
        namespace_args = {
            "subcommand": _Test_SubCommand_Check,
            "config_path": _Test_Config,
            "swagger_doc_url": _Swagger_API_Document_URL,
            "stop_if_fail": stop_if_fail,
            "check_entire_api": under_test_check_props.entire_check,
            "check_api_path": under_test_check_props.api_path,
            "check_api_http_method": under_test_check_props.http_method,
            "check_api_parameters": under_test_check_props.api_parameters,
        }
        namespace = Namespace(**namespace_args)
        arguments = deserialize.subcommand_check(namespace)
        assert isinstance(arguments, SubcmdCheckArguments)
        assert arguments.subparser_name == _Test_SubCommand_Check
        assert arguments.config_path == _Test_Config
        assert arguments.swagger_doc_url == _Swagger_API_Document_URL
        assert arguments.stop_if_fail is stop_if_fail
        assert arguments.check_api_path is expected_check_props.api_path
        assert arguments.check_api_http_method is expected_check_props.http_method
        assert arguments.check_api_parameters is expected_check_props.api_parameters

    def test_parser_subcommand_inspect_arguments(
        self,
        deserialize: Type[DeserializeParsedArgs],
    ):
        namespace_args = {
            "subcommand": _Test_SubCommand_Inspect,
            "config_path": _Test_Config,
        }
        namespace = Namespace(**namespace_args)
        arguments = deserialize.subcommand_inspect(namespace)
        assert isinstance(arguments, SubcmdInspectArguments)
        assert arguments.subparser_name == _Test_SubCommand_Inspect
        assert arguments.config_path == _Test_Config
