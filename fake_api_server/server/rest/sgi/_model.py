import logging
import subprocess
from dataclasses import dataclass
from typing import List

logger = logging.getLogger(__name__)


@dataclass
class CommandOptions:
    """*The data object for the reality usage of target command of SGI tool. e.g., *gunicorn**"""

    bind: str
    workers: str
    log_level: str

    def __str__(self):
        """Combine all command line options as one line which be concatenated by a one space string value `' '`.

        Returns:
            A string value which is the options of command.

        """
        return " ".join(self.all_options)

    @property
    def all_options(self) -> List[str]:
        """:obj:`list` of :obj:`str`: Properties with only getter for a list object of all properties."""
        return [self.bind, self.workers, self.log_level]


@dataclass
class Command:
    """*The data object for command line which would be used finally in *PyFake-API-Server**"""

    entry_point: str
    options: CommandOptions
    app: str
    app_module_path: str = "fake_api_server.server"

    @property
    def line(self) -> str:
        """:obj:`str`: Properties with only getter for a string value of command line with options."""
        return " ".join([self.entry_point, str(self.options), self.app_path])

    @property
    def app_path(self) -> str:
        return f"'{self.app_module_path}:{self.app}'"

    def run(self) -> None:
        """Run the command line.

        Returns:
            None.

        """
        logger.debug(f"Command line for set up application by SGI tool: {self.line}")
        subprocess.run(self.line, shell=True)
