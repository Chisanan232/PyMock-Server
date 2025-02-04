"""*Web application with Python web framework*

This module provides which library of Python web framework you could use to set up a web application.
"""

import logging
from abc import ABCMeta, abstractmethod
from typing import Any, Dict, List, Optional, Union

from fake_api_server._utils import import_web_lib
from fake_api_server.model.api_config import MockAPIs
from fake_api_server.model.api_config.apis import MockAPI

from .code_generator import (
    BaseWebServerCodeGenerator,
    FastAPICodeGenerator,
    FlaskCodeGenerator,
)
from .process import HTTPRequestProcess, HTTPResponseProcess
from .request import FastAPIRequest, FlaskRequest
from .response import FastAPIResponse, FlaskResponse

logger = logging.getLogger(__name__)


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

        self._code_generator = self.init_code_generator()

        self._http_request = self.init_http_request_process()
        self._http_response = self.init_http_response_process()

    @property
    def web_application(self) -> Any:
        """:obj:`Any`: Property with only getter for the instance of web application, e.g., *Flask*, *FastAPI*, etc."""
        if not self._web_application:
            self._web_application = self.setup()
        return self._web_application

    @property
    def mock_api_details(self) -> Dict[str, Dict[str, MockAPI]]:
        if not self._mock_api_details:
            self._mock_api_details = getattr(self._code_generator, "_mock_api_details")
            return self._mock_api_details
        return self._mock_api_details

    @abstractmethod
    def setup(self) -> Any:
        """Initial object for setting up web application.

        Returns:
            An object which should be an instance of loading web application server.

        """

    @abstractmethod
    def init_code_generator(self) -> BaseWebServerCodeGenerator:
        pass

    @abstractmethod
    def init_http_request_process(self) -> HTTPRequestProcess:
        pass

    @abstractmethod
    def init_http_response_process(self) -> HTTPResponseProcess:
        pass

    def create_api(self, mocked_apis: MockAPIs) -> None:
        """
        [Entry point for generating Python code]
        """
        aggregated_mocked_apis = self._get_all_api_details(mocked_apis)
        for api_name, api_config in aggregated_mocked_apis.items():
            if api_name and api_config:
                logger.debug(f"api_name: {api_name}")
                annotate_function_pycode = self._code_generator.annotate_function(api_name, api_config)
                add_api_pycode = self._code_generator.add_api(
                    api_name, api_config, base_url=mocked_apis.base.url if mocked_apis.base else None
                )
                logger.debug(f"annotate_function_pycode: {annotate_function_pycode}")
                # pylint: disable=exec-used
                exec(annotate_function_pycode)
                # pylint: disable=exec-used
                logger.debug(f"add_api_pycode: {add_api_pycode}")
                exec(add_api_pycode)

    @abstractmethod
    def _get_all_api_details(self, mocked_apis) -> Dict[str, Union[Optional[MockAPI], List[MockAPI]]]:
        """
        Part of [Entry point for generating Python code]
        """

    def _request_process(self, **kwargs) -> "flask.Response":  # type: ignore
        self._http_request.mock_api_details = self.mock_api_details
        return self._http_request.process(**kwargs)

    def _response_process(self, **kwargs) -> Union[str, dict]:
        # TODO: Add the setting logic to unit test
        self._http_response.mock_api_details = self.mock_api_details
        return self._http_response.process(**kwargs)


class FlaskServer(BaseAppServer):
    """*Build a web application with *Flask**"""

    def setup(self) -> "flask.Flask":  # type: ignore
        return import_web_lib.flask().Flask(__name__)

    def init_code_generator(self) -> FlaskCodeGenerator:
        return FlaskCodeGenerator()

    def _get_all_api_details(self, mocked_apis: MockAPIs) -> Dict[str, List[MockAPI]]:  # type: ignore[override]
        return mocked_apis.group_by_url()

    def init_http_request_process(self) -> HTTPRequestProcess:
        return HTTPRequestProcess(
            request=FlaskRequest(),
            response=FlaskResponse(),
        )

    def init_http_response_process(self) -> HTTPResponseProcess:
        return HTTPResponseProcess(
            request=FlaskRequest(),
        )


class FastAPIServer(BaseAppServer):
    """*Build a web application with *FastAPI**"""

    def __init__(self):
        super().__init__()
        self._api_has_params: bool = False

    def setup(self) -> "fastapi.FastAPI":  # type: ignore
        return import_web_lib.fastapi().FastAPI()

    def init_code_generator(self) -> FastAPICodeGenerator:
        return FastAPICodeGenerator()

    def _get_all_api_details(self, mocked_apis: MockAPIs) -> Dict[str, Optional[MockAPI]]:  # type: ignore[override]
        return mocked_apis.apis

    def init_http_request_process(self) -> HTTPRequestProcess:
        return HTTPRequestProcess(
            request=FastAPIRequest(),
            response=FastAPIResponse(),
        )

    def init_http_response_process(self) -> HTTPResponseProcess:
        return HTTPResponseProcess(
            request=FastAPIRequest(),
        )
