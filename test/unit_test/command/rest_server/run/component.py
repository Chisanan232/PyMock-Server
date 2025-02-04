import re
from unittest.mock import MagicMock, Mock, patch

import pytest

from fake_api_server.command.rest_server.run.component import SubCmdRunComponent
from fake_api_server.model.command.rest_server.cmd_args import SubcmdRunArguments
from fake_api_server.model.subcmd_common import SysArg

# isort: off
from test._values import (
    SubCommand,
    _Bind_Host_And_Port,
    _Log_Level,
    _Test_Auto_Type,
    _Test_Config,
    _Workers_Amount,
)

# isort: on


class TestSubCmdRunComponent:
    @pytest.fixture(scope="class")
    def component(self) -> SubCmdRunComponent:
        return SubCmdRunComponent()

    @patch("fake_api_server.command.rest_server.run.component.import_web_lib.auto_ready", return_value=None)
    def test_auto_with_nonexist_lib(self, mock_auto_ready: Mock, component: SubCmdRunComponent):
        with pytest.raises(RuntimeError) as exc_info:
            component._initial_server_gateway(lib=_Test_Auto_Type)
        assert re.search(r"doesn't have valid web library", str(exc_info.value), re.IGNORECASE)
        mock_auto_ready.assert_called_once()

    def test_assert_error_with_empty_args(self, component: SubCmdRunComponent):
        # Mock functions
        component._initial_server_gateway = MagicMock()
        mock_server_gateway = Mock()
        mock_server_gateway.run = MagicMock()
        component._server_gateway = mock_server_gateway

        invalid_args = SubcmdRunArguments(
            subparser_structure=SysArg.parse([SubCommand.RestServer, SubCommand.Run]),
            app_type="",
            config=_Test_Config,
            bind=_Bind_Host_And_Port.value,
            workers=_Workers_Amount.value,
            log_level=_Log_Level.value,
        )

        # Run target function to test
        with pytest.raises(AssertionError) as exc_info:
            component.process(parser=Mock(), args=invalid_args)

        # Verify result
        assert re.search(r"Option '.{1,20}' value cannot be empty.", str(exc_info.value), re.IGNORECASE)
        component._initial_server_gateway.assert_not_called()
        component._server_gateway.run.assert_not_called()
