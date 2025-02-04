from fake_api_server.command._base.options import CommandOption
from fake_api_server.command.subcommand import SubCommandLine, SubCommandSection
from fake_api_server.model.subcmd_common import SubCommandAttr


class BaseSubCommandRestServer(CommandOption):
    sub_cmd: SubCommandAttr = SubCommandAttr(
        title=SubCommandSection.Foo,
        dest=SubCommandLine.Foo,
        description="Some operations for mocking REST API server.",
        help="Set up an application to mock HTTP server which adopts REST API to communicate between client and server.",
    )
    in_sub_cmd = SubCommandLine.Foo
