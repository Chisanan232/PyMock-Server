import json
import os
import re
from typing import Type
from unittest.mock import Mock, mock_open, patch

import pytest

from pymock_api.exceptions import FileFormatNotSupport
from pymock_api.model.api_config import IteratorItem, ResponseProperty
from pymock_api.model.api_config.apis import HTTPResponse
from pymock_api.model.enums import ResponseStrategy
from pymock_api.server.application.response import HTTPResponse as _HTTPResponse

from ...._values import (
    _General_String_Value,
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

    # @staticmethod
    # def with_object_strategy() -> HTTPResponse:
    #     return HTTPResponse(strategy=ResponseStrategy.OBJECT, properties=_HTTP_Response_Properties_With_Object_Strategy)

    @staticmethod
    def with_invalid_strategy() -> HTTPResponse:
        http_response = Mock()
        http_response.strategy = "invalid strategy"
        return http_response


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

    @pytest.mark.parametrize(
        ("mock_response_data", "expect_result"),
        [
            # *int* type value only
            (
                HTTPResponse(
                    strategy=ResponseStrategy.OBJECT,
                    properties=[ResponseProperty(name="id", required=True, value_type="int")],
                ),
                {"id": "random integer"},
            ),
            # *str* type value only
            (
                HTTPResponse(
                    strategy=ResponseStrategy.OBJECT,
                    properties=[ResponseProperty(name="role", required=True, value_type="str")],
                ),
                {"role": "random string"},
            ),
            # *list* type value only (only one data which has name and no nested data)
            (
                HTTPResponse(
                    strategy=ResponseStrategy.OBJECT,
                    properties=[
                        ResponseProperty(
                            name="white_list",
                            required=True,
                            value_type="list",
                            items=[
                                IteratorItem(name="name", value_type="str", required=True),
                            ],
                        )
                    ],
                ),
                {"white_list": [{"name": "random string"}]},
            ),
            # *list* type value only (only one data without name and no nested data)
            (
                HTTPResponse(
                    strategy=ResponseStrategy.OBJECT,
                    properties=[
                        ResponseProperty(
                            name="white_list",
                            required=True,
                            value_type="list",
                            items=[
                                IteratorItem(name="", value_type="str", required=True),
                            ],
                        )
                    ],
                ),
                {"white_list": ["random string"]},
            ),
            # *list* type value only (no nested data)
            (
                HTTPResponse(
                    strategy=ResponseStrategy.OBJECT,
                    properties=[
                        ResponseProperty(
                            name="details",
                            required=True,
                            value_type="list",
                            items=[
                                IteratorItem(name="name", value_type="str", required=True),
                                IteratorItem(name="id", value_type="int", required=True),
                                IteratorItem(name="key", value_type="str", required=True),
                            ],
                        )
                    ],
                ),
                {"details": [{"key": "random string", "id": "random integer", "name": "random string"}]},
            ),
            # *dict* type value only (no nested data)
            (
                HTTPResponse(
                    strategy=ResponseStrategy.OBJECT,
                    properties=[
                        ResponseProperty(
                            name="details",
                            required=True,
                            value_type="dict",
                            items=[
                                IteratorItem(name="name", value_type="str", required=True),
                                IteratorItem(name="id", value_type="int", required=True),
                                IteratorItem(name="key", value_type="str", required=True),
                            ],
                        )
                    ],
                ),
                {"details": {"key": "random string", "id": "random integer", "name": "random string"}},
            ),
            # *dict* type value with nested data
            (
                HTTPResponse(
                    strategy=ResponseStrategy.OBJECT,
                    properties=[
                        ResponseProperty(
                            name="details",
                            required=True,
                            value_type="dict",
                            items=[
                                IteratorItem(name="name", value_type="str", required=True),
                                IteratorItem(name="id", value_type="int", required=True),
                                IteratorItem(
                                    name="key",
                                    value_type="dict",
                                    required=True,
                                    items=[
                                        IteratorItem(name="base_authentication", value_type="str", required=True),
                                        IteratorItem(name="projects", value_type="str", required=True),
                                    ],
                                ),
                            ],
                        )
                    ],
                ),
                {
                    "details": {
                        "id": "random integer",
                        "name": "random string",
                        "key": {"base_authentication": "random string", "projects": "random string"},
                    }
                },
            ),
            # *dict* type value with more deeper nested data
            (
                HTTPResponse(
                    strategy=ResponseStrategy.OBJECT,
                    properties=[
                        ResponseProperty(
                            name="details",
                            required=True,
                            value_type="dict",
                            items=[
                                IteratorItem(name="name", value_type="str", required=True),
                                IteratorItem(name="id", value_type="int", required=True),
                                IteratorItem(
                                    name="projects",
                                    value_type="list",
                                    required=True,
                                    items=[
                                        IteratorItem(name="name", value_type="str", required=True),
                                        IteratorItem(name="description", value_type="str", required=True),
                                        IteratorItem(name="author", value_type="str", required=True),
                                        IteratorItem(
                                            name="languages",
                                            value_type="list",
                                            required=True,
                                            items=[
                                                IteratorItem(name="", value_type="str", required=True),
                                            ],
                                        ),
                                        IteratorItem(name="url", value_type="str", required=True),
                                        IteratorItem(
                                            name="start",
                                            value_type="list",
                                            required=True,
                                            items=[
                                                IteratorItem(name="number", value_type="int", required=True),
                                                IteratorItem(
                                                    name="people",
                                                    value_type="list",
                                                    required=True,
                                                    items=[
                                                        IteratorItem(name="name", value_type="str", required=True),
                                                        IteratorItem(name="url", value_type="str", required=True),
                                                    ],
                                                ),
                                            ],
                                        ),
                                        IteratorItem(
                                            name="tags",
                                            value_type="list",
                                            required=True,
                                            items=[
                                                IteratorItem(name="", value_type="str", required=True),
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                        )
                    ],
                ),
                {
                    "details": {
                        "name": "random string",
                        "id": "random integer",
                        "projects": [
                            {
                                "name": "random string",
                                "description": "random string",
                                "author": "random string",
                                "languages": ["random string"],
                                "url": "random string",
                                "start": [
                                    {
                                        "number": "random integer",
                                        "people": [{"name": "random string", "url": "random string"}],
                                    },
                                ],
                                "tags": ["random string"],
                            },
                        ],
                    }
                },
            ),
        ],
    )
    def test_response_with_object(
        self, http_resp: Type[_HTTPResponse], mock_response_data: HTTPResponse, expect_result: dict
    ):
        resp_data = http_resp.generate(data=mock_response_data)
        assert resp_data is not None
        assert resp_data == expect_result

    def test_response_with_invalid_strategy(self, http_resp: Type[_HTTPResponse]):
        with pytest.raises(TypeError) as exc_info:
            http_resp.generate(data=_MockHTTPResponse.with_invalid_strategy())
        assert re.search(r".{0,32}invalid.{0,32}", str(exc_info.value), re.IGNORECASE)
