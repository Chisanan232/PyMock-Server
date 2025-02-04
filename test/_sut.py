from typing import Optional

from fake_api_server.runner import CommandRunner

CMD_RUNNER: Optional[CommandRunner] = None


def initial_runner() -> None:
    global CMD_RUNNER
    if not CMD_RUNNER:
        CMD_RUNNER = CommandRunner()


def get_runner() -> CommandRunner:
    assert CMD_RUNNER
    return CMD_RUNNER


# Instantiate command runner first
initial_runner()
