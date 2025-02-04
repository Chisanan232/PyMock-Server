from typing import Union

import pytest

from fake_api_server.model.api_config.value import ValueFormat
from fake_api_server.model.rest_api_doc_config._js_handlers import (
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
            ("date", ApiDocValueFormat.Date),
            (ApiDocValueFormat.DateTime, ApiDocValueFormat.DateTime),
            (ApiDocValueFormat.Int32, ApiDocValueFormat.Int32),
            (ApiDocValueFormat.Int64, ApiDocValueFormat.Int64),
            (ApiDocValueFormat.Float, ApiDocValueFormat.Float),
            (ApiDocValueFormat.Double, ApiDocValueFormat.Double),
            ("date-time", ApiDocValueFormat.DateTime),
            ("date-Time", ApiDocValueFormat.DateTime),
            ("int64", ApiDocValueFormat.Int64),
            ("INT32", ApiDocValueFormat.Int32),
            ("email", ApiDocValueFormat.EMail),
            ("UUID", ApiDocValueFormat.UUID),
            ("Uri", ApiDocValueFormat.URI),
            ("Url", ApiDocValueFormat.URL),
            ("ipv4", ApiDocValueFormat.IPv4),
            ("IPv6", ApiDocValueFormat.IPv6),
        ],
    )
    def test_to_enum(self, under_test_value: Union[str, ApiDocValueFormat], expected_value: ApiDocValueFormat):
        assert ApiDocValueFormat.to_enum(under_test_value) is expected_value

    def test_to_enum_with_invalid_value(self):
        with pytest.raises(ValueError):
            ApiDocValueFormat.to_enum("invalid value")

    @pytest.mark.parametrize(
        ("api_doc_format", "pymock_format"),
        [
            (ApiDocValueFormat.Date, ValueFormat.Date),
            (ApiDocValueFormat.DateTime, ValueFormat.DateTime),
            (ApiDocValueFormat.Int32, ValueFormat.Integer),
            (ApiDocValueFormat.Int64, ValueFormat.Integer),
            (ApiDocValueFormat.Float, ValueFormat.BigDecimal),
            (ApiDocValueFormat.Double, ValueFormat.BigDecimal),
            (ApiDocValueFormat.EMail, ValueFormat.EMail),
            (ApiDocValueFormat.UUID, ValueFormat.UUID),
            (ApiDocValueFormat.URI, ValueFormat.URI),
            (ApiDocValueFormat.URL, ValueFormat.URL),
            (ApiDocValueFormat.IPv4, ValueFormat.IPv4),
            (ApiDocValueFormat.IPv6, ValueFormat.IPv6),
        ],
    )
    def test_to_pymock_value_format(self, api_doc_format: ApiDocValueFormat, pymock_format: ValueFormat):
        assert api_doc_format.to_pymock_value_format() is pymock_format
