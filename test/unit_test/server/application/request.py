import re
from abc import ABCMeta, abstractmethod

import pytest

from pymock_api.server.application.request import (
    BaseCurrentRequest,
    FastAPIRequest,
    FlaskRequest,
)


class BaseCurrentRequestTestSpec(metaclass=ABCMeta):
    @pytest.fixture(scope="function")
    @abstractmethod
    def request_util(self) -> BaseCurrentRequest:
        pass

    def test_api_parameters_with_missing_argument(self, request_util: FastAPIRequest):
        with pytest.raises(ValueError) as exc_info:
            request_util.api_parameters()
        assert re.search(r"missing .{0,128} argument", str(exc_info.value), re.IGNORECASE)


class TestFlaskRequest(BaseCurrentRequestTestSpec):
    @pytest.fixture(scope="function")
    def request_util(self) -> FlaskRequest:
        return FlaskRequest()


class TestFastAPIRequest(BaseCurrentRequestTestSpec):
    @pytest.fixture(scope="function")
    def request_util(self) -> FastAPIRequest:
        return FastAPIRequest()
