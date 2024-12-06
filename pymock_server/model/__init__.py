"""*The data model in PyMock-Server*

content ...
"""

import pathlib
from argparse import Namespace
from typing import Optional

from pymock_server.exceptions import NotSupportAPIDocumentVersion

from .api_config import APIConfig, MockAPIs
from .api_config.apis import HTTP, APIParameter, HTTPRequest, HTTPResponse, MockAPI
from .api_config.base import BaseConfig
from .api_config.template import TemplateConfig
from .cmd_args import (
    DeserializeParsedArgs,
    ParserArguments,
    SubcmdAddArguments,
    SubcmdCheckArguments,
    SubcmdGetArguments,
    SubcmdPullArguments,
    SubcmdRunArguments,
    SubcmdSampleArguments,
)
from .rest_api_doc_config.config import (
    BaseAPIDocumentConfig,
    OpenAPIDocumentConfig,
    SwaggerAPIDocumentConfig,
    get_api_doc_version,
)
from .rest_api_doc_config.version import OpenAPIVersion


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
    def subcmd_add(cls, args: Namespace) -> SubcmdAddArguments:
        """Deserialize the object *argparse.Namespace* to *ParserArguments*.

        Args:
            args (Namespace): The arguments which be parsed from current command line.

        Returns:
            A *ParserArguments* type object.

        """
        return DeserializeParsedArgs.subcommand_add(args)

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
    def subcmd_get(cls, args: Namespace) -> SubcmdGetArguments:
        """Deserialize the object *argparse.Namespace* to *ParserArguments*.

        Args:
            args (Namespace): The arguments which be parsed from current command line.

        Returns:
            A *ParserArguments* type object.

        """
        return DeserializeParsedArgs.subcommand_get(args)

    @classmethod
    def subcmd_sample(cls, args: Namespace) -> SubcmdSampleArguments:
        """Deserialize the object *argparse.Namespace* to *ParserArguments*.

        Args:
            args (Namespace): The arguments which be parsed from current command line.

        Returns:
            A *ParserArguments* type object.

        """
        return DeserializeParsedArgs.subcommand_sample(args)

    @classmethod
    def subcmd_pull(cls, args: Namespace) -> SubcmdPullArguments:
        """Deserialize the object *argparse.Namespace* to *ParserArguments*.

        Args:
            args (Namespace): The arguments which be parsed from current command line.

        Returns:
            A *ParserArguments* type object.

        """
        return DeserializeParsedArgs.subcommand_pull(args)


def deserialize_api_doc_config(data: dict) -> BaseAPIDocumentConfig:
    api_doc_version = get_api_doc_version(data)
    if api_doc_version is OpenAPIVersion.V2:
        return SwaggerAPIDocumentConfig().deserialize(data)
    elif api_doc_version is OpenAPIVersion.V3:
        return OpenAPIDocumentConfig().deserialize(data)
    else:
        raise NotSupportAPIDocumentVersion(
            api_doc_version.name if isinstance(api_doc_version, OpenAPIVersion) else str(api_doc_version)
        )


def load_config(path: str, is_pull: bool = False, base_file_path: str = "") -> Optional[APIConfig]:
    api_config = APIConfig()
    api_config_path = pathlib.Path(path)
    api_config.config_file_name = api_config_path.name
    api_config.base_file_path = base_file_path if base_file_path else str(api_config_path.parent)
    api_config.is_pull = is_pull
    return api_config.from_yaml(path=path, is_pull=is_pull)


def generate_empty_config(name: str = "", description: str = "") -> APIConfig:
    return APIConfig(
        name=name,
        description=description,
        apis=MockAPIs(template=TemplateConfig(), base=BaseConfig(url=""), apis={}),
    )
