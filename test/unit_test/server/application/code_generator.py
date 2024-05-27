from abc import ABCMeta, abstractmethod
from typing import List, Optional, Union
from unittest.mock import Mock, patch

import pytest

from pymock_api.model import MockAPI
from pymock_api.model.api_config.apis import HTTP, APIParameter
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

    @pytest.mark.parametrize(
        ("mock_api_key", "mock_api", "expected_api_func_naming"),
        [
            # NOTE: It should implement the test data here in child-class
        ],
    )
    def test_generate_pycode_about_annotating_function(
        self, sut: BaseWebServerCodeGenerator, mock_api_key: str, mock_api: MockAPI, expected_api_func_naming: str
    ):
        mock_api.http.request.parameters = [APIParameter().deserialize(p) for p in _Test_API_Parameters]

        annotate_function_pycode = sut.annotate_function(
            api_name=mock_api_key, api_config=self._mock_api_config_data(mock_api)
        )

        assert f"def {expected_api_func_naming}(" in annotate_function_pycode

    @abstractmethod
    def _mock_api_config_data(self, api: MockAPI) -> Union[MockAPI, List[MockAPI]]:
        pass

    @pytest.mark.parametrize("base_url", [None, "Has base URL"])
    def test_generate_pycode_about_adding_api(self, sut: BaseWebServerCodeGenerator, base_url: Optional[str]):
        # TODO: Should think a better implementation of this test
        for_test_api_name = "Function name"
        for_test_url = "this is an url path"
        for_test_req_method = "HTTP method"
        api_config = Mock(MockAPI(url=Mock(), http=Mock(HTTP())))
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
    def sut(self) -> FlaskCodeGenerator:
        return FlaskCodeGenerator()

    @pytest.mark.parametrize(
        ("mock_api_key", "mock_api", "expected_api_func_naming"),
        [
            ("/foo/api/url", MockAPI(url="/foo/api/url", http=Mock(HTTP())), "foo_api_url"),
            ("/foo-boo/api/url", MockAPI(url="/foo-boo/api/url", http=Mock(HTTP())), "foo_boo_api_url"),
        ],
    )
    def test_generate_pycode_about_annotating_function(
        self, sut: FlaskCodeGenerator, mock_api_key: str, mock_api: MockAPI, expected_api_func_naming: str
    ):
        super().test_generate_pycode_about_annotating_function(
            sut=sut, mock_api_key=mock_api_key, mock_api=mock_api, expected_api_func_naming=expected_api_func_naming
        )

    def _mock_api_config_data(self, api: MockAPI) -> List[MockAPI]:
        return [api]

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
    def sut(self) -> FastAPICodeGenerator:
        return FastAPICodeGenerator()

    @pytest.mark.parametrize(
        ("mock_api_key", "mock_api", "expected_api_func_naming"),
        [
            ("foo_api_url", MockAPI(url="/foo/api/url", http=Mock(HTTP())), "foo_api_url"),
            ("foo-boo_api_url", MockAPI(url="/foo-boo/api/url", http=Mock(HTTP())), "foo_boo_api_url"),
        ],
    )
    def test_generate_pycode_about_annotating_function(
        self, sut: FastAPICodeGenerator, mock_api_key: str, mock_api: MockAPI, expected_api_func_naming: str
    ):
        super().test_generate_pycode_about_annotating_function(
            sut=sut, mock_api_key=mock_api_key, mock_api=mock_api, expected_api_func_naming=expected_api_func_naming
        )

    def _mock_api_config_data(self, api: MockAPI) -> MockAPI:
        return api

    def _get_api_config_param(self, api_config: MockAPI) -> MockAPI:
        return api_config

    def _get_url_criteria(self, base_url: Optional[str]) -> str:
        for_test_url = "this is an url path"
        return f"{base_url}{for_test_url}" if base_url else for_test_url

    def _get_http_method_in_generating_code(self, method: str) -> str:
        return method.lower()

    @pytest.mark.parametrize(
        ("api_name", "expect_api_name"),
        [
            ("get_foo", "GetFooParameter"),
            ("get_foo-boo_export", "GetFooBooExportParameter"),
        ],
    )
    def test__api_name_as_camel_case(self, sut: FastAPICodeGenerator, api_name: str, expect_api_name: str):
        api_name_with_camel_case = sut._api_name_as_camel_case(api_name=api_name)
        assert api_name_with_camel_case == expect_api_name

    def test__add_api_with_invalid_value(self, sut: BaseWebServerCodeGenerator):
        ut_url = "This is URL path"
        ut_api_config = ["Invalid API configuration"]
        with patch.object(sut, "_record_api_params_info"):
            with pytest.raises(TypeError):
                sut.add_api(api_name=ut_url, api_config=ut_api_config)
