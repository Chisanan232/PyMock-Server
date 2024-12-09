import re
from abc import ABCMeta, abstractmethod
from collections import namedtuple
from typing import Dict, List, Optional, Union
from unittest.mock import Mock, patch

import pytest

from pymock_server.model import MockAPI
from pymock_server.model.api_config.apis import HTTP, APIParameter
from pymock_server.server.rest.application.code_generator import (
    BaseWebServerCodeGenerator,
    FastAPICodeGenerator,
    FlaskCodeGenerator,
)

# isort: off
from test._values import _Test_API_Parameters

# isort: on


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
        return annotate_function_pycode

    @abstractmethod
    def _mock_api_config_data(self, api: MockAPI) -> Union[MockAPI, List[MockAPI]]:
        pass

    @pytest.mark.parametrize("base_url", [None, "Has base URL"])
    def test_generate_pycode_about_adding_api(self, sut: BaseWebServerCodeGenerator, base_url: Optional[str]):
        for_test_api_name = "Function name"
        for_test_url = "this is an url path"
        for_test_req_method = "HTTP method"
        api_config = Mock(MockAPI(url=Mock(), http=Mock(HTTP())))
        api_config.url = for_test_url
        api_config.http.request.method = for_test_req_method

        add_api_pycode = sut.add_api(
            api_name=for_test_api_name, api_config=self._get_api_config_param(api_config), base_url=base_url
        )

        clean_add_api_pycode = add_api_pycode.replace("  ", "").replace("\n", "")
        expect_pycode = self._expect_controller_pycode(
            method=for_test_req_method, base_url=base_url, url=for_test_url, api_name=for_test_api_name
        )
        search_expect_pycode = re.search(re.escape(expect_pycode), clean_add_api_pycode)

        assert (
            self._get_url_criteria(base_url) in add_api_pycode
            and self._get_http_method_in_generating_code(for_test_req_method) in add_api_pycode
        )
        assert search_expect_pycode is not None

    @abstractmethod
    def _get_api_config_param(self, api_config: MockAPI) -> Union[MockAPI, List[MockAPI]]:
        pass

    @property
    def _server_instance(self) -> str:
        return "self.web_application"

    @abstractmethod
    def _expect_controller_pycode(self, method: str, base_url: Optional[str], url: str, api_name: str) -> str:
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

    @pytest.mark.parametrize(
        ("api_name", "expect_var_mapping_table"),
        [
            # NOTE: It should implement the test data here in child-class
        ],
    )
    def test__parse_variable_in_api(
        self, sut: BaseWebServerCodeGenerator, api_name: str, expect_var_mapping_table: Dict[str, str]
    ):
        var_mapping_table = sut._parse_variable_in_api(api_function_name=api_name)
        assert var_mapping_table == expect_var_mapping_table


class TestFlaskCodeGenerator(WebServerCodeGeneratorTestSpec):
    @pytest.fixture(scope="function")
    def sut(self) -> FlaskCodeGenerator:
        return FlaskCodeGenerator()

    @pytest.mark.parametrize(
        ("mock_api_key", "mock_api", "expected_api_func_naming"),
        [
            ("/foo/api/url", MockAPI(url="/foo/api/url", http=Mock(HTTP())), "foo_api_url"),
            ("/foo-boo/api/url", MockAPI(url="/foo-boo/api/url", http=Mock(HTTP())), "foo_boo_api_url"),
            (
                "/foo-boo/api/url/<id>",
                MockAPI(url="/foo-boo/api/url/<id>", http=Mock(HTTP())),
                "foo_boo_api_url_var_id",
            ),
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

    def _expect_controller_pycode(self, method: str, base_url: Optional[str], url: str, api_name: str) -> str:
        """
        Python code:
        self.web_application.route("Function name", methods=['HTTP method'])()
        """
        new_api_name = f"{base_url}{api_name}" if base_url else api_name
        return f"{self._server_instance}.route(\"{new_api_name}\", methods=['{self._get_http_method_in_generating_code(method)}'])()"

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

    @pytest.mark.parametrize(
        ("api_name", "expect_var_mapping_table"),
        [
            ("/foo/api/url", {}),
            ("/foo-boo/api/url", {}),
            ("/foo/api/url/<id>", {"<id>": "var_id"}),
            ("/foo-boo/api/url/<id>", {"<id>": "var_id"}),
            ("/foo/api/url/<id>/test/<other-id>", {"<id>": "var_id", "<other-id>": "var_other_id"}),
            ("/foo/api/url/<id>/<other-id>", {"<id>": "var_id", "<other-id>": "var_other_id"}),
            ("/foo-boo/api/url/<id>", {"<id>": "var_id"}),
            ("/foo-boo/api/url/<id>/test/<other-id>", {"<id>": "var_id", "<other-id>": "var_other_id"}),
            ("/foo-boo/api/url/<id>/<other-id>", {"<id>": "var_id", "<other-id>": "var_other_id"}),
        ],
    )
    def test__parse_variable_in_api(
        self, sut: BaseWebServerCodeGenerator, api_name: str, expect_var_mapping_table: Dict[str, str]
    ):
        super().test__parse_variable_in_api(
            sut=sut, api_name=api_name, expect_var_mapping_table=expect_var_mapping_table
        )


FastAPIGenCodeExpect = namedtuple("FastAPIGenCodeExpect", ("func_naming", "req_body_obj_naming"))


class TestFastAPICodeGenerator(WebServerCodeGeneratorTestSpec):
    @pytest.fixture(scope="function")
    def sut(self) -> FastAPICodeGenerator:
        return FastAPICodeGenerator()

    @pytest.mark.parametrize(
        ("mock_api_key", "mock_api", "expect"),
        [
            (
                "foo_api_url",
                MockAPI(url="/foo/api/url", http=Mock(HTTP())),
                FastAPIGenCodeExpect("foo_api_url", "FooApiUrlParameter"),
            ),
            (
                "foo-boo_api_url",
                MockAPI(url="/foo-boo/api/url", http=Mock(HTTP())),
                FastAPIGenCodeExpect("foo_boo_api_url", "FooBooApiUrlParameter"),
            ),
            (
                "foo-boo_api_url_{id}",
                MockAPI(url="/foo-boo/api/url/{id}", http=Mock(HTTP())),
                FastAPIGenCodeExpect("foo_boo_api_url_var_id", "FooBooApiUrlVarIdParameter"),
            ),
        ],
    )
    def test_generate_pycode_about_annotating_function(
        self,
        sut: FastAPICodeGenerator,
        mock_api_key: str,
        mock_api: MockAPI,
        expect: FastAPIGenCodeExpect,
    ):
        annotate_function_pycode = super().test_generate_pycode_about_annotating_function(
            sut=sut, mock_api_key=mock_api_key, mock_api=mock_api, expected_api_func_naming=expect.func_naming
        )

        assert expect.req_body_obj_naming in annotate_function_pycode

    def _mock_api_config_data(self, api: MockAPI) -> MockAPI:
        return api

    def _get_api_config_param(self, api_config: MockAPI) -> MockAPI:
        return api_config

    def _expect_controller_pycode(self, method: str, base_url: Optional[str], url: str, api_name: str) -> str:
        """
        Python code:
        self.web_application.http method(path="this is an url path")(function name)
        """
        api_path = f"{base_url}{url}" if base_url else url
        return (
            f'{self._server_instance}.{self._get_http_method_in_generating_code(method)}(path="{api_path}")({api_name})'
        )

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

    @pytest.mark.parametrize(
        ("api_name", "expect_var_mapping_table"),
        [
            ("foo_api_url", {}),
            ("foo-boo_api_url", {}),
            ("foo_api_url_{id}", {"{id}": "var_id"}),
            ("foo-boo_api_url_{id}", {"{id}": "var_id"}),
            ("foo_api_url_{id}_test_{other-id}", {"{id}": "var_id", "{other-id}": "var_other_id"}),
            ("foo_api_url_{id}_{other-id}", {"{id}": "var_id", "{other-id}": "var_other_id"}),
            ("foo-boo_api_url_{id}", {"{id}": "var_id"}),
            ("foo-boo_api_url_{id}_test_{other-id}", {"{id}": "var_id", "{other-id}": "var_other_id"}),
            ("foo-boo_api_url_{id}_{other-id}", {"{id}": "var_id", "{other-id}": "var_other_id"}),
        ],
    )
    def test__parse_variable_in_api(
        self, sut: BaseWebServerCodeGenerator, api_name: str, expect_var_mapping_table: Dict[str, str]
    ):
        super().test__parse_variable_in_api(
            sut=sut, api_name=api_name, expect_var_mapping_table=expect_var_mapping_table
        )
