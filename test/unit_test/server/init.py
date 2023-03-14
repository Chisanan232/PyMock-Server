import sys
from typing import Type
from unittest.mock import Mock, patch

import pytest

import pymock_api.server as mock_server

from ..._values import _Test_Config

mock_flask_server = Mock(mock_server.FlaskServer())
mock_server_obj = Mock(mock_server.MockHTTPServer)


class TestSetupApp:
    @pytest.fixture(scope="function")
    def setup_app(self) -> Type[mock_server.SetupApp]:
        return mock_server.SetupApp

    @patch("pymock_api.server.MockHTTPServer", return_value=mock_server_obj)
    @patch("pymock_api.server.FlaskServer", return_value=mock_flask_server)
    @patch("os.environ.get", return_value=_Test_Config)
    def test_by_flask(
        self,
        mock_get_os_env: Mock,
        mock_flask_server_obj: Mock,
        mock_http_server: Mock,
        setup_app: Type[mock_server.SetupApp],
    ):
        setup_app.by_flask()
        mock_get_os_env.assert_called_once_with("MockAPI_Config", "api.yaml")
        mock_flask_server_obj.assert_called_once()
        mock_http_server.assert_called_once_with(
            config_path=_Test_Config, app_server=mock_flask_server, auto_setup=True
        )

    @patch("os.environ.get", return_value=_Test_Config)
    def test_inner_get_config_path(self, mock_get_os_env: Mock, setup_app: Type[mock_server.SetupApp]):
        path = setup_app._get_config_path()
        mock_get_os_env.assert_called_once_with("MockAPI_Config", "api.yaml")
        assert path == _Test_Config

    @patch("pymock_api.server.MockHTTPServer", return_value=mock_server_obj)
    def test_initial_mock_server(self, mock_http_server: Mock, setup_app: Type[mock_server.SetupApp]):
        server = setup_app._initial_mock_server(config_path=_Test_Config, app_server=mock_flask_server)
        mock_http_server.assert_called_once_with(
            config_path=_Test_Config, app_server=mock_flask_server, auto_setup=True
        )
        assert server == mock_server_obj


class TestLoadApp:
    @pytest.fixture(scope="function")
    def load_app(self) -> Type[mock_server.load_app]:
        return mock_server.load_app

    @patch.object(mock_server.SetupApp, "by_flask")
    def test_with_flask(self, mock_setup_by_flask: Mock, load_app: Type[mock_server.load_app]):
        mock_import_flask = Mock()
        sys.modules["flask"] = mock_import_flask

        load_app.with_flask()

        # mock_import_flask.assert_called_once()
        mock_setup_by_flask.assert_called_once()

    def test_inner_load_app_by_importing(self, load_app: Type[mock_server.load_app]):
        mock_import_function = Mock()
        mock_success_function = Mock()
        mock_fail_function = Mock()

        load_app._load_app_by_importing(
            import_callback=mock_import_function,
            import_success_callback=mock_success_function,
            import_err_callback=mock_fail_function,
        )

        mock_import_function.assert_called_once()
        mock_success_function.assert_called_once()
        mock_fail_function.assert_not_called()

    def test_bad_inner_load_app_by_importing(self, load_app: Type[mock_server.load_app]):
        test_exc = ImportError("This is PyTest exception.")

        def _import() -> None:
            raise test_exc

        def _handle_success() -> None:
            pass

        def _handle_error(e: Exception) -> None:
            raise e

        with pytest.raises(ImportError) as exc_info:
            load_app._load_app_by_importing(
                import_callback=_import, import_success_callback=_handle_success, import_err_callback=_handle_error
            )
        assert str(exc_info.value) == str(test_exc)


class TestCreateAppFunctions:
    @patch.object(mock_server.load_app, "with_flask")
    def test_create_flask_app(self, mock_load_app: Mock):
        mock_server.create_flask_app()
        mock_load_app.assert_called_once()
