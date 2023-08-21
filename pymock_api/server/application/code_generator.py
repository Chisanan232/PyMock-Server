from abc import ABCMeta, abstractmethod
from typing import Dict, List, Optional, Union, cast

from ...model.api_config import HTTPRequest, HTTPResponse, MockAPI


class BaseWebServerCodeGenerator(metaclass=ABCMeta):
    def __init__(self):
        # The data structure would be:
        # {
        #     <API URL path>: {
        #         <HTTP method>: <API details>
        #     }
        # }
        self._mock_api_details: Dict[str, Dict[str, MockAPI]] = {}

    def annotate_function(self, api_name: str, api_config: List[MockAPI]) -> str:
        """
        [Generating code]
        """
        initial_global_server = f"""global SERVER\nSERVER = self\n"""
        define_function_for_api = self._define_api_function_pycode(api_name, api_config)
        return initial_global_server + define_function_for_api

    def _define_api_function_pycode(self, api_name: str, api_config: List[MockAPI]) -> str:
        """
        [Generating code]
        """
        api_function_name = "_".join(api_name.split("/")[1:]).replace("-", "_")
        return f"""def {api_function_name}() -> Union[str, dict]:
            {self._run_request_process_pycode()}
            {self._handle_request_process_result_pycode()}
            {self._generate_response_pycode()}
        """

    def _run_request_process_pycode(self, **kwargs) -> str:
        """
        [Generating code]
        """
        return """
        process_result = SERVER._request_process()
        """

    def _handle_request_process_result_pycode(self, **kwargs) -> str:
        """
        [Generating code]
        """
        return """
        if process_result.status_code != 200:
            return process_result
        """

    def _generate_response_pycode(self) -> str:
        """
        [Generating code]
        """
        return f"""
        return SERVER._response_process()
        """

    @abstractmethod
    def add_api(self, api_name: str, api_config: Union[MockAPI, List[MockAPI]], base_url: Optional[str] = None) -> str:
        """
        [Generating code] but doing data processing first
        """
        if isinstance(api_config, list):
            url = api_name
        elif isinstance(api_config, MockAPI):
            url = api_config.url  # type: ignore[assignment]
        else:
            raise TypeError
        self._record_api_params_info(url=self.url_path(url=url, base_url=base_url), api_config=api_config)
        return ""

    def url_path(self, url: Optional[str], base_url: Optional[str] = None) -> str:
        """
        [Data processing]
        """
        assert url
        return f"{base_url}{url}" if base_url else f"{url}"

    def _record_api_params_info(self, url: str, api_config: Union[MockAPI, List[MockAPI]]) -> None:
        """
        [Generating code] but doing data processing first
        This processing for the outer function which would be called by the generating code
        """
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

    @abstractmethod
    def _api_controller_name(self, api_name: str) -> str:
        pass


class FlaskCodeGenerator(BaseWebServerCodeGenerator):
    def add_api(self, api_name: str, api_config: Union[MockAPI, List[MockAPI]], base_url: Optional[str] = None) -> str:
        super().add_api(api_name=api_name, api_config=api_config, base_url=base_url)
        # TODO: Should align the data structure and remove this checking
        if not isinstance(api_config, list):
            raise TypeError("")
        acceptance_method = [cast(HTTPRequest, self._ensure_http(ac, "request")).method for ac in api_config]
        return f"""self.web_application.route(
                "{self.url_path(api_name, base_url)}", methods={acceptance_method}
                )({self._api_controller_name(api_name)})
            """

    def _ensure_http(self, api_config: MockAPI, http_attr: str) -> Union[HTTPRequest, HTTPResponse]:
        """
        [Data processing]
        """
        assert api_config.http and getattr(
            api_config.http, http_attr
        ), "The configuration *HTTP* value should not be empty."
        return getattr(api_config.http, http_attr)

    def _api_controller_name(self, api_name: str) -> str:
        return "_".join(api_name.split("/")[1:]).replace("-", "_")


class FastAPICodeGenerator(BaseWebServerCodeGenerator):
    def annotate_function(self, api_name: str, api_config: MockAPI) -> str:  # type: ignore[override]
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

    def add_api(self, api_name: str, api_config: Union[MockAPI, List[MockAPI]], base_url: Optional[str] = None) -> str:
        super().add_api(api_name=api_name, api_config=api_config, base_url=base_url)
        # TODO: Should align the data structure and remove this checking
        if not isinstance(api_config, MockAPI):
            raise TypeError("")
        http_method = api_config.http.request.method.lower()  # type: ignore[union-attr]
        url_path = self.url_path(api_config.url, base_url)
        return f"""self.web_application.{http_method}(
                path="{url_path}")({self._api_controller_name(api_name)})
            """

    def _api_controller_name(self, api_name: str) -> str:
        return api_name
