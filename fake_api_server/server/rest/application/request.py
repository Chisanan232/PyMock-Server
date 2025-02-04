import json
import re
from abc import ABCMeta, abstractmethod
from typing import Any, Dict, List

from fake_api_server._utils import import_web_lib
from fake_api_server.model.api_config.apis import APIParameter


class BaseCurrentRequest(metaclass=ABCMeta):
    int_type_value_is_string: bool = False

    @abstractmethod
    def request_instance(self, **kwargs) -> Any:
        pass

    @abstractmethod
    def api_parameters(self, **kwargs) -> dict:
        pass

    def find_api_detail_by_api_path(self, mock_api_details: Dict[str, dict], api_path: str) -> dict:
        return mock_api_details[api_path]

    @abstractmethod
    def api_path(self, request: Any) -> str:
        pass

    @abstractmethod
    def http_method(self, request: Any) -> str:
        pass


class FlaskRequest(BaseCurrentRequest):
    # For Flask, the API parameter always be string even it's integer.
    int_type_value_is_string: bool = True

    def request_instance(self, **kwargs) -> "flask.Request":  # type: ignore
        return import_web_lib.flask().request

    def api_parameters(self, **kwargs) -> dict:
        request: "flask.Request" = kwargs.get("request", self.request_instance())  # type: ignore
        handled_api_params = {}
        if request.method.upper() == "GET":
            mock_api_details = kwargs.get("mock_api_details", None)
            if not mock_api_details:
                raise ValueError("Missing necessary argument *mock_api_details*.")
            mock_api_params_info: List[APIParameter] = self.find_api_detail_by_api_path(
                mock_api_details, self.api_path(request)
            )[self.http_method(request)].http.request.parameters
            iterable_mock_api_params = list(filter(lambda p: p.value_type == "list", mock_api_params_info))

            # Get iterable parameters (only for HTTP method *GET*)
            for mock_api_param in iterable_mock_api_params:
                iterable_api_param = request.args.getlist(mock_api_param.name)
                handled_api_params[mock_api_param.name] = iterable_api_param

        # Get general parameters
        api_params = request.args if request.method.upper() == "GET" else request.form or request.data
        if api_params and isinstance(api_params, bytes):
            api_params = json.loads(api_params.decode("utf-8"))

        if handled_api_params:
            for k, v in api_params.items():
                if k not in handled_api_params.keys():
                    handled_api_params[k] = v
            return handled_api_params
        return api_params

    def find_api_detail_by_api_path(self, mock_api_details: Dict[str, dict], api_path: str) -> dict:

        def _find_mapping_api(api: str):
            simple_api_path_parts = re.sub(r"<\w{1,32}>", "<>", api).split("<>")
            search_regular = r""
            for api_part in simple_api_path_parts:
                search_regular += re.escape(api_part) + r"\w{1,256}"
            return re.search(search_regular, api_path)

        try:
            return mock_api_details[api_path]
        except KeyError:
            api_has_variable = list(filter(lambda p: re.search(r"<\w{1,32}>", p) is not None, mock_api_details.keys()))
            mapping_variable_api = list(filter(lambda api: _find_mapping_api(api) is not None, api_has_variable))
            if len(mapping_variable_api) > 1:
                mapping_variable_api = list(
                    filter(
                        lambda api: len(api) == max(map(lambda a: len(a), mapping_variable_api)), mapping_variable_api
                    )
                )
            assert len(mapping_variable_api) == 1
            return mock_api_details[mapping_variable_api[0]]

    def api_path(self, request: "flask.Request") -> str:  # type: ignore[name-defined]
        return request.path

    def http_method(self, request: "flask.Request") -> str:  # type: ignore[name-defined]
        return request.method.upper()


class FastAPIRequest(BaseCurrentRequest):
    def request_instance(self, **kwargs) -> "fastapi.Request":  # type: ignore[name-defined]
        return kwargs.get("request")

    def api_parameters(self, **kwargs) -> dict:
        mock_api_details = kwargs.get("mock_api_details", None)
        if not mock_api_details:
            raise ValueError("Missing necessary argument *mock_api_details*.")
        api_params_info: List[APIParameter] = mock_api_details[self.api_path(kwargs["request"])][
            self.http_method(kwargs["request"])
        ].http.request.parameters
        api_param_names = list(map(lambda e: e.name, api_params_info))
        api_param = {}
        if "model" in kwargs.keys():
            for param_name in api_param_names:
                if hasattr(kwargs["model"], param_name):
                    api_param[param_name] = getattr(kwargs["model"], param_name)
        return api_param

    def api_path(self, request: "fastapi.Request") -> str:  # type: ignore[name-defined]
        return request.scope["root_path"] + request.scope["route"].path

    def http_method(self, request: "fastapi.Request") -> str:  # type: ignore[name-defined]
        return request.method.upper()
