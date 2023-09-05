import glob
import json
import os.path
import pathlib
import re
from abc import ABCMeta, abstractmethod
from argparse import ArgumentParser, Namespace
from typing import Callable, List, Optional, Type, Union
from unittest.mock import MagicMock, Mock, call, patch

import pytest
from yaml import load as yaml_load

from pymock_api.model.swagger_config import set_component_definition

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Dumper, Loader  # type: ignore

from pymock_api._utils.file_opt import YAML
from pymock_api.command.options import SubCommand, get_all_subcommands
from pymock_api.command.process import (
    BaseCommandProcessor,
    NoSubCmd,
    SubCmdAdd,
    SubCmdCheck,
    SubCmdGet,
    SubCmdPull,
    SubCmdRun,
    SubCmdSample,
    make_command_chain,
    run_command_chain,
)
from pymock_api.model import (
    ParserArguments,
    SubcmdAddArguments,
    SubcmdCheckArguments,
    SubcmdGetArguments,
    SubcmdPullArguments,
    SubcmdRunArguments,
    SubcmdSampleArguments,
    deserialize_swagger_api_config,
)
from pymock_api.model.enums import Format, ResponseStrategy, SampleType
from pymock_api.server import ASGIServer, Command, CommandOptions, WSGIServer

from ..._values import (
    _API_Doc_Source,
    _Base_URL,
    _Bind_Host_And_Port,
    _Cmd_Arg_API_Path,
    _Cmd_Arg_HTTP_Method,
    _Generate_Sample,
    _Log_Level,
    _Print_Sample,
    _Sample_Data_Type,
    _Sample_File_Path,
    _Show_Detail_As_Format,
    _Test_App_Type,
    _Test_Auto_Type,
    _Test_Config,
    _Test_FastAPI_App_Type,
    _Test_HTTP_Method,
    _Test_HTTP_Resp,
    _Test_Response_Strategy,
    _Test_SubCommand_Add,
    _Test_SubCommand_Check,
    _Test_SubCommand_Get,
    _Test_SubCommand_Pull,
    _Test_SubCommand_Run,
    _Test_SubCommand_Sample,
    _Test_URL,
    _Workers_Amount,
)

_Fake_SubCmd: str = "pytest-subcmd"
_Fake_Duplicated_SubCmd: str = "pytest-duplicated"
_No_SubCmd_Amt: int = 1
_Fake_Amt: int = 1


def _given_parser_args(
    subcommand: str = None,
    app_type: str = None,
    config_path: str = None,
    swagger_doc_url: str = None,
    stop_if_fail: bool = True,
    get_api_path: str = _Cmd_Arg_API_Path,
) -> Union[SubcmdRunArguments, SubcmdAddArguments, SubcmdCheckArguments, SubcmdGetArguments, ParserArguments]:
    if subcommand == "run":
        return SubcmdRunArguments(
            subparser_name=subcommand,
            app_type=app_type,
            config=_Test_Config,
            bind=_Bind_Host_And_Port.value,
            workers=_Workers_Amount.value,
            log_level=_Log_Level.value,
        )
    elif subcommand == "add":
        return SubcmdAddArguments(
            subparser_name=subcommand,
            api_config_path=_Sample_File_Path,
            api_path=_Test_URL,
            http_method=_Test_HTTP_Method,
            parameters=[],
            response_strategy=ResponseStrategy.STRING,
            response_value=_Test_HTTP_Resp,
        )
    elif subcommand == "check":
        return SubcmdCheckArguments(
            subparser_name=subcommand,
            config_path=(config_path or _Test_Config),
            swagger_doc_url=swagger_doc_url,
            stop_if_fail=stop_if_fail,
            check_api_path=True,
            check_api_parameters=True,
            check_api_http_method=True,
        )
    elif subcommand == "get":
        return SubcmdGetArguments(
            subparser_name=subcommand,
            config_path=(config_path or _Test_Config),
            show_detail=True,
            show_as_format=Format[_Show_Detail_As_Format.upper()],
            api_path=get_api_path,
            http_method=_Cmd_Arg_HTTP_Method,
        )
    else:
        return ParserArguments(
            subparser_name=None,
        )


def _given_command_option() -> CommandOptions:
    return CommandOptions(bind=_Bind_Host_And_Port.value, workers=_Workers_Amount.value, log_level=_Log_Level.value)


def _given_command(app_type: str) -> Command:
    mock_parser_arg = _given_parser_args(subcommand="run", app_type=app_type)
    mock_cmd_option_obj = _given_command_option()
    return Command(entry_point="SGI tool command", app=mock_parser_arg.app_type, options=mock_cmd_option_obj)


class FakeYAML(YAML):
    pass


class FakeCommandProcess(BaseCommandProcessor):
    responsible_subcommand: str = _Fake_SubCmd

    def _parse_process(self, parser: ArgumentParser, cmd_args: Optional[List[str]] = None) -> ParserArguments:
        return

    def _run(self, args: ParserArguments) -> None:
        pass


class TestSubCmdProcessChain:
    @pytest.fixture(scope="class")
    def cmd_processor(self) -> FakeCommandProcess:
        return FakeCommandProcess()

    def test_next(self, cmd_processor: FakeCommandProcess):
        next_cmd = cmd_processor._next
        assert (next_cmd != cmd_processor) and (next_cmd is not cmd_processor)

    def test_next_exceed_length(self, cmd_processor: FakeCommandProcess):
        with pytest.raises(StopIteration):
            for _ in range(len(make_command_chain()) + 1):
                assert cmd_processor._next

    @pytest.mark.parametrize(
        ("subcmd", "expected_result"),
        [
            (_Fake_SubCmd, True),
            ("not-mapping-subcmd", False),
        ],
    )
    def test_is_responsible(self, subcmd: str, expected_result: bool, cmd_processor: FakeCommandProcess):
        arg = ParserArguments(subparser_name=subcmd)
        is_responsible = cmd_processor._is_responsible(subcmd=None, args=arg)
        assert is_responsible is expected_result

    @pytest.mark.parametrize(
        ("chk_result", "should_dispatch"),
        [
            (True, False),
            (False, True),
        ],
    )
    def test_process(self, chk_result: bool, should_dispatch: bool, cmd_processor: FakeCommandProcess):
        cmd_processor._is_responsible = MagicMock(return_value=chk_result)
        cmd_processor._run = MagicMock()

        arg = ParserArguments(subparser_name=_Fake_SubCmd)
        cmd_processor.process(arg)

        cmd_processor._is_responsible.assert_called_once_with(subcmd=None, args=arg)
        if should_dispatch:
            cmd_processor._run.assert_not_called()
        else:
            cmd_processor._run.assert_called_once_with(arg)

    @patch("copy.copy")
    def test_copy(self, mock_copy: Mock, cmd_processor: FakeCommandProcess):
        cmd_processor.copy()
        mock_copy.assert_called_once_with(cmd_processor)


class BaseCommandProcessorTestSpec(metaclass=ABCMeta):
    @pytest.fixture(scope="function")
    @abstractmethod
    def cmd_ps(self) -> BaseCommandProcessor:
        pass

    @pytest.fixture(scope="function")
    def object_under_test(self, cmd_ps: BaseCommandProcessor) -> Callable:
        return cmd_ps.process

    @pytest.fixture(scope="function")
    def entry_point_under_test(self) -> Callable:
        return run_command_chain

    def test_with_command_processor(self, object_under_test: Callable, **kwargs):
        kwargs["cmd_ps"] = object_under_test
        self._test_process(**kwargs)

    def test_with_run_entry_point(self, entry_point_under_test: Callable, **kwargs):
        kwargs["cmd_ps"] = entry_point_under_test
        self._test_process(**kwargs)

    @abstractmethod
    def _test_process(self, **kwargs):
        pass

    def test_parse(self, cmd_ps: BaseCommandProcessor):
        args_namespace = self._given_cmd_args_namespace()
        cmd_ps._parse_cmd_arguments = MagicMock(return_value=args_namespace)

        api_parser = MagicMock()
        api_parser.subcommand = self._given_subcmd()
        cmd_ps.mock_api_parser = api_parser

        arguments = cmd_ps.parse(parser=cmd_ps.mock_api_parser.parse(), cmd_args=None)

        assert isinstance(arguments, self._expected_argument_type())

    @abstractmethod
    def _given_cmd_args_namespace(self) -> Namespace:
        pass

    @abstractmethod
    def _given_subcmd(self) -> Optional[str]:
        pass

    @abstractmethod
    def _expected_argument_type(self) -> Type[Union[Namespace, ParserArguments]]:
        pass


class TestNoSubCmd(BaseCommandProcessorTestSpec):
    @pytest.fixture(scope="function")
    def cmd_ps(self) -> NoSubCmd:
        return NoSubCmd()

    def test_with_command_processor(self, object_under_test: Callable, **kwargs):
        kwargs = {
            "cmd_ps": object_under_test,
        }
        self._test_process(**kwargs)

    def test_with_run_entry_point(self, entry_point_under_test: Callable, **kwargs):
        kwargs = {
            "cmd_ps": entry_point_under_test,
        }
        self._test_process(**kwargs)

    def _test_process(self, cmd_ps: Callable):
        mock_parser_arg = _given_parser_args(subcommand=None)
        command = _given_command(app_type="Python web library")
        command.run = MagicMock()

        with patch.object(WSGIServer, "generate", return_value=command) as mock_sgi_generate:
            cmd_ps(mock_parser_arg)
            mock_sgi_generate.assert_not_called()
            command.run.assert_not_called()

    def _given_cmd_args_namespace(self) -> Namespace:
        args_namespace = Namespace()
        args_namespace.subcommand = None
        return args_namespace

    def _given_subcmd(self) -> Optional[str]:
        return None

    def _expected_argument_type(self) -> Type[Namespace]:
        return Namespace


class TestSubCmdRun(BaseCommandProcessorTestSpec):
    @pytest.fixture(scope="function")
    def cmd_ps(self) -> SubCmdRun:
        return SubCmdRun()

    @pytest.mark.parametrize(
        ("app_type", "should_raise_exc"),
        [
            (_Test_App_Type, False),
            (_Test_FastAPI_App_Type, False),
            (_Test_Auto_Type, False),
            ("invalid app-type which is not a Python web library or framework", True),
        ],
    )
    def test_with_command_processor(self, app_type: str, should_raise_exc: bool, object_under_test: Callable):
        kwargs = {
            "app_type": app_type,
            "should_raise_exc": should_raise_exc,
            "cmd_ps": object_under_test,
        }
        self._test_process(**kwargs)

    @pytest.mark.parametrize(
        ("app_type", "should_raise_exc"),
        [
            (_Test_App_Type, False),
            (_Test_FastAPI_App_Type, False),
            (_Test_Auto_Type, False),
            ("invalid app-type which is not a Python web library or framework", True),
        ],
    )
    def test_with_run_entry_point(self, app_type: str, should_raise_exc: bool, entry_point_under_test: Callable):
        kwargs = {
            "app_type": app_type,
            "should_raise_exc": should_raise_exc,
            "cmd_ps": entry_point_under_test,
        }
        self._test_process(**kwargs)

    def _test_process(self, app_type: str, should_raise_exc: bool, cmd_ps: Callable):
        mock_parser_arg = _given_parser_args(subcommand=_Test_SubCommand_Run, app_type=app_type)
        command = _given_command(app_type="Python web library")
        command.run = MagicMock()

        with patch.object(ASGIServer, "generate", return_value=command) as mock_asgi_generate:
            with patch.object(WSGIServer, "generate", return_value=command) as mock_wsgi_generate:
                if should_raise_exc:
                    with pytest.raises(ValueError) as exc_info:
                        cmd_ps(mock_parser_arg)
                    assert "Invalid value" in str(exc_info.value)
                    mock_asgi_generate.assert_not_called()
                    mock_wsgi_generate.assert_not_called()
                    command.run.assert_not_called()
                else:
                    cmd_ps(mock_parser_arg)
                    if app_type == "auto":
                        mock_asgi_generate.assert_called_once_with(mock_parser_arg)
                        mock_wsgi_generate.assert_not_called()
                    elif app_type == "flask":
                        mock_asgi_generate.assert_not_called()
                        mock_wsgi_generate.assert_called_once_with(mock_parser_arg)
                    elif app_type == "fastapi":
                        mock_asgi_generate.assert_called_once_with(mock_parser_arg)
                        mock_wsgi_generate.assert_not_called()
                    else:
                        assert False, "Please use valid *app-type* option value."
                    command.run.assert_called_once()

    def _given_cmd_args_namespace(self) -> Namespace:
        args_namespace = Namespace()
        args_namespace.subcommand = SubCommand.Run
        args_namespace.config = _Test_Config
        args_namespace.app_type = _Test_App_Type
        args_namespace.bind = _Bind_Host_And_Port.value
        args_namespace.workers = _Workers_Amount.value
        args_namespace.log_level = _Log_Level.value
        return args_namespace

    def _given_subcmd(self) -> Optional[str]:
        return SubCommand.Run

    def _expected_argument_type(self) -> Type[SubcmdRunArguments]:
        return SubcmdRunArguments


class TestSubCmdAdd(BaseCommandProcessorTestSpec):
    @pytest.fixture(scope="function")
    def cmd_ps(self) -> SubCmdAdd:
        return SubCmdAdd()

    @pytest.mark.parametrize(
        ("url_path", "method", "params", "response_strategy", "response_value"),
        [
            ("/foo", "", [], _Test_Response_Strategy, [""]),
            ("/foo", "GET", [], _Test_Response_Strategy, [""]),
            ("/foo", "POST", [], _Test_Response_Strategy, ["This is PyTest response"]),
            ("/foo", "PUT", [], _Test_Response_Strategy, ["Wow testing."]),
        ],
    )
    def test_with_command_processor(
        self,
        url_path: str,
        method: str,
        params: List[dict],
        response_strategy: ResponseStrategy,
        response_value: List[str],
        object_under_test: Callable,
    ):
        kwargs = {
            "url_path": url_path,
            "method": method,
            "params": params,
            "response_strategy": response_strategy,
            "response_value": response_value,
            "cmd_ps": object_under_test,
        }
        self._test_process(**kwargs)

    @pytest.mark.parametrize(
        ("url_path", "method", "params", "response_strategy", "response_value"),
        [
            ("/foo", "", "", _Test_Response_Strategy, [""]),
            ("/foo", "GET", [], _Test_Response_Strategy, [""]),
            ("/foo", "POST", [], _Test_Response_Strategy, ["This is PyTest response"]),
            ("/foo", "PUT", [], _Test_Response_Strategy, ["Wow testing."]),
        ],
    )
    def test_with_run_entry_point(
        self,
        url_path: str,
        method: str,
        params: List[dict],
        response_strategy: ResponseStrategy,
        response_value: List[str],
        entry_point_under_test: Callable,
    ):
        kwargs = {
            "url_path": url_path,
            "method": method,
            "params": params,
            "response_strategy": response_strategy,
            "response_value": response_value,
            "cmd_ps": entry_point_under_test,
        }
        self._test_process(**kwargs)

    def _test_process(
        self,
        url_path: str,
        method: str,
        params: List[dict],
        response_strategy: ResponseStrategy,
        response_value: List[str],
        cmd_ps: Callable,
    ):
        FakeYAML.serialize = MagicMock()
        FakeYAML.write = MagicMock()
        mock_parser_arg = SubcmdAddArguments(
            subparser_name=_Test_SubCommand_Add,
            api_config_path=_Test_Config,
            api_path=url_path,
            http_method=method,
            parameters=params,
            response_strategy=response_strategy,
            response_value=response_value,
        )

        with patch("pymock_api.command.add.component.YAML", return_value=FakeYAML) as mock_instantiate_writer:
            cmd_ps(mock_parser_arg)

            mock_instantiate_writer.assert_called_once()
            FakeYAML.write.assert_called_once()

    def _given_cmd_args_namespace(self) -> Namespace:
        args_namespace = Namespace()
        args_namespace.subcommand = SubCommand.Add
        args_namespace.api_config_path = ""
        args_namespace.api_path = _Test_URL
        args_namespace.http_method = _Test_HTTP_Method
        args_namespace.parameters = ""
        args_namespace.response_strategy = _Test_Response_Strategy
        args_namespace.response_value = _Test_HTTP_Resp
        return args_namespace

    def _given_subcmd(self) -> Optional[str]:
        return SubCommand.Add

    def _expected_argument_type(self) -> Type[SubcmdAddArguments]:
        return SubcmdAddArguments


API_NAME: str = "google_home"
YAML_PATHS_WITH_EX_CODE: List[tuple] = []


def _get_all_yaml(config_type: str, exit_code: Union[str, int]) -> None:
    yaml_dir = os.path.join(
        str(pathlib.Path(__file__).parent.parent.parent), "data", "check_test", "config", config_type, "*.yaml"
    )
    global YAML_PATHS_WITH_EX_CODE
    for yaml_config_path in glob.glob(yaml_dir):
        expected_exit_code = exit_code if isinstance(exit_code, str) and exit_code.isdigit() else str(exit_code)
        for stop_if_fail in (False, True):
            one_test_scenario = (yaml_config_path, stop_if_fail, expected_exit_code)
            YAML_PATHS_WITH_EX_CODE.append(one_test_scenario)


def _expected_err_msg(file: str) -> str:
    file = file.split("/")[-1] if "/" in file else file
    file_name: List[str] = file.split("-")
    config_key = file_name[0].replace("no_", "").replace(".yaml", "").replace("_", ".").replace("api.name", API_NAME)
    return f"Configuration *{config_key}* content"


_get_all_yaml(config_type="valid", exit_code=0)
_get_all_yaml(config_type="invalid", exit_code=1)


class TestSubCmdCheck(BaseCommandProcessorTestSpec):
    @pytest.fixture(scope="function")
    def cmd_ps(self) -> SubCmdCheck:
        return SubCmdCheck()

    @pytest.mark.parametrize(
        ("config_path", "stop_if_fail", "expected_exit_code"),
        YAML_PATHS_WITH_EX_CODE,
    )
    def test_with_command_processor(
        self, config_path: str, stop_if_fail: bool, expected_exit_code: str, object_under_test: Callable
    ):
        kwargs = {
            "config_path": config_path,
            "stop_if_fail": stop_if_fail,
            "expected_exit_code": expected_exit_code,
            "cmd_ps": object_under_test,
        }
        self._test_process(**kwargs)

    @pytest.mark.parametrize(
        ("config_path", "stop_if_fail", "expected_exit_code"),
        YAML_PATHS_WITH_EX_CODE,
    )
    def test_with_run_entry_point(
        self, config_path: str, stop_if_fail: bool, expected_exit_code: str, entry_point_under_test: Callable
    ):
        kwargs = {
            "config_path": config_path,
            "stop_if_fail": stop_if_fail,
            "expected_exit_code": expected_exit_code,
            "cmd_ps": entry_point_under_test,
        }
        self._test_process(**kwargs)

    def _test_process(self, config_path: str, stop_if_fail: bool, expected_exit_code: str, cmd_ps: Callable):
        mock_parser_arg = _given_parser_args(
            subcommand=_Test_SubCommand_Check, config_path=config_path, stop_if_fail=stop_if_fail
        )
        with pytest.raises(SystemExit) as exc_info:
            cmd_ps(mock_parser_arg)
        assert expected_exit_code in str(exc_info.value)
        # TODO: Add one more checking of the error message content with function *_expected_err_msg*

    def _given_cmd_args_namespace(self) -> Namespace:
        args_namespace = Namespace()
        args_namespace.subcommand = SubCommand.Check
        args_namespace.config_path = _Test_Config
        args_namespace.swagger_doc_url = "http://127.0.0.1:8080/docs"
        args_namespace.stop_if_fail = True
        args_namespace.check_api_path = True
        args_namespace.check_api_http_method = True
        args_namespace.check_api_parameters = True
        return args_namespace

    def _given_subcmd(self) -> Optional[str]:
        return SubCommand.Check

    def _expected_argument_type(self) -> Type[SubcmdCheckArguments]:
        return SubcmdCheckArguments


GET_YAML_PATHS_WITH_EX_CODE: List[tuple] = []


def _get_all_yaml_for_subcmd_get(
    get_api_path: str, is_valid_config: bool, exit_code: Union[str, int], acceptable_error: bool = None
) -> None:
    is_valid_path = "valid" if is_valid_config else "invalid"
    if is_valid_config is False and acceptable_error is not None:
        config_folder = "warn" if acceptable_error else "error"
        entire_config_path = (
            str(pathlib.Path(__file__).parent.parent.parent),
            "data",
            "get_test",
            is_valid_path,
            config_folder,
            "*.yaml",
        )
    else:
        entire_config_path = (
            str(pathlib.Path(__file__).parent.parent.parent),
            "data",
            "get_test",
            is_valid_path,
            "*.yaml",
        )
    yaml_dir = os.path.join(*entire_config_path)
    global GET_YAML_PATHS_WITH_EX_CODE
    for yaml_config_path in glob.glob(yaml_dir):
        expected_exit_code = exit_code if isinstance(exit_code, str) and exit_code.isdigit() else str(exit_code)
        one_test_scenario = (yaml_config_path, get_api_path, expected_exit_code)
        GET_YAML_PATHS_WITH_EX_CODE.append(one_test_scenario)


# With valid configuration
_get_all_yaml_for_subcmd_get(get_api_path="/foo-home", is_valid_config=True, exit_code=0)
_get_all_yaml_for_subcmd_get(get_api_path="/not-exist-api", is_valid_config=True, exit_code=1)

# With invalid configuration
_get_all_yaml_for_subcmd_get(get_api_path="/foo-home", is_valid_config=False, acceptable_error=True, exit_code=0)
_get_all_yaml_for_subcmd_get(get_api_path="/foo-home", is_valid_config=False, acceptable_error=False, exit_code=1)
_get_all_yaml_for_subcmd_get(get_api_path="/not-exist-api", is_valid_config=False, acceptable_error=True, exit_code=1)
_get_all_yaml_for_subcmd_get(get_api_path="/not-exist-api", is_valid_config=False, acceptable_error=False, exit_code=1)


class TestSubCmdGet(BaseCommandProcessorTestSpec):
    @pytest.fixture(scope="function")
    def cmd_ps(self) -> SubCmdGet:
        return SubCmdGet()

    @pytest.mark.parametrize(
        ("yaml_config_path", "get_api_path", "expected_exit_code"),
        GET_YAML_PATHS_WITH_EX_CODE,
    )
    def test_with_command_processor(
        self, yaml_config_path: str, get_api_path: str, expected_exit_code: int, object_under_test: Callable, **kwargs
    ):
        kwargs = {
            "yaml_config_path": yaml_config_path,
            "get_api_path": get_api_path,
            "expected_exit_code": expected_exit_code,
            "cmd_ps": object_under_test,
        }
        self._test_process(**kwargs)

    @pytest.mark.parametrize(
        ("yaml_config_path", "get_api_path", "expected_exit_code"),
        GET_YAML_PATHS_WITH_EX_CODE,
    )
    def test_with_run_entry_point(
        self,
        yaml_config_path: str,
        get_api_path: str,
        expected_exit_code: int,
        entry_point_under_test: Callable,
        **kwargs,
    ):
        kwargs = {
            "yaml_config_path": yaml_config_path,
            "get_api_path": get_api_path,
            "expected_exit_code": expected_exit_code,
            "cmd_ps": entry_point_under_test,
        }
        self._test_process(**kwargs)

    def _test_process(self, yaml_config_path: str, get_api_path: str, expected_exit_code: int, cmd_ps: Callable):
        mock_parser_arg = _given_parser_args(
            subcommand=_Test_SubCommand_Get, config_path=yaml_config_path, get_api_path=get_api_path
        )
        with pytest.raises(SystemExit) as exc_info:
            cmd_ps(mock_parser_arg)
        assert str(expected_exit_code) == str(exc_info.value)

    def _given_cmd_args_namespace(self) -> Namespace:
        args_namespace = Namespace()
        args_namespace.subcommand = SubCommand.Get
        args_namespace.config_path = _Test_Config
        args_namespace.show_detail = True
        args_namespace.show_as_format = _Show_Detail_As_Format
        args_namespace.api_path = _Cmd_Arg_API_Path
        args_namespace.http_method = _Cmd_Arg_HTTP_Method
        return args_namespace

    def _given_subcmd(self) -> Optional[str]:
        return SubCommand.Get

    def _expected_argument_type(self) -> Type[SubcmdGetArguments]:
        return SubcmdGetArguments


class TestSubCmdSample(BaseCommandProcessorTestSpec):
    @pytest.fixture(scope="function")
    def cmd_ps(self) -> SubCmdSample:
        return SubCmdSample()

    @pytest.mark.parametrize(
        ("oprint", "generate", "output"),
        [
            (False, False, "test-api.yaml"),
            (True, False, "test-api.yaml"),
            (False, True, "test-api.yaml"),
            (True, True, "test-api.yaml"),
        ],
    )
    def test_with_command_processor(self, oprint: bool, generate: bool, output: str, object_under_test: Callable):
        kwargs = {
            "oprint": oprint,
            "generate": generate,
            "output": output,
            "cmd_ps": object_under_test,
        }
        self._test_process(**kwargs)

    @pytest.mark.parametrize(
        ("oprint", "generate", "output"),
        [
            (False, False, "test-api.yaml"),
            (True, False, "test-api.yaml"),
            (False, True, "test-api.yaml"),
            (True, True, "test-api.yaml"),
        ],
    )
    def test_with_run_entry_point(self, oprint: bool, generate: bool, output: str, entry_point_under_test: Callable):
        kwargs = {
            "oprint": oprint,
            "generate": generate,
            "output": output,
            "cmd_ps": entry_point_under_test,
        }
        self._test_process(**kwargs)

    def _test_process(self, oprint: bool, generate: bool, output: str, cmd_ps: Callable):
        sample_config = {
            "name": "PyTest",
        }
        FakeYAML.serialize = MagicMock(return_value=f"{sample_config}")
        FakeYAML.write = MagicMock()
        mock_parser_arg = SubcmdSampleArguments(
            subparser_name=_Test_SubCommand_Sample,
            print_sample=oprint,
            generate_sample=generate,
            sample_output_path=output,
            sample_config_type=SampleType.ALL,
        )

        with patch("builtins.print", autospec=True, side_effect=print) as mock_print:
            with patch(
                "pymock_api.command.sample.component.get_sample_by_type", return_value=sample_config
            ) as mock_get_sample_by_type:
                with patch(
                    "pymock_api.command.sample.component.YAML", return_value=FakeYAML
                ) as mock_instantiate_writer:
                    cmd_ps(mock_parser_arg)

                    mock_instantiate_writer.assert_called_once()
                    mock_get_sample_by_type.assert_called_once_with(mock_parser_arg.sample_config_type)
                    FakeYAML.serialize.assert_called_once()

                    if oprint and generate:
                        mock_print.assert_has_calls(
                            [
                                call(f"{sample_config}"),
                                call(f"🍻  Write sample configuration into file {output}."),
                            ]
                        )
                        FakeYAML.write.assert_called_once()
                    elif oprint and not generate:
                        mock_print.assert_has_calls(
                            [
                                call(f"{sample_config}"),
                            ]
                        )
                        FakeYAML.write.assert_not_called()
                    elif not oprint and generate:
                        mock_print.assert_has_calls(
                            [
                                call(f"🍻  Write sample configuration into file {output}."),
                            ]
                        )
                        FakeYAML.write.assert_called_once()
                    else:
                        mock_print.assert_not_called()
                        FakeYAML.write.assert_not_called()

    def _given_cmd_args_namespace(self) -> Namespace:
        args_namespace = Namespace()
        args_namespace.subcommand = SubCommand.Sample
        args_namespace.generate_sample = _Generate_Sample
        args_namespace.print_sample = _Print_Sample
        args_namespace.file_path = _Sample_File_Path
        args_namespace.sample_config_type = _Sample_Data_Type
        return args_namespace

    def _given_subcmd(self) -> Optional[str]:
        return SubCommand.Sample

    def _expected_argument_type(self) -> Type[SubcmdSampleArguments]:
        return SubcmdSampleArguments

    def test__parse_process_with_invalid_type(self, cmd_ps: SubCmdSample):
        cmd_arg_namespace = self._given_cmd_args_namespace()
        cmd_arg_namespace.sample_config_type = "invalid_type"
        parser = Mock()
        cmd_args = Mock()
        with patch.object(cmd_ps, "_parse_cmd_arguments", return_value=cmd_arg_namespace) as mock_parse_cmd_arguments:
            with pytest.raises(SystemExit) as exc_info:
                cmd_ps._parse_process(parser, cmd_args)
            mock_parse_cmd_arguments.assert_called_once_with(parser, cmd_args)
            assert str(exc_info.value) == "1"


PULL_YAML_PATHS_WITH_CONFIG: List[tuple] = []


def _get_all_yaml_for_subcmd_pull() -> None:
    def _get_path(data_type: str, file_extension: str) -> str:
        return os.path.join(
            str(pathlib.Path(__file__).parent.parent.parent),
            "data",
            "pull_test",
            data_type,
            f"*.{file_extension}",
        )

    config_yaml_path = _get_path("config", "yaml")
    swagger_json_path = _get_path("swagger", "json")

    global PULL_YAML_PATHS_WITH_CONFIG
    for yaml_config_path, json_path in zip(sorted(glob.glob(config_yaml_path)), sorted(glob.glob(swagger_json_path))):
        one_test_scenario = (json_path, yaml_config_path)
        PULL_YAML_PATHS_WITH_CONFIG.append(one_test_scenario)


_get_all_yaml_for_subcmd_pull()


class TestSubCmdPull(BaseCommandProcessorTestSpec):
    @pytest.fixture(scope="function")
    def cmd_ps(self) -> SubCmdPull:
        return SubCmdPull()

    @pytest.mark.parametrize(
        ("swagger_config", "expected_config"),
        PULL_YAML_PATHS_WITH_CONFIG,
    )
    def test_with_command_processor(self, swagger_config: str, expected_config: str, object_under_test: Callable):
        kwargs = {
            "swagger_config": swagger_config,
            "expected_config": expected_config,
            "cmd_ps": object_under_test,
        }
        self._test_process(**kwargs)

    @pytest.mark.parametrize(
        ("swagger_config", "expected_config"),
        PULL_YAML_PATHS_WITH_CONFIG,
    )
    def test_with_run_entry_point(self, swagger_config: str, expected_config: str, entry_point_under_test: Callable):
        kwargs = {
            "swagger_config": swagger_config,
            "expected_config": expected_config,
            "cmd_ps": entry_point_under_test,
        }
        self._test_process(**kwargs)

    def _test_process(self, swagger_config: str, expected_config: str, cmd_ps: Callable):
        FakeYAML.write = MagicMock()
        base_url = _Base_URL if ("has-base" in swagger_config and "has-base" in expected_config) else ""
        mock_parser_arg = SubcmdPullArguments(
            subparser_name=_Test_SubCommand_Pull,
            source=_API_Doc_Source,
            base_url=base_url,
            config_path=_Test_Config,
        )

        with open(swagger_config, "r") as file:
            swagger_json_data = json.loads(file.read())

        with open(expected_config, "r") as file:
            expected_config_data = yaml_load(file, Loader=Loader)

        set_component_definition(swagger_json_data)
        with patch("pymock_api.command.pull.component.YAML", return_value=FakeYAML) as mock_instantiate_writer:
            with patch(
                "pymock_api.command.pull.component.URLLibHTTPClient.request", return_value=swagger_json_data
            ) as mock_swagger_request:
                # Run target function
                print(f"[DEBUG in test] run target function: {cmd_ps}")
                cmd_ps(mock_parser_arg)

                mock_instantiate_writer.assert_called_once()
                mock_swagger_request.assert_called_once_with(method="GET", url=f"http://{_API_Doc_Source}/")

                # Run one core logic of target function
                print(f"[DEBUG in test] run one core logic of target function")
                debug_swagger_api_config = deserialize_swagger_api_config(swagger_json_data)
                print(f"[DEBUG in test] debug_swagger_api_config: {debug_swagger_api_config}")
                debug_api_config = debug_swagger_api_config.to_api_config(mock_parser_arg.base_url)
                print(f"[DEBUG in test] debug_api_config: {debug_api_config}")
                print(f"[DEBUG in test] debug_api_config.apis.apis: {debug_api_config.apis.apis}")
                print(f"[DEBUG in test] debug_api_config.apis.apis['get_foo']: {debug_api_config.apis.apis['get_foo']}")
                print(
                    f"[DEBUG in test] debug_api_config.apis.apis['get_foo'].http.request: {debug_api_config.apis.apis['get_foo'].http.request}"
                )
                print(
                    f"[DEBUG in test] debug_api_config.apis.apis['get_foo'].http.response: {debug_api_config.apis.apis['get_foo'].http.response}"
                )
                print(f"[DEBUG in test] debug_api_config.serialize(): {debug_api_config.serialize()}")
                confirm_expected_config_data = (
                    deserialize_swagger_api_config(swagger_json_data)
                    .to_api_config(mock_parser_arg.base_url)
                    .serialize()
                )
                print(f"[DEBUG in test] expected_config_data: {expected_config_data}")
                print(f"[DEBUG in test] confirm_expected_config_data: {confirm_expected_config_data}")
                assert expected_config_data["name"] == confirm_expected_config_data["name"]
                assert expected_config_data["description"] == confirm_expected_config_data["description"]
                assert len(expected_config_data["mocked_apis"].keys()) == len(
                    confirm_expected_config_data["mocked_apis"].keys()
                )
                expected_config_data_keys = sorted(expected_config_data["mocked_apis"].keys())
                confirm_expected_config_data_keys = sorted(confirm_expected_config_data["mocked_apis"].keys())
                for expected_key, confirm_expected_key in zip(
                    expected_config_data_keys, confirm_expected_config_data_keys
                ):
                    assert expected_key == confirm_expected_key
                    if expected_key != "base":
                        # Verify mock API URL
                        assert (
                            expected_config_data["mocked_apis"][expected_key]["url"]
                            == confirm_expected_config_data["mocked_apis"][confirm_expected_key]["url"]
                        )
                        # Verify mock API request properties - HTTP method
                        assert (
                            expected_config_data["mocked_apis"][expected_key]["http"]["request"]["method"]
                            == confirm_expected_config_data["mocked_apis"][confirm_expected_key]["http"]["request"][
                                "method"
                            ]
                        )
                        # Verify mock API request properties - request parameters
                        assert (
                            expected_config_data["mocked_apis"][expected_key]["http"]["request"]["parameters"]
                            == confirm_expected_config_data["mocked_apis"][confirm_expected_key]["http"]["request"][
                                "parameters"
                            ]
                        )
                        # Verify mock API response properties
                        assert (
                            expected_config_data["mocked_apis"][expected_key]["http"]["response"]["strategy"]
                            == confirm_expected_config_data["mocked_apis"][confirm_expected_key]["http"]["response"][
                                "strategy"
                            ]
                        )
                        assert expected_config_data["mocked_apis"][expected_key]["http"]["response"].get(
                            "value", None
                        ) == confirm_expected_config_data["mocked_apis"][confirm_expected_key]["http"]["response"].get(
                            "value", None
                        )
                        assert expected_config_data["mocked_apis"][expected_key]["http"]["response"].get(
                            "path", None
                        ) == confirm_expected_config_data["mocked_apis"][confirm_expected_key]["http"]["response"].get(
                            "path", None
                        )
                        assert expected_config_data["mocked_apis"][expected_key]["http"]["response"].get(
                            "properties", None
                        ) == confirm_expected_config_data["mocked_apis"][confirm_expected_key]["http"]["response"].get(
                            "properties", None
                        )
                    else:
                        # Verify base info
                        assert (
                            expected_config_data["mocked_apis"][expected_key]
                            == confirm_expected_config_data["mocked_apis"][confirm_expected_key]
                        )

                FakeYAML.write.assert_called_once_with(path=_Test_Config, config=expected_config_data)

    def _given_cmd_args_namespace(self) -> Namespace:
        args_namespace = Namespace()
        args_namespace.subcommand = SubCommand.Pull
        args_namespace.source = _API_Doc_Source
        args_namespace.base_url = _Base_URL
        args_namespace.config_path = _Test_Config
        return args_namespace

    def _given_subcmd(self) -> Optional[str]:
        return SubCommand.Pull

    def _expected_argument_type(self) -> Type[SubcmdPullArguments]:
        return SubcmdPullArguments


def test_make_command_chain():
    assert len(get_all_subcommands()) == len(make_command_chain()) - _No_SubCmd_Amt - _Fake_Amt


def test_make_command_chain_if_duplicated_subcmd():
    class FakeCmdPS(BaseCommandProcessor):
        responsible_subcommand: str = _Fake_Duplicated_SubCmd

        def run(self, args: ParserArguments) -> None:
            pass

    class FakeDuplicatedCmdPS(BaseCommandProcessor):
        responsible_subcommand: str = _Fake_Duplicated_SubCmd

        def run(self, args: ParserArguments) -> None:
            pass

    with pytest.raises(ValueError) as exc_info:
        make_command_chain()
    assert re.search(r"subcommand.{1,64}has been used", str(exc_info.value), re.IGNORECASE)

    # Remove the invalid object for test could run finely.
    from pymock_api.command.process import _COMMAND_CHAIN

    _COMMAND_CHAIN.pop(-1)
