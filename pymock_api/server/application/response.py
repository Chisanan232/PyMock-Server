import json
import os
from abc import ABCMeta, abstractmethod
from pydoc import locate
from typing import Any, List, Union

from ..._utils import import_web_lib
from ...exceptions import FileFormatNotSupport
from ...model.api_config import ResponseProperty
from ...model.api_config.apis import HTTPResponse as MockAPIHTTPResponseConfig
from ...model.enums import ResponseStrategy


class BaseResponse(metaclass=ABCMeta):
    @abstractmethod
    def generate(self, body: str, status_code: int) -> Any:
        """
        [Data processing for both HTTP request] (May also could provide this feature for HTTP response part?)
        """


class FlaskResponse(BaseResponse):
    def generate(self, body: str, status_code: int) -> "flask.Response":  # type: ignore
        return import_web_lib.flask().Response(body, status=status_code)


class FastAPIResponse(BaseResponse):
    def generate(self, body: str, status_code: int) -> "fastapi.Response":  # type: ignore
        return import_web_lib.fastapi().Response(body, status_code=status_code)


class HTTPResponse:
    """*Data processing of HTTP response for mocked HTTP application*

    Handle the HTTP response value from the mocked APIs configuration.
    """

    valid_file_format: List[str] = ["json"]

    @classmethod
    def generate(cls, data: MockAPIHTTPResponseConfig) -> Union[str, dict]:
        """Generate the HTTP response by the data. It would try to parse it as JSON format data in the beginning. If it
        works, it returns the handled data which is JSON format. But if it gets fail, it would change to check whether
        it is a file path or not. If it is, it would search and read the file to get the content value and parse it to
        return. If it isn't, it returns the data directly.

        Args:
            data (str): The HTTP response value.

        Returns:
            A string type or dict type value.

        """
        if data.strategy is ResponseStrategy.STRING:
            return cls._generate_response_as_string(data)
        elif data.strategy is ResponseStrategy.FILE:
            return cls._generate_response_by_file(data)
        elif data.strategy is ResponseStrategy.OBJECT:
            return cls._generate_response_from_object(data)
        else:
            raise TypeError(f"Cannot identify invalid HTTP response strategy *{data.strategy}*.")

    @classmethod
    def _generate_response_as_string(cls, data: MockAPIHTTPResponseConfig) -> str:
        response_value = data.value
        try:
            return json.loads(response_value)
        except:  # pylint: disable=broad-except, bare-except
            return response_value

    @classmethod
    def _generate_response_by_file(cls, data: MockAPIHTTPResponseConfig) -> Union[str, dict]:
        file_path = data.path
        if cls._is_file(path=file_path):
            return cls._read_file(path=file_path)
        # FIXME: Here would be invalid value as file path. How to handle it?
        return data.path

    @classmethod
    def _generate_response_from_object(cls, data: MockAPIHTTPResponseConfig) -> dict:

        def _initial_resp_details(v: ResponseProperty) -> Union[str, dict]:
            assert v.value_type
            if locate(v.value_type) is str:
                # lowercase_letters = string.ascii_lowercase
                # value = "".join([random.choice(lowercase_letters) for _ in range(5)])
                value = "random string"
            elif locate(v.value_type) is int:
                # value = int("".join([random.choice([f"{i}" for i in range(10)]) for _ in range(5)]))
                value = "random integer"
            elif locate(v.value_type) in (list, dict):
                value = [] if locate(v.value_type) is list else {}  # type: ignore[assignment]
                item = {}
                for i in v.items or []:
                    item[i.name] = _initial_resp_details(i)  # type: ignore[arg-type]
                if locate(v.value_type) is list:
                    value.append(item)  # type: ignore[attr-defined]
                    assert isinstance(value, list)
                else:
                    value = item  # type: ignore[assignment]
                    assert isinstance(value, dict)
            else:
                raise NotImplementedError
            return value

        response_properties = data.properties
        response = {}
        for v in response_properties:
            # TODO: Handle the value with key *format*
            response[v.name] = _initial_resp_details(v)
        return response

    @classmethod
    def _is_file(cls, path: str) -> bool:
        """Check whether the data is a file path or not.

        Args:
            path (str): A string type value.

        Returns:
            It returns ``True`` if it is a file path and the file exists, nor it returns ``False``.

        """
        path_sep_by_dot = path.split(".")
        path_sep_by_dot_without_non = list(filter(lambda e: e, path_sep_by_dot))
        if len(path_sep_by_dot_without_non) > 1:
            support = path_sep_by_dot[-1] in cls.valid_file_format
            if not support:
                raise FileFormatNotSupport(cls.valid_file_format)
            return support
        else:
            return False

    @classmethod
    def _read_file(cls, path: str) -> dict:
        """Read file by the path to get its content and parse it as JSON format value.

        Args:
            path (str): The file path which records JSON format value.

        Returns:
            A dict type value which be parsed from JSON format value.

        """
        exist_file = os.path.exists(path)
        if not exist_file:
            raise FileNotFoundError(f"The target configuration file {path} doesn't exist.")

        with open(path, "r", encoding="utf-8") as file_stream:
            data = file_stream.read()
        return json.loads(data)
