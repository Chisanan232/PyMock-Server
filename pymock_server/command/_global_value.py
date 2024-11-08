from typing import List

from .subcommand import SubCommandLine

SUBCOMMAND: List[str] = [SubCommandLine.RestServer.value]


class SubCommandInterface:
    @staticmethod
    def get() -> List[str]:
        return SUBCOMMAND

    @staticmethod
    def extend(v: List[str]) -> None:
        assert isinstance(v, list)
        global SUBCOMMAND
        SUBCOMMAND.extend(v)
