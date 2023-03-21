import os
import re
from typing import Type
from unittest.mock import Mock, patch

import flask
import pytest

import pymock_api.server as mock_server

from .._spec import MockAPI_Config_Path, run_test

LOAD_APP_TYPE = Type[mock_server.load_app]


class TestLoadApp:
    @pytest.fixture(scope="function")
    def load_app(self) -> LOAD_APP_TYPE:
        os.environ["MockAPI_Config"] = MockAPI_Config_Path
        return mock_server.load_app

    @run_test.with_file
    def test_by_flask(self, load_app: LOAD_APP_TYPE):
        load_app.by_flask()
        assert isinstance(mock_server.flask_app, flask.Flask)

    @run_test.with_file
    @patch.object(mock_server.FlaskServer, "setup", side_effect=RuntimeError("Import error for PyTest"))
    def test_by_flask_when_cannot_import(self, mock_flask_server: Mock):
        with pytest.raises(RuntimeError) as exc_info:
            mock_server.load_app.by_flask()
        mock_flask_server.assert_called_once()
        assert re.search(r"Import error for PyTest", str(exc_info.value))
