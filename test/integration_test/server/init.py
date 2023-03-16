import re
from abc import abstractmethod
from typing import Type
from unittest.mock import Mock, patch

import flask
import pytest

import pymock_api.server as mock_server

from .._spec import ConfigFile

LOAD_APP_TYPE = Type[mock_server.load_app]


class ServerInitTestSpec(ConfigFile):
    @pytest.fixture(scope="function")
    @abstractmethod
    def initial_app(self) -> LOAD_APP_TYPE:
        pass

    @property
    def file_path(self) -> str:
        return "api.yaml"

    @staticmethod
    def _test_with_file(function):
        def _(self, initial_app):
            # Ensure that it doesn't have file
            self._delete_file()
            # Create the target file before run test
            self.generate()

            try:
                # Run the test item
                function(self, initial_app)
            finally:
                # Delete file finally
                self._delete_file()

        return _


class TestLoadApp(ServerInitTestSpec):
    @pytest.fixture(scope="function")
    def initial_app(self) -> LOAD_APP_TYPE:
        return mock_server.load_app

    @ServerInitTestSpec._test_with_file
    def test_by_flask(self, initial_app: LOAD_APP_TYPE):
        initial_app.by_flask()
        assert isinstance(mock_server.flask_app, flask.Flask)

    @ConfigFile._test_with_file
    @patch.object(mock_server.FlaskServer, "setup", side_effect=RuntimeError("Import error for PyTest"))
    def test_by_flask_when_cannot_import(self, mock_flask_server: Mock):
        with pytest.raises(RuntimeError) as exc_info:
            mock_server.load_app.by_flask()
        mock_flask_server.assert_called_once()
        assert re.search(r"Import error for PyTest", str(exc_info.value))
