import re
from typing import Callable, Union
from unittest.mock import Mock, patch

import pytest

import pymock_server.server as mock_server
from pymock_server.exceptions import FunctionNotFoundError


def _fake_function() -> None:
    # This is fake function for PyTest
    pass


class TestSetupServerGateway:
    @pytest.mark.parametrize(
        ("app", "expected_app"),
        [("create_flask_app()", "create_flask_app()"), (mock_server.create_flask_app, "create_flask_app()")],
    )
    @patch("pymock_server.server.rest.sgi.WSGIServer")
    def test_setup_wsgi(self, mock_instantiate_wsgi: Mock, app: Union[str, Callable], expected_app: str):
        mock_server.setup_server_gateway.wsgi(web_app=app)
        mock_instantiate_wsgi.assert_called_once_with(app=expected_app)

    @pytest.mark.parametrize(
        ("sut_func", "app", "expected_error"),
        [
            ("wsgi", "create_not_exist_app()", FunctionNotFoundError),
            ("wsgi", _fake_function, FunctionNotFoundError),
        ],
    )
    @patch("pymock_server.server.rest.sgi.WSGIServer")
    def test_bad_setup_wsgi(
        self, mock_instantiate_wsgi: Mock, sut_func: str, app: Union[str, Callable], expected_error: Exception
    ):
        with pytest.raises(expected_error) as exc_info:
            module_dicts_not_have_target_functions = {"not exist target function": ""}
            getattr(mock_server.setup_server_gateway, sut_func)(
                web_app=app, module_dict=module_dicts_not_have_target_functions
            )
        assert re.search(r"cannot find .{0,32}function", str(exc_info.value), re.IGNORECASE)
        mock_instantiate_wsgi.assert_not_called()

    @pytest.mark.parametrize(
        ("app", "expected_app"),
        [("create_fastapi_app", "create_fastapi_app"), (mock_server.create_fastapi_app, "create_fastapi_app")],
    )
    @patch("pymock_server.server.rest.sgi.ASGIServer")
    def test_setup_asgi(self, mock_instantiate_asgi: Mock, app: Union[str, Callable], expected_app: str):
        mock_server.setup_server_gateway.asgi(web_app=app)
        mock_instantiate_asgi.assert_called_once_with(app=expected_app)
