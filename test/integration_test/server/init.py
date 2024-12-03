import os
import re
from typing import Type
from unittest.mock import patch

import fastapi
import flask
import pytest

import pymock_server.server as mock_server

from ..._file_utils import MockAPI_Config_Yaml_Path, yaml_factory
from ..._spec import run_test

LOAD_APP_TYPE = Type[mock_server.load_app]


class TestLoadApp:
    @pytest.fixture(scope="function")
    def load_app(self) -> LOAD_APP_TYPE:
        os.environ["MockAPI_Config"] = MockAPI_Config_Yaml_Path
        return mock_server.load_app

    @run_test.with_file(yaml_factory)
    @pytest.mark.parametrize(
        ("web_lib", "expected"),
        [
            ("flask", flask.Flask),
            ("fastapi", fastapi.FastAPI),
        ],
    )
    def test_by_flask(self, load_app: LOAD_APP_TYPE, web_lib: str, expected):
        getattr(load_app, f"by_{web_lib}")()
        assert isinstance(getattr(mock_server, f"{web_lib}_app"), expected)

    @run_test.with_file(yaml_factory)
    @pytest.mark.parametrize(
        ("web_lib", "expected"),
        [
            ("Flask", flask.Flask),
            ("FastAPI", fastapi.FastAPI),
        ],
    )
    def test_by_flask_when_cannot_import(self, web_lib: str, expected):
        with patch.object(
            getattr(mock_server, f"{web_lib}Server"), "setup", side_effect=RuntimeError("Import error for PyTest")
        ) as mock_web_server:
            with pytest.raises(RuntimeError) as exc_info:
                getattr(mock_server.load_app, f"by_{web_lib.lower()}")()
            mock_web_server.assert_called_once()
            assert re.search(r"Import error for PyTest", str(exc_info.value))
