"""*The wrapper of application which ruled by SGI (server gateway interface)*

The factory to generate SGI application instance to run Python web framework.
"""

import re
from typing import Callable, Union

from ...exceptions import FunctionNotFoundError
from .cmd import ASGIServer, WSGIServer
from .cmdoption import ASGICmdOption, WSGICmdOption


class setup_server_gateway:
    @classmethod
    def wsgi(cls, web_app: Union[str, Callable], module_dict: dict = None) -> WSGIServer:
        if module_dict:
            cls._ensure_function_exists(web_app, module_dict)
        web_app = f"{web_app.__qualname__}()" if isinstance(web_app, Callable) else web_app
        return WSGIServer(app=web_app)

    @classmethod
    def asgi(cls, web_app: Union[str, Callable], module_dict: dict = None) -> ASGIServer:
        if module_dict:
            cls._ensure_function_exists(web_app, module_dict)
        web_app = web_app.__name__ if isinstance(web_app, Callable) else web_app
        return ASGIServer(app=web_app)

    @classmethod
    def _ensure_function_exists(cls, function: Union[str, Callable], module_dict: dict) -> None:
        function = (
            function.__qualname__ if isinstance(function, Callable) else re.search(r"\w{0,32}", function).group(0)
        )
        if function not in module_dict.keys():
            raise FunctionNotFoundError(function=function)
