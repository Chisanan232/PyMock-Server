"""*The data model in PyMock-API*

content ...
"""

from argparse import Namespace
from typing import Optional

from .api_config import APIConfig
from .cmd_args import (
    DeserializeParsedArgs,
    ParserArguments,
    SubcmdCheckArguments,
    SubcmdConfigArguments,
    SubcmdInspectArguments,
    SubcmdRunArguments,
)


class deserialize_args:
    @classmethod
    def subcmd_run(cls, args: Namespace) -> SubcmdRunArguments:
        """Deserialize the object *argparse.Namespace* to *ParserArguments*.

        Args:
            args (Namespace): The arguments which be parsed from current command line.

        Returns:
            A *ParserArguments* type object.

        """
        return DeserializeParsedArgs.subcommand_run(args)

    @classmethod
    def subcmd_config(cls, args: Namespace) -> SubcmdConfigArguments:
        """Deserialize the object *argparse.Namespace* to *ParserArguments*.

        Args:
            args (Namespace): The arguments which be parsed from current command line.

        Returns:
            A *ParserArguments* type object.

        """
        return DeserializeParsedArgs.subcommand_config(args)

    @classmethod
    def subcmd_check(cls, args: Namespace) -> SubcmdCheckArguments:
        """Deserialize the object *argparse.Namespace* to *ParserArguments*.

        Args:
            args (Namespace): The arguments which be parsed from current command line.

        Returns:
            A *ParserArguments* type object.

        """
        return DeserializeParsedArgs.subcommand_check(args)

    @classmethod
    def subcmd_inspect(cls, args: Namespace) -> SubcmdInspectArguments:
        """Deserialize the object *argparse.Namespace* to *ParserArguments*.

        Args:
            args (Namespace): The arguments which be parsed from current command line.

        Returns:
            A *ParserArguments* type object.

        """
        return DeserializeParsedArgs.subcommand_inspect(args)


def load_config(path: str) -> Optional[APIConfig]:
    return APIConfig().from_yaml(path=path)
