import logging
import random
import re
from typing import Any, Dict, List, Optional, Tuple

import pytest

try:
    from http import HTTPMethod, HTTPStatus
except ImportError:
    from http import HTTPStatus
    from pymock_server.model.http import HTTPMethod

from pymock_server.exceptions import CannotParsingAPIDocumentVersion
from pymock_server.model import MockAPI, OpenAPIVersion
from pymock_server.model.api_config import APIConfig as PyMockEntireAPIConfig
from pymock_server.model.rest_api_doc_config._base import (
    Transferable,
    get_openapi_version,
    set_openapi_version,
)
from pymock_server.model.rest_api_doc_config._model_adapter import (
    APIAdapter,
    PropertyDetailAdapter,
    RequestParameterAdapter,
    ResponsePropertyAdapter,
)
from pymock_server.model.rest_api_doc_config.base_config import (
    BaseReferenceConfigProperty,
    BaseReferencialConfig,
    _BaseAPIConfigWithMethod,
    set_component_definition,
)
from pymock_server.model.rest_api_doc_config.config import (
    APIConfig as APIDocOneAPIConfig,
)
from pymock_server.model.rest_api_doc_config.config import (
    APIConfigWithMethodV2,
    APIConfigWithMethodV3,
    HttpConfigV2,
    HttpConfigV3,
    OpenAPIDocumentConfig,
    ReferenceConfig,
    ReferenceConfigProperty,
    RequestParameter,
    RequestSchema,
    SwaggerAPIDocumentConfig,
    get_api_doc_version,
)
from pymock_server.model.rest_api_doc_config.content_type import ContentType

# isort: off

from test.unit_test.model.rest_api_doc_config._base_config import (
    DESERIALIZE_V2_OPENAPI_DOC_TEST_CASE,
    BaseAPIConfigWithMethodTestSuite,
    BaseAPIDocConfigTestSuite,
    BaseReferencialConfigTestSuite,
    _OpenAPIDocumentDataModelTestSuite,
)
from test.unit_test.model.rest_api_doc_config._test_case import (
    DeserializeV3OpenAPIConfigTestCaseFactory,
)

# isort: on

logger = logging.getLogger(__name__)

DESERIALIZE_V2_OPENAPI_ENTIRE_CONFIG_TEST_CASE = DESERIALIZE_V2_OPENAPI_DOC_TEST_CASE.entire_config
DESERIALIZE_V2_OPENAPI_ENTIRE_API_TEST_CASE = DESERIALIZE_V2_OPENAPI_DOC_TEST_CASE.each_apis
DESERIALIZE_V2_OPENAPI_API_REQUEST_PARAMETERS_TEST_CASE = (
    DESERIALIZE_V2_OPENAPI_DOC_TEST_CASE.reference_api_http_request_parameters
)
PARSE_V2_OPENAPI_REQUEST_PARAMETERS_WITH_REFERENCE_INFO_TEST_CASE = (
    DESERIALIZE_V2_OPENAPI_DOC_TEST_CASE.general_api_http_request_parameters
)
PARSE_V2_OPENAPI_RESPONSES_TEST_CASE = DESERIALIZE_V2_OPENAPI_DOC_TEST_CASE.entire_api_http_response

DeserializeV3OpenAPIConfigTestCaseFactory.load()
V3_OPENAPI_API_DOC_CONFIG_TEST_CASE = DeserializeV3OpenAPIConfigTestCaseFactory.get_test_case()
DESERIALIZE_V3_OPENAPI_ENTIRE_CONFIG_TEST_CASE = V3_OPENAPI_API_DOC_CONFIG_TEST_CASE.entire_config
PARSE_V3_OPENAPI_RESPONSES_TEST_CASE = V3_OPENAPI_API_DOC_CONFIG_TEST_CASE.entire_api_http_response
DESERIALIZE_V3_OPENAPI_ENTIRE_API_TEST_CASE = V3_OPENAPI_API_DOC_CONFIG_TEST_CASE.each_apis


class TestReferenceConfigProperty(BaseReferencialConfigTestSuite):

    @pytest.fixture(scope="function")
    def under_test(self) -> ReferenceConfigProperty:
        return ReferenceConfigProperty()

    @pytest.mark.parametrize(
        ("under_test", "expect_result"),
        [
            (ReferenceConfigProperty(ref=None), ""),
            (ReferenceConfigProperty(ref=""), ""),
            (ReferenceConfigProperty(ref="reference value"), "ref"),
            (ReferenceConfigProperty(additionalProperties=ReferenceConfigProperty(ref=None)), ""),
            (ReferenceConfigProperty(additionalProperties=ReferenceConfigProperty(ref="")), ""),
            (
                ReferenceConfigProperty(additionalProperties=ReferenceConfigProperty(ref="reference value")),
                "additionalProperties",
            ),
        ],
    )
    def test_has_ref(self, under_test: BaseReferencialConfig, expect_result: str):
        super().test_has_ref(under_test, expect_result)

    @pytest.mark.parametrize(
        ("under_test", "expect_result"),
        [
            (ReferenceConfigProperty(ref="reference value"), "reference value"),
            (
                ReferenceConfigProperty(additionalProperties=ReferenceConfigProperty(ref="reference value")),
                "reference value",
            ),
        ],
    )
    def test_get_ref(self, under_test: BaseReferencialConfig, expect_result: str):
        super().test_get_ref(under_test, expect_result)

    @pytest.mark.parametrize(
        ("under_test", "expect_result"),
        [
            (ReferenceConfigProperty(), True),
            (ReferenceConfigProperty(value_type=None), True),
            (ReferenceConfigProperty(ref=None), True),
            (ReferenceConfigProperty(value_type=""), True),
            (ReferenceConfigProperty(ref=""), True),
            (ReferenceConfigProperty(value_type="data type", ref=""), False),
            (ReferenceConfigProperty(value_type=None, ref="reference value"), False),
        ],
    )
    def test_is_empty(self, under_test: ReferenceConfigProperty, expect_result: str):
        assert under_test.is_empty() == expect_result


class TestRequestParameter(BaseReferencialConfigTestSuite):

    @pytest.fixture(scope="function")
    def under_test(self) -> RequestParameter:
        return RequestParameter()

    def test_converting_with_invalid_items(self, under_test: RequestParameter):
        with pytest.raises(ValueError):
            under_test.deserialize(data={"items": ["invalid data type"]})

    @pytest.mark.parametrize(
        ("under_test", "expect_result"),
        [
            (RequestParameter(schema=None), ""),
            (RequestParameter(schema=RequestSchema(ref=None)), ""),
            (RequestParameter(schema=RequestSchema(ref="")), ""),
            (RequestParameter(schema=RequestSchema(ref="reference value")), "schema"),
        ],
    )
    def test_has_ref(self, under_test: BaseReferencialConfig, expect_result: str):
        super().test_has_ref(under_test, expect_result)

    @pytest.mark.parametrize(
        ("under_test", "expect_result"),
        [
            (RequestParameter(schema=RequestSchema(ref="reference value")), "reference value"),
        ],
    )
    def test_get_ref(self, under_test: BaseReferencialConfig, expect_result: str):
        super().test_get_ref(under_test, expect_result)

    @pytest.mark.parametrize(
        ("openapi_doc_data", "entire_openapi_config"), PARSE_V2_OPENAPI_REQUEST_PARAMETERS_WITH_REFERENCE_INFO_TEST_CASE
    )
    def test_process_has_ref_request_parameters_with_valid_value(
        self, under_test: RequestParameter, openapi_doc_data: dict, entire_openapi_config: dict
    ):
        # Pre-process
        set_component_definition(entire_openapi_config.get("definitions", {}))

        # Run target function
        openapi_doc_data_model = under_test.deserialize(openapi_doc_data)
        parameters = openapi_doc_data_model.process_has_ref_request_parameters()

        # Verify
        assert parameters and isinstance(parameters, list)
        assert len(parameters) == len(entire_openapi_config["definitions"]["UpdateFooRequest"]["properties"].keys())
        type_checksum = list(map(lambda p: isinstance(p, RequestParameterAdapter), parameters))
        assert False not in type_checksum

    @pytest.mark.parametrize("openapi_doc_data", DESERIALIZE_V2_OPENAPI_API_REQUEST_PARAMETERS_TEST_CASE)
    def test_process_has_ref_request_parameters_with_invalid_value(
        self, under_test: RequestParameter, openapi_doc_data: dict
    ):
        with pytest.raises(ValueError) as exc_info:
            # Run target function
            openapi_doc_data_model = under_test.deserialize(openapi_doc_data)
            openapi_doc_data_model.process_has_ref_request_parameters()

        # Verify
        assert re.search(r".{1,64}no ref.{1,64}", str(exc_info.value), re.IGNORECASE)


class TestReferenceConfig(BaseAPIDocConfigTestSuite):

    @pytest.fixture(scope="function")
    def under_test(self) -> ReferenceConfig:
        return ReferenceConfig()

    @pytest.mark.parametrize(
        ("test_response_data", "expected_value"),
        [
            (
                ReferenceConfig(value_type="object"),
                ResponsePropertyAdapter(
                    data=[
                        PropertyDetailAdapter(
                            name="THIS_IS_EMPTY", required=False, value_type=None, format=None, items=[]
                        )
                    ],
                ),
            ),
        ],
    )
    def test__process_reference_object_with_empty_body_response(
        self,
        test_response_data: ReferenceConfig,
        expected_value: ResponsePropertyAdapter,
    ):
        response_config = test_response_data.process_reference_object(
            init_response=ResponsePropertyAdapter.initial_response_data(),
        )
        assert response_config == expected_value


class TestHttpConfigV3:

    @pytest.fixture(scope="function")
    def data_model(self) -> HttpConfigV3:
        return HttpConfigV3()

    @pytest.mark.parametrize(
        ("given_content_type", "find_content_type", "expect_result"),
        [
            (ContentType.APPLICATION_JSON, ContentType.APPLICATION_JSON, ContentType.APPLICATION_JSON),
            (
                ContentType.APPLICATION_OCTET_STREAM,
                ContentType.APPLICATION_OCTET_STREAM,
                ContentType.APPLICATION_OCTET_STREAM,
            ),
            (ContentType.ALL, ContentType.ALL, ContentType.ALL),
            (ContentType.APPLICATION_OCTET_STREAM, ContentType.APPLICATION_JSON, None),
            (ContentType.APPLICATION_JSON, ContentType.ALL, None),
            (ContentType.ALL, ContentType.APPLICATION_OCTET_STREAM, None),
        ],
    )
    def test_exist_setting(
        self,
        data_model: HttpConfigV3,
        given_content_type: ContentType,
        find_content_type: ContentType,
        expect_result: Optional[ContentType],
    ):
        # given
        data_model.content = {given_content_type: HttpConfigV2()}

        # when
        exist_content_type = data_model.exist_setting(content_type=find_content_type)

        # should
        assert exist_content_type == expect_result

    @pytest.mark.parametrize(
        "content_type", [ContentType.APPLICATION_JSON, ContentType.APPLICATION_OCTET_STREAM, ContentType.ALL]
    )
    def test_get_setting(self, data_model: HttpConfigV3, content_type: ContentType):
        # given
        content_type_setting = HttpConfigV2()
        data_model.content = {content_type: content_type_setting}

        # when
        exist_content_type_setting = data_model.get_setting(content_type=content_type)

        # should
        assert exist_content_type_setting == content_type_setting

    @pytest.mark.parametrize(
        "content_type", [ContentType.APPLICATION_JSON, ContentType.APPLICATION_OCTET_STREAM, ContentType.ALL]
    )
    def test_get_setting_with_invalid_content_type(self, data_model: HttpConfigV3, content_type: ContentType):
        # given
        data_model.content = {content_type: HttpConfigV2()}

        # when
        not_exist_content_type = random.choice(list(filter(lambda t: t is not content_type, ContentType)))
        with pytest.raises(ValueError) as exc_info:
            data_model.get_setting(content_type=not_exist_content_type)

        # should
        assert re.search(r"cannot find.{0,64}content type.{0,64}", str(exc_info.value), re.IGNORECASE)


class TestAPIConfigWithMethodV2(BaseAPIConfigWithMethodTestSuite):

    @pytest.fixture(scope="function")
    def under_test(self) -> APIConfigWithMethodV2:
        return APIConfigWithMethodV2()

    @pytest.mark.parametrize(
        ("openapi_doc_data", "entire_openapi_config", "doc_version", "schema_key", "api_data_model"),
        DESERIALIZE_V2_OPENAPI_ENTIRE_API_TEST_CASE,
    )
    def test_to_request_adapter(
        self,
        under_test: APIConfigWithMethodV2,
        openapi_doc_data: dict,
        entire_openapi_config: dict,
        doc_version: OpenAPIVersion,
        schema_key: str,
        api_data_model: APIConfigWithMethodV2,
    ):
        super().test_to_request_adapter(
            under_test=under_test,
            openapi_doc_data=openapi_doc_data,
            entire_openapi_config=entire_openapi_config,
            doc_version=doc_version,
            schema_key=schema_key,
            api_data_model=api_data_model,
        )

    def _verify_req_parameter(self, openapi_doc_data: dict, parameters: List[RequestParameterAdapter]) -> None:
        assert parameters and isinstance(parameters, list)
        assert len(parameters) == len(openapi_doc_data["parameters"])
        type_checksum = list(map(lambda p: isinstance(p, RequestParameterAdapter), parameters))
        assert False not in type_checksum

    @pytest.mark.parametrize(("api_detail", "entire_config"), PARSE_V2_OPENAPI_RESPONSES_TEST_CASE)
    def test_to_responses_adapter(self, under_test: _BaseAPIConfigWithMethod, api_detail: dict, entire_config: dict):
        super().test_to_responses_adapter(
            under_test=under_test,
            api_detail=api_detail,
            entire_config=entire_config,
        )

    @property
    def _api_doc_version(self) -> OpenAPIVersion:
        return OpenAPIVersion.V2

    @property
    def _common_objects_yaml_schema(self) -> str:
        return "definitions"

    def _deserialize_as_response_model(self, resp_200: dict) -> HttpConfigV2:
        return HttpConfigV2.deserialize(resp_200)


class TestAPIConfigWithMethodV3(BaseAPIConfigWithMethodTestSuite):

    @pytest.fixture(scope="function")
    def under_test(self) -> APIConfigWithMethodV3:
        return APIConfigWithMethodV3()

    @pytest.mark.parametrize(
        ("openapi_doc_data", "entire_openapi_config", "doc_version", "schema_key", "api_data_model"),
        DESERIALIZE_V3_OPENAPI_ENTIRE_API_TEST_CASE,
    )
    def test_to_request_adapter(
        self,
        under_test: APIConfigWithMethodV3,
        openapi_doc_data: dict,
        entire_openapi_config: dict,
        doc_version: OpenAPIVersion,
        schema_key: str,
        api_data_model: APIConfigWithMethodV3,
    ):
        super().test_to_request_adapter(
            under_test=under_test,
            openapi_doc_data=openapi_doc_data,
            entire_openapi_config=entire_openapi_config,
            doc_version=doc_version,
            schema_key=schema_key,
            api_data_model=api_data_model,
        )

    def _verify_req_parameter(self, openapi_doc_data: dict, parameters: List[RequestParameterAdapter]) -> None:
        assert isinstance(parameters, list)
        logger.debug(f"openapi_doc_data: {openapi_doc_data}")
        if parameters:
            if "requestBody" in openapi_doc_data.keys():
                request_body = openapi_doc_data.get("requestBody", {})
                data_format = list(filter(lambda b: b in request_body["content"].keys(), ["application/json", "*/*"]))
                assert len(data_format) == 1
                req_body_model = RequestParameter().deserialize(request_body["content"][data_format[0]])
                assert len(parameters) == len(req_body_model.get_schema_ref().properties.keys())
            elif "parameters" in openapi_doc_data.keys():
                all_params = []
                for param in openapi_doc_data["parameters"]:
                    req_body_model = RequestParameter().deserialize(param)
                    if req_body_model.has_ref():
                        all_params.extend(list(req_body_model.get_schema_ref().properties.keys()))
                    else:
                        all_params.append(param)
                assert len(parameters) == len(all_params)
            else:
                raise ValueError("")
            type_checksum = list(map(lambda p: isinstance(p, RequestParameterAdapter), parameters))
            assert False not in type_checksum

    @pytest.mark.parametrize(("api_detail", "entire_config"), PARSE_V3_OPENAPI_RESPONSES_TEST_CASE)
    def test_to_responses_adapter(self, under_test: _BaseAPIConfigWithMethod, api_detail: dict, entire_config: dict):
        super().test_to_responses_adapter(
            under_test=under_test,
            api_detail=api_detail,
            entire_config=entire_config,
        )

    @property
    def _api_doc_version(self) -> OpenAPIVersion:
        return OpenAPIVersion.V3

    @property
    def _common_objects_yaml_schema(self) -> str:
        return "components"

    def _deserialize_as_response_model(self, resp_200: dict) -> HttpConfigV2:
        v3_http_config = HttpConfigV3.deserialize(resp_200)
        resp_format: List[ContentType] = list(
            filter(
                lambda ct: v3_http_config.exist_setting(content_type=ct) is not None,
                ContentType,
            )
        )
        logger.debug(f"has content, resp_format: {resp_format}")
        status_200_response_setting = v3_http_config.get_setting(content_type=resp_format[0])
        return status_200_response_setting


class TestAPIAdapter(_OpenAPIDocumentDataModelTestSuite):
    @pytest.fixture(scope="function")
    def data_model(self) -> APIAdapter:
        return APIAdapter()

    @pytest.mark.parametrize(
        ("openapi_doc_data", "entire_openapi_config", "doc_version", "schema_key", "api_data_model"),
        DESERIALIZE_V2_OPENAPI_ENTIRE_API_TEST_CASE + DESERIALIZE_V3_OPENAPI_ENTIRE_API_TEST_CASE,
    )
    def test_deserialize(
        self,
        data_model: Transferable,
        openapi_doc_data: dict,
        entire_openapi_config: dict,
        doc_version: OpenAPIVersion,
        schema_key: str,
        api_data_model: _BaseAPIConfigWithMethod,
    ):
        # Previous process
        set_openapi_version(doc_version)
        set_component_definition(entire_openapi_config.get(schema_key, {}))

        # Run test
        openapi_doc_data = api_data_model.deserialize(openapi_doc_data)
        super().test_deserialize(openapi_doc_data, data_model)

        # Finally
        set_openapi_version(OpenAPIVersion.V3)

    def _initial(self, data: APIAdapter) -> None:
        data.path = ""
        data.http_method = ""
        data.parameters = []
        data.response = {}

    def _verify_result(self, data: APIAdapter, og_data: _BaseAPIConfigWithMethod) -> None:

        def _verify_param_details(expect_key: List[Any], expect_params: Dict[str, BaseReferenceConfigProperty]) -> None:
            assert len(data.parameters) == len(expect_key)
            for _param in data.parameters:
                find_map_og_param: List[Tuple[str, BaseReferenceConfigProperty]] = list(
                    filter(lambda i: i[0] == _param.name, expect_params.items())
                )
                assert len(find_map_og_param) == 1
                map_og_param: BaseReferenceConfigProperty = find_map_og_param[0][1]
                assert _param.value_type == map_og_param.value_type
                assert _param.default == map_og_param.default
                if map_og_param.items:
                    assert _param.items

        assert data is not None
        assert data.path == ""
        assert data.http_method == ""

        if get_openapi_version() is OpenAPIVersion.V3:
            assert isinstance(og_data, APIConfigWithMethodV3)
            request_body = og_data.request_body
            has_ref_params: List[RequestParameter] = (
                list(filter(lambda p: p.has_ref(), og_data.parameters)) if og_data.parameters else None
            )
            if request_body:
                req_param_format: List[ContentType] = list(
                    filter(
                        lambda ct: request_body.exist_setting(content_type=ct) is not None,
                        ContentType,
                    )
                )
                logger.debug(f"has content, req_param_format: {req_param_format}")
                req_param_setting = request_body.get_setting(content_type=req_param_format[0])
                req_param_data_model = req_param_setting.get_schema_ref()

                _verify_param_details(
                    expect_key=list(req_param_data_model.properties.keys()),
                    expect_params=req_param_data_model.properties,
                )
            elif has_ref_params:
                all_params_key: List[str] = []
                all_params: Dict[str, BaseReferenceConfigProperty] = {}
                for param in has_ref_params:
                    all_params_key.extend(list(param.get_schema_ref().properties.keys()))
                    all_params.update(param.get_schema_ref().properties)

                _verify_param_details(expect_key=all_params_key, expect_params=all_params)
            else:
                assert len(data.parameters) == len(og_data.parameters)
                assert data.parameters == [param.to_adapter() for param in og_data.parameters]
        elif get_openapi_version() is OpenAPIVersion.V2:
            assert isinstance(og_data, APIConfigWithMethodV2)
            has_ref_params: List[RequestParameter] = (
                list(filter(lambda p: p.has_ref(), og_data.parameters)) if og_data.parameters else None
            )
            has_ref_all_params_key: List[str] = []
            has_ref_all_params: Dict[str, BaseReferenceConfigProperty] = {}
            for param in has_ref_params:
                has_ref_all_params_key.extend(list(param.get_schema_ref().properties.keys()))
                has_ref_all_params.update(param.get_schema_ref().properties)

            if has_ref_params:
                _verify_param_details(expect_key=og_data.parameters, expect_params=has_ref_all_params)
            else:
                assert len(data.parameters) == len(og_data.parameters)
                assert data.parameters == [param.to_adapter() for param in og_data.parameters]
        else:
            raise NotImplementedError(f"It doesn't support API document version {get_openapi_version()} yet.")

    def _given_props(self, data_model: APIAdapter) -> None:
        params = RequestParameterAdapter()
        params.name = "arg1"
        params.required = False
        params.value_type = "string"
        params.default = "default_value_pytest"

        data_model.path = "/test/v1/foo-home"
        data_model.http_method = "POST"
        data_model.parameters = [params]
        data_model.response = ResponsePropertyAdapter(
            data=[
                PropertyDetailAdapter(name="key1", value_type="str", required=True),
            ],
        )
        data_model.tags = ["first tag", "second tag"]

    def _verify_api_config_model(self, under_test: MockAPI, data_from: APIAdapter) -> None:
        assert under_test.url == data_from.path
        assert under_test.http.request.method == data_from.http_method
        assert len(under_test.http.request.parameters) == len(data_from.parameters)
        for p in under_test.http.request.parameters:
            api_param_in_data_from = list(filter(lambda _p: _p.name == p.name, data_from.parameters))
            assert len(api_param_in_data_from) == 1
            param_data_from = api_param_in_data_from[0]
            assert p.name == param_data_from.name
            assert p.required == param_data_from.required
            assert p.value_type == param_data_from.value_type
            assert p.default == param_data_from.default
            assert p.value_format is None
        assert under_test.tag == data_from.tags[0]
        assert under_test.http.response.value == ""
        assert len(under_test.http.response.properties) == 1
        assert under_test.http.response.properties[0].serialize() == data_from.response.data[0].serialize()


class TestSwaggerAPIDocumentConfig(_OpenAPIDocumentDataModelTestSuite):
    @pytest.fixture(scope="function")
    def data_model(self) -> SwaggerAPIDocumentConfig:
        return SwaggerAPIDocumentConfig()

    @pytest.mark.parametrize("openapi_doc_data", DESERIALIZE_V2_OPENAPI_ENTIRE_CONFIG_TEST_CASE)
    def test_deserialize(self, openapi_doc_data: dict, data_model: Transferable):
        set_component_definition(openapi_doc_data.get("definitions", {}))
        super().test_deserialize(openapi_doc_data, data_model)

    def _initial(self, data: OpenAPIDocumentConfig) -> None:
        data.paths = {}

    def _verify_result(self, data: OpenAPIDocumentConfig, og_data: dict) -> None:
        path_with_method_number = [len(v.keys()) for v in og_data["paths"].values()]
        data_model_apis = [len(v) for v in data.paths.values()]
        assert sum(data_model_apis) == sum(path_with_method_number)
        for path, api_config in data.paths.items():
            apis = api_config.to_adapter(path)
            for api in apis:
                assert api.path in og_data["paths"].keys()
                assert api.http_method.lower() in og_data["paths"][api.path].keys()
                assert len(api.parameters) == len(og_data["paths"][api.path][api.http_method.lower()]["parameters"])

    def _given_props(self, data_model: OpenAPIDocumentConfig) -> None:
        params = RequestParameter()
        params.name = "arg1"
        params.required = False
        params.value_type = "str"
        params.default = "default_value_pytest"

        api_with_one_method = APIConfigWithMethodV2()
        api_with_one_method.parameters = [params]
        api_with_one_method.responses = {
            HTTPStatus.OK: HttpConfigV2(
                schema=ReferenceConfigProperty(
                    value_type="str",
                )
            )
        }

        apis = APIDocOneAPIConfig()
        apis.api = {HTTPMethod.POST: api_with_one_method}

        data_model.paths = {"/test/v1/foo-home": apis}

    def _verify_api_config_model(self, under_test: PyMockEntireAPIConfig, data_from: OpenAPIDocumentConfig) -> None:
        assert len(under_test.apis.apis.keys()) == len(data_from.paths)
        for api_path, api_details in under_test.apis.apis.items():
            logger.debug(f"api_path: {api_path}")
            # Find the mapping expect API config

            def _find_path(_http_method: HTTPMethod) -> bool:
                return api_path == f'{_http_method.name.lower()}{path.replace("/", "_")}'

            expect_api_setting: Optional[Tuple[str, HTTPMethod, _BaseAPIConfigWithMethod]] = None
            for path, api_config in data_from.paths.items():
                expect_apis = list(filter(lambda _http_method: _find_path(_http_method), api_config.api.keys()))
                if len(expect_apis):
                    # (path, HTTP method, API config)
                    expect_api_setting = (path, expect_apis[0], api_config.api[expect_apis[0]])
                    break

            assert expect_api_setting
            expect_path = expect_api_setting[0]
            expect_http_method = expect_api_setting[1]
            expect_api_config = expect_api_setting[2]

            assert api_details.url == expect_path
            assert api_details.http.request.method == expect_http_method.value
            for api_param in api_details.http.request.parameters:
                api_param_in_data_from = list(
                    filter(lambda _p: _p.name == api_param.name, expect_api_config.parameters)
                )
                assert len(api_param_in_data_from) == 1
                param_data_from = api_param_in_data_from[0]
                assert param_data_from is not None
                assert api_param.required == param_data_from.required
                assert api_param.value_type == param_data_from.value_type
                assert api_param.default == param_data_from.default
            assert HTTPStatus.OK in expect_api_config.responses.keys()
            response = expect_api_config.responses[HTTPStatus.OK]
            assert isinstance(response, HttpConfigV2)
            assert api_details.http.response.properties == []

    @pytest.mark.parametrize(
        "path",
        [
            # base path
            "/api/v1/test",
            "api/v1/test",
            # API path
            "api/v1/test/foo-home",
            "/api/v1/test/foo-home",
        ],
    )
    def test__align_url_format(self, path: str, data_model: OpenAPIDocumentConfig):
        handled_url = OpenAPIDocumentConfig()._align_url_format(path=path)
        assert re.search(r"/.{1,32}/.{1,32}/.{1,32}", handled_url)


class TestOpenAPIDocumentConfig(_OpenAPIDocumentDataModelTestSuite):
    @pytest.fixture(scope="function")
    def data_model(self) -> OpenAPIDocumentConfig:
        return OpenAPIDocumentConfig()

    @pytest.mark.parametrize("openapi_doc_data", DESERIALIZE_V3_OPENAPI_ENTIRE_CONFIG_TEST_CASE)
    def test_deserialize(self, openapi_doc_data: dict, data_model: Transferable):
        """
        modify the test data at this test
        """
        set_component_definition(openapi_doc_data.get("components", {}))
        super().test_deserialize(openapi_doc_data, data_model)

    def _initial(self, data: OpenAPIDocumentConfig) -> None:
        data.paths = {}

    def _verify_result(self, data: OpenAPIDocumentConfig, og_data: dict) -> None:
        path_with_method_number = [len(v.keys()) for v in og_data["paths"].values()]
        data_model_apis = [len(v) for v in data.paths.values()]
        assert sum(data_model_apis) == sum(path_with_method_number)
        for api_path, api_config in data.paths.items():
            assert api_path in og_data["paths"].keys()
            apis = api_config.to_adapter(api_path)
            for api in apis:
                assert api.http_method.lower() in og_data["paths"][api.path].keys()

                api_http_details = og_data["paths"][api.path][api.http_method.lower()]
                if api.http_method.upper() == "GET":
                    expected_parameters = 0
                    api_req_params_data_model = list(
                        map(lambda e: RequestParameter().deserialize(e), api_http_details.get("parameters", []))
                    )
                    for param in api_req_params_data_model:
                        if param.has_ref():
                            expected_parameters += len(param.get_schema_ref().properties.keys())
                        else:
                            if param.query_in != "path":
                                expected_parameters += 1
                    assert len(api.parameters) == expected_parameters
                else:
                    request_body = api_http_details.get("requestBody", {})
                    if request_body:
                        data_format = list(
                            filter(lambda b: b in request_body["content"].keys(), ["application/json", "*/*"])
                        )
                        assert len(data_format) == 1
                        req_body_model = RequestParameter().deserialize(request_body["content"][data_format[0]])
                        assert len(api.parameters) == len(req_body_model.get_schema_ref().properties.keys())
                    else:
                        expected_parameters = 0
                        api_req_params_data_model = list(
                            map(lambda e: RequestParameter().deserialize(e), api_http_details["parameters"])
                        )
                        for param in api_req_params_data_model:
                            if param.has_ref():
                                expected_parameters += len(param.get_schema_ref().properties.keys())
                            else:
                                expected_parameters += 1
                        assert len(api.parameters) == expected_parameters

    def _given_props(self, data_model: OpenAPIDocumentConfig) -> None:
        params = RequestParameter()
        params.name = "arg1"
        params.required = False
        params.value_type = "str"
        params.default = "default_value_pytest"

        api_with_one_method = APIConfigWithMethodV2()
        api_with_one_method.parameters = [params]
        api_with_one_method.responses = {
            HTTPStatus.OK: HttpConfigV2(
                schema=ReferenceConfigProperty(
                    value_type="str",
                )
            )
        }

        apis = APIDocOneAPIConfig()
        apis.api = {HTTPMethod.POST: api_with_one_method}

        data_model.paths = {"/test/v1/foo-home": apis}

    def _verify_api_config_model(self, under_test: PyMockEntireAPIConfig, data_from: OpenAPIDocumentConfig) -> None:
        assert len(under_test.apis.apis.keys()) == len(data_from.paths)
        for api_path, api_details in under_test.apis.apis.items():
            logger.debug(f"api_path: {api_path}")
            # Find the mapping expect API config

            def _find_path(_http_method: HTTPMethod) -> bool:
                return api_path == f'{_http_method.name.lower()}{path.replace("/", "_")}'

            expect_api_setting: Optional[Tuple[str, HTTPMethod, _BaseAPIConfigWithMethod]] = None
            for path, api_config in data_from.paths.items():
                expect_apis = list(filter(lambda _http_method: _find_path(_http_method), api_config.api.keys()))
                if len(expect_apis):
                    # (path, HTTP method, API config)
                    expect_api_setting = (path, expect_apis[0], api_config.api[expect_apis[0]])
                    break

            assert expect_api_setting
            expect_path = expect_api_setting[0]
            expect_http_method = expect_api_setting[1]
            expect_api_config = expect_api_setting[2]

            assert api_details.url == expect_path
            assert api_details.http.request.method == expect_http_method.value
            for api_param in api_details.http.request.parameters:
                api_param_in_data_from = list(
                    filter(lambda _p: _p.name == api_param.name, expect_api_config.parameters)
                )
                assert len(api_param_in_data_from) == 1
                param_data_from = api_param_in_data_from[0]
                assert param_data_from is not None
                assert api_param.required == param_data_from.required
                assert api_param.value_type == param_data_from.value_type
                assert api_param.default == param_data_from.default
            assert HTTPStatus.OK in expect_api_config.responses.keys()
            response = expect_api_config.responses[HTTPStatus.OK]
            assert isinstance(response, HttpConfigV2)
            assert api_details.http.response.properties == []

    @pytest.mark.parametrize(
        "path",
        [
            # base path
            "/api/v1/test",
            "api/v1/test",
            # API path
            "api/v1/test/foo-home",
            "/api/v1/test/foo-home",
        ],
    )
    def test__align_url_format(self, path: str, data_model: OpenAPIDocumentConfig):
        handled_url = OpenAPIDocumentConfig()._align_url_format(path=path)
        assert re.search(r"/.{1,32}/.{1,32}/.{1,32}", handled_url)

    def _verify_result_with_openapi_v3(self, data: OpenAPIDocumentConfig, og_data: dict) -> None:
        path_with_method_number = [len(v.keys()) for v in og_data["paths"].values()]
        data_model_apis = [len(v) for v in data.paths.values()]
        assert sum(data_model_apis) == sum(path_with_method_number)
        for api_path, api_config in data.paths.items():
            assert api_path in og_data["paths"].keys()
            apis = api_config.to_adapter(api_path)
            for api in apis:
                assert api.http_method.lower() in og_data["paths"][api.path].keys()

                api_http_details = og_data["paths"][api.path][api.http_method.lower()]
                if api.http_method.upper() == "GET":
                    expected_parameters = 0
                    api_req_params_data_model = list(
                        map(lambda e: RequestParameter().deserialize(e), api_http_details.get("parameters", []))
                    )
                    for param in api_req_params_data_model:
                        if param.has_ref():
                            expected_parameters += len(param.get_schema_ref().properties.keys())
                        else:
                            expected_parameters += 1
                    assert len(api.parameters) == expected_parameters
                else:
                    request_body = api_http_details.get("requestBody", {})
                    if request_body:
                        data_format = list(
                            filter(lambda b: b in request_body["content"].keys(), ["application/json", "*/*"])
                        )
                        assert len(data_format) == 1
                        req_body_model = RequestParameter().deserialize(request_body["content"][data_format[0]])
                        assert len(api.parameters) == len(req_body_model.get_schema_ref().properties.keys())
                    else:
                        expected_parameters = 0
                        api_req_params_data_model = list(
                            map(lambda e: RequestParameter().deserialize(e), api_http_details["parameters"])
                        )
                        for param in api_req_params_data_model:
                            if param.has_ref():
                                expected_parameters += len(param.get_schema_ref().properties.keys())
                            else:
                                expected_parameters += 1
                        assert len(api.parameters) == expected_parameters


def test_get_api_doc_version_with_invalid_version():
    data = {"doesn't have key which could identify which version the API document is.": ""}
    with pytest.raises(CannotParsingAPIDocumentVersion):
        get_api_doc_version(data)
