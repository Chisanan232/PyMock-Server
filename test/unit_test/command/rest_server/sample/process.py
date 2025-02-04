import logging
import sys
from argparse import Namespace
from typing import Callable, List, Optional, Type
from unittest.mock import MagicMock, Mock, call, patch

import pytest

# isort: off
from test._values import (
    SubCommand,
    _Generate_Sample,
    _Print_Sample,
    _Sample_Data_Type,
    _Sample_File_Path,
)
from test.unit_test.command._base.process import BaseCommandProcessorTestSpec

# isort: on

from fake_api_server._utils import YAML
from fake_api_server.command.rest_server.sample.process import SubCmdSample
from fake_api_server.command.subcommand import SubCommandLine
from fake_api_server.model import SubcmdSampleArguments
from fake_api_server.model.command.rest_server._sample import SampleType
from fake_api_server.model.subcmd_common import SysArg


class FakeYAML(YAML):
    pass


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
            subparser_structure=SysArg.parse([SubCommand.RestServer, SubCommand.Sample]),
            print_sample=oprint,
            generate_sample=generate,
            sample_output_path=output,
            sample_config_type=SampleType.ALL,
        )
        cmd_parser = Mock()

        with patch.object(sys, "argv", self._given_command_line()):
            with patch(
                "fake_api_server.command.rest_server.sample.component.logger", autospec=True, side_effect=logging
            ) as mock_logging:
                with patch(
                    "fake_api_server.command.rest_server.sample.component.get_sample_by_type",
                    return_value=sample_config,
                ) as mock_get_sample_by_type:
                    with patch(
                        "fake_api_server.command.rest_server.sample.component.YAML", return_value=FakeYAML
                    ) as mock_instantiate_writer:
                        cmd_ps(cmd_parser, mock_parser_arg)

                        mock_instantiate_writer.assert_called_once()
                        mock_get_sample_by_type.assert_called_once_with(mock_parser_arg.sample_config_type)
                        FakeYAML.serialize.assert_called_once()

                        if oprint and generate:
                            mock_logging.assert_has_calls(
                                [
                                    call.info(f"{sample_config}"),
                                    call.info(f"🍻  Write sample configuration into file {output}."),
                                ]
                            )
                            FakeYAML.write.assert_called_once()
                        elif oprint and not generate:
                            mock_logging.assert_has_calls(
                                [
                                    call.info(f"{sample_config}"),
                                ]
                            )
                            FakeYAML.write.assert_not_called()
                        elif not oprint and generate:
                            mock_logging.assert_has_calls(
                                [
                                    call.info(f"🍻  Write sample configuration into file {output}."),
                                ]
                            )
                            FakeYAML.write.assert_called_once()
                        else:
                            mock_logging.assert_not_called()
                            FakeYAML.write.assert_not_called()

    def _given_command_line(self) -> List[str]:
        return ["rest-server", "sample"]

    def _given_cmd_args_namespace(self) -> Namespace:
        args_namespace = Namespace()
        args_namespace.subcommand = SubCommand.RestServer
        setattr(args_namespace, SubCommand.RestServer, SubCommand.Sample)
        args_namespace.generate_sample = _Generate_Sample
        args_namespace.print_sample = _Print_Sample
        args_namespace.file_path = _Sample_File_Path
        args_namespace.sample_config_type = _Sample_Data_Type
        return args_namespace

    def _given_subcmd(self) -> Optional[SysArg]:
        return SysArg(
            pre_subcmd=SysArg(pre_subcmd=SysArg(subcmd=SubCommandLine.Base), subcmd=SubCommandLine.RestServer),
            subcmd=SubCommandLine.Sample,
        )

    def _expected_argument_type(self) -> Type[SubcmdSampleArguments]:
        return SubcmdSampleArguments

    def test__parse_process_with_invalid_type(self, cmd_ps: SubCmdSample):
        cmd_arg_namespace = self._given_cmd_args_namespace()
        cmd_arg_namespace.sample_config_type = "invalid_type"
        cmd_args = Mock()
        with pytest.raises(SystemExit) as exc_info:
            cmd_ps._parse_process(cmd_args)
        assert str(exc_info.value) == "1"
