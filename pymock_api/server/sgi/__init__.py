"""*The wrapper of application which ruled by SGI (server gateway interface)*

The factory to generate SGI application instance to run Python web framework.
"""

from argparse import Namespace

from ._model import Command, CommandOptions, Deserialize, ParserArguments
from .cmd import WSGICmd
from .cmdoption import WSGICmdOption


def deserialize_parser_args(args: Namespace) -> ParserArguments:
    """Deserialize the object *argparse.Namespace* to *ParserArguments*.

    Args:
        args (Namespace): The arguments which be parsed from current command line.

    Returns:
        A *ParserArguments* type object.

    """
    return Deserialize.parser_arguments(args)
