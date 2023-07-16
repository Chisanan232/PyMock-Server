import glob
import os.path
import pathlib
import re
from abc import ABCMeta, abstractmethod
from argparse import ArgumentParser, Namespace
from typing import Callable, List, Optional, Type, Union
from unittest.mock import MagicMock, Mock, call, patch

import pytest

from pymock_api._utils.file_opt import YAML
from pymock_api.command.options import SubCommand, get_all_subcommands
from pymock_api.command.process import (
    BaseCommandProcessor,
    NoSubCmd,
    SubCmdAdd,
    SubCmdCheck,
    SubCmdInspect,
    SubCmdRun,
    make_command_chain,
    run_command_chain,
)
from pymock_api.model import (
    ParserArguments,
    SubcmdCheckArguments,
    SubcmdConfigArguments,
    SubcmdInspectArguments,
    SubcmdRunArguments,
)
from pymock_api.server import ASGIServer, Command, CommandOptions, WSGIServer

from ..._values import (
    _Bind_Host_And_Port,
    _Generate_Sample,
    _Log_Level,
    _Print_Sample,
    _Sample_File_Path,
    _Test_App_Type,
    _Test_Auto_Type,
    _Test_Config,
    _Test_FastAPI_App_Type,
    _Test_SubCommand_Add,
    _Test_SubCommand_Check,
    _Test_SubCommand_Inspect,
    _Test_SubCommand_Run,
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
) -> Union[SubcmdRunArguments, SubcmdConfigArguments, SubcmdCheckArguments, SubcmdInspectArguments, ParserArguments]:
    if subcommand == "run":
        return SubcmdRunArguments(
            subparser_name=subcommand,
            app_type=app_type,
            config=_Test_Config,
            bind=_Bind_Host_And_Port.value,
            workers=_Workers_Amount.value,
            log_level=_Log_Level.value,
        )
    elif subcommand == "config":
        return SubcmdConfigArguments(
            subparser_name=subcommand,
            print_sample=_Print_Sample,
            generate_sample=_Generate_Sample,
            sample_output_path=_Sample_File_Path,
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
    elif subcommand == "inspect":
        return SubcmdInspectArguments(
            subparser_name=subcommand,
            config_path=(config_path or _Test_Config),
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
        FakeYAML.serialize = MagicMock()
        FakeYAML.write = MagicMock()
        mock_parser_arg = SubcmdConfigArguments(
            subparser_name=_Test_SubCommand_Add,
            print_sample=oprint,
            generate_sample=generate,
            sample_output_path=output,
        )

        with patch("builtins.print", autospec=True, side_effect=print) as mock_print:
            with patch("pymock_api.command.config.component.YAML", return_value=FakeYAML) as mock_instantiate_writer:
                cmd_ps(mock_parser_arg)

                mock_instantiate_writer.assert_called_once()
                FakeYAML.serialize.assert_called_once()

                if oprint:
                    mock_print.assert_has_calls([call(f"It will write below content into file {output}:")])
                else:
                    mock_print.assert_not_called()

                if generate:
                    FakeYAML.write.assert_called_once()
                else:
                    FakeYAML.write.assert_not_called()

    def _given_cmd_args_namespace(self) -> Namespace:
        args_namespace = Namespace()
        args_namespace.subcommand = SubCommand.Add
        args_namespace.generate_sample = _Generate_Sample
        args_namespace.print_sample = _Print_Sample
        args_namespace.file_path = _Sample_File_Path
        return args_namespace

    def _given_subcmd(self) -> Optional[str]:
        return SubCommand.Add

    def _expected_argument_type(self) -> Type[SubcmdConfigArguments]:
        return SubcmdConfigArguments


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


class TestSubCmdInspect(BaseCommandProcessorTestSpec):
    @pytest.fixture(scope="function")
    def cmd_ps(self) -> SubCmdInspect:
        return SubCmdInspect()

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
        mock_parser_arg = _given_parser_args(
            subcommand=_Test_SubCommand_Inspect,
            config_path="./test/data/check_test/config/valid/sample-with_general_string_value.yaml",
        )
        cmd_ps(mock_parser_arg)

    def _given_cmd_args_namespace(self) -> Namespace:
        args_namespace = Namespace()
        args_namespace.subcommand = SubCommand.Inspect
        args_namespace.config_path = _Test_Config
        return args_namespace

    def _given_subcmd(self) -> Optional[str]:
        return SubCommand.Inspect

    def _expected_argument_type(self) -> Type[SubcmdInspectArguments]:
        return SubcmdInspectArguments


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
