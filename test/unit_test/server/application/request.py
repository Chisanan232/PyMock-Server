import re

import pytest

from pymock_api.server.application.request import FastAPIRequest


class TestFastAPIRequest:
    @pytest.fixture(scope="function")
    def request_util(self) -> FastAPIRequest:
        return FastAPIRequest()

    def test_api_parameters_with_missing_argument(self, request_util: FastAPIRequest):
        with pytest.raises(ValueError) as exc_info:
            request_util.api_parameters()
        assert re.search(r"missing .{0,128} argument", str(exc_info.value), re.IGNORECASE)
