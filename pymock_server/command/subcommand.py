from dataclasses import dataclass
from enum import Enum


@dataclass
class SubCommand:
    Base: str = "subcommand"
    RestServer: str = "rest-server"
    Run: str = "run"
    Add: str = "add"
    Check: str = "check"
    Get: str = "get"
    Sample: str = "sample"
    Pull: str = "pull"


class SubCommandSection(Enum):
    Base: str = "subcommands"
    ApiServer: str = "API server subcommands"
