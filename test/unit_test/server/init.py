import re
from typing import Callable, Type, Union
from unittest.mock import Mock, patch

import pytest

import pymock_api.server as mock_server
from pymock_api.exceptions import FunctionNotFoundError

from ..._values import _Test_Config

mock_flask_server = Mock(mock_server.FlaskServer())
mock_fastapi_server = Mock(mock_server.FastAPIServer())
mock_server_obj = Mock(mock_server.MockHTTPServer)


def _fake_function() -> None:
    # This is fake function for PyTest
    pass


class TestLoadApp:
    @pytest.fixture(scope="function")
    def load_app(self) -> Type[mock_server.load_app]:
        return mock_server.load_app

    @patch("pymock_api.server.MockHTTPServer", return_value=mock_server_obj)
    @patch("pymock_api.server.FlaskServer", return_value=mock_flask_server)
    @patch("os.environ.get", return_value=_Test_Config)
    def test_by_flask(
        self,
        mock_get_os_env: Mock,
        mock_flask_server_obj: Mock,
        mock_http_server: Mock,
        load_app: Type[mock_server.load_app],
    ):
        load_app.by_flask()
        # FIXME: Strange error.
        # mock_get_os_env.assert_called_once_with("MockAPI_Config", "api.yaml")
        mock_flask_server_obj.assert_called_once()
        mock_http_server.assert_called_once_with(
            config_path=_Test_Config, app_server=mock_flask_server, auto_setup=True
        )

    @patch("pymock_api.server.MockHTTPServer", return_value=mock_server_obj)
    @patch("pymock_api.server.FastAPIServer", return_value=mock_fastapi_server)
    @patch("os.environ.get", return_value=_Test_Config)
    def test_by_flask(
        self,
        mock_get_os_env: Mock,
        mock_fastapi_server_obj: Mock,
        mock_http_server: Mock,
        load_app: Type[mock_server.load_app],
    ):
        load_app.by_fastapi()
        # FIXME: Strange error.
        # mock_get_os_env.assert_called_once_with("MockAPI_Config", "api.yaml")
        mock_fastapi_server_obj.assert_called_once()
        mock_http_server.assert_called_once_with(
            config_path=_Test_Config, app_server=mock_fastapi_server, auto_setup=True
        )

    @patch("os.environ.get", return_value=_Test_Config)
    def test_inner_get_config_path(self, mock_get_os_env: Mock, load_app: Type[mock_server.load_app]):
        path = load_app._get_config_path()
        mock_get_os_env.assert_called_once_with("MockAPI_Config", "api.yaml")
        assert path == _Test_Config

    @patch("pymock_api.server.MockHTTPServer", return_value=mock_server_obj)
    def test_initial_mock_server(self, mock_http_server: Mock, load_app: Type[mock_server.load_app]):
        server = load_app._initial_mock_server(config_path=_Test_Config, app_server=mock_flask_server)
        mock_http_server.assert_called_once_with(
            config_path=_Test_Config, app_server=mock_flask_server, auto_setup=True
        )
        assert server == mock_server_obj


class TestCreateAppFunctions:
    @patch.object(mock_server.load_app, "by_flask")
    def test_create_flask_app(self, mock_load_app: Mock):
        mock_server.create_flask_app()
        mock_load_app.assert_called_once()

    @patch.object(mock_server.load_app, "by_fastapi")
    def test_create_flask_app(self, mock_load_app: Mock):
        mock_server.create_fastapi_app()
        mock_load_app.assert_called_once()


class TestSetupServerGateway:
    @pytest.mark.parametrize(
        ("app", "expected_app"),
        [("create_flask_app()", "create_flask_app()"), (mock_server.create_flask_app, "create_flask_app()")],
    )
    @patch("pymock_api.server.WSGIServer")
    def test_setup_wsgi(self, mock_instantiate_wsgi: Mock, app: Union[str, Callable], expected_app: str):
        mock_server.setup_server_gateway.wsgi(web_app=app)
        mock_instantiate_wsgi.assert_called_once_with(app=expected_app)

    @pytest.mark.parametrize(
        ("app", "expected_error"),
        [
            ("create_not_exist_app()", FunctionNotFoundError),
            (_fake_function, FunctionNotFoundError),
        ],
    )
    @patch("pymock_api.server.WSGIServer")
    def test_bad_setup_wsgi(self, mock_instantiate_wsgi: Mock, app: Union[str, Callable], expected_error: Exception):
        with pytest.raises(expected_error) as exc_info:
            mock_server.setup_server_gateway.wsgi(web_app=app)
        assert re.search(r"cannot find .{0,32}function", str(exc_info.value), re.IGNORECASE)
        mock_instantiate_wsgi.assert_not_called()

    @pytest.mark.parametrize(
        ("app", "expected_app"),
        [("create_fastapi_app", "create_fastapi_app"), (mock_server.create_fastapi_app, "create_fastapi_app")],
    )
    @patch("pymock_api.server.ASGIServer")
    def test_setup_asgi(self, mock_instantiate_asgi: Mock, app: Union[str, Callable], expected_app: str):
        mock_server.setup_server_gateway.asgi(web_app=app)
        mock_instantiate_asgi.assert_called_once_with(app=expected_app)
