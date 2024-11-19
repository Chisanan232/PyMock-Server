from pymock_server.command._base._base_options import CommandOption
from pymock_server.command.subcommand import SubCommandLine, SubCommandSection
from pymock_server.model.subcmd_common import SubCommandAttr


class BaseSubCommandRestServer(CommandOption):
    sub_cmd: SubCommandAttr = SubCommandAttr(
        title=SubCommandSection.ApiServer,
        dest=SubCommandLine.RestServer,
        description="Some operations for mocking REST API server.",
        help="Set up an application to mock HTTP server which adopts REST API to communicate between client and server.",
    )
    in_sub_cmd = SubCommandLine.RestServer
