from abc import ABCMeta, abstractmethod
from collections import namedtuple
from typing import Any, Union
from unittest.mock import patch

import pytest

from pymock_api.server.application import BaseAppServer
from pymock_api.server.sgi import BaseSGI

MockerModule = namedtuple("MockerModule", ["module_path", "return_value"])


class AppServerTestSpec(metaclass=ABCMeta):
    @pytest.fixture(scope="function")
    @abstractmethod
    def sut(self) -> Union[BaseAppServer, BaseSGI]:
        pass

    @property
    @abstractmethod
    def expected_sut_type(self) -> Any:
        pass

    @abstractmethod
    def run_target_function(self, sut: Union[BaseAppServer, BaseSGI]) -> Any:
        pass

    @property
    @abstractmethod
    def mocker(self) -> MockerModule:
        pass

    def test_generating_instance_function(self, sut: Union[BaseAppServer, BaseSGI]):
        with patch(self.mocker.module_path, return_value=self.mocker.return_value) as instantiate_ps:
            web_app = self.run_target_function(sut)
            instantiate_ps.assert_called_once()
            assert isinstance(
                web_app, self.expected_sut_type
            ), f"The web application server it generates should be *{self.expected_sut_type}* type object."
