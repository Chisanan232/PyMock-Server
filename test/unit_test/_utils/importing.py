import re
from typing import Type
from unittest.mock import Mock, patch

import flask
import pytest

from pymock_api._utils.importing import ensure_importing, import_web_lib


def fake_function() -> str:
    return "Fake function for PyTest"


class TestImportWebLib:
    @pytest.fixture(scope="function")
    def import_web_lib(self) -> Type[import_web_lib]:
        return import_web_lib

    def test_import_web_lib(self, import_web_lib: Type[import_web_lib]):
        assert import_web_lib.flask() == flask


@patch.object(import_web_lib, "flask")
def test_ensure_importing(mock_import_lib: Mock):
    fake_function_with_decorator = ensure_importing(import_web_lib.flask)(fake_function)
    assert fake_function_with_decorator() == "Fake function for PyTest"
    mock_import_lib.assert_called_once()


@patch.object(import_web_lib, "flask", side_effect=ImportError("No module named 'flask'"))
def test_ensure_importing_fail(mock_import_lib: Mock):
    with pytest.raises(RuntimeError) as exc_info:
        fake_function_with_decorator = ensure_importing(import_web_lib.flask)(fake_function)
        fake_function_with_decorator()
    mock_import_lib.assert_called_once()
    assert re.search(r"Cannot load.{0,256}cannot import.{0,256}", str(exc_info.value))


@patch.object(import_web_lib, "flask", side_effect=ImportError("No module named 'flask'"))
def test_ensure_importing_fail_with_error_handle(mock_import_lib: Mock):
    mock_error_handle = Mock()
    with pytest.raises(RuntimeError) as exc_info:
        fake_function_with_decorator = ensure_importing(import_web_lib.flask, import_err_callback=mock_error_handle)(
            fake_function
        )
        fake_function_with_decorator()
    mock_import_lib.assert_called_once()
    mock_error_handle.assert_called_once()
    assert re.search(r"Cannot load.{0,256}cannot import.{0,256}", str(exc_info.value))
