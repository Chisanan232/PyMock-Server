import json
from abc import ABCMeta, abstractmethod
from typing import Any, List

from ..._utils import import_web_lib
from ...model.api_config import APIParameter


class BaseCurrentRequest(metaclass=ABCMeta):
    @abstractmethod
    def request_instance(self, **kwargs) -> Any:
        pass

    @abstractmethod
    def api_parameters(self, **kwargs) -> dict:
        pass

    @abstractmethod
    def api_path(self, request: Any) -> str:
        pass

    @abstractmethod
    def http_method(self, request: Any) -> str:
        pass


class FlaskRequest(BaseCurrentRequest):
    def request_instance(self, **kwargs) -> "flask.Request":  # type: ignore
        return import_web_lib.flask().request

    def api_parameters(self, **kwargs) -> dict:
        request: "flask.Request" = kwargs.get("request", self.request_instance())  # type: ignore
        api_params = request.args if request.method.upper() == "GET" else request.form or request.data or request.json
        if isinstance(api_params, bytes):
            api_params = json.loads(api_params.decode("utf-8"))
        return api_params

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
