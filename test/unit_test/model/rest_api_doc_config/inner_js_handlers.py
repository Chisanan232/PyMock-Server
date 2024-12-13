from typing import Union

import pytest

from pymock_server.model.rest_api_doc_config._js_handlers import (
    ApiDocValueFormat,
    convert_js_type,
)


@pytest.mark.parametrize(
    ("js_type", "py_type"),
    [
        ("string", "str"),
        ("integer", "int"),
        ("number", "int"),
        ("boolean", "bool"),
        ("array", "list"),
        ("object", "dict"),
        ("file", "file"),
    ],
)
def test_convert_js_type(js_type: str, py_type: str):
    assert convert_js_type(js_type) == py_type


def test_fail_convert_js_type():
    with pytest.raises(TypeError) as exc_info:
        convert_js_type("JS type which does not support to convert")
    assert "cannot parse JS type" in str(exc_info.value)


class TestApiDocValueFormat:

    @pytest.mark.parametrize(
        ("under_test_value", "expected_value"),
        [
            (ApiDocValueFormat.DateTime, ApiDocValueFormat.DateTime),
            (ApiDocValueFormat.Int32, ApiDocValueFormat.Int32),
            (ApiDocValueFormat.Int64, ApiDocValueFormat.Int64),
            (ApiDocValueFormat.Float, ApiDocValueFormat.Float),
            (ApiDocValueFormat.Double, ApiDocValueFormat.Double),
            (ApiDocValueFormat.Password, ApiDocValueFormat.Password),
            ("date-time", ApiDocValueFormat.DateTime),
            ("date-Time", ApiDocValueFormat.DateTime),
            ("int64", ApiDocValueFormat.Int64),
            ("INT32", ApiDocValueFormat.Int32),
        ],
    )
    def test_to_enum(
        self, under_test_value: Union[str, ApiDocValueFormat.Int32], expected_value: ApiDocValueFormat.Int32
    ):
        assert ApiDocValueFormat.to_enum(under_test_value) is expected_value

    def test_to_enum_with_invalid_value(self):
        with pytest.raises(ValueError):
            ApiDocValueFormat.to_enum("invalid value")
