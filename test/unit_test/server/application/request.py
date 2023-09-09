import re
from abc import ABCMeta, abstractmethod
from unittest.mock import Mock, patch

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

    def test_api_parameters_with_missing_argument(self, request_util: FastAPIRequest):
        request = Mock()
        request.path = "/test-api-path"
        request.method = "GET"
        request.args = "parameters"

        with patch.object(request_util, "request_instance", return_value=request) as mock_request_instance:
            super().test_api_parameters_with_missing_argument(request_util)
            mock_request_instance.assert_called_once()


class TestFastAPIRequest(BaseCurrentRequestTestSpec):
    @pytest.fixture(scope="function")
    def request_util(self) -> FastAPIRequest:
        return FastAPIRequest()
