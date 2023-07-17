from unittest.mock import MagicMock, patch

import pytest

from pymock_api.command.inspect.component import SubCmdGetComponent
from pymock_api.model.cmd_args import SubcmdInspectArguments


class TestSubCmdGetComponent:
    @pytest.fixture(scope="class")
    def component(self) -> SubCmdGetComponent:
        return SubCmdGetComponent()
