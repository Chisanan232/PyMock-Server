import re
from test._values import _Test_SubCommand_Add
from unittest.mock import MagicMock, Mock, patch

import pytest

from pymock_server._utils.file.operation import YAML
from pymock_server.command.rest_server.sample.component import SubCmdSampleComponent
from pymock_server.command.subcommand import SubCommand
from pymock_server.model._sample import SampleType
from pymock_server.model.cmd_args import SubcmdSampleArguments
from pymock_server.model.subcmd_common import SysArg


class FakeYAML(YAML):
    pass


class TestSubCmdSampleComponent:
    @pytest.fixture(scope="class")
    def component(self) -> SubCmdSampleComponent:
        return SubCmdSampleComponent()

    def test_assert_error_with_empty_args(self, component: SubCmdSampleComponent):
        # Mock functions
        FakeYAML.serialize = MagicMock()
        FakeYAML.write = MagicMock()

        invalid_args = SubcmdSampleArguments(
            subparser_name=_Test_SubCommand_Add,
            subparser_structure=SysArg.parse([SubCommand.RestServer, SubCommand.Add]),
            print_sample=False,
            generate_sample=True,
            sample_output_path="",
            sample_config_type=SampleType.ALL,
        )

        # Run target function to test
        with patch(
            "pymock_server.command.rest_server.sample.component.YAML", return_value=FakeYAML
        ) as mock_instantiate_writer:
            with patch(
                "pymock_server.command.rest_server.sample.component.get_sample_by_type", return_value=FakeYAML
            ) as mock_get_sample_by_type:
                with pytest.raises(AssertionError) as exc_info:
                    component.process(parser=Mock(), args=invalid_args)

                # Verify result
                assert re.search(r"Option '.{1,20}' value cannot be empty.", str(exc_info.value), re.IGNORECASE)
                mock_instantiate_writer.assert_called_once()
                mock_get_sample_by_type.assert_called_once_with(invalid_args.sample_config_type)
                FakeYAML.serialize.assert_called_once()
                FakeYAML.write.assert_not_called()
