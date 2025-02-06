from fake_api_server.command._base.options import CommandOption
from fake_api_server.command.subcommand import SubCommandLine, SubCommandSection
from fake_api_server.model.subcmd_common import SubCommandAttr


class BaseSubCommandRestServer(CommandOption):
    sub_cmd: SubCommandAttr = SubCommandAttr(
        title=SubCommandSection.ApiServer,
        dest=SubCommandLine.RestServer,
        description="Some operations for faking a RESTful API server.",
        help="Set up an application to fake HTTP server which adopts RESTful API to communicate between client and "
        "server.",
    )
    in_sub_cmd = SubCommandLine.RestServer
