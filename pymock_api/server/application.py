"""*Web application with Python web framework*

This module provides which library of Python web framework you could use to set up a web application.
"""

import json
import os
import re
from abc import ABCMeta, abstractmethod
from pydoc import locate
from typing import Any, Dict, List, Optional, Union, cast

from .._utils.importing import import_web_lib
from ..exceptions import FileFormatNotSupport
from ..model.api_config import (
    APIParameter,
    HTTPRequest,
    HTTPResponse,
    MockAPI,
    MockAPIs,
)


class BaseAppServer(metaclass=ABCMeta):
    """*Base class for set up web application*"""

    def __init__(self):
        self._web_application = None
        self._api_params: Dict[str, MockAPI] = {}

    @property
    def web_application(self) -> Any:
        """:obj:`Any`: Property with only getter for the instance of web application, e.g., *Flask*, *FastAPI*, etc."""
        if not self._web_application:
            self._web_application = self.setup()
        return self._web_application

    @abstractmethod
    def setup(self) -> Any:
        """Initial object for setting up web application.

        Returns:
            An object which should be an instance of loading web application server.

        """
        pass

    def create_api(self, mocked_apis: MockAPIs) -> None:
        for api_name, api_config in mocked_apis.apis.items():
            if api_config:
                annotate_function_pycode = self._annotate_function(api_name, api_config)
                add_api_pycode = self._add_api(
                    api_name, api_config, base_url=mocked_apis.base.url if mocked_apis.base else None
                )
                print(f"[DEBUG in src] annotate_function_pycode: {annotate_function_pycode}")
                # pylint: disable=exec-used
                exec(annotate_function_pycode)
                # pylint: disable=exec-used
                exec(add_api_pycode)

    def _annotate_function(self, api_name: str, api_config: MockAPI) -> str:
        initial_global_server = f"""global SERVER\nSERVER = self\n"""
        define_function_for_api = f"""def {api_name}() -> Union[str, dict]:
            process_result = SERVER._request_process()
            if process_result.status_code != 200:
                return process_result
            return _HTTPResponse.generate(data='{cast(HTTPResponse, self._ensure_http(api_config, "response")).value}')
        """
        return initial_global_server + define_function_for_api

    def _request_process(self, **kwargs) -> "flask.Response":  # type: ignore
        print(f"[DEBUG in src] kwargs: {kwargs}")
        request = self._get_current_request(**kwargs)
        req_params = self._get_api_current_params_info(**kwargs)

        print(f"[DEBUG in src] request: {request}")
        print(f"[DEBUG in src] req_params: {req_params}")

        api_params_info: List[APIParameter] = self._api_params[self._get_current_api_path(request)].http.request.parameters  # type: ignore[union-attr]
        for param_info in api_params_info:
            if param_info.required and param_info.name not in req_params.keys():
                return self._generate_http_response(f"Miss required parameter *{param_info.name}*.", status_code=400)
            one_req_param_value = req_params.get(param_info.name, None)
            if one_req_param_value:
                if param_info.value_type and not isinstance(one_req_param_value, locate(param_info.value_type)):  # type: ignore[arg-type]
                    return self._generate_http_response(
                        f"The type of data from Font-End site (*{type(one_req_param_value)}*) is different with the "
                        f"implementation of Back-End site (*{type(param_info.value_type)}*).",
                        status_code=400,
                    )
                if param_info.value_format and not re.search(
                    param_info.value_format, one_req_param_value, re.IGNORECASE
                ):
                    return self._generate_http_response(
                        f"The format of data from Font-End site (value: *{one_req_param_value}*) is incorrect. Its "
                        f"format should be '{param_info.value_format}'.",
                        status_code=400,
                    )
        return self._generate_http_response(body="OK.", status_code=200)

    @abstractmethod
    def _get_current_api_path(self, request: Any) -> str:
        pass

    @abstractmethod
    def _get_current_request(self, **kwargs) -> Any:
        pass

    @abstractmethod
    def _get_api_current_params_info(self, **kwargs) -> dict:
        pass

    def _ensure_http(self, api_config: MockAPI, http_attr: str) -> Union[HTTPRequest, HTTPResponse]:
        assert api_config.http and getattr(
            api_config.http, http_attr
        ), "The configuration *HTTP* value should not be empty."
        return getattr(api_config.http, http_attr)

    @abstractmethod
    def _add_api(self, api_name: str, api_config: MockAPI, base_url: Optional[str] = None) -> str:
        self._record_api_params_info(url=self.url_path(api_config=api_config, base_url=base_url), api_config=api_config)
        return ""

    def url_path(self, api_config: MockAPI, base_url: Optional[str] = None) -> str:
        return f"{base_url}{api_config.url}" if base_url else f"{api_config.url}"

    def _record_api_params_info(self, url: str, api_config: MockAPI) -> None:
        self._api_params[url] = api_config

    @abstractmethod
    def _generate_http_response(self, body: str, status_code: int) -> Any:
        pass


class FlaskServer(BaseAppServer):
    """*Build a web application with *Flask**"""

    def setup(self) -> "flask.Flask":  # type: ignore
        return import_web_lib.flask().Flask(__name__)

    # def _request_process(self, **kwargs) -> "flask.Response":  # type: ignore
    #     request = self._get_current_request(**kwargs)
    #     req_params = self._get_api_current_parms_info(request, **kwargs)
    #
    #     api_params_info: List[APIParameter] = self._api_params[request.path].http.request.parameters  # type: ignore[union-attr]
    #     for param_info in api_params_info:
    #         if param_info.required and param_info.name not in req_params.keys():
    #             return self._generate_http_response(f"Miss required parameter *{param_info.name}*.", status_code=400)
    #         one_req_param_value = req_params.get(param_info.name, None)
    #         if one_req_param_value:
    #             if param_info.value_type and not isinstance(one_req_param_value, locate(param_info.value_type)):  # type: ignore[arg-type]
    #                 return self._generate_http_response(
    #                     f"The type of data from Font-End site (*{type(one_req_param_value)}*) is different with the "
    #                     f"implementation of Back-End site (*{type(param_info.value_type)}*).",
    #                     status_code=400,
    #                 )
    #             if param_info.value_format and not re.search(
    #                 param_info.value_format, one_req_param_value, re.IGNORECASE
    #             ):
    #                 return self._generate_http_response(
    #                     f"The format of data from Font-End site (value: *{one_req_param_value}*) is incorrect. Its "
    #                     f"format should be '{param_info.value_format}'.",
    #                     status_code=400,
    #                 )
    #     return self._generate_http_response(body="OK.", status_code=200)

    def _get_current_request(self, **kwargs) -> "flask.Request":  # type: ignore
        return import_web_lib.flask().request

    def _get_current_api_path(self, request: "flask.Request") -> str:  # type: ignore
        return request.path

    def _get_api_current_params_info(self, **kwargs) -> dict:
        request: "flask.Request" = kwargs.get("request", import_web_lib.flask().request)  # type: ignore
        api_params = request.args if request.method.upper() == "GET" else request.form or request.data or request.json
        if isinstance(api_params, bytes):
            api_params = json.loads(api_params.decode("utf-8"))
        return api_params

    def _generate_http_response(self, body: str, status_code: int) -> "flask.Response":  # type: ignore
        return import_web_lib.flask().Response(body, status=status_code)

    def _add_api(self, api_name: str, api_config: MockAPI, base_url: Optional[str] = None) -> str:
        super()._add_api(api_name=api_name, api_config=api_config, base_url=base_url)
        return f"""self.web_application.route(
            "{self.url_path(api_config, base_url)}", methods=["{cast(HTTPRequest, self._ensure_http(api_config, "request")).method}"]
            )({api_name})
        """


class FastAPIServer(BaseAppServer):
    """*Build a web application with *FastAPI**"""

    def setup(self) -> "fastapi.FastAPI":  # type: ignore
        return import_web_lib.fastapi().FastAPI()

    def _annotate_function(self, api_name: str, api_config: MockAPI) -> str:
        initial_global_server = f"""global SERVER\nSERVER = self\n"""
        new_api_name = "".join(map(lambda n: f"{n[0].upper()}{n[1:]}", api_name.split("_")))
        parameter_class = f"{new_api_name}Parameter"
        define_parameters_model = f"""from pydantic import BaseModel\nclass {parameter_class}(BaseModel):\n"""
        for prop in api_config.http.request.parameters:  # type: ignore[union-attr]
            if prop.default:
                define_parameters_model += f"    {prop.name}: {prop.value_type} = '{prop.default}'\n"
            else:
                define_parameters_model += f"    {prop.name}: {prop.value_type}\n"
        import_fastapi = "from fastapi import Request as FastAPIRequest\n"
        define_function_for_api = f"""def {api_name}(model: {parameter_class}, request: FastAPIRequest):
            process_result = SERVER._request_process(model=model, request=request)
            if process_result.status_code != 200:
                return process_result
            return _HTTPResponse.generate(data='{cast(HTTPResponse, self._ensure_http(api_config, "response")).value}')
        """
        return import_fastapi + initial_global_server + define_parameters_model + define_function_for_api

    # def _request_process(self, **kwargs) -> "fastapi.Response":  # type: ignore
    #     print(f"[DEBUG in src] Here is request process by FastAPI.")
    #     # FIXME: Implement the request process in FastAPI strategy
    #     request: "fastapi.Request" = self._get_current_request(**kwargs)
    #     api_params_info: List[APIParameter] = self._api_params[request.scope['root_path'] + request.scope['route'].path].http.request.parameters  # type: ignore[union-attr]
    #     for param_info in api_params_info:
    #         if param_info.required and param_info.name not in kwargs.keys():
    #             return self._generate_http_response(f"Miss required parameter *{param_info.name}*.", status_code=400)
    #     return self._generate_http_response("OK.", status_code=200)

    def _get_current_request(self, **kwargs) -> "fastapi.Request":  # type: ignore[name-defined]
        return kwargs.get("request")

    def _get_current_api_path(self, request: "fastapi.Request") -> str:  # type: ignore[name-defined]
        print(f"[DEBUG in src] request: {request}")
        return request.scope["root_path"] + request.scope["route"].path

    def _get_api_current_params_info(self, **kwargs) -> dict:
        api_params_info: List[APIParameter] = self._api_params[self._get_current_api_path(kwargs["request"])].http.request.parameters  # type: ignore[union-attr]
        api_param_names = list(map(lambda e: e.name, api_params_info))
        api_param = {}
        for param_name in api_param_names:
            api_param[param_name] = getattr(kwargs["model"], param_name)
        return api_param

    def _generate_http_response(self, body: str, status_code: int) -> "fastapi.Response":  # type: ignore
        return import_web_lib.fastapi().Response(body, status_code=status_code)

    def _add_api(self, api_name: str, api_config: MockAPI, base_url: Optional[str] = None) -> str:
        super()._add_api(api_name=api_name, api_config=api_config, base_url=base_url)
        return f"""self.web_application.api_route(
            path="{self.url_path(api_config, base_url)}", methods=["{cast(HTTPRequest, self._ensure_http(api_config, "request")).method}"]
            )({api_name})
        """


class _HTTPResponse:
    """*Data processing of HTTP response for mocked HTTP application*

    Handle the HTTP response value from the mocked APIs configuration.
    """

    valid_file_format: List[str] = ["json"]

    @classmethod
    def generate(cls, data: str) -> Union[str, dict]:
        """Generate the HTTP response by the data. It would try to parse it as JSON format data in the beginning. If it
        works, it returns the handled data which is JSON format. But if it gets fail, it would change to check whether
        it is a file path or not. If it is, it would search and read the file to get the content value and parse it to
        return. If it isn't, it returns the data directly.

        Args:
            data (str): The HTTP response value.

        Returns:
            A string type or dict type value.

        """
        try:
            return json.loads(data)
        except:  # pylint: disable=broad-except, bare-except
            if cls._is_file(path=data):
                return cls._read_file(path=data)
        return data

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
