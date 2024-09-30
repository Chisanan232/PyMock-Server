import json
import os
import re
from decimal import Decimal
from typing import Type, Union
from unittest.mock import Mock, mock_open, patch

import pytest

from pymock_api.exceptions import FileFormatNotSupport
from pymock_api.model.api_config import IteratorItem, ResponseProperty
from pymock_api.model.api_config.apis import HTTPResponse, ResponseStrategy
from pymock_api.model.api_config.format import Format
from pymock_api.model.api_config.value import FormatStrategy, ValueFormat
from pymock_api.model.api_config.variable import Size, Variable
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
            # *list* type value with deeper nested data
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
                    "details": [
                        {
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
                    ],
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

    @pytest.mark.parametrize(
        ("mock_response_data", "expect_result"),
        [
            # # *list* type value only (only one data which has name and no nested data)
            # size with max & min
            (
                HTTPResponse(
                    strategy=ResponseStrategy.OBJECT,
                    properties=[
                        ResponseProperty(
                            name="white_list",
                            required=True,
                            value_type="list",
                            value_format=Format(size=Size(max_value=4, min_value=1)),
                            items=[
                                IteratorItem(name="name", value_type="str", required=True),
                            ],
                        )
                    ],
                ),
                {"white_list": [{"name": "random string"}]},
            ),
            # size with only_equal
            (
                HTTPResponse(
                    strategy=ResponseStrategy.OBJECT,
                    properties=[
                        ResponseProperty(
                            name="white_list",
                            required=True,
                            value_type="list",
                            value_format=Format(size=Size(only_equal=3)),
                            items=[
                                IteratorItem(name="name", value_type="str", required=True),
                            ],
                        )
                    ],
                ),
                {"white_list": [{"name": "random string"}, {"name": "random string"}, {"name": "random string"}]},
            ),
            # # *list* type value only (only one data without name and no nested data)
            # size with max & min
            (
                HTTPResponse(
                    strategy=ResponseStrategy.OBJECT,
                    properties=[
                        ResponseProperty(
                            name="white_list",
                            required=True,
                            value_type="list",
                            value_format=Format(size=Size(max_value=11, min_value=5)),
                            items=[
                                IteratorItem(name="", value_type="str", required=True),
                            ],
                        )
                    ],
                ),
                {"white_list": ["random string"]},
            ),
            # size with only_equal
            (
                HTTPResponse(
                    strategy=ResponseStrategy.OBJECT,
                    properties=[
                        ResponseProperty(
                            name="white_list",
                            required=True,
                            value_type="list",
                            value_format=Format(size=Size(only_equal=2)),
                            items=[
                                IteratorItem(name="", value_type="str", required=True),
                            ],
                        )
                    ],
                ),
                {"white_list": ["random string", "random string"]},
            ),
            # # *list* type value only (no nested data)
            # size with max & min
            (
                HTTPResponse(
                    strategy=ResponseStrategy.OBJECT,
                    properties=[
                        ResponseProperty(
                            name="details",
                            required=True,
                            value_type="list",
                            value_format=Format(size=Size(max_value=20, min_value=10)),
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
            # size with only_equal
            (
                HTTPResponse(
                    strategy=ResponseStrategy.OBJECT,
                    properties=[
                        ResponseProperty(
                            name="details",
                            required=True,
                            value_type="list",
                            value_format=Format(size=Size(only_equal=5)),
                            items=[
                                IteratorItem(name="name", value_type="str", required=True),
                                IteratorItem(name="id", value_type="int", required=True),
                                IteratorItem(name="key", value_type="str", required=True),
                            ],
                        )
                    ],
                ),
                {
                    "details": [
                        {"key": "random string", "id": "random integer", "name": "random string"},
                        {"key": "random string", "id": "random integer", "name": "random string"},
                        {"key": "random string", "id": "random integer", "name": "random string"},
                        {"key": "random string", "id": "random integer", "name": "random string"},
                        {"key": "random string", "id": "random integer", "name": "random string"},
                    ]
                },
            ),
        ],
    )
    def test_response_with_object_with_format_and_size(
        self, http_resp: Type[_HTTPResponse], mock_response_data: HTTPResponse, expect_result: dict
    ):
        resp_data = http_resp.generate(data=mock_response_data)
        assert resp_data is not None
        size_setting = mock_response_data.properties[0].value_format.size
        if size_setting.only_equal:
            assert resp_data == expect_result
        else:
            assert len(resp_data.values()) == 1
            for k, v in resp_data.items():
                chk_eles = list(map(lambda e: e == expect_result[k][0], v))
                assert False not in chk_eles
                assert size_setting.min_value <= len(v) <= size_setting.max_value

    @pytest.mark.parametrize(
        ("mock_response_data", "expect_result"),
        [
            # *str* type value with *format* (random string)
            (
                HTTPResponse(
                    strategy=ResponseStrategy.OBJECT,
                    properties=[
                        ResponseProperty(
                            name="role",
                            required=True,
                            value_type="str",
                            value_format=Format(strategy=FormatStrategy.BY_DATA_TYPE),
                        )
                    ],
                ),
                str,
            ),
            # *int* type value with *format* (random integer)
            (
                HTTPResponse(
                    strategy=ResponseStrategy.OBJECT,
                    properties=[
                        ResponseProperty(
                            name="role",
                            required=True,
                            value_type="int",
                            value_format=Format(strategy=FormatStrategy.BY_DATA_TYPE),
                        )
                    ],
                ),
                int,
            ),
            # *float* type value with *format* (random big decimal)
            (
                HTTPResponse(
                    strategy=ResponseStrategy.OBJECT,
                    properties=[
                        ResponseProperty(
                            name="role",
                            required=True,
                            value_type="float",
                            value_format=Format(strategy=FormatStrategy.BY_DATA_TYPE),
                        )
                    ],
                ),
                Decimal,
            ),
            # *bool* type value with *format* (random boolean)
            (
                HTTPResponse(
                    strategy=ResponseStrategy.OBJECT,
                    properties=[
                        ResponseProperty(
                            name="role",
                            required=True,
                            value_type="bool",
                            value_format=Format(strategy=FormatStrategy.BY_DATA_TYPE),
                        )
                    ],
                ),
                bool,
            ),
            # *str* type value with *format* (from enums value)
            (
                HTTPResponse(
                    strategy=ResponseStrategy.OBJECT,
                    properties=[
                        ResponseProperty(
                            name="role",
                            required=True,
                            value_type="str",
                            value_format=Format(
                                strategy=FormatStrategy.FROM_ENUMS, enums=["ENUM_1", "ENUM_2", "ENUM_3"]
                            ),
                        )
                    ],
                ),
                ["ENUM_1", "ENUM_2", "ENUM_3"],
            ),
            # *str* type value with *format* (customize value with big decimal)
            (
                HTTPResponse(
                    strategy=ResponseStrategy.OBJECT,
                    properties=[
                        ResponseProperty(
                            name="role",
                            required=True,
                            value_type="str",
                            value_format=Format(
                                strategy=FormatStrategy.CUSTOMIZE,
                                customize="<price_value>",
                                variables=[
                                    Variable(
                                        name="price_value",
                                        value_format=ValueFormat.BigDecimal,
                                        digit=None,
                                        size=None,
                                        enum=None,
                                    )
                                ],
                            ),
                        )
                    ],
                ),
                r"\d{0,64}(\.)\d{0,64}",
            ),
            # *str* type value with *format* (customize value with big decimal)
            (
                HTTPResponse(
                    strategy=ResponseStrategy.OBJECT,
                    properties=[
                        ResponseProperty(
                            name="role",
                            required=True,
                            value_type="float",
                            value_format=Format(
                                strategy=FormatStrategy.CUSTOMIZE,
                                customize="<price_value> <currency_code>",
                                variables=[
                                    Variable(
                                        name="price_value",
                                        value_format=ValueFormat.BigDecimal,
                                        digit=None,
                                        size=None,
                                        enum=None,
                                    ),
                                    Variable(
                                        name="currency_code",
                                        value_format=ValueFormat.Enum,
                                        digit=None,
                                        size=None,
                                        enum=["USD", "TWD"],
                                    ),
                                ],
                            ),
                        )
                    ],
                ),
                r"\d{0,64}(\.)\d{0,64} \w{0,10}",
            ),
        ],
    )
    def test_response_with_object_with_format(
        self, http_resp: Type[_HTTPResponse], mock_response_data: HTTPResponse, expect_result: Union[type, list, str]
    ):
        resp_data = http_resp.generate(data=mock_response_data)
        assert resp_data is not None
        resp_data_value = resp_data["role"]
        if isinstance(expect_result, type):
            assert isinstance(resp_data_value, expect_result)
        elif isinstance(expect_result, list):
            assert resp_data_value in expect_result
        elif isinstance(expect_result, str):
            assert re.search(expect_result, str(resp_data_value), re.IGNORECASE) is not None
        else:
            raise AssertionError(
                f"Doesn't implement the verify logic at this test scenario (expect_result: '{expect_result}')."
            )

    @pytest.mark.parametrize(
        ("mock_response_data", "expect_result_data_type"),
        [
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
                                IteratorItem(
                                    name="name",
                                    value_type="str",
                                    required=True,
                                    value_format=Format(strategy=FormatStrategy.BY_DATA_TYPE),
                                ),
                                IteratorItem(
                                    name="id",
                                    value_type="int",
                                    required=True,
                                    value_format=Format(strategy=FormatStrategy.BY_DATA_TYPE),
                                ),
                                IteratorItem(
                                    name="projects",
                                    value_type="list",
                                    required=True,
                                    items=[
                                        IteratorItem(
                                            name="name",
                                            value_type="str",
                                            required=True,
                                            value_format=Format(strategy=FormatStrategy.BY_DATA_TYPE),
                                        ),
                                        IteratorItem(
                                            name="description",
                                            value_type="str",
                                            required=True,
                                            value_format=Format(strategy=FormatStrategy.BY_DATA_TYPE),
                                        ),
                                        IteratorItem(
                                            name="author",
                                            value_type="str",
                                            required=True,
                                            value_format=Format(strategy=FormatStrategy.BY_DATA_TYPE),
                                        ),
                                        IteratorItem(
                                            name="languages",
                                            value_type="list",
                                            required=True,
                                            items=[
                                                IteratorItem(
                                                    name="",
                                                    value_type="str",
                                                    required=True,
                                                    value_format=Format(
                                                        strategy=FormatStrategy.FROM_ENUMS,
                                                        enums=["Python", "Scala", "Java", "JavaScript", "Kotlin"],
                                                    ),
                                                ),
                                            ],
                                        ),
                                        IteratorItem(
                                            name="url",
                                            value_type="str",
                                            required=True,
                                            value_format=Format(
                                                strategy=FormatStrategy.CUSTOMIZE,
                                                customize="https://<random_string>.com",
                                                variables=[
                                                    Variable(
                                                        name="random_string",
                                                        value_format=ValueFormat.String,
                                                        size=Size(max_value=128, min_value=10),
                                                    )
                                                ],
                                            ),
                                        ),
                                        IteratorItem(
                                            name="start",
                                            value_type="list",
                                            required=True,
                                            items=[
                                                IteratorItem(
                                                    name="number",
                                                    value_type="int",
                                                    required=True,
                                                    value_format=Format(strategy=FormatStrategy.BY_DATA_TYPE),
                                                ),
                                                IteratorItem(
                                                    name="people",
                                                    value_type="list",
                                                    required=True,
                                                    items=[
                                                        IteratorItem(
                                                            name="name",
                                                            value_type="str",
                                                            required=True,
                                                            value_format=Format(strategy=FormatStrategy.BY_DATA_TYPE),
                                                        ),
                                                        IteratorItem(
                                                            name="url",
                                                            value_type="str",
                                                            required=True,
                                                            value_format=Format(
                                                                strategy=FormatStrategy.CUSTOMIZE,
                                                                customize="https://<random_string>.com",
                                                                variables=[
                                                                    Variable(
                                                                        name="random_string",
                                                                        value_format=ValueFormat.String,
                                                                        size=Size(max_value=128, min_value=10),
                                                                    )
                                                                ],
                                                            ),
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        ),
                                        IteratorItem(
                                            name="tags",
                                            value_type="list",
                                            required=True,
                                            items=[
                                                IteratorItem(
                                                    name="",
                                                    value_type="str",
                                                    required=True,
                                                    value_format=Format(strategy=FormatStrategy.BY_DATA_TYPE),
                                                ),
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
                        "name": str,
                        "id": int,
                        "projects": [
                            {
                                "name": str,
                                "description": str,
                                "author": str,
                                "languages": ["enum list", "Python", "Scala", "Java", "JavaScript", "Kotlin"],
                                "url": r"https://[\w,.]{10,128}\.com",
                                "start": [
                                    {
                                        "number": int,
                                        "people": [{"name": str, "url": r"https://[\w,.]{10,128}\.com"}],
                                    },
                                ],
                                "tags": [str],
                            },
                        ],
                    }
                },
            ),
            # *list* type value with deeper nested data
            (
                HTTPResponse(
                    strategy=ResponseStrategy.OBJECT,
                    properties=[
                        ResponseProperty(
                            name="details",
                            required=True,
                            value_type="list",
                            items=[
                                IteratorItem(
                                    name="name",
                                    value_type="str",
                                    required=True,
                                    value_format=Format(strategy=FormatStrategy.BY_DATA_TYPE),
                                ),
                                IteratorItem(
                                    name="id",
                                    value_type="int",
                                    required=True,
                                    value_format=Format(strategy=FormatStrategy.BY_DATA_TYPE),
                                ),
                                IteratorItem(
                                    name="projects",
                                    value_type="list",
                                    required=True,
                                    items=[
                                        IteratorItem(
                                            name="name",
                                            value_type="str",
                                            required=True,
                                            value_format=Format(strategy=FormatStrategy.BY_DATA_TYPE),
                                        ),
                                        IteratorItem(
                                            name="description",
                                            value_type="str",
                                            required=True,
                                            value_format=Format(strategy=FormatStrategy.BY_DATA_TYPE),
                                        ),
                                        IteratorItem(
                                            name="author",
                                            value_type="str",
                                            required=True,
                                            value_format=Format(strategy=FormatStrategy.BY_DATA_TYPE),
                                        ),
                                        IteratorItem(
                                            name="languages",
                                            value_type="list",
                                            required=True,
                                            items=[
                                                IteratorItem(
                                                    name="",
                                                    value_type="str",
                                                    required=True,
                                                    value_format=Format(
                                                        strategy=FormatStrategy.FROM_ENUMS, enums=["Python", "Scala"]
                                                    ),
                                                ),
                                            ],
                                        ),
                                        IteratorItem(
                                            name="url",
                                            value_type="str",
                                            required=True,
                                            value_format=Format(
                                                strategy=FormatStrategy.CUSTOMIZE,
                                                customize="https://<random_string>.com",
                                                variables=[
                                                    Variable(
                                                        name="random_string",
                                                        value_format=ValueFormat.String,
                                                        size=Size(max_value=64, min_value=32),
                                                    )
                                                ],
                                            ),
                                        ),
                                        IteratorItem(
                                            name="start",
                                            value_type="list",
                                            required=True,
                                            items=[
                                                IteratorItem(
                                                    name="number",
                                                    value_type="int",
                                                    required=True,
                                                    value_format=Format(strategy=FormatStrategy.BY_DATA_TYPE),
                                                ),
                                                IteratorItem(
                                                    name="people",
                                                    value_type="list",
                                                    required=True,
                                                    items=[
                                                        IteratorItem(
                                                            name="name",
                                                            value_type="str",
                                                            required=True,
                                                            value_format=Format(strategy=FormatStrategy.BY_DATA_TYPE),
                                                        ),
                                                        IteratorItem(
                                                            name="url",
                                                            value_type="str",
                                                            required=True,
                                                            value_format=Format(
                                                                strategy=FormatStrategy.CUSTOMIZE,
                                                                customize="https://<random_string>.com",
                                                                variables=[
                                                                    Variable(
                                                                        name="random_string",
                                                                        value_format=ValueFormat.String,
                                                                        size=Size(max_value=64, min_value=32),
                                                                    )
                                                                ],
                                                            ),
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        ),
                                        IteratorItem(
                                            name="tags",
                                            value_type="list",
                                            required=True,
                                            items=[
                                                IteratorItem(
                                                    name="",
                                                    value_type="str",
                                                    required=True,
                                                    value_format=Format(strategy=FormatStrategy.BY_DATA_TYPE),
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                        )
                    ],
                ),
                {
                    "details": [
                        {
                            "name": str,
                            "id": int,
                            "projects": [
                                {
                                    "name": str,
                                    "description": str,
                                    "author": str,
                                    "languages": ["enum list", "Python", "Scala"],
                                    "url": r"https://[\w,.]{32,64}\.com",
                                    "start": [
                                        {
                                            "number": int,
                                            "people": [{"name": str, "url": r"https://[\w,.]{32,64}\.com"}],
                                        },
                                    ],
                                    "tags": [str],
                                },
                            ],
                        }
                    ],
                },
            ),
        ],
    )
    def test_response_with_nested_object_with_format(
        self,
        http_resp: Type[_HTTPResponse],
        mock_response_data: HTTPResponse,
        expect_result_data_type: Union[list, dict],
    ):
        resp_data = http_resp.generate(data=mock_response_data)
        assert resp_data is not None
        assert type(resp_data) == type(expect_result_data_type)
        self._verify_response(resp_data, expect_result_data_type)

    def _verify_response(self, http_resp: Union[list, dict], expect_value_data_type: Union[list, dict]) -> None:
        if isinstance(http_resp, dict):
            assert isinstance(expect_value_data_type, dict)
            for k, v in http_resp.items():
                assert k in expect_value_data_type.keys()
                if isinstance(v, (str, int, float, bool, Decimal)):
                    if isinstance(v, str) and expect_value_data_type[k] is not str:
                        # Check by regular expression for the customize part
                        assert re.search(expect_value_data_type[k], v) is not None
                        continue
                    assert isinstance(v, expect_value_data_type[k])
                else:
                    if isinstance(expect_value_data_type[k], list) and "enum list" in expect_value_data_type[k]:
                        # Check for the enum part
                        assert v[0] in expect_value_data_type[k]
                        continue
                    self._verify_response(v, expect_value_data_type[k])
        else:
            assert isinstance(http_resp, list)
            assert isinstance(expect_value_data_type, list)
            for v in http_resp:
                if isinstance(v, (str, int, float, bool, Decimal)):
                    if isinstance(v, str) and expect_value_data_type[0] is not str:
                        # Check by regular expression for the customize part
                        assert re.search(expect_value_data_type[0], v) is not None
                        continue
                    assert isinstance(v, expect_value_data_type[0])
                else:
                    self._verify_response(v, expect_value_data_type[0])

    def test_response_with_invalid_strategy(self, http_resp: Type[_HTTPResponse]):
        with pytest.raises(TypeError) as exc_info:
            http_resp.generate(data=_MockHTTPResponse.with_invalid_strategy())
        assert re.search(r".{0,32}invalid.{0,32}", str(exc_info.value), re.IGNORECASE)
