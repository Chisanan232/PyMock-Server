"""*Handle importing*"""

from typing import Callable


class import_web_lib:
    """*Import the Python library and return it.*"""

    @staticmethod
    def flask() -> "flask":
        """Import Python web framework *flask*."""
        import flask

        return flask


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
