"""*Handle importing*"""

import re
from typing import Callable, List, Optional

SUPPORT_WEB_FRAMEWORK: List[str] = ["flask", "fastapi"]
SUPPORT_SGI_SERVER: List[str] = ["gunicorn", "uvicorn"]


class import_web_lib:
    """*Import the Python library and return it.*"""

    @staticmethod
    def flask() -> "flask":  # type: ignore
        """Import Python web framework *flask*."""
        import flask

        return flask

    @staticmethod
    def fastapi() -> "fastapi":  # type: ignore
        """Import Python web framework *fastapi*."""
        import fastapi

        return fastapi

    @staticmethod
    def auto_ready() -> Optional[str]:
        self = import_web_lib
        all_ready_funs = list(filter(lambda e: re.search(r"\w{1,16}_ready", e), dir(self)))
        ready_funs = list(filter(lambda e: not re.search(r"^(_|auto)\w{1,16}", e), all_ready_funs))
        could_import_lib = list(map(lambda e: getattr(self, e)(), ready_funs))
        try:
            return ready_funs[could_import_lib.index(True)].replace("_ready", "")
        except ValueError:
            return None

    @staticmethod
    def flask_ready() -> bool:
        return import_web_lib._chk_lib_ready(import_web_lib.flask)

    @staticmethod
    def fastapi_ready() -> bool:
        return import_web_lib._chk_lib_ready(import_web_lib.fastapi)

    @staticmethod
    def _chk_lib_ready(lib_import: Callable) -> bool:
        try:
            lib_import()
        except ImportError:
            return False
        else:
            return True


def ensure_importing(import_callback: Callable, import_err_callback: Optional[Callable] = None) -> Callable:
    """Load application if importing works finely without any issue. Or it will do nothing.

    Args:
        import_callback (Callable): The callback function to import module.
        import_err_callback (Callable): The callback function which would be run if it failed at importing.

    Returns:
        None

    """

    def _import(function: Callable) -> Callable:
        def _(*args: tuple, **kwargs: dict) -> None:
            try:
                import_callback()
            except (ImportError, ModuleNotFoundError) as e:
                if import_err_callback:
                    import_err_callback(e)
                module = str(e).split(" ")[-1]
                raise RuntimeError(
                    f"Cannot load fake application because current Python runtime environment cannot import {module}."
                ) from e
            else:
                return function(*args, **kwargs)

        return _

    return _import
