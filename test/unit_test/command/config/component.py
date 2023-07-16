import re
from unittest.mock import MagicMock, patch

import pytest

from pymock_api._utils.file_opt import YAML
from pymock_api.command.config.component import SubCmdConfigComponent
from pymock_api.model.cmd_args import SubcmdConfigArguments

from ...._values import (
    _Bind_Host_And_Port,
    _Generate_Sample,
    _Log_Level,
    _Print_Sample,
    _Sample_File_Path,
    _Swagger_API_Document_URL,
    _Test_App_Type,
    _Test_Auto_Type,
    _Test_Config,
    _Test_FastAPI_App_Type,
    _Test_SubCommand_Check,
    _Test_SubCommand_Config,
    _Test_SubCommand_Inspect,
    _Test_SubCommand_Run,
    _Workers_Amount,
)


class FakeYAML(YAML):
    pass


class TestSubCmdConfigComponent:
    @pytest.fixture(scope="class")
    def component(self) -> SubCmdConfigComponent:
        return SubCmdConfigComponent()

    def test_assert_error_with_empty_args(self, component: SubCmdConfigComponent):
        # Mock functions
        FakeYAML.serialize = MagicMock()
        FakeYAML.write = MagicMock()

        invalid_args = SubcmdConfigArguments(
            subparser_name=_Test_SubCommand_Config,
            print_sample=False,
            generate_sample=True,
            sample_output_path="",
        )

        # Run target function to test
        with patch("pymock_api.command.config.component.YAML", return_value=FakeYAML) as mock_instantiate_writer:
            with pytest.raises(AssertionError) as exc_info:
                component.process(invalid_args)

            # Verify result
            assert re.search(r"Option '.{1,20}' value cannot be empty.", str(exc_info.value), re.IGNORECASE)
            mock_instantiate_writer.assert_called_once()
            FakeYAML.serialize.assert_called_once()
            FakeYAML.write.assert_not_called()
