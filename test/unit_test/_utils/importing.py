import re
from typing import Type
from unittest.mock import Mock, patch

import fastapi
import flask
import pytest

from pymock_api._utils.importing import ensure_importing, import_web_lib


def fake_function() -> str:
    return "Fake function for PyTest"


class TestImportWebLib:
    @pytest.fixture(scope="function")
    def import_web_lib(self) -> Type[import_web_lib]:
        return import_web_lib

    def test_import_web_lib_flask(self, import_web_lib: Type[import_web_lib]):
        assert import_web_lib.flask() == flask

    def test_import_web_lib_fastapi(self, import_web_lib: Type[import_web_lib]):
        assert import_web_lib.fastapi() == fastapi


@pytest.mark.parametrize("web_lib", ["flask", "fastapi"])
def test_ensure_importing(web_lib: str):
    with patch.object(import_web_lib, web_lib) as mock_import_lib:
        import_web_lib_func = getattr(import_web_lib, web_lib)
        fake_function_with_decorator = ensure_importing(import_web_lib_func)(fake_function)
        assert fake_function_with_decorator() == "Fake function for PyTest"
        mock_import_lib.assert_called_once()


@pytest.mark.parametrize("web_lib", ["flask", "fastapi"])
def test_ensure_importing_fail(web_lib: str):
    with patch.object(
        import_web_lib, web_lib, side_effect=ImportError(f"No module named '{web_lib}'")
    ) as mock_import_lib:
        import_web_lib_func = getattr(import_web_lib, web_lib)
        with pytest.raises(RuntimeError) as exc_info:
            fake_function_with_decorator = ensure_importing(import_web_lib_func)(fake_function)
            fake_function_with_decorator()
        mock_import_lib.assert_called_once()
        assert re.search(r"Cannot load.{0,256}cannot import.{0,256}", str(exc_info.value))


@pytest.mark.parametrize("web_lib", ["flask", "fastapi"])
def test_ensure_importing_fail_with_error_handle(web_lib: str):
    mock_error_handle = Mock()
    with patch.object(
        import_web_lib, web_lib, side_effect=ImportError(f"No module named '{web_lib}'")
    ) as mock_import_lib:
        import_web_lib_func = getattr(import_web_lib, web_lib)
        with pytest.raises(RuntimeError) as exc_info:
            fake_function_with_decorator = ensure_importing(import_web_lib_func, import_err_callback=mock_error_handle)(
                fake_function
            )
            fake_function_with_decorator()
        mock_import_lib.assert_called_once()
        mock_error_handle.assert_called_once()
        assert re.search(r"Cannot load.{0,256}cannot import.{0,256}", str(exc_info.value))
