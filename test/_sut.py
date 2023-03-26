from pymock_api.runner import CommandRunner

CMD_RUNNER: CommandRunner = None


def initial_runner() -> None:
    global CMD_RUNNER
    if not CMD_RUNNER:
        CMD_RUNNER = CommandRunner()


def get_runner() -> CommandRunner:
    return CMD_RUNNER


# Instantiate command runner first
initial_runner()
