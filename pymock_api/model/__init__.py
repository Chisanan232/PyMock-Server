"""*The data model in PyMock-API*

content ...
"""

from argparse import Namespace
from typing import Optional

from .api_config import APIConfig
from .cmd_args import Deserialize, ParserArguments


def deserialize_parser_args(args: Namespace, subcmd: Optional[str] = None) -> ParserArguments:
    """Deserialize the object *argparse.Namespace* to *ParserArguments*.

    Args:
        args (Namespace): The arguments which be parsed from current command line.

    Returns:
        A *ParserArguments* type object.

    """
    return Deserialize.parser_arguments(args, subcmd)
