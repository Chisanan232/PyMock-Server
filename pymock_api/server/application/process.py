import re
from abc import ABC, ABCMeta, abstractmethod
from pydoc import locate
from typing import Any, Dict, List, Union

from ...model.api_config import APIParameter, HTTPRequest, HTTPResponse, MockAPI
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


class HTTPRequestProcess(BaseHTTPProcess):
    def __init__(self, request: BaseCurrentRequest, response: BaseResponse):
        super().__init__(request=request)
        self._response: BaseResponse = response

    def process(self, **kwargs) -> Any:
        request = self._get_current_request(**kwargs)
        req_params = self._get_current_api_parameters(**kwargs)

        api_params_info: List[APIParameter] = self.mock_api_details[self._get_current_api_path(request)][self._get_current_request_http_method(request)].http.request.parameters  # type: ignore[union-attr]
        for param_info in api_params_info:
            # Check the required parameter
            one_req_param_value = req_params.get(param_info.name, None)
            if param_info.required and (param_info.name not in req_params.keys() or one_req_param_value is None):
                return self._generate_http_response(f"Miss required parameter *{param_info.name}*.", status_code=400)
            if one_req_param_value:
                # Check the data type of parameter
                if param_info.value_type and not isinstance(one_req_param_value, locate(param_info.value_type)):  # type: ignore[arg-type]
                    return self._generate_http_response(
                        f"The type of data from Font-End site (*{type(one_req_param_value)}*) is different with the "
                        f"implementation of Back-End site (*{locate(param_info.value_type)}*).",
                        status_code=400,
                    )
                # Check the element of list
                if param_info.value_type and locate(param_info.value_type) is list and param_info.items:
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
                                        f"with the implementation of Back-End site (*{locate(param_info.value_type)}*).",
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
                                    f"with the implementation of Back-End site (*{locate(param_info.value_type)}*).",
                                    status_code=400,
                                )
                # Check the data format of parameter
                if param_info.value_format and not re.search(
                    param_info.value_format, one_req_param_value, re.IGNORECASE
                ):
                    return self._generate_http_response(
                        f"The format of data from Font-End site (value: *{one_req_param_value}*) is incorrect. Its "
                        f"format should be '{param_info.value_format}'.",
                        status_code=400,
                    )
        return self._generate_http_response(body="OK.", status_code=200)

    def _generate_http_response(self, body: str, status_code: int) -> Any:
        return self._response.generate(body=body, status_code=status_code)


class HTTPResponseProcess(BaseHTTPProcess):
    def process(self, **kwargs) -> Union[str, dict]:
        request = self._get_current_request(**kwargs)
        api_params_info: MockAPI = self.mock_api_details[self._get_current_api_path(request)][
            self._get_current_request_http_method(request)
        ]
        response_value = self._ensure_http(api_params_info, "response").value  # type: ignore[union-attr]
        return MockHTTPResponse.generate(data=response_value)

    def _ensure_http(self, api_config: MockAPI, http_attr: str) -> Union[HTTPRequest, HTTPResponse]:
        assert api_config.http and getattr(
            api_config.http, http_attr
        ), "The configuration *HTTP* value should not be empty."
        return getattr(api_config.http, http_attr)
