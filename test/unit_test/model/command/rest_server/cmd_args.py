from abc import ABCMeta, abstractmethod
from argparse import Namespace
from collections import namedtuple
from typing import Type

# isort: off

import pytest

from fake_api_server._utils.file import Format
from fake_api_server.model.command.rest_server._sample import SampleType
from fake_api_server.model.command.rest_server.cmd_args import (
    SubcmdAddArguments,
    SubcmdCheckArguments,
    SubcmdGetArguments,
    SubcmdPullArguments,
    SubcmdRunArguments,
    SubcmdSampleArguments,
    ParserArguments,
)
from fake_api_server.model.subcmd_common import SysArg

# isort: off
from test._values import (
    SubCommand,
    _API_Doc_Source,
    _API_Doc_Source_File,
    _Base_URL,
    _Bind_Host_And_Port,
    _Cmd_Arg_API_Path,
    _Cmd_Arg_HTTP_Method,
    _Default_Base_File_Path,
    _Default_Include_Template_Config,
    _Generate_Sample,
    _Log_Level,
    _Print_Sample,
    _Sample_Data_Type,
    _Sample_File_Path,
    _Show_Detail_As_Format,
    _Swagger_API_Document_URL,
    _Test_App_Type,
    _Test_Config,
    _Test_Divide_Api,
    _Test_Divide_Http,
    _Test_Divide_Http_Request,
    _Test_Divide_Http_Response,
    _Test_Dry_Run,
    _Test_HTTP_Method,
    _Test_HTTP_Resp,
    _Test_Request_With_Https,
    _Test_Response_Strategy,
    _Test_SubCommand_Add,
    _Test_SubCommand_Check,
    _Test_SubCommand_Get,
    _Test_SubCommand_Pull,
    _Test_SubCommand_Run,
    _Test_SubCommand_Sample,
    _Test_Tag,
    _Test_URL,
    _Workers_Amount,
)

# isort: on

check_attrs = namedtuple("check_attrs", ("entire_check", "api_path", "http_method", "api_parameters"))
expected_check_attrs = namedtuple("expected_check_attrs", ("entire_check", "api_path", "http_method", "api_parameters"))


class CmdArgsDeserializeTestSuite(metaclass=ABCMeta):
    @pytest.fixture(scope="function")
    @abstractmethod
    def cmd_arg_data_model(self) -> Type[ParserArguments]:
        pass

    def test_deserialize(self, cmd_arg_data_model: Type[ParserArguments], **kwargs):
        namespace = self._given_namespace()
        argument = cmd_arg_data_model.deserialize(namespace)
        self._verify_arg_model(argument=argument)

    @abstractmethod
    def _given_namespace(self, **kwargs) -> Namespace:
        pass

    @abstractmethod
    def _verify_arg_model(self, **kwargs) -> None:
        pass


class TestSubcmdRunArguments(CmdArgsDeserializeTestSuite):
    @pytest.fixture(scope="function")
    def cmd_arg_data_model(self) -> Type[ParserArguments]:
        return SubcmdRunArguments

    def _given_namespace(self) -> Namespace:
        namespace_args = {
            "subcommand": SubCommand.RestServer,
            SubCommand.RestServer: _Test_SubCommand_Run,
            "config": _Test_Config,
            "app_type": _Test_App_Type,
            "bind": _Bind_Host_And_Port.value,
            "workers": _Workers_Amount.value,
            "log_level": _Log_Level.value,
        }
        return Namespace(**namespace_args)

    def _verify_arg_model(self, argument: SubcmdRunArguments) -> None:
        assert isinstance(argument, SubcmdRunArguments)
        assert argument.subparser_structure == SysArg.parse([SubCommand.RestServer, _Test_SubCommand_Run])
        assert argument.config == _Test_Config
        assert argument.app_type == _Test_App_Type
        assert argument.bind == _Bind_Host_And_Port.value
        assert argument.workers == _Workers_Amount.value
        assert argument.log_level == _Log_Level.value


class TestSubcmdAddArguments(CmdArgsDeserializeTestSuite):
    @pytest.fixture(scope="function")
    def cmd_arg_data_model(self) -> Type[ParserArguments]:
        return SubcmdAddArguments

    def _given_namespace(self) -> Namespace:
        namespace_args = {
            "subcommand": SubCommand.RestServer,
            SubCommand.RestServer: _Test_SubCommand_Add,
            "config_path": _Sample_File_Path,
            "tag": _Test_Tag,
            "api_path": _Test_URL,
            "http_method": _Test_HTTP_Method,
            "parameters": ['{"name": "arg1", "required": false, "default": "val1", "type": "str"}'],
            "response_strategy": _Test_Response_Strategy,
            "response_value": [_Test_HTTP_Resp],
            "base_file_path": _Default_Base_File_Path,
            "base_url": _Base_URL,
            "include_template_config": _Default_Include_Template_Config,
            "dry_run": _Test_Dry_Run,
            "divide_api": _Test_Divide_Api,
            "divide_http": _Test_Divide_Http,
            "divide_http_request": _Test_Divide_Http_Request,
            "divide_http_response": _Test_Divide_Http_Response,
        }
        return Namespace(**namespace_args)

    def _verify_arg_model(self, argument: SubcmdAddArguments) -> None:
        assert isinstance(argument, SubcmdAddArguments)
        assert argument.subparser_structure == SysArg.parse([SubCommand.RestServer, _Test_SubCommand_Add])
        assert argument.config_path == _Sample_File_Path
        assert argument.tag == _Test_Tag
        assert argument.api_path == _Test_URL
        assert argument.http_method == _Test_HTTP_Method
        assert argument.parameters == [{"name": "arg1", "required": False, "default": "val1", "type": "str"}]
        assert argument.response_value == [_Test_HTTP_Resp]
        assert argument.base_file_path == _Default_Base_File_Path
        assert argument.base_url == _Base_URL
        assert argument.include_template_config == _Default_Include_Template_Config
        assert argument.dry_run == _Test_Dry_Run
        assert argument.divide_api == _Test_Divide_Api
        assert argument.divide_http == _Test_Divide_Http
        assert argument.divide_http_request == _Test_Divide_Http_Request
        assert argument.divide_http_response == _Test_Divide_Http_Response


class TestSubcmdGetArguments(CmdArgsDeserializeTestSuite):
    @pytest.fixture(scope="function")
    def cmd_arg_data_model(self) -> Type[ParserArguments]:
        return SubcmdGetArguments

    def _given_namespace(self) -> Namespace:
        namespace_args = {
            "subcommand": SubCommand.RestServer,
            SubCommand.RestServer: _Test_SubCommand_Get,
            "config_path": _Test_Config,
            "show_detail": True,
            "show_as_format": _Show_Detail_As_Format,
            "api_path": _Cmd_Arg_API_Path,
            "http_method": _Cmd_Arg_HTTP_Method,
        }
        return Namespace(**namespace_args)

    def _verify_arg_model(self, argument: SubcmdGetArguments) -> None:
        assert isinstance(argument, SubcmdGetArguments)
        assert argument.subparser_structure == SysArg.parse([SubCommand.RestServer, _Test_SubCommand_Get])
        assert argument.config_path == _Test_Config
        assert argument.show_detail == True
        assert argument.show_as_format == Format[_Show_Detail_As_Format.upper()]
        assert argument.api_path == _Cmd_Arg_API_Path
        assert argument.http_method == _Cmd_Arg_HTTP_Method


class TestSubcmdCheckArguments(CmdArgsDeserializeTestSuite):
    @pytest.fixture(scope="function")
    def cmd_arg_data_model(self) -> Type[ParserArguments]:
        return SubcmdCheckArguments

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
    def test_deserialize(
        self,
        cmd_arg_data_model: Type[ParserArguments],
        stop_if_fail: bool,
        under_test_check_props: check_attrs,
        expected_check_props: expected_check_attrs,
    ):
        namespace = self._given_namespace(stop_if_fail, under_test_check_props, expected_check_props)
        argument = SubcmdCheckArguments.deserialize(namespace)
        self._verify_arg_model(argument, stop_if_fail, under_test_check_props, expected_check_props)

    def _given_namespace(
        self,
        stop_if_fail: bool,
        under_test_check_props: check_attrs,
        expected_check_props: expected_check_attrs,
    ) -> Namespace:
        namespace_args = {
            "subcommand": SubCommand.RestServer,
            SubCommand.RestServer: _Test_SubCommand_Check,
            "config_path": _Test_Config,
            "swagger_doc_url": _Swagger_API_Document_URL,
            "stop_if_fail": stop_if_fail,
            "check_entire_api": under_test_check_props.entire_check,
            "check_api_path": under_test_check_props.api_path,
            "check_api_http_method": under_test_check_props.http_method,
            "check_api_parameters": under_test_check_props.api_parameters,
        }
        return Namespace(**namespace_args)

    def _verify_arg_model(
        self,
        argument: SubcmdCheckArguments,
        stop_if_fail: bool,
        under_test_check_props: check_attrs,
        expected_check_props: expected_check_attrs,
    ) -> None:
        assert isinstance(argument, SubcmdCheckArguments)
        assert argument.subparser_structure == SysArg.parse([SubCommand.RestServer, _Test_SubCommand_Check])
        assert argument.config_path == _Test_Config
        assert argument.swagger_doc_url == _Swagger_API_Document_URL
        assert argument.stop_if_fail is stop_if_fail
        assert argument.check_api_path is expected_check_props.api_path
        assert argument.check_api_http_method is expected_check_props.http_method
        assert argument.check_api_parameters is expected_check_props.api_parameters


class TestSubcmdSampleArguments(CmdArgsDeserializeTestSuite):
    @pytest.fixture(scope="function")
    def cmd_arg_data_model(self) -> Type[ParserArguments]:
        return SubcmdSampleArguments

    def _given_namespace(self) -> Namespace:
        namespace_args = {
            "subcommand": SubCommand.RestServer,
            SubCommand.RestServer: _Test_SubCommand_Sample,
            "generate_sample": _Generate_Sample,
            "print_sample": _Print_Sample,
            "file_path": _Sample_File_Path,
            "sample_config_type": _Sample_Data_Type,
        }
        return Namespace(**namespace_args)

    def _verify_arg_model(self, argument: SubcmdSampleArguments) -> None:
        assert isinstance(argument, SubcmdSampleArguments)
        assert argument.subparser_structure == SysArg.parse([SubCommand.RestServer, _Test_SubCommand_Sample])
        assert argument.generate_sample == _Generate_Sample
        assert argument.print_sample == _Print_Sample
        assert argument.sample_output_path == _Sample_File_Path
        assert argument.sample_config_type == SampleType.ALL


class TestSubcmdPullArguments(CmdArgsDeserializeTestSuite):
    @pytest.fixture(scope="function")
    def cmd_arg_data_model(self) -> Type[ParserArguments]:
        return SubcmdPullArguments

    def _given_namespace(self) -> Namespace:
        namespace_args = {
            "subcommand": SubCommand.RestServer,
            SubCommand.RestServer: _Test_SubCommand_Pull,
            "request_with_https": _Test_Request_With_Https,
            "source": _API_Doc_Source,
            "source_file": _API_Doc_Source_File,
            "config_path": _Test_Config,
            "base_url": _Base_URL,
            "base_file_path": _Default_Base_File_Path,
            "include_template_config": _Default_Include_Template_Config,
            "dry_run": _Test_Dry_Run,
            "divide_api": _Test_Divide_Api,
            "divide_http": _Test_Divide_Http,
            "divide_http_request": _Test_Divide_Http_Request,
            "divide_http_response": _Test_Divide_Http_Response,
        }
        return Namespace(**namespace_args)

    def _verify_arg_model(self, argument: SubcmdPullArguments) -> None:
        assert isinstance(argument, SubcmdPullArguments)
        assert argument.subparser_structure == SysArg.parse([SubCommand.RestServer, _Test_SubCommand_Pull])
        assert argument.request_with_https == _Test_Request_With_Https
        assert argument.source == _API_Doc_Source
        assert argument.source_file == _API_Doc_Source_File
        assert argument.config_path == _Test_Config
        assert argument.base_url == _Base_URL
        assert argument.base_file_path == _Default_Base_File_Path
        assert argument.include_template_config == _Default_Include_Template_Config
        assert argument.dry_run == _Test_Dry_Run
        assert argument.divide_api == _Test_Divide_Api
        assert argument.divide_http == _Test_Divide_Http
        assert argument.divide_http_request == _Test_Divide_Http_Request
        assert argument.divide_http_response == _Test_Divide_Http_Response
