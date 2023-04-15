"""*Handle importing*"""

from typing import Callable


class import_web_lib:
    """*Import the Python library and return it.*"""

    @staticmethod
    def flask() -> "flask":
        """Import Python web framework *flask*."""
        import flask

        return flask

    @staticmethod
    def fastapi() -> "fastapi":
        """Import Python web framework *fastapi*."""
        import fastapi

        return fastapi

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


def ensure_importing(import_callback: Callable, import_err_callback: Callable = None) -> Callable:
    """Load application if importing works finely without any issue. Or it will do nothing.

    Args:
        import_callback (Callable): The callback function to import module.
        import_err_callback (Callable): The callback function which would be run if it failed at importing.

    Returns:
        None

    """

    def _import(function) -> Callable:
        def _(*args, **kwargs) -> None:
            try:
                import_callback()
            except (ImportError, ModuleNotFoundError) as e:
                if import_err_callback:
                    import_err_callback(e)
                module = str(e).split(" ")[-1]
                raise RuntimeError(
                    f"Cannot load mocked application because current Python runtime environment cannot import {module}."
                ) from e
            else:
                return function(*args, **kwargs)

        return _

    return _import
