from typing import List, Tuple, Union

import pytest

from pymock_server._utils.uri_protocol import URISchema

_Test_Data: List[Tuple[Union[str, URISchema], str]] = []
uri_enum = [(uri, uri) for uri in URISchema]
uri_enum_value = [(uri.value, uri) for uri in URISchema]
_Test_Data.extend(uri_enum)
_Test_Data.extend(uri_enum_value)


class TestURISchema:
    @pytest.mark.parametrize(("value", "expected"), _Test_Data)
    def test_to_enum(self, value: Union[str, URISchema], expected: URISchema) -> None:
        assert URISchema.to_enum(value) is expected

    def test_to_enum_with_invalid(self):
        with pytest.raises(ValueError):
            URISchema.to_enum("invalid value")
