import re
from typing import List, Optional
from unittest.mock import MagicMock, patch

import pytest

from pymock_api import APIConfig
from pymock_api._utils.file_opt import YAML
from pymock_api.command.sample.component import SubCmdSampleComponent
from pymock_api.model import MockAPI, generate_empty_config
from pymock_api.model.cmd_args import SubcmdSampleArguments

from ...._values import (
    _Test_Config,
    _Test_HTTP_Method,
    _Test_HTTP_Resp,
    _Test_SubCommand_Add,
    _Test_URL,
    _TestConfig,
)


class FakeYAML(YAML):
    pass


class TestSubCmdConfigComponent:
    @pytest.fixture(scope="class")
    def component(self) -> SubCmdSampleComponent:
        return SubCmdSampleComponent()

    def test_assert_error_with_empty_args(self, component: SubCmdSampleComponent):
        # Mock functions
        FakeYAML.serialize = MagicMock()
        FakeYAML.write = MagicMock()

        invalid_args = SubcmdSampleArguments(
            subparser_name=_Test_SubCommand_Add,
            print_sample=False,
            generate_sample=True,
            sample_output_path="",
        )

        # Run target function to test
        with patch("pymock_api.command.sample.component.YAML", return_value=FakeYAML) as mock_instantiate_writer:
            with pytest.raises(AssertionError) as exc_info:
                component.process(invalid_args)

            # Verify result
            assert re.search(r"Option '.{1,20}' value cannot be empty.", str(exc_info.value), re.IGNORECASE)
            mock_instantiate_writer.assert_called_once()
            FakeYAML.serialize.assert_called_once()
            FakeYAML.write.assert_not_called()
