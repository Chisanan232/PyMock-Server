from abc import ABCMeta, abstractmethod
from typing import List, Optional, Union
from unittest.mock import Mock, patch

import pytest

from pymock_api.model.api_config import APIParameter, MockAPI
from pymock_api.server.application.code_generator import (
    BaseWebServerCodeGenerator,
    FastAPICodeGenerator,
    FlaskCodeGenerator,
)

from ...._values import _Test_API_Parameters


class WebServerCodeGeneratorTestSpec(metaclass=ABCMeta):
    @pytest.fixture(scope="function")
    @abstractmethod
    def sut(self) -> BaseWebServerCodeGenerator:
        pass

    def test_generate_pycode_about_annotating_function(self, sut: BaseWebServerCodeGenerator):
        for_test_api_name = "/Function/name"
        api = Mock(MockAPI(url=Mock(), http=Mock()))
        api.http.request.parameters = [APIParameter().deserialize(p) for p in _Test_API_Parameters]

        annotate_function_pycode = sut.annotate_function(api_name=for_test_api_name, api_config=api)

        assert sut._api_controller_name(for_test_api_name) in annotate_function_pycode

    @pytest.mark.parametrize("base_url", [None, "Has base URL"])
    def test_generate_pycode_about_adding_api(self, sut: BaseWebServerCodeGenerator, base_url: Optional[str]):
        # TODO: Should think a better implementation of this test
        for_test_api_name = "Function name"
        for_test_url = "this is an url path"
        for_test_req_method = "HTTP method"
        api_config = Mock(MockAPI(url=Mock(), http=Mock()))
        api_config.url = for_test_url
        api_config.http.request.method = for_test_req_method

        add_api_pycode = sut.add_api(
            api_name=for_test_api_name, api_config=self._get_api_config_param(api_config), base_url=base_url
        )

        assert (
            self._get_url_criteria(base_url) in add_api_pycode
            and self._get_http_method_in_generating_code(for_test_req_method) in add_api_pycode
        )

    @abstractmethod
    def _get_api_config_param(self, api_config: MockAPI) -> Union[MockAPI, List[MockAPI]]:
        pass

    @abstractmethod
    def _get_url_criteria(self, base_url: Optional[str]) -> str:
        pass

    @abstractmethod
    def _get_http_method_in_generating_code(self, method: str) -> str:
        pass

    def test__record_api_params_info_with_invalid_value(self, sut: BaseWebServerCodeGenerator):
        ut_url = "This is URL path"
        ut_api_config = "Invalid API configuration"
        with pytest.raises(TypeError):
            sut._record_api_params_info(url=ut_url, api_config=ut_api_config)


class TestFlaskCodeGenerator(WebServerCodeGeneratorTestSpec):
    @pytest.fixture(scope="function")
    def sut(self) -> BaseWebServerCodeGenerator:
        return FlaskCodeGenerator()

    def _get_api_config_param(self, api_config: MockAPI) -> List[MockAPI]:
        return [api_config]

    def _get_url_criteria(self, base_url: Optional[str]) -> str:
        return "Function name"

    def _get_http_method_in_generating_code(self, method: str) -> str:
        return method

    def test__add_api_with_invalid_value(self, sut: BaseWebServerCodeGenerator):
        ut_url = "This is URL path"
        ut_api_config = MockAPI(url=ut_url)
        with patch.object(sut, "_record_api_params_info"):
            with pytest.raises(TypeError):
                sut.add_api(api_name=ut_url, api_config=ut_api_config)


class TestFastAPICodeGenerator(WebServerCodeGeneratorTestSpec):
    @pytest.fixture(scope="function")
    def sut(self) -> BaseWebServerCodeGenerator:
        return FastAPICodeGenerator()

    def _get_api_config_param(self, api_config: MockAPI) -> MockAPI:
        return api_config

    def _get_url_criteria(self, base_url: Optional[str]) -> str:
        for_test_url = "this is an url path"
        return f"{base_url}{for_test_url}" if base_url else for_test_url

    def _get_http_method_in_generating_code(self, method: str) -> str:
        return method.lower()

    def test__add_api_with_invalid_value(self, sut: BaseWebServerCodeGenerator):
        ut_url = "This is URL path"
        ut_api_config = ["Invalid API configuration"]
        with patch.object(sut, "_record_api_params_info"):
            with pytest.raises(TypeError):
                sut.add_api(api_name=ut_url, api_config=ut_api_config)
