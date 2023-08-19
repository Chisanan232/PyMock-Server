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
        # The data structure would be:
        # {
        #     <API URL path>: {
        #         <HTTP method>: <API details>
        #     }
        # }
        self._mock_api_details: Dict[str, Dict[str, MockAPI]] = {}
        self._api_functions: Dict[str, str] = {}

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
        aggregated_mocked_apis = self._get_all_api_details(mocked_apis)
        for api_name, api_config in aggregated_mocked_apis.items():
            if api_name and api_config:
                annotate_function_pycode = self._annotate_function(api_name, api_config)  # type: ignore[arg-type]
                add_api_pycode = self._add_api(
                    api_name, api_config, base_url=mocked_apis.base.url if mocked_apis.base else None
                )
                print(f"[DEBUG in src] annotate_function_pycode: {annotate_function_pycode}")
                # pylint: disable=exec-used
                exec(annotate_function_pycode)
                # pylint: disable=exec-used
                print(f"[DEBUG in src] add_api_pycode: {add_api_pycode}")
                exec(add_api_pycode)

    @abstractmethod
    def _get_all_api_details(self, mocked_apis) -> Dict[str, Union[Optional[MockAPI], List[MockAPI]]]:
        pass

    def _annotate_function(self, api_name: str, api_config: List[MockAPI]) -> str:
        initial_global_server = f"""global SERVER\nSERVER = self\n"""
        define_function_for_api = self._define_api_function_pycode(api_name, api_config)
        return initial_global_server + define_function_for_api

    def _define_api_function_pycode(self, api_name: str, api_config: List[MockAPI]) -> str:
        api_function_name = "_".join(api_name.split("/")[1:]).replace("-", "_")
        # api_functions = []
        # for ac in api_config:
        #     function_name = f"{ac.http.request.method}_{api_function_name}"
        #     api_function = f"""def {function_name}() -> Union[str, dict]:
        #         {self._run_request_process_pycode()}
        #         {self._handle_request_process_result_pycode()}
        #         {self._generate_response_pycode(api_config)}
        #     """
        #     self._api_functions[api_function] = api_function
        #     api_functions.append(api_function)
        # return "".join(api_functions)
        return f"""def {api_function_name}() -> Union[str, dict]:
            {self._run_request_process_pycode()}
            {self._handle_request_process_result_pycode()}
            {self._generate_response_pycode()}
        """

    def _run_request_process_pycode(self, **kwargs) -> str:
        return """
        process_result = SERVER._request_process()
        """

    def _handle_request_process_result_pycode(self, **kwargs) -> str:
        return """
        if process_result.status_code != 200:
            return process_result
        """

    def _generate_response_pycode(self) -> str:
        return f"""
        return SERVER._response_process()
        """

    def _ensure_http(self, api_config: MockAPI, http_attr: str) -> Union[HTTPRequest, HTTPResponse]:
        assert api_config.http and getattr(
            api_config.http, http_attr
        ), "The configuration *HTTP* value should not be empty."
        return getattr(api_config.http, http_attr)

    @abstractmethod
    def _add_api(self, api_name: str, api_config: Union[MockAPI, List[MockAPI]], base_url: Optional[str] = None) -> str:
        if isinstance(api_config, list):
            url = api_name
        elif isinstance(api_config, MockAPI):
            url = api_config.url  # type: ignore[assignment]
        else:
            raise TypeError
        self._record_api_params_info(url=self.url_path(url=url, base_url=base_url), api_config=api_config)
        return ""

    def url_path(self, url: Optional[str], base_url: Optional[str] = None) -> str:
        assert url
        return f"{base_url}{url}" if base_url else f"{url}"

    def _record_api_params_info(self, url: str, api_config: Union[MockAPI, List[MockAPI]]) -> None:
        if isinstance(api_config, list):
            for ac in api_config:
                url_details = self._mock_api_details.get(url, {})
                url_details[ac.http.request.method] = ac  # type: ignore[union-attr]
                self._mock_api_details[url] = url_details
        elif isinstance(api_config, MockAPI):
            url_details = self._mock_api_details.get(url, {})
            url_details[api_config.http.request.method] = api_config  # type: ignore[union-attr]
            self._mock_api_details[url] = url_details
        else:
            raise TypeError("")

    def _request_process(self, **kwargs) -> "flask.Response":  # type: ignore
        request = self._get_current_request(**kwargs)
        req_params = self._get_current_api_parameters(**kwargs)

        api_params_info: List[APIParameter] = self._mock_api_details[self._get_current_api_path(request)][self._get_current_request_http_method(request)].http.request.parameters  # type: ignore[union-attr]
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
                        f"implementation of Back-End site (*{type(param_info.value_type)}*).",
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

    def _response_process(self, **kwargs) -> Union[str, dict]:
        request = self._get_current_request(**kwargs)
        api_params_info: MockAPI = self._mock_api_details[self._get_current_api_path(request)][
            self._get_current_request_http_method(request)
        ]
        response_value = self._ensure_http(api_params_info, "response").value  # type: ignore[union-attr]
        return _HTTPResponse.generate(data=response_value)

    @abstractmethod
    def _get_current_request(self, **kwargs) -> Any:
        pass

    @abstractmethod
    def _get_current_api_parameters(self, **kwargs) -> dict:
        pass

    @abstractmethod
    def _get_current_api_path(self, request: Any) -> str:
        pass

    @abstractmethod
    def _get_current_request_http_method(self, request: Any) -> str:
        pass

    @abstractmethod
    def _generate_http_response(self, body: str, status_code: int) -> Any:
        pass

    @abstractmethod
    def _api_controller_name(self, api_name: str) -> str:
        pass


class FlaskServer(BaseAppServer):
    """*Build a web application with *Flask**"""

    def setup(self) -> "flask.Flask":  # type: ignore
        return import_web_lib.flask().Flask(__name__)

    def _get_all_api_details(self, mocked_apis: MockAPIs) -> Dict[str, List[MockAPI]]:  # type: ignore[override]
        return mocked_apis.group_by_url()

    def _get_current_request(self, **kwargs) -> "flask.Request":  # type: ignore
        return import_web_lib.flask().request

    def _get_current_api_parameters(self, **kwargs) -> dict:
        request: "flask.Request" = kwargs.get("request", self._get_current_request())  # type: ignore
        api_params = request.args if request.method.upper() == "GET" else request.form or request.data or request.json
        if isinstance(api_params, bytes):
            api_params = json.loads(api_params.decode("utf-8"))
        return api_params

    def _get_current_api_path(self, request: "flask.Request") -> str:  # type: ignore[name-defined]
        return request.path

    def _get_current_request_http_method(self, request: "flask.Request") -> str:  # type: ignore[name-defined]
        return request.method.upper()

    def _generate_http_response(self, body: str, status_code: int) -> "flask.Response":  # type: ignore
        return import_web_lib.flask().Response(body, status=status_code)

    def _add_api(self, api_name: str, api_config: List[MockAPI], base_url: Optional[str] = None) -> str:  # type: ignore[override]
        super()._add_api(api_name=api_name, api_config=api_config, base_url=base_url)
        # TODO: Should align the data structure and remove this checking
        if not isinstance(api_config, list):
            raise TypeError("")
        acceptance_method = [cast(HTTPRequest, self._ensure_http(ac, "request")).method for ac in api_config]
        return f"""self.web_application.route(
            "{self.url_path(api_name, base_url)}", methods={acceptance_method}
            )({self._api_controller_name(api_name)})
        """

    def _api_controller_name(self, api_name: str) -> str:
        return "_".join(api_name.split("/")[1:]).replace("-", "_")


class FastAPIServer(BaseAppServer):
    """*Build a web application with *FastAPI**"""

    def __init__(self):
        super().__init__()
        self._api_has_params: bool = False

    def setup(self) -> "fastapi.FastAPI":  # type: ignore
        return import_web_lib.fastapi().FastAPI()

    def _get_all_api_details(self, mocked_apis: MockAPIs) -> Dict[str, Optional[MockAPI]]:  # type: ignore[override]
        return mocked_apis.apis

    def _annotate_function(self, api_name: str, api_config: MockAPI) -> str:  # type: ignore[override]
        import_fastapi = "from fastapi import Request as FastAPIRequest\n"
        initial_global_server = f"""global SERVER\nSERVER = self\n"""
        define_params_model = self._annotate_api_parameters_model_pycode(api_name, api_config)
        define_function_for_api = self._define_api_function_pycode(api_name, api_config)
        return import_fastapi + initial_global_server + define_params_model + define_function_for_api

    def _define_api_function_pycode(self, api_name: str, api_config: MockAPI) -> str:  # type: ignore[override]
        # The code implementation is different if the HTTP method is *GET* or not
        if api_config.http.request.method.upper() != "GET":  # type: ignore[union-attr]
            api_func_signature = ""
            # Process the function signature if API has parameter settings
            if api_config.http.request.parameters:  # type: ignore[union-attr]
                parameter_class = self._api_name_as_camel_case(api_name)
                api_func_signature = f"model: {parameter_class}, " if self._api_has_params else ""
            # Combine all the string value as a valid Python code
            return f"""def {api_name}({api_func_signature}request: FastAPIRequest):
                {self._run_request_process_pycode()}
                {self._handle_request_process_result_pycode()}
                {self._generate_response_pycode()}
            """
        else:
            function_args = ""
            assign_value_to_model = ""
            instantiate_model = ""
            # Process the function signature if API has parameter settings
            for param in api_config.http.request.parameters:  # type: ignore[union-attr]
                if param.default is not None:
                    if param.value_type == "str":
                        default_value = f"'{param.default}'"
                    else:
                        default_value = f"{param.default}"
                    function_args += f", {param.name}: {param.value_type} = {default_value}"
                else:
                    function_args += f", {param.name}: {param.value_type} = None"
                assign_value_to_model += f"""
        setattr(model, '{param.name}', {param.name})
                """
            # Instantiate and assign data into objects as data model
            if api_config.http.request.parameters:  # type: ignore[union-attr]
                parameter_class = self._api_name_as_camel_case(api_name)
                instantiate_model = f"""
        class {parameter_class}: pass
        model = {parameter_class}()
                """
            # Combine all the string value as a valid Python code
            return f"""def {api_name}(request: FastAPIRequest{function_args}):
                {instantiate_model}
                {assign_value_to_model}
                {self._run_request_process_pycode()}
                {self._handle_request_process_result_pycode()}
                {self._generate_response_pycode()}
            """

    def _api_name_as_camel_case(self, api_name: str) -> str:
        # api_function_name = "_".join(api_name.split("/")[1:]).replace("-", "_")
        # camel_case_api_name = "".join(map(lambda n: f"{n[0].upper()}{n[1:]}", api_function_name.split("_")))
        camel_case_api_name = "".join(map(lambda n: f"{n[0].upper()}{n[1:]}", api_name.split("_")))
        return f"{camel_case_api_name}Parameter"

    def _annotate_api_parameters_model_pycode(self, api_name: str, api_config: MockAPI) -> str:
        define_parameters_model = ""
        if api_config.http.request.parameters:  # type: ignore[union-attr]
            # The code implementation is different if the HTTP method is *GET* or not
            if api_config.http.request.method.upper() == "GET":  # type: ignore[union-attr]
                # API with HTTP method *GET* doesn't need to use 'pydantic.BaseModel' object to process API parameters
                self._api_has_params = True
                return define_parameters_model
            else:
                # API without HTTP method *GET* needs to use 'pydantic.BaseModel' object to process API parameters
                self._api_has_params = True
                # Handle the class annotation
                parameter_class = self._api_name_as_camel_case(api_name)
                define_parameters_model = f"""from pydantic import BaseModel\nclass {parameter_class}(BaseModel):\n"""
            # Handle the class's attributes
            for prop in api_config.http.request.parameters:  # type: ignore[union-attr]
                if prop.default is not None:
                    define_parameters_model += f"    {prop.name}: {prop.value_type} = '{prop.default}'\n"
                else:
                    if prop.required:
                        define_parameters_model += f"    {prop.name}: {prop.value_type}\n"
                    else:
                        define_parameters_model += f"    {prop.name}: {prop.value_type} = None\n"
            return define_parameters_model
        else:
            self._api_has_params = False
            return define_parameters_model

    def _run_request_process_pycode(self, **kwargs) -> str:
        return (
            """
        process_result = SERVER._request_process(model=model, request=request)
        """
            if self._api_has_params
            else """
        process_result = SERVER._request_process(request=request)
        """
        )

    def _generate_response_pycode(self) -> str:
        return f"""
        return SERVER._response_process(request=request)
        """

    def _get_current_request(self, **kwargs) -> "fastapi.Request":  # type: ignore[name-defined]
        return kwargs.get("request")

    def _get_current_api_parameters(self, **kwargs) -> dict:
        api_params_info: List[APIParameter] = self._mock_api_details[self._get_current_api_path(kwargs["request"])][self._get_current_request_http_method(kwargs["request"])].http.request.parameters  # type: ignore[union-attr]
        api_param_names = list(map(lambda e: e.name, api_params_info))
        api_param = {}
        if "model" in kwargs.keys():
            for param_name in api_param_names:
                if hasattr(kwargs["model"], param_name):
                    api_param[param_name] = getattr(kwargs["model"], param_name)
        return api_param

    def _get_current_api_path(self, request: "fastapi.Request") -> str:  # type: ignore[name-defined]
        return request.scope["root_path"] + request.scope["route"].path

    def _get_current_request_http_method(self, request: "fastapi.Request") -> str:  # type: ignore[name-defined]
        return request.method.upper()

    def _generate_http_response(self, body: str, status_code: int) -> "fastapi.Response":  # type: ignore
        return import_web_lib.fastapi().Response(body, status_code=status_code)

    def _add_api(self, api_name: str, api_config: MockAPI, base_url: Optional[str] = None) -> str:  # type: ignore[override]
        super()._add_api(api_name=api_name, api_config=api_config, base_url=base_url)
        http_method = api_config.http.request.method.lower()  # type: ignore[union-attr]
        url_path = self.url_path(api_config.url, base_url)
        return f"""self.web_application.{http_method}(
            path="{url_path}")({self._api_controller_name(api_name)})
        """

    def _api_controller_name(self, api_name: str) -> str:
        return api_name


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
