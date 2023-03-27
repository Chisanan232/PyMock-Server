"""*The data model in PyMock-API*

content ...
"""

from argparse import Namespace

from .api_config import APIConfig
from .cmd_args import DeserializeParsedArgs, ParserArguments


def deserialize_subcommand_run_args(args: Namespace) -> ParserArguments:
    """Deserialize the object *argparse.Namespace* to *ParserArguments*.

    Args:
        args (Namespace): The arguments which be parsed from current command line.

    Returns:
        A *ParserArguments* type object.

    """
    return DeserializeParsedArgs.subcommand_run(args)
