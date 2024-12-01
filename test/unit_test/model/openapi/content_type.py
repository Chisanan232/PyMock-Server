from typing import Type, Union

import pytest

from pymock_api.model.openapi.content_type import ContentType

from ..enums import EnumTestSuite


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
