import json
import os
from pydoc import locate
from typing import Type
from unittest.mock import mock_open, patch

import pytest

from pymock_api.exceptions import FileFormatNotSupport
from pymock_api.model import HTTPResponse
from pymock_api.model.enums import ResponseStrategy
from pymock_api.server.application.response import HTTPResponse as _HTTPResponse

from ...._values import (
    _General_String_Value,
    _HTTP_Response_Properties_With_Object_Strategy,
    _Json_File_Content,
    _Json_File_Name,
    _Not_Exist_File_Name,
    _Not_Json_File_Name,
    _Unexpected_File_Name,
)


class _MockHTTPResponse:
    @staticmethod
    def with_string_strategy() -> HTTPResponse:
        return HTTPResponse(strategy=ResponseStrategy.STRING, value=_General_String_Value)

    @staticmethod
    def with_json_format_string_strategy() -> HTTPResponse:
        json_content_str = json.dumps(_Json_File_Content)
        return HTTPResponse(strategy=ResponseStrategy.STRING, value=json_content_str)

    @staticmethod
    def with_file_strategy() -> HTTPResponse:
        return HTTPResponse(strategy=ResponseStrategy.FILE, path=_Json_File_Name)

    @staticmethod
    def with_not_exist_file_strategy() -> HTTPResponse:
        return HTTPResponse(strategy=ResponseStrategy.FILE, path=_Not_Exist_File_Name)

    @staticmethod
    def with_not_json_file_strategy() -> HTTPResponse:
        return HTTPResponse(strategy=ResponseStrategy.FILE, path=_Not_Json_File_Name)

    @staticmethod
    def with_unexpected_file_strategy() -> HTTPResponse:
        return HTTPResponse(strategy=ResponseStrategy.FILE, path=_Unexpected_File_Name)

    @staticmethod
    def with_object_strategy() -> HTTPResponse:
        return HTTPResponse(strategy=ResponseStrategy.OBJECT, properties=_HTTP_Response_Properties_With_Object_Strategy)


class TestInnerHTTPResponse:
    @pytest.fixture(scope="function")
    def http_resp(self) -> Type[_HTTPResponse]:
        return _HTTPResponse

    def test_response_with_string_data(self, http_resp: Type[_HTTPResponse]):
        resp_data = http_resp.generate(data=_MockHTTPResponse.with_string_strategy())
        assert resp_data == _General_String_Value, ""

    def test_response_with_json_format_string_data(self, http_resp: Type[_HTTPResponse]):
        resp_data = http_resp.generate(data=_MockHTTPResponse.with_json_format_string_strategy())
        assert resp_data == json.loads(json.dumps(_Json_File_Content)), ""

    def test_response_with_json_file_name(self, http_resp: Type[_HTTPResponse]):
        with patch.object(os.path, "exists", return_value=True) as os_path_exists:
            json_content_str = json.dumps(_Json_File_Content)
            with patch("builtins.open", mock_open(read_data=json_content_str)) as mock_file_stream:
                # Run target function to test
                resp_data = http_resp.generate(data=_MockHTTPResponse.with_file_strategy())

                # Verify result
                os_path_exists.assert_called_once_with(_Json_File_Name)
                mock_file_stream.assert_called_once_with(_Json_File_Name, "r", encoding="utf-8")
                assert open(_Json_File_Name).read() == json_content_str, ""
                assert resp_data == _Json_File_Content, ""

    def test_response_with_not_exist_json_file_name(self, http_resp: Type[_HTTPResponse]):
        with patch("builtins.open", mock_open(read_data=None)) as mock_file_stream:
            with pytest.raises(FileNotFoundError) as exc_info:
                # Run target function to test
                http_resp.generate(data=_MockHTTPResponse.with_not_exist_file_strategy())
                # Verify result
                expected_err_msg = f"The target configuration file {_Not_Exist_File_Name} doesn't exist."
                assert str(exc_info) == expected_err_msg, f"The error message should be same as '{expected_err_msg}'."
                mock_file_stream.assert_not_called()

    def test_response_with_not_json_file_name(self, http_resp: Type[_HTTPResponse]):
        with patch("builtins.open", mock_open(read_data=None)) as mock_file_stream:
            with pytest.raises(FileFormatNotSupport) as exc_info:
                # Run target function to test
                http_resp.generate(data=_MockHTTPResponse.with_not_json_file_strategy())
                # Verify result
                expected_err_msg = f"It doesn't support reading '{', '.join(http_resp.valid_file_format)}' format file."
                assert str(exc_info) == expected_err_msg, f"The error message should be same as '{expected_err_msg}'."
                mock_file_stream.assert_not_called()

    def test_response_with_unexpected_file_name(self, http_resp: Type[_HTTPResponse]):
        with patch("builtins.open", mock_open(read_data=None)) as mock_file_stream:
            # Run target function to test
            response = http_resp.generate(data=_MockHTTPResponse.with_unexpected_file_strategy())
            # Verify result
            assert response == _Unexpected_File_Name
            mock_file_stream.assert_not_called()

    def test_response_with_object(self, http_resp: Type[_HTTPResponse]):
        resp_data = http_resp.generate(data=_MockHTTPResponse.with_object_strategy())
        """
        {'details': [{'key': 'random string',
                      'level': 'random integer',
                      'name': 'random string'},
                     {'key': 'random string',
                      'level': 'random integer',
                      'name': 'random string'},
                     {'key': 'random string',
                      'level': 'random integer',
                      'name': 'random string'}],
         'id': 'random integer',
         'role': 'random string'}
        """
        assert resp_data
        for k, v in resp_data.items():
            prop = list(filter(lambda p: p["name"] == k, _HTTP_Response_Properties_With_Object_Strategy))
            assert prop and len(prop) == 1

            # TODO: Change to here easy and clear verify
            # assert isinstance(v, locate(prop[0]["type"]))
            if locate(prop[0]["type"]) is str:
                assert v == "random string"
            elif locate(prop[0]["type"]) is int:
                assert v == "random integer"
            elif locate(prop[0]["type"]) is list:
                assert type(v) is list
                for v_ele in v:
                    for v_ele_k, v_ele_v in v_ele.items():
                        v_list_ele = list(filter(lambda p: p["name"] == v_ele_k, prop[0]["items"]))
                        assert v_list_ele and len(v_list_ele) == 1
                        if locate(v_list_ele[0]["type"]) is str:
                            assert v_ele_v == "random string"
                        elif locate(v_list_ele[0]["type"]) is int:
                            assert v_ele_v == "random integer"
                        else:
                            assert False, "Invalid data type of response for verifying."
            else:
                assert False, "Invalid data type of response for verifying."
