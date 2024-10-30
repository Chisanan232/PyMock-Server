import pytest

from pymock_server.model.rest_api_doc_config._js_handlers import convert_js_type


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
