from typing import Type, Union

import pytest

from fake_api_server.model.rest_api_doc_config.content_type import ContentType

# isort: off
from test.unit_test.model._enums import EnumTestSuite

# isort: on


class TestContentType(EnumTestSuite):
    @pytest.fixture(scope="function")
    def enum_obj(self) -> Type[ContentType]:
        return ContentType

    @pytest.mark.parametrize(
        "value",
        [
            ContentType.APPLICATION_JSON,
            ContentType.APPLICATION_OCTET_STREAM,
            ContentType.ALL,
            "application/json",
            "application/octet-stream",
            "*/*",
        ],
    )
    def test_to_enum(self, value: Union[str, ContentType], enum_obj: Type[ContentType]):
        super().test_to_enum(value, enum_obj)
