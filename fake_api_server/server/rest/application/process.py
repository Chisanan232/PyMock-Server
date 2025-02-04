import re
from abc import ABC, ABCMeta, abstractmethod
from pydoc import locate
from typing import Any, Dict, List, Union, cast

from fake_api_server.model import MockAPI
from fake_api_server.model.api_config.apis import (
    APIParameter,
    HTTPRequest,
    HTTPResponse,
)

from .request import BaseCurrentRequest
from .response import BaseResponse
from .response import HTTPResponse as MockHTTPResponse


class BaseMockAPIProcess(metaclass=ABCMeta):
    @abstractmethod
    def process(self, **kwargs) -> Any:
        pass


class BaseHTTPProcess(BaseMockAPIProcess, ABC):
    def __init__(self, request: BaseCurrentRequest):
        self._request: BaseCurrentRequest = request

        # The data structure would be:
        # {
        #     <API URL path>: {
        #         <HTTP method>: <API details>
        #     }
        # }
        self._mock_api_details: Dict[str, Dict[str, MockAPI]] = {}

    @property
    def mock_api_details(self) -> Dict[str, Dict[str, MockAPI]]:
        return self._mock_api_details

    @mock_api_details.setter
    def mock_api_details(self, details: Dict[str, Dict[str, MockAPI]]) -> None:
        self._mock_api_details = details

    def _get_current_request(self, **kwargs) -> Any:
        return self._request.request_instance(**kwargs)

    def _get_current_api_parameters(self, **kwargs) -> dict:
        kwargs["mock_api_details"] = self.mock_api_details
        return self._request.api_parameters(**kwargs)

    def _get_current_api_path(self, request: Any) -> str:
        return self._request.api_path(request=request)

    def _get_current_request_http_method(self, request: Any) -> str:
        return self._request.http_method(request=request)

    def _find_detail_by_api_path(self, api_path: str) -> dict:
        return self._request.find_api_detail_by_api_path(self.mock_api_details, api_path)


class HTTPRequestProcess(BaseHTTPProcess):
    def __init__(self, request: BaseCurrentRequest, response: BaseResponse):
        super().__init__(request=request)
        self._response: BaseResponse = response

    def process(self, **kwargs) -> Any:
        request = self._get_current_request(**kwargs)
        req_params = self._get_current_api_parameters(**kwargs)

        api_params_info: List[APIParameter] = self._find_detail_by_api_path(self._get_current_api_path(request))[
            self._get_current_request_http_method(request)
        ].http.request.parameters
        for param_info in api_params_info:
            # Check the required parameter
            one_req_param_value = req_params.get(param_info.name, None)
            if param_info.required and (param_info.name not in req_params.keys() or one_req_param_value is None):
                return self._generate_http_response(f"Miss required parameter *{param_info.name}*.", status_code=400)
            if one_req_param_value:
                # Check the data type of parameter
                assert param_info.value_type, "It must cannot miss the value type value of each parameters."
                value_py_data_type: type = locate(param_info.value_type)  # type: ignore[assignment]
                if value_py_data_type in [int, float, "big_decimal"] and self._request.int_type_value_is_string:
                    # For the Flask part. It would always be string type of each API parameter.
                    if re.search(r"\d{1,128}", str(one_req_param_value)) is None:
                        return self._generate_http_response(
                            f"The type of data from Font-End site (*{type(one_req_param_value)}*) is different with the "
                            f"implementation of Back-End site (*{value_py_data_type}*).",
                            status_code=400,
                        )
                else:
                    if param_info.value_type and not isinstance(one_req_param_value, value_py_data_type):
                        return self._generate_http_response(
                            f"The type of data from Font-End site (*{type(one_req_param_value)}*) is different with the "
                            f"implementation of Back-End site (*{value_py_data_type}*).",
                            status_code=400,
                        )
                # Check the element of list
                if param_info.value_type and value_py_data_type is list and param_info.items:
                    assert isinstance(one_req_param_value, list)
                    for e in one_req_param_value:
                        if len(param_info.items) > 1:
                            assert isinstance(e, dict), "The data type of item object must be *dict* type."
                            for item in param_info.items:
                                if item.required is True and item.name not in e.keys():
                                    return self._generate_http_response(
                                        f"Miss required parameter *{param_info.name}.{item.name}*.",
                                        status_code=400,
                                    )
                                if item.value_type and not isinstance(e[item.name], locate(item.value_type)):  # type: ignore[arg-type]
                                    return self._generate_http_response(
                                        f"The type of data from Font-End site (*{type(one_req_param_value)}*) is different "
                                        f"with the implementation of Back-End site (*{value_py_data_type}*).",
                                        status_code=400,
                                    )
                        elif len(param_info.items) == 1:
                            assert isinstance(
                                e, (str, int, float)
                            ), "The data type of item object must be *str*, *int* or *float* type."
                            item = param_info.items[0]
                            if item.value_type and not isinstance(e, locate(item.value_type)):  # type: ignore[arg-type]
                                return self._generate_http_response(
                                    f"The type of data from Font-End site (*{type(one_req_param_value)}*) is different "
                                    f"with the implementation of Back-End site (*{value_py_data_type}*).",
                                    status_code=400,
                                )
                # Check the data format of parameter
                assert param_info.value_type, "Miss required property *value_type*."
                assert isinstance(value_py_data_type, type)
                value_format = param_info.value_format
                if param_info.value_format and not value_format.value_format_is_match(  # type: ignore[union-attr]
                    data_type=value_py_data_type, value=one_req_param_value
                ):
                    return self._generate_http_response(
                        f"The format of data from Font-End site (param: '{param_info.name}', "
                        f"value: '{one_req_param_value}') is incorrect. Its format should be "
                        f"{param_info.value_format.expect_format_log_msg(data_type=value_py_data_type)}.",
                        status_code=400,
                    )
        return self._generate_http_response(body="OK.", status_code=200)

    def _generate_http_response(self, body: str, status_code: int) -> Any:
        return self._response.generate(body=body, status_code=status_code)


class HTTPResponseProcess(BaseHTTPProcess):
    def process(self, **kwargs) -> Union[str, dict]:
        request = self._get_current_request(**kwargs)
        api_params_info: MockAPI = self._find_detail_by_api_path(self._get_current_api_path(request))[
            self._get_current_request_http_method(request)
        ]
        response = cast(HTTPResponse, self._ensure_http(api_params_info, "response"))
        return MockHTTPResponse.generate(data=response)

    def _ensure_http(self, api_config: MockAPI, http_attr: str) -> Union[HTTPRequest, HTTPResponse]:
        assert api_config.http and getattr(
            api_config.http, http_attr
        ), "The configuration *HTTP* value should not be empty."
        return getattr(api_config.http, http_attr)
