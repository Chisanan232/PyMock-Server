import pytest

from pymock_api.model.openapi._js_handlers import convert_js_type


@pytest.mark.parametrize(
    ("js_type", "py_type"),
    [
        ("string", "str"),
        ("integer", "int"),
        ("boolean", "bool"),
        ("array", "list"),
    ],
)
def test_convert_js_type(js_type: str, py_type: str):
    assert convert_js_type(js_type) == py_type


def test_fail_convert_js_type():
    with pytest.raises(TypeError) as exc_info:
        convert_js_type("JS type which does not support to convert")
    assert "cannot parse JS type" in str(exc_info.value)
