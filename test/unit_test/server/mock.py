import json
import os
from typing import Callable, Type
from unittest.mock import Mock, mock_open, patch

import pytest

from pymock_api.exceptions import FileFormatNotSupport
from pymock_api.model.api_config import APIConfig, MockAPIs
from pymock_api.server.application import FlaskServer
from pymock_api.server.mock import MockHTTPServer, _HTTPResponse

_General_String_Value: str = "This is test message for PyTest."
_Json_File_Name: str = "test.json"
_Json_File_Content: dict = {"responseCode": "200", "errorMessage": "OK", "content": "This is YouTube home."}
_Not_Exist_File_Name: str = "not_exist.json"
_Not_Json_File_Name: str = "test.yaml"


class TestMockHTTPServer:
    def test_instantiate_arg_config_path_by_default(self):
        def _instantiate() -> MockHTTPServer:
            return MockHTTPServer()

        TestMockHTTPServer._template_test(instantiate_callback=_instantiate, assert_config_path="api.yaml")

    def test_instantiate_arg_config_path_by_valid_file(self):
        config_file_path = "target_config.yaml"

        def _instantiate() -> MockHTTPServer:
            return MockHTTPServer(config_path=config_file_path)

        TestMockHTTPServer._template_test(instantiate_callback=_instantiate, assert_config_path=config_file_path)

    def test_instantiate_arg_app_server_by_default(self):
        def _instantiate() -> MockHTTPServer:
            return MockHTTPServer()

        TestMockHTTPServer._template_test(instantiate_callback=_instantiate, assert_config_path="api.yaml")

    def test_instantiate_arg_app_server_by_valid_obj(self):
        mock_app_server = Mock(FlaskServer())

        def _instantiate() -> MockHTTPServer:
            return MockHTTPServer(app_server=mock_app_server)

        TestMockHTTPServer._template_test(
            instantiate_callback=_instantiate, assert_config_path="api.yaml", assert_app_server=mock_app_server
        )

    def test_instantiate_arg_app_server_by_invalid_obj(self):
        class InvalidServer:
            pass

        with patch("pymock_api.server.mock.load_config") as mock_load_config:
            invalid_server = InvalidServer()
            try:
                MockHTTPServer(app_server=invalid_server)
            except TypeError as e:
                # Verify result
                expected_err_msg = (
                    f"The instance {invalid_server} must be *pymock_api.application.BaseAppServer* type object."
                )
                assert str(e) == expected_err_msg, f"The error message should be same as '{expected_err_msg}'."
                mock_load_config.assert_called_once_with(config_path="api.yaml")
            else:
                # Verify result
                assert False, "It should raise an exception about 'TypeError'."

    def test_instantiate_arg_auto_setup(self):
        def _instantiate() -> MockHTTPServer:
            return MockHTTPServer(auto_setup=True)

        TestMockHTTPServer._template_test(
            instantiate_callback=_instantiate, assert_config_path="api.yaml", auto_setup=True
        )

    @staticmethod
    def _template_test(
        instantiate_callback: Callable,
        assert_config_path: str,
        assert_app_server: Mock = None,
        auto_setup: bool = False,
    ) -> None:
        def _run_test(mock_load_config: Mock, mock_app_server: Mock, instantiate_flask_app_server: bool) -> None:
            # Run target function to test
            with patch.object(MockHTTPServer, "create_apis", return_value=None) as mock_create_apis:
                instantiate_callback()

                # Verify running result
                mock_load_config.assert_called_once_with(config_path=assert_config_path)

                if instantiate_flask_app_server:
                    mock_app_server.assert_called_once()
                else:
                    mock_app_server.assert_not_called()

                if auto_setup:
                    mock_create_apis.assert_called_once()
                else:
                    mock_create_apis.assert_not_called()

        # Mock functions and objects
        mock_api_config = Mock(
            APIConfig(name=Mock(), description=Mock(), apis=Mock(MockAPIs(base=Mock(), apis=Mock())))
        )
        # Note: About patch to the function in __init__ module of sub-package
        # pylint: disable=line-too-long
        # Refer: https://stackoverflow.com/questions/55723133/patching-a-function-inside-a-package-init-and-use-it-within-a-module-inside
        with patch("pymock_api.server.mock.load_config", return_value=mock_api_config) as mock_load_config:
            if assert_app_server:
                _run_test(
                    mock_load_config=mock_load_config,
                    mock_app_server=assert_app_server,
                    instantiate_flask_app_server=False,
                )
            else:
                with patch("pymock_api.server.mock.FlaskServer") as mock_flask_server_obj:
                    _run_test(
                        mock_load_config=mock_load_config,
                        mock_app_server=mock_flask_server_obj,
                        instantiate_flask_app_server=True,
                    )


class TestInnerHTTPResponse:
    @pytest.fixture(scope="function")
    def http_resp(self) -> Type[_HTTPResponse]:
        return _HTTPResponse

    def test_response_with_string_data(self, http_resp: Type[_HTTPResponse]):
        resp_data = http_resp.generate(data=_General_String_Value)
        assert resp_data == _General_String_Value, ""

    def test_response_with_json_format_string_data(self, http_resp: Type[_HTTPResponse]):
        json_content_str = json.dumps(_Json_File_Content)
        resp_data = http_resp.generate(data=json_content_str)
        assert resp_data == json.loads(json_content_str), ""

    def test_response_with_json_file_name(self, http_resp: Type[_HTTPResponse]):
        with patch.object(os.path, "exists", return_value=True) as os_path_exists:
            json_content_str = json.dumps(_Json_File_Content)
            with patch("builtins.open", mock_open(read_data=json_content_str)) as mock_file_stream:
                # Run target function to test
                resp_data = http_resp.generate(data=_Json_File_Name)

                # Verify result
                os_path_exists.assert_called_once_with(_Json_File_Name)
                mock_file_stream.assert_called_once_with(_Json_File_Name, "r", encoding="utf-8")
                assert open(_Json_File_Name).read() == json_content_str, ""
                assert resp_data == _Json_File_Content, ""

    def test_response_with_not_exist_json_file_name(self, http_resp: Type[_HTTPResponse]):
        with patch("builtins.open", mock_open(read_data=None)) as mock_file_stream:
            try:
                # Run target function to test
                http_resp.generate(data=_Not_Exist_File_Name)
            except FileNotFoundError as e:
                # Verify result
                expected_err_msg = f"The target configuration file {_Not_Exist_File_Name} doesn't exist."
                assert str(e) == expected_err_msg, f"The error message should be same as '{expected_err_msg}'."
                mock_file_stream.assert_not_called()
            else:
                # Verify result
                assert False, "It should raise an exception about 'FileNotFoundError'."

    def test_response_with_not_json_file_name(self, http_resp: Type[_HTTPResponse]):
        with patch("builtins.open", mock_open(read_data=None)) as mock_file_stream:
            try:
                # Run target function to test
                http_resp.generate(data=_Not_Json_File_Name)
            except FileFormatNotSupport as e:
                # Verify result
                expected_err_msg = f"It doesn't support reading '{', '.join(http_resp.valid_file_format)}' format file."
                assert str(e) == expected_err_msg, f"The error message should be same as '{expected_err_msg}'."
                mock_file_stream.assert_not_called()
            else:
                # Verify result
                assert False, "It should raise an exception about 'FileNotFoundError'."
