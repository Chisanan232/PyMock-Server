"""*The data model in PyFake-API-Server*

content ...
"""

import pathlib
from typing import Optional

from fake_api_server.exceptions import NotSupportAPIDocumentVersion
from fake_api_server.model.command.rest_server.cmd_args import (
    ParserArguments,
    SubcmdAddArguments,
    SubcmdCheckArguments,
    SubcmdGetArguments,
    SubcmdPullArguments,
    SubcmdRunArguments,
    SubcmdSampleArguments,
)

from .api_config import FakeAPIConfig, MockAPIs
from .api_config.apis import HTTP, APIParameter, HTTPRequest, HTTPResponse, MockAPI
from .api_config.base import BaseConfig
from .api_config.template import TemplateConfig
from .command.rest_server import RestServerCliArgsDeserialization
from .rest_api_doc_config.config import (
    BaseAPIDocumentConfig,
    OpenAPIDocumentConfig,
    SwaggerAPIDocumentConfig,
    get_api_doc_version,
)
from .rest_api_doc_config.version import OpenAPIVersion


class deserialize_args:
    cli_rest_server: RestServerCliArgsDeserialization = RestServerCliArgsDeserialization()


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


def load_config(path: str, is_pull: bool = False, base_file_path: str = "") -> Optional[FakeAPIConfig]:
    api_config = FakeAPIConfig()
    api_config_path = pathlib.Path(path)
    api_config.config_file_name = api_config_path.name
    api_config.base_file_path = base_file_path if base_file_path else str(api_config_path.parent)
    api_config.is_pull = is_pull
    return api_config.from_yaml(path=path, is_pull=is_pull)


def generate_empty_config(name: str = "", description: str = "") -> FakeAPIConfig:
    return FakeAPIConfig(
        name=name,
        description=description,
        apis=MockAPIs(template=TemplateConfig(), base=BaseConfig(url=""), apis={}),
    )
