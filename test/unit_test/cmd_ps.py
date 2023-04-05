import re
from abc import ABCMeta, abstractmethod
from typing import Callable
from unittest.mock import MagicMock, Mock, call, patch

import pytest

from pymock_api.cmd import get_all_subcommands
from pymock_api.cmd_ps import (
    BaseCommandProcessor,
    NoSubCmd,
    SubCmdConfig,
    SubCmdRun,
    make_command_chain,
    run_command_chain,
)
from pymock_api.model import ParserArguments, SubcmdConfigArguments
from pymock_api.server import ASGIServer, WSGIServer

from .._values import _Test_App_Type, _Test_FastAPI_App_Type
from .runner import FakeYAML, _given_command, _given_parser_args

_Fake_SubCmd: str = "pytest-subcmd"
_Fake_Duplicated_SubCmd: str = "pytest-duplicated"
_No_SubCmd_Amt: int = 1
_Fake_Amt: int = 1


class FakeCommandProcess(BaseCommandProcessor):
    responsible_subcommand: str = _Fake_SubCmd

    def run(self, args: ParserArguments) -> None:
        pass


class TestSubCmdProcessChain:
    @pytest.fixture(scope="class")
    def cmd_processor(self) -> FakeCommandProcess:
        return FakeCommandProcess()

    def test_next(self, cmd_processor: FakeCommandProcess):
        next_cmd = cmd_processor.next
        assert (next_cmd != cmd_processor) and (next_cmd is not cmd_processor)

    def test_next_exceed_length(self, cmd_processor: FakeCommandProcess):
        with pytest.raises(StopIteration):
            for _ in range(len(make_command_chain()) + 1):
                assert cmd_processor.next

    @pytest.mark.parametrize(
        ("subcmd", "expected_result"),
        [
            (_Fake_SubCmd, True),
            ("not-mapping-subcmd", False),
        ],
    )
    def test_is_responsible(self, subcmd: str, expected_result: bool, cmd_processor: FakeCommandProcess):
        arg = ParserArguments(subparser_name=subcmd)
        is_responsible = cmd_processor.is_responsible(arg)
        assert is_responsible is expected_result

    @pytest.mark.parametrize(
        ("chk_result", "should_dispatch"),
        [
            (True, False),
            (False, True),
        ],
    )
    def test_receive(self, chk_result: bool, should_dispatch: bool, cmd_processor: FakeCommandProcess):
        cmd_processor.is_responsible = MagicMock(return_value=chk_result)
        cmd_processor.run = MagicMock()
        cmd_processor.dispatch_to_next = MagicMock()

        arg = ParserArguments(subparser_name=_Fake_SubCmd)
        cmd_processor.receive(arg)

        cmd_processor.is_responsible.assert_called_once_with(arg)
        if should_dispatch:
            cmd_processor.run.assert_not_called()
            cmd_processor.dispatch_to_next.assert_called_once_with(arg)
        else:
            cmd_processor.run.assert_called_once_with(arg)
            cmd_processor.dispatch_to_next.assert_not_called()

    @patch("copy.copy")
    def test_copy(self, mock_copy: Mock, cmd_processor: FakeCommandProcess):
        cmd_processor.copy()
        mock_copy.assert_called_once_with(cmd_processor)


class CommandProcessorTestSpec(metaclass=ABCMeta):
    @pytest.fixture(scope="function")
    @abstractmethod
    def cmd_ps(self) -> BaseCommandProcessor:
        pass

    @pytest.fixture(scope="function")
    def object_under_test(self, cmd_ps: BaseCommandProcessor) -> Callable:
        return cmd_ps.receive

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


class TestNoSubCmd(CommandProcessorTestSpec):
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

        with patch("pymock_api.cmd_ps.YAML", return_value=FakeYAML) as mock_instantiate_writer:
            with patch.object(WSGIServer, "generate", return_value=command) as mock_sgi_generate:
                cmd_ps(mock_parser_arg)
                mock_sgi_generate.assert_not_called()
                command.run.assert_not_called()
                mock_instantiate_writer.assert_not_called()


class TestSubCmdRun(CommandProcessorTestSpec):
    @pytest.fixture(scope="function")
    def cmd_ps(self) -> SubCmdRun:
        return SubCmdRun()

    @pytest.mark.parametrize(
        ("app_type", "should_raise_exc"),
        [
            (_Test_App_Type, False),
            (_Test_FastAPI_App_Type, False),
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
        mock_parser_arg = _given_parser_args(subcommand="run", app_type=app_type)
        command = _given_command(app_type="Python web library")
        command.run = MagicMock()

        with patch("pymock_api.cmd_ps.YAML", return_value=FakeYAML) as mock_instantiate_writer:
            with patch.object(ASGIServer, "generate", return_value=command) as mock_asgi_generate:
                with patch.object(WSGIServer, "generate", return_value=command) as mock_wsgi_generate:
                    if should_raise_exc:
                        with pytest.raises(ValueError) as exc_info:
                            cmd_ps(mock_parser_arg)
                        assert "Invalid value" in str(exc_info.value)
                        mock_asgi_generate.assert_not_called()
                        mock_wsgi_generate.assert_not_called()
                        command.run.assert_not_called()
                        mock_instantiate_writer.assert_not_called()
                    else:
                        cmd_ps(mock_parser_arg)
                        if app_type == "flask":
                            mock_asgi_generate.assert_not_called()
                            mock_wsgi_generate.assert_called_once_with(mock_parser_arg)
                        else:
                            mock_asgi_generate.assert_called_once_with(mock_parser_arg)
                            mock_wsgi_generate.assert_not_called()
                        command.run.assert_called_once()
                        mock_instantiate_writer.assert_not_called()


class TestSubCmdConfig(CommandProcessorTestSpec):
    @pytest.fixture(scope="function")
    def cmd_ps(self) -> SubCmdConfig:
        return SubCmdConfig()

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
            subparser_name="config",
            print_sample=oprint,
            generate_sample=generate,
            sample_output_path=output,
        )

        with patch("builtins.print", autospec=True, side_effect=print) as mock_print:
            with patch("pymock_api.cmd_ps.YAML", return_value=FakeYAML) as mock_instantiate_writer:
                cmd_ps(mock_parser_arg)

                if oprint or generate:
                    mock_instantiate_writer.assert_called_once()
                    FakeYAML.serialize.assert_called_once()
                else:
                    mock_instantiate_writer.assert_not_called()
                    FakeYAML.serialize.assert_not_called()

                if oprint:
                    mock_print.assert_has_calls([call(f"It will write below content into file {output}:")])
                else:
                    mock_print.assert_not_called()

                if generate:
                    FakeYAML.write.assert_called_once()
                else:
                    FakeYAML.write.assert_not_called()


# class TestCommandProcessor:
#     # @patch.object(argparse.ArgumentParser, "parse_args", return_value=MOCK_ARGS_PARSE_RESULT)
#     # @patch.object(deserialize_args, "subcmd_run")
#     # def test_parse(self, mock_deserialize: Mock, mock_parse_args: Mock, cmd_ps_chain: List["BaseCommandProcessor"]):
#     #     self._run_chain(cmd_ps_chain, mock_parser_arg)
#     #     runner.parse_subcmd_run()
#     #
#     #     mock_parse_args.assert_called_once_with(None)
#     #     mock_deserialize.assert_called_once_with(MOCK_ARGS_PARSE_RESULT)


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
