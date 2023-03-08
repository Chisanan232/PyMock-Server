from abc import ABCMeta, abstractmethod
from typing import Any, Union
from unittest.mock import patch

import pytest

from pymock_api.server.application import BaseAppServer
from pymock_api.server.sgi import BaseSGI


class AppServerTestSpec(metaclass=ABCMeta):
    @pytest.fixture(scope="function")
    @abstractmethod
    def app_server(self) -> Union[BaseAppServer, BaseSGI]:
        pass

    @property
    @abstractmethod
    def web_app_object_type(self) -> Any:
        pass

    @abstractmethod
    def run_target_function(self, app_server: Union[BaseAppServer, BaseSGI]) -> Any:
        pass

    @property
    @abstractmethod
    def mocker(self) -> str:
        pass

    @property
    @abstractmethod
    def mocker_return_value(self) -> Any:
        pass

    def test_generating_instance_function(self, app_server: Union[BaseAppServer, BaseSGI]):
        with patch(self.mocker, return_value=self.mocker_return_value) as instantiate_ps:
            web_app = self.run_target_function(app_server)
            instantiate_ps.assert_called_once()
            assert isinstance(
                web_app, self.web_app_object_type
            ), f"The web application server it generates should be *{self.web_app_object_type}* type object."
