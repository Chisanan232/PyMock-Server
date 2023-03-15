import re
import sys
from abc import abstractmethod
from typing import Type, Union
from unittest.mock import Mock

import flask
import pytest

import pymock_api.server as mock_server

from .._spec import SpecWithFileOpt

SETUP_APP_TYPE = Type[mock_server.SetupApp]
LOAD_APP_TYPE = Type[mock_server.load_app]


class ServerInitTestSpec(SpecWithFileOpt):
    @pytest.fixture(scope="function")
    @abstractmethod
    def initial_app(self) -> Union[SETUP_APP_TYPE, LOAD_APP_TYPE]:
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
            self._write_test_file()

            try:
                # Run the test item
                function(self, initial_app)
            finally:
                # Delete file finally
                self._delete_file()

        return _


class TestSetupApp(ServerInitTestSpec):
    @pytest.fixture(scope="function")
    def initial_app(self) -> SETUP_APP_TYPE:
        return mock_server.SetupApp

    @ServerInitTestSpec._test_with_file
    def test_by_flask(self, initial_app: SETUP_APP_TYPE):
        initial_app.by_flask()
        assert isinstance(mock_server.flask_app, flask.Flask)

    @pytest.mark.skip(reason="Not finish this test because not sure how to mock 'import'.")
    @SpecWithFileOpt._test_with_file
    def test_by_flask_when_cannot_import(self):
        assert "flask" in sys.modules
        mock_import = Mock(side_effect=ImportError("Import error named 'flask'"))
        sys.modules["flask"] = mock_import
        import pymock_api.server as sut_server

        with pytest.raises(RuntimeError) as exc_info:
            sut_server.SetupApp.by_flask()
        mock_import.assert_called_once()
        assert re.search(r"Cannot load.[0,256]cannot import 'flask'.[0,256]", str(exc_info.value))


class TestLoadApp(ServerInitTestSpec):
    @pytest.fixture(scope="function")
    def initial_app(self) -> LOAD_APP_TYPE:
        return mock_server.load_app

    @ServerInitTestSpec._test_with_file
    def test_with_flask(self, initial_app: LOAD_APP_TYPE):
        initial_app.with_flask()
        assert isinstance(mock_server.flask_app, flask.Flask)

    @pytest.mark.skip(reason="Not finish this test because not sure how to mock 'import'.")
    @ServerInitTestSpec._test_with_file
    def test_with_flask_when_cannot_import(self, initial_app: LOAD_APP_TYPE):
        sys.modules.pop("flask")
        with pytest.raises(RuntimeError) as exc_info:
            initial_app.with_flask()
        assert re.search(r"Cannot load.[0,256]cannot import.[0,256]", str(exc_info.value))
