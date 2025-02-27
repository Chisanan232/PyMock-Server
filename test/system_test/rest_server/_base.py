from abc import ABC

# isort: off
from test.system_test._base import CommandTestSpec

# isort: on


class SubCmdRestServerTestSuite(CommandTestSpec, ABC):

    @property
    def command_line(self) -> str:
        return f"python3 {self.Server_Running_Entry_Point} rest-server {self.options}"
