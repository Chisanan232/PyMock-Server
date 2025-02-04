import re
from typing import Any, Callable, Optional, Type
from unittest.mock import MagicMock, Mock, _patch, patch

import fastapi
import flask
import pytest

from fake_api_server._utils.importing import ensure_importing, import_web_lib


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

    @pytest.mark.parametrize(
        ("site_effect", "lib_ready"),
        [(None, True), (ImportError("PyTest ImportError"), False)],
    )
    def test_flask_ready(self, site_effect: Any, lib_ready: bool, import_web_lib: Type[import_web_lib]):
        # Mock function
        og_flask = import_web_lib.flask
        import_web_lib.flask = MagicMock(site_effect=site_effect)
        # Run target function under test
        assert import_web_lib.flask_ready()
        # Annotate the function back to correct implementation
        import_web_lib.flask = og_flask

    @pytest.mark.parametrize(
        ("site_effect", "lib_ready"),
        [(None, True), (ImportError("PyTest ImportError"), False)],
    )
    def test_fastapi_ready(self, site_effect: Any, lib_ready: bool, import_web_lib: Type[import_web_lib]):
        # Mock function
        og_fastapi = import_web_lib.fastapi
        import_web_lib.fastapi = MagicMock(site_effect=site_effect)
        # Run target function under test
        assert import_web_lib.fastapi_ready()
        # Annotate the function back to correct implementation
        import_web_lib.fastapi = og_fastapi

    @pytest.mark.parametrize(
        ("flask_ready_return", "fastapi_ready_return", "ready_lib"),
        [
            (True, True, "fastapi"),
            (True, False, "flask"),
            (False, True, "fastapi"),
            (False, False, None),
        ],
    )
    def test_auto_ready(
        self,
        flask_ready_return: bool,
        fastapi_ready_return: bool,
        ready_lib: Optional[str],
        import_web_lib: Type[import_web_lib],
    ):
        # Mock function
        og_flask_ready = import_web_lib.flask_ready
        og_fastapi_ready = import_web_lib.fastapi_ready
        import_web_lib.flask_ready = MagicMock(return_value=flask_ready_return)
        import_web_lib.fastapi_ready = MagicMock(return_value=fastapi_ready_return)
        # Run target function under test
        assert import_web_lib.auto_ready() == ready_lib
        # Annotate the function back to correct implementation
        import_web_lib.flask_ready = og_flask_ready
        import_web_lib.fastapi_ready = og_fastapi_ready


class TestEnsureImporting:
    @pytest.mark.parametrize("web_lib", ["flask", "fastapi"])
    def test_ensure_importing(self, web_lib: str):
        with self._given_importing(web_lib) as mock_import_lib:
            assert self._when_ensure_import(web_lib)() == "Fake function for PyTest"
            mock_import_lib.assert_called_once()

    @pytest.mark.parametrize("web_lib", ["flask", "fastapi"])
    def test_ensure_importing_fail(self, web_lib: str):
        with self._given_importing(web_lib, side_effect=ImportError(f"No module named '{web_lib}'")) as mock_import_lib:
            with pytest.raises(RuntimeError) as exc_info:
                self._when_ensure_import(web_lib)()
            mock_import_lib.assert_called_once()
            assert re.search(r"Cannot load.{0,256}cannot import.{0,256}", str(exc_info.value))

    @pytest.mark.parametrize("web_lib", ["flask", "fastapi"])
    def test_ensure_importing_fail_with_error_handle(self, web_lib: str):
        mock_error_handle = Mock()
        with self._given_importing(web_lib, side_effect=ImportError(f"No module named '{web_lib}'")) as mock_import_lib:
            with pytest.raises(RuntimeError) as exc_info:
                self._when_ensure_import(web_lib, err_callback=mock_error_handle)()
            mock_import_lib.assert_called_once()
            mock_error_handle.assert_called_once()
            assert re.search(r"Cannot load.{0,256}cannot import.{0,256}", str(exc_info.value))

    def _given_importing(self, web_lib: str, side_effect=None) -> _patch:
        return patch.object(import_web_lib, web_lib, side_effect=side_effect)

    def _when_ensure_import(self, web_lib: str, err_callback: Callable = None) -> Callable:
        return ensure_importing(getattr(import_web_lib, web_lib), import_err_callback=err_callback)(fake_function)
