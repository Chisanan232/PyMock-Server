from enum import Enum
from typing import List, Union

from fake_api_server.exceptions import NotFoundCommandLine


class SubCommandLine(Enum):
    Base = "subcommand"
    RestServer = "rest-server"
    Run = "run"
    Add = "add"
    Check = "check"
    Get = "get"
    Sample = "sample"
    Pull = "pull"

    @staticmethod
    def to_enum(v: Union[str, "SubCommandLine"]) -> "SubCommandLine":
        if isinstance(v, SubCommandLine):
            return v
        for subcmd in SubCommandLine:
            if subcmd.value.lower() == v.lower():
                return subcmd
        raise NotFoundCommandLine(v)

    @staticmethod
    def major_cli() -> List["SubCommandLine"]:
        return [
            SubCommandLine.RestServer,
        ]


class SubCommandSection(Enum):
    # Base = "subcommands"
    Base = "API servers"
    ApiServer = "API server subcommands"
