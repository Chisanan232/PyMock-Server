from dataclasses import dataclass


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


@dataclass
class SubCommandSection:
    Base: str = "subcommands"
    ApiServer: str = "API server subcommands"
