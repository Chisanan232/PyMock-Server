from unittest.mock import MagicMock, patch

import pytest

from pymock_api.command.inspect.component import SubCmdInspectComponent
from pymock_api.model.cmd_args import SubcmdInspectArguments


class TestSubCmdInspectComponent:
    @pytest.fixture(scope="class")
    def component(self) -> SubCmdInspectComponent:
        return SubCmdInspectComponent()
