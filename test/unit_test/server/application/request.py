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

    def test_api_parameters_with_missing_argument(self, request_util: BaseCurrentRequest):
        with pytest.raises(ValueError) as exc_info:
            request_util.api_parameters()
        assert re.search(r"missing .{0,128} argument", str(exc_info.value), re.IGNORECASE)


class TestFlaskRequest(BaseCurrentRequestTestSpec):
    @pytest.fixture(scope="function")
    def request_util(self) -> FlaskRequest:
        return FlaskRequest()

    def test_api_parameters_with_missing_argument(self, request_util: FlaskRequest):
        request = Mock()
        request.path = "/test-api-path"
        request.method = "GET"
        request.args = "parameters"

        with patch.object(request_util, "request_instance", return_value=request) as mock_request_instance:
            super().test_api_parameters_with_missing_argument(request_util)
            mock_request_instance.assert_called_once()

    @pytest.mark.parametrize(
        ("api_path", "expected_key"),
        [
            ("/foo", "/foo"),
            ("/foo/123", "/foo/<id>"),
            ("/foo/123/process/666", "/foo/<id>/process/<work_id>"),
        ],
    )
    def test_find_api_detail_by_api_path(self, request_util: FlaskRequest, api_path: str, expected_key: str):
        mock_api_details = {
            "/foo": {"value": "this is foo."},
            "/foo/<id>": {"value": "this is foo with ID *<id>*."},
            "/foo/<id>/process/<work_id>": {"value": "this is foo with ID *<id>* by worker *<work_id>*."},
        }
        detail = request_util.find_api_detail_by_api_path(mock_api_details, api_path=api_path)
        assert detail == mock_api_details[expected_key]


class TestFastAPIRequest(BaseCurrentRequestTestSpec):
    @pytest.fixture(scope="function")
    def request_util(self) -> FastAPIRequest:
        return FastAPIRequest()
