from enum import Enum
from typing import List, Union


class SubCommandLine(Enum):
    Base: str = "subcommand"
    RestServer: str = "rest-server"
    Run: str = "run"
    Add: str = "add"
    Check: str = "check"
    Get: str = "get"
    Sample: str = "sample"
    Pull: str = "pull"

    @staticmethod
    def to_enum(v: Union[str, "SubCommandLine"]) -> "SubCommandLine":
        if isinstance(v, SubCommandLine):
            return v
        for subcmd in SubCommandLine:
            if subcmd.value.lower() == v.lower():
                return subcmd
        raise ValueError(f"Cannot map anyone subcommand line with value '{v}'.")

    @staticmethod
    def major_cli() -> List["SubCommandLine"]:
        return [
            SubCommandLine.RestServer,
        ]


class SubCommandSection(Enum):
    Base: str = "subcommands"
    ApiServer: str = "API server subcommands"
